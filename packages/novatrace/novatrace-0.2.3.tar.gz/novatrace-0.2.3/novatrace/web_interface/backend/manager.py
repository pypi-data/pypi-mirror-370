import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from novatrace.database.model import Session, Project, Trace, TraceTypes
    from sqlalchemy import func, desc, and_, or_
except ImportError:
    print("Warning: Could not import database models")

class DatabaseManager:
    def _init_(self):
        try:
            # Buscar connect.db dinámicamente desde el directorio actual hacia arriba
            self.db_path = self._find_connect_db()
            print(f"Dashboard connecting to database: {self.db_path}")

            # Create engine using the same path as NovaTrace
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            self.engine = create_engine(f"sqlite:///{self.db_path}")
            SessionLocal = sessionmaker(bind=self.engine)
            self.session = SessionLocal()

        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.session = None

    def _find_connect_db(self):
        """Buscar connect.db dinámicamente desde múltiples puntos de referencia."""
        import sys

        # Múltiples puntos de inicio para buscar connect.db
        search_starting_points = [
            os.getcwd(),  # Directorio de trabajo actual
            os.path.dirname(sys.argv[0]) if sys.argv[0] else os.getcwd(),  # Directorio del script principal
            os.path.abspath('.'),  # Directorio absoluto actual
        ]

        # Agregar directorios únicos de sys.path que no sean de librerías
        for path in sys.path:
            if path and not path.startswith(('/usr', '/opt', '.venv', 'lib', 'site-packages')):
                search_starting_points.append(path)

        # Remover duplicados manteniendo el orden
        unique_starting_points = []
        for point in search_starting_points:
            if point and point not in unique_starting_points:
                unique_starting_points.append(point)

        for start_dir in unique_starting_points:
            if not os.path.exists(start_dir):
                continue

            # Primero intentar en el directorio de inicio
            db_path = os.path.join(start_dir, 'connect.db')
            if os.path.exists(db_path):
                print(f"Found connect.db at: {db_path}")
                return db_path

            # Buscar hacia arriba en la estructura de directorios
            search_dir = start_dir
            max_levels = 5  # Limitar la búsqueda a 5 niveles hacia arriba

            for level in range(max_levels):
                parent_dir = os.path.dirname(search_dir)
                if parent_dir == search_dir:  # Llegamos a la raíz del sistema
                    break

                db_path = os.path.join(parent_dir, 'connect.db')
                if os.path.exists(db_path):
                    print(f"Found connect.db in parent directory (level {level + 1}): {db_path}")
                    return db_path

                search_dir = parent_dir

        # Si no se encuentra connect.db, usar el directorio de trabajo actual
        fallback_path = os.path.join(os.getcwd(), 'connect.db')
        print(f"connect.db not found, using fallback: {fallback_path}")
        return fallback_path

    def get_dashboard_stats(self):
        """Get basic dashboard statistics."""
        if not self.session:
            return {}
        
        try:
            # Basic counts
            total_sessions = self.session.query(Session).count()
            total_projects = self.session.query(Project).count()
            total_traces = self.session.query(Trace).count()
            
            # Cost and tokens
            cost_tokens = self.session.query(
                func.sum(Trace.call_cost).label('total_cost'),
                func.sum(Trace.input_tokens + Trace.output_tokens).label('total_tokens')
            ).first()
            
            total_cost = float(cost_tokens.total_cost or 0)
            total_tokens = int(cost_tokens.total_tokens or 0)
            
            # Trace types stats
            trace_types = self.session.query(
                TraceTypes.name,
                func.count(Trace.id).label('count')
            ).join(Trace).group_by(TraceTypes.name).all()
            
            trace_types_stats = {trace_type.name: trace_type.count for trace_type in trace_types}
            
            # Recent projects
            recent_projects = self.session.query(Project).order_by(desc(Project.created_at)).limit(5).all()
            recent_projects_list = [
                {
                    "name": project.name,
                    "created_at": project.created_at.strftime("%Y-%m-%d %H:%M") if project.created_at else "Unknown"
                }
                for project in recent_projects
            ]
            
            # Recent traces
            recent_traces = self.session.query(
                Trace, Project.name.label('project_name'), TraceTypes.name.label('type_name')
            ).join(Project).join(TraceTypes).order_by(desc(Trace.request_time)).limit(10).all()
            
            recent_traces_list = []
            for trace in recent_traces:
                # Limpiar el valor del costo
                cost_value = trace.Trace.call_cost or 0
                try:
                    # Convertir a float y luego formatear con 4 decimales
                    clean_cost = float(str(cost_value).replace('$', ''))
                    formatted_cost = f"${clean_cost:.4f}"
                except (ValueError, TypeError):
                    formatted_cost = "$0.0000"
                
                recent_traces_list.append({
                    "type_name": trace.type_name,
                    "project_name": trace.project_name,
                    "duration_ms": int(trace.Trace.duration_ms or 0),
                    "total_tokens": int((trace.Trace.input_tokens or 0) + (trace.Trace.output_tokens or 0)),
                    "call_cost": formatted_cost
                })
            
            return {
                "total_sessions": total_sessions,
                "total_projects": total_projects,
                "total_traces": total_traces,
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "trace_types_stats": trace_types_stats,
                "recent_projects": recent_projects_list,
                "recent_traces": recent_traces_list
            }
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
    
    def get_model_usage_by_project(self):
        """Get model usage statistics by project."""
        if not self.session:
            return []
        
        try:
            # Get traces grouped by project and model
            project_model_usage = self.session.query(
                Project.name.label('project_name'),
                Trace.model_name.label('model_name'),
                func.count(Trace.id).label('trace_count'),
                func.sum(Trace.call_cost).label('total_cost'),
                func.sum(Trace.input_tokens + Trace.output_tokens).label('total_tokens')
            ).join(Project).filter(
                Trace.model_name.isnot(None)
            ).group_by(Project.name, Trace.model_name).all()
            
            # Process data by project
            projects_data = defaultdict(lambda: {
                'total_traces': 0,
                'models': defaultdict(lambda: {'count': 0, 'cost': 0, 'tokens': 0})
            })
            
            for row in project_model_usage:
                project_name = row.project_name
                model_name = row.model_name or "Unknown"
                trace_count = row.trace_count or 0
                total_cost = float(row.total_cost or 0)
                total_tokens = int(row.total_tokens or 0)
                
                projects_data[project_name]['total_traces'] += trace_count
                projects_data[project_name]['models'][model_name]['count'] += trace_count
                projects_data[project_name]['models'][model_name]['cost'] += total_cost
                projects_data[project_name]['models'][model_name]['tokens'] += total_tokens
            
            # Calculate percentages and format data
            result = []
            for project_name, project_data in projects_data.items():
                total_traces = project_data['total_traces']
                models_list = []
                
                for model_name, model_data in project_data['models'].items():
                    percentage = (model_data['count'] / total_traces * 100) if total_traces > 0 else 0
                    models_list.append({
                        'name': model_name,
                        'usage': round(percentage, 1),
                        'count': model_data['count'],
                        'cost': round(model_data['cost'], 4),
                        'tokens': model_data['tokens'],
                        'color': self.get_model_color_dynamic(model_name)
                    })
                
                # Sort by usage
                models_list.sort(key=lambda x: x['usage'], reverse=True)
                
                result.append({
                    'project_name': project_name,
                    'total_traces': total_traces,
                    'models': models_list[:4],  # Top 4 models
                    'primary_model': models_list[0]['name'] if models_list else 'Unknown',
                    'primary_model_usage': models_list[0]['usage'] if models_list else 0,
                    'primary_model_count': models_list[0]['count'] if models_list else 0,
                    'primary_model_cost': models_list[0]['cost'] if models_list else 0,
                    'primary_model_color': models_list[0]['color'] if models_list else 'gray',
                    'models_count': len(models_list),
                    # Preparar strings de todos los modelos para mostrar fácilmente
                    'all_models_text': ', '.join([f"{m['name']} ({m['usage']:.1f}%)" for m in models_list[:4]]),
                    'secondary_models': models_list[1:4] if len(models_list) > 1 else [],
                    # Preparar información detallada de cada modelo
                    'model1_name': models_list[0]['name'] if len(models_list) > 0 else '',
                    'model1_usage': models_list[0]['usage'] if len(models_list) > 0 else 0,
                    'model1_count': models_list[0]['count'] if len(models_list) > 0 else 0,
                    'model1_cost': models_list[0]['cost'] if len(models_list) > 0 else 0,
                    'model1_color': models_list[0]['color'] if len(models_list) > 0 else 'gray',
                    'model2_name': models_list[1]['name'] if len(models_list) > 1 else '',
                    'model2_usage': models_list[1]['usage'] if len(models_list) > 1 else 0,
                    'model2_count': models_list[1]['count'] if len(models_list) > 1 else 0,
                    'model2_cost': models_list[1]['cost'] if len(models_list) > 1 else 0,
                    'model2_color': models_list[1]['color'] if len(models_list) > 1 else 'gray',
                    'model3_name': models_list[2]['name'] if len(models_list) > 2 else '',
                    'model3_usage': models_list[2]['usage'] if len(models_list) > 2 else 0,
                    'model3_count': models_list[2]['count'] if len(models_list) > 2 else 0,
                    'model3_cost': models_list[2]['cost'] if len(models_list) > 2 else 0,
                    'model3_color': models_list[2]['color'] if len(models_list) > 2 else 'gray',
                    'has_model2': len(models_list) > 1,
                    'has_model3': len(models_list) > 2
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting model usage by project: {e}")
            return []

    def get_all_project_models(self):
        """Get all models for all projects in a flat structure for Reflex foreach."""
        if not self.session:
            return []
        
        try:
            project_models = self.get_model_usage_by_project()
            
            # Flatten all models with project info
            flattened_models = []
            for project in project_models:
                for model in project['models']:
                    flattened_models.append({
                        'project_name': project['project_name'],
                        'project_total_traces': project['total_traces'],
                        'model_name': model['name'],
                        'model_usage': model['usage'],
                        'model_count': model['count'],
                        'model_cost': model['cost'],
                        'model_tokens': model['tokens'],
                        'model_color': model['color']
                    })
            
            return flattened_models
            
        except Exception as e:
            print(f"Error getting all project models: {e}")
            return []
    
    def get_project_session_models_grouped(self):
        """Get models grouped by project > session > model using ORM."""
        if not self.session:
            print("❌ DEBUG: No database session available")
            return {}
            
        try:
            print("🔍 DEBUG: Loading project-session-models grouped using ORM...")
            
            # Usar ORM para obtener datos agrupados por proyecto, sesión y modelo
            project_session_model_data = self.session.query(
                Project.name.label('project_name'),
                Session.name.label('session_name'),
                Trace.model_name.label('model_name'),
                func.count(Trace.id).label('model_count'),
                func.sum(Trace.call_cost).label('model_cost')
            ).select_from(Trace).join(
                Project, Trace.project_id == Project.id
            ).join(
                Session, Project.session_id == Session.id
            ).filter(
                Trace.model_name.isnot(None)
            ).group_by(Project.name, Session.name, Trace.model_name).order_by(
                Project.name, Session.name, func.count(Trace.id).desc()
            ).all()
            
            print(f"🔍 DEBUG: ORM query results: {len(project_session_model_data)} rows")
            
            if not project_session_model_data:
                print("⚠️ DEBUG: No data found in query")
                return {}
            
            # Calcular totales por proyecto y sesión para porcentajes
            session_totals = {}
            session_total_data = self.session.query(
                Project.name.label('project_name'),
                Session.name.label('session_name'),
                func.count(Trace.id).label('total_traces')
            ).select_from(Trace).join(
                Project, Trace.project_id == Project.id
            ).join(
                Session, Project.session_id == Session.id
            ).group_by(Project.name, Session.name).all()
            
            for row in session_total_data:
                key = f"{row.project_name}|{row.session_name}"
                session_totals[key] = row.total_traces
            
            print(f"🔍 DEBUG: Session totals: {session_totals}")
            
            # Procesar los resultados para agrupar por proyecto > sesión > modelo
            projects_dict = {}
            
            for row in project_session_model_data:
                project_name = row.project_name
                session_name = row.session_name
                model_name = row.model_name
                model_count = row.model_count
                model_cost = row.model_cost or 0.0
                
                # Calcular porcentaje dentro de la sesión
                session_key = f"{project_name}|{session_name}"
                total_traces = session_totals.get(session_key, 1)
                model_usage = (model_count / total_traces * 100) if total_traces > 0 else 0
                
                print(f"🔍 DEBUG: Processing: {project_name} > {session_name} > {model_name}, {model_count} traces ({model_usage:.1f}%)")
                
                # Crear estructura anidada
                if project_name not in projects_dict:
                    projects_dict[project_name] = {
                        'project_name': project_name,
                        'sessions': {}
                    }
                
                if session_name not in projects_dict[project_name]['sessions']:
                    projects_dict[project_name]['sessions'][session_name] = {
                        'session_name': session_name,
                        'total_traces': total_traces,
                        'models': []
                    }
                
                # Agregar modelo a la sesión
                projects_dict[project_name]['sessions'][session_name]['models'].append({
                    'model_name': model_name,
                    'model_count': model_count,
                    'model_cost': f"{model_cost:.4f}",
                    'model_usage': f"{model_usage:.1f}",
                    'model_color': self.get_model_color_dynamic(model_name)
                })
            
            print(f"✅ DEBUG: Final projects dict: {list(projects_dict.keys())}")
            return projects_dict
        
        except Exception as e:
            print(f"❌ DEBUG: Error getting project-session-models grouped: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_project_models_grouped(self):
        """Get models grouped by project using ORM instead of raw SQL."""
        if not self.session:
            return {}
            
        try:
            print("Loading project models grouped using ORM...")
            
            # Usar ORM para obtener datos agrupados por proyecto y modelo
            project_model_data = self.session.query(
                Project.name.label('project_name'),
                Trace.model_name.label('model_name'),
                func.count(Trace.id).label('model_count'),
                func.sum(Trace.call_cost).label('model_cost')
            ).join(Project).filter(
                Trace.model_name.isnot(None)
            ).group_by(Project.name, Trace.model_name).order_by(
                Project.name, func.count(Trace.id).desc()
            ).all()
            
            print(f"ORM query results: {len(project_model_data)} rows")
            
            if not project_model_data:
                return {}
            
            # Calcular totales por proyecto para porcentajes usando ORM
            project_totals = {}
            project_total_data = self.session.query(
                Project.name.label('project_name'),
                func.count(Trace.id).label('total_traces')
            ).join(Project).group_by(Project.name).all()
            
            for row in project_total_data:
                project_totals[row.project_name] = row.total_traces
            
            # Procesar los resultados para agrupar por proyecto
            projects_dict = {}
            
            for row in project_model_data:
                project_name = row.project_name
                model_name = row.model_name
                model_count = row.model_count
                model_cost = row.model_cost or 0.0
                
                # Calcular porcentaje
                total_traces = project_totals.get(project_name, 1)
                model_usage = (model_count / total_traces * 100) if total_traces > 0 else 0
                
                print(f"Processing: {project_name}, {model_name}, {model_count} traces ({model_usage:.1f}%)")
                
                if project_name not in projects_dict:
                    projects_dict[project_name] = {
                        'project_name': project_name,
                        'total_traces': total_traces,
                        'models': []
                    }
                
                # Agregar modelo al proyecto
                projects_dict[project_name]['models'].append({
                    'model_name': model_name,
                    'model_count': model_count,
                    'model_cost': f"{model_cost:.4f}",
                    'model_usage': f"{model_usage:.1f}",
                    'model_color': self.get_model_color_dynamic(model_name)
                })
            
            print(f"Final projects dict: {list(projects_dict.keys())}")
            return projects_dict
        
        except Exception as e:
            print(f"Error getting project models grouped: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_model_color_dynamic(self, model_name):
        """Generate dynamic color scheme for any model name using hash-based algorithm."""
        if not model_name:
            return 'gray'
        
        # Lista de colores disponibles en Radix UI
        available_colors = [
            'blue', 'green', 'red', 'purple', 'orange', 'teal', 
            'cyan', 'pink', 'yellow', 'indigo', 'violet', 'amber',
            'lime', 'emerald', 'sky', 'rose', 'fuchsia', 'slate'
        ]
        
        # Usar hash del nombre del modelo para generar un índice consistente
        model_hash = hash(model_name.lower())
        color_index = abs(model_hash) % len(available_colors)
        
        selected_color = available_colors[color_index]
        
        print(f"Dynamic color for '{model_name}': {selected_color} (hash: {model_hash}, index: {color_index})")
        return selected_color
    
    def get_model_color(self, model_name):
        """Legacy method - redirects to dynamic color generation."""
        return self.get_model_color_dynamic(model_name)
    
    def get_performance_alerts(self):
        """Get performance alerts based on actual data."""
        if not self.session:
            return []
        
        try:
            alerts = []
            now = datetime.now()
            
            # Check for high cost in last hour
            hour_ago = now - timedelta(hours=1)
            recent_cost = self.session.query(
                func.sum(Trace.call_cost)
            ).filter(Trace.request_time >= hour_ago).scalar() or 0
            
            if recent_cost > 1.0:  # Alert if more than $1 in last hour
                alerts.append({
                    'type': 'error',
                    'message': f'High cost detected: ${recent_cost:.2f} in last hour',
                    'time': 'Just now',
                    'icon': '🔴'
                })
            
            # Check for slow responses
            slow_traces = self.session.query(Trace).filter(
                and_(
                    Trace.duration_ms > 5000,  # More than 5 seconds
                    Trace.request_time >= hour_ago
                )
            ).count()
            
            if slow_traces > 0:
                alerts.append({
                    'type': 'warning',
                    'message': f'{slow_traces} slow responses (>5s) in last hour',
                    'time': '15 min ago',
                    'icon': '🟡'
                })
            
            # Check error rate (assuming errors are traces with very high duration or cost 0)
            total_recent = self.session.query(Trace).filter(Trace.request_time >= hour_ago).count()
            error_traces = self.session.query(Trace).filter(
                and_(
                    Trace.request_time >= hour_ago,
                    or_(Trace.call_cost == 0, Trace.duration_ms > 30000)
                )
            ).count()
            
            error_rate = (error_traces / total_recent * 100) if total_recent > 0 else 0
            
            if error_rate > 5:  # More than 5% error rate
                alerts.append({
                    'type': 'error',
                    'message': f'High error rate: {error_rate:.1f}% in last hour',
                    'time': '30 min ago',
                    'icon': '🔴'
                })
            elif len(alerts) == 0:
                alerts.append({
                    'type': 'success',
                    'message': 'All systems operational',
                    'time': '1 hour ago',
                    'icon': '🟢'
                })
            
            return alerts
            
        except Exception as e:
            print(f"Error getting performance alerts: {e}")
            return []
    
    def get_real_time_stats(self):
        """Get real-time statistics."""
        if not self.session:
            return {}
        
        try:
            now = datetime.now()
            last_5_min = now - timedelta(minutes=5)
            
            # Active requests (recent traces)
            active_requests = self.session.query(Trace).filter(
                Trace.request_time >= last_5_min
            ).count()
            
            # Average response time (last hour)
            hour_ago = now - timedelta(hours=1)
            avg_response = self.session.query(
                func.avg(Trace.duration_ms)
            ).filter(Trace.request_time >= hour_ago).scalar() or 0
            
            # Error rate calculation
            total_traces = self.session.query(Trace).filter(Trace.request_time >= hour_ago).count()
            error_traces = self.session.query(Trace).filter(
                and_(
                    Trace.request_time >= hour_ago,
                    or_(Trace.call_cost == 0, Trace.duration_ms > 30000)
                )
            ).count()
            
            error_rate = (error_traces / total_traces * 100) if total_traces > 0 else 0
            
            # Queue length (pending traces - simulate)
            queue_length = max(0, active_requests - 2)
            
            return {
                'active_requests': active_requests,
                'avg_response_time': f"{avg_response/1000:.1f}s" if avg_response else "0s",
                'error_rate': f"{error_rate:.2f}%",
                'queue_length': queue_length
            }
            
        except Exception as e:
            print(f"Error getting real-time stats: {e}")
            return {}
    
    def get_cost_analytics(self):
        """Get cost analytics data."""
        if not self.session:
            return {}
        
        try:
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            
            # Daily spend
            daily_cost = self.session.query(
                func.sum(Trace.call_cost)
            ).filter(Trace.request_time >= today).scalar() or 0
            
            # Yesterday's spend
            yesterday_cost = self.session.query(
                func.sum(Trace.call_cost)
            ).filter(
                and_(Trace.request_time >= yesterday, Trace.request_time < today)
            ).scalar() or 0
            
            # Weekly spend
            weekly_cost = self.session.query(
                func.sum(Trace.call_cost)
            ).filter(Trace.request_time >= week_ago).scalar() or 0
            
            # Cost per 1K tokens
            total_tokens = self.session.query(
                func.sum(Trace.input_tokens + Trace.output_tokens)
            ).filter(Trace.request_time >= week_ago).scalar() or 1
            
            cost_per_1k = (weekly_cost / total_tokens * 1000) if total_tokens > 0 else 0
            
            # Calculate trends
            daily_trend = ((daily_cost - yesterday_cost) / yesterday_cost * 100) if yesterday_cost > 0 else 0
            
            return {
                'cost_per_1k': f"${cost_per_1k:.4f}",
                'daily_spend': f"${daily_cost:.2f}",
                'daily_trend': daily_trend,
                'monthly_projection': f"${daily_cost * 30:.0f}",
                'weekly_trend': -15  # Simulated for now
            }
            
        except Exception as e:
            print(f"Error getting cost analytics: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if hasattr(self, 'session') and self.session:
            self.session.close()
    
    def get_filtered_real_time_stats(self, project_filter=None, session_filter=None, model_filter=None):
        """Obtener métricas en tiempo real con filtros aplicados."""
        if not self.session:
            return {
                'active_requests': '0',
                'avg_response_time': '0s',
                'error_rate': '0.00%',
                'queue_length': 0
            }
        
        try:
            now = datetime.now()
            last_5_min = now - timedelta(minutes=5)
            hour_ago = now - timedelta(hours=1)
            
            # Base query
            query = self.session.query(Trace)
            
            # Aplicar filtros
            if project_filter:
                query = query.join(Project).filter(Project.name == project_filter)
            if session_filter:
                query = query.join(Session).filter(Session.name == session_filter)
            if model_filter:
                query = query.filter(Trace.model_name == model_filter)
            
            # Active requests (últimos 5 minutos)
            active_requests = query.filter(Trace.request_time >= last_5_min).count()
            
            # Traces de la última hora para otros cálculos
            hour_traces = query.filter(Trace.request_time >= hour_ago).all()
            
            if not hour_traces:
                return {
                    'active_requests': str(active_requests),
                    'avg_response_time': '0s',
                    'error_rate': '0.00%',
                    'queue_length': 0
                }
            
            # Calcular métricas
            total_traces = len(hour_traces)
            error_traces = len([t for t in hour_traces if t.call_cost == 0 or (t.duration_ms and t.duration_ms > 30000)])
            avg_duration = sum(t.duration_ms or 0 for t in hour_traces) / total_traces if total_traces > 0 else 0
            
            error_rate = (error_traces / total_traces * 100) if total_traces > 0 else 0
            queue_length = max(0, active_requests - 2)
            
            return {
                'active_requests': str(active_requests),
                'avg_response_time': f"{avg_duration/1000:.1f}s" if avg_duration else "0s",
                'error_rate': f"{error_rate:.2f}%",
                'queue_length': queue_length
            }
            
        except Exception as e:
            print(f"Error getting filtered real time stats: {e}")
            return {
                'active_requests': '0',
                'avg_response_time': '0s',
                'error_rate': '0.00%',
                'queue_length': 0
            }

    def get_filtered_cost_analytics(self, project_filter=None, session_filter=None, model_filter=None):
        """Obtener análisis de costos con filtros aplicados."""
        if not self.session:
            return {
                'cost_per_1k': '$0.000',
                'daily_spend': '$0.00',
                'monthly_projection': '$0'
            }
        
        try:
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            
            # Base query
            query = self.session.query(Trace)
            
            # Aplicar filtros
            if project_filter:
                query = query.join(Project).filter(Project.name == project_filter)
            if session_filter:
                query = query.join(Session).filter(Session.name == session_filter)
            if model_filter:
                query = query.filter(Trace.model_name == model_filter)
            
            # Obtener traces filtrados
            daily_traces = query.filter(Trace.request_time >= today).all()
            weekly_traces = query.filter(Trace.request_time >= week_ago).all()
            
            if not weekly_traces:
                return {
                    'cost_per_1k': '$0.000',
                    'daily_spend': '$0.00',
                    'monthly_projection': '$0'
                }
            
            # Calcular costos
            daily_cost = sum(t.call_cost or 0 for t in daily_traces)
            weekly_cost = sum(t.call_cost or 0 for t in weekly_traces)
            total_tokens = sum((t.input_tokens or 0) + (t.output_tokens or 0) for t in weekly_traces)
            
            cost_per_1k = (weekly_cost / total_tokens * 1000) if total_tokens > 0 else 0
            monthly_projection = daily_cost * 30
            
            return {
                'cost_per_1k': f"${cost_per_1k:.4f}",
                'daily_spend': f"${daily_cost:.2f}",
                'monthly_projection': f"${monthly_projection:.0f}"
            }
            
        except Exception as e:
            print(f"Error getting filtered cost analytics: {e}")
            return {
                'cost_per_1k': '$0.000',
                'daily_spend': '$0.00',
                'monthly_projection': '$0'
            }