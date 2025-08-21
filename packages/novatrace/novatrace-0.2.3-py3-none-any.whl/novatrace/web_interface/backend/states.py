import reflex as rx
from typing import Dict, List, Any
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ..connect import db_manager
except ImportError:
    # Fallback for when running directly
    try:
        from connect import db_manager
    except ImportError:
        # Final fallback with absolute imports
        web_interface_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, web_interface_path)
        from connect import db_manager

# Tipos específicos para Reflex foreach operations con sesiones
class ModelInfo(rx.Base):
    model_name: str
    model_count: int
    model_cost: float
    model_usage: float
    model_color: str

class SessionInfo(rx.Base):
    session_name: str
    total_traces: int
    models: List[ModelInfo]

class ProjectInfo(rx.Base):
    project_name: str
    sessions: List[SessionInfo]

def format_number_compact(number):
    """Format large numbers with k/m suffixes."""
    try:
        # Convert to int if it's not already
        num = int(number) if number is not None else 0
        if num >= 1_000_000:
            return f"{num / 1_000_000:.2f}m".rstrip('0').rstrip('.')
        elif num >= 1_000:
            return f"{num / 1_000:.1f}k".rstrip('0').rstrip('.')
        else:
            return str(num)
    except (ValueError, TypeError):
        return str(number) if number is not None else "0"

class State(rx.State):
    """Main application state."""
    
    # Navigation state
    current_tab: str = "analytics"
    current_page: str = "analytics"  # Added missing variable
    
    # Real-time statistics
    real_time_stats: Dict[str, Any] = {
        "active_requests": "0",
        "avg_response_time": "0ms",
        "error_rate": "0%",
        "queue_length": "0"
    }
    
    # Cost analytics
    cost_analytics: Dict[str, Any] = {
        "cost_per_1k": "$0.000",
        "daily_spend": "$0.00",
        "monthly_projection": "$0"
    }
    
    # Projects data as typed objects for hierarchical display
    projects_data: List[ProjectInfo] = []
    
    # Dashboard data - keeps backward compatibility
    recent_traces: List[Dict[str, Any]] = []
    recent_projects: List[Dict[str, Any]] = []
    total_projects: int = 0
    total_sessions: int = 0
    total_traces: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    model_usage_by_project: List[Dict[str, Any]] = []
    all_project_models: List[Dict[str, Any]] = []
    project_models_grouped: List[Dict[str, Any]] = []  # Missing variable
    performance_alerts: List[Dict[str, Any]] = []
    trace_types_stats: Dict[str, Any] = {}
    is_loading: bool = False
    last_updated: str = ""
    
    # Debug info
    debug_message: str = "Not loaded yet"

    def debug_load_data(self):
        """Manual debug method to load data."""
        try:
            print("🔍 DEBUG: Manual data load triggered")
            self.debug_message = "Loading data..."
            
            # Test database connection
            grouped_data = db_manager.get_project_session_models_grouped()
            self.debug_message = f"Database returned: {len(grouped_data)} projects"
            print(f"🔍 DEBUG: Database returned {len(grouped_data)} projects")
            
            if grouped_data:
                # Convert to typed objects
                projects_list = []
                for project_name, project_data in grouped_data.items():
                    sessions_list = []
                    for session_name, session_data in project_data.get('sessions', {}).items():
                        models_list = []
                        for model_dict in session_data.get('models', []):
                            model_info = ModelInfo(
                                model_name=model_dict.get('model_name', 'Unknown'),
                                model_count=model_dict.get('model_count', 0),
                                model_cost=float(model_dict.get('model_cost', 0.0)),
                                model_usage=float(model_dict.get('model_usage', 0.0)),
                                model_color=model_dict.get('model_color', 'gray')
                            )
                            models_list.append(model_info)
                        
                        session_info = SessionInfo(
                            session_name=session_name,
                            total_traces=session_data.get('total_traces', 0),
                            models=models_list
                        )
                        sessions_list.append(session_info)
                    
                    project_info = ProjectInfo(
                        project_name=project_name,
                        sessions=sessions_list
                    )
                    projects_list.append(project_info)
                
                self.projects_data = projects_list
                self.debug_message = f"✅ Loaded {len(projects_list)} projects successfully"
                print(f"🔍 DEBUG: Successfully loaded {len(projects_list)} projects")
            else:
                self.debug_message = "❌ No data returned from database"
                print("🔍 DEBUG: No data returned from database")
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.debug_message = error_msg
            print(f"🔍 DEBUG: {error_msg}")
            import traceback
            traceback.print_exc()
    
    @rx.var
    def total_traces_formatted(self) -> str:
        """Format total traces with k/m suffix."""
        return format_number_compact(self.total_traces)
    
    @rx.var
    def total_tokens_formatted(self) -> str:
        """Format total tokens with k/m suffix."""
        return format_number_compact(self.total_tokens)
    
    @rx.var
    def total_cost_formatted(self) -> str:
        """Format total cost with currency."""
        return f"${self.total_cost:.2f}"

    def load_dashboard_data(self):
        """Load comprehensive dashboard data from the database."""
        self.is_loading = True
        
        try:
            # Get basic stats
            stats = db_manager.get_dashboard_stats()
            
            self.total_sessions = stats.get("total_sessions", 0)
            self.total_projects = stats.get("total_projects", 0)
            self.total_traces = stats.get("total_traces", 0)
            self.total_cost = round(stats.get("total_cost", 0.0), 3)
            self.total_tokens = stats.get("total_tokens", 0)
            self.trace_types_stats = stats.get("trace_types_stats", {})
            self.recent_projects = stats.get("recent_projects", [])
            self.recent_traces = stats.get("recent_traces", [])
            
            # Load advanced analytics
            self.load_model_usage_by_project()
            self.load_all_project_models()
            self.load_project_models_grouped()
            self.load_projects_data_typed()  # NEW: Load typed data
            self.load_performance_alerts()
            self.load_real_time_stats()
            self.load_cost_analytics()
            
            # Update timestamp
            self.last_updated = datetime.now().strftime("%H:%M:%S")
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
        finally:
            self.is_loading = False
    
    def load_model_usage_by_project(self):
        """Load model usage statistics by project."""
        try:
            model_data = db_manager.get_model_usage_by_project()
            self.model_usage_by_project = model_data
        except Exception as e:
            print(f"Error loading model usage: {e}")
            self.model_usage_by_project = []

    def load_all_project_models(self):
        """Load all project models in flat structure."""
        try:
            all_models = db_manager.get_all_project_models()
            self.all_project_models = all_models
        except Exception as e:
            print(f"Error loading all project models: {e}")
            self.all_project_models = []

    def load_project_models_grouped(self):
        """Load project models in grouped structure for proper nesting."""
        try:
            print("Loading project models grouped...")
            grouped_models_dict = db_manager.get_project_models_grouped()
            print(f"Received dict with {len(grouped_models_dict)} projects")
            
            # Convertir a lista de proyectos con modelos anidados
            grouped_list = []
            for project_name, project_data in grouped_models_dict.items():
                print(f"Processing project: {project_name} with {len(project_data['models'])} models")
                
                project_item = {
                    "project_name": project_name,
                    "total_traces": project_data["total_traces"],
                    "models": project_data["models"]
                }
                grouped_list.append(project_item)
            
            print(f"Final grouped list has {len(grouped_list)} projects")
            self.project_models_grouped = grouped_list
        except Exception as e:
            print(f"Error loading project models grouped: {e}")
            self.project_models_grouped = []

    def load_projects_data_typed(self):
        """Load project-session-models as typed objects for Reflex foreach."""
        try:
            print("🔍 DEBUG: Starting load_projects_data_typed...")
            grouped_data_dict = db_manager.get_project_session_models_grouped()
            print(f"🔍 DEBUG: Got grouped data: {type(grouped_data_dict)}, length: {len(grouped_data_dict) if grouped_data_dict else 'None'}")
            print(f"🔍 DEBUG: First few items: {list(grouped_data_dict.keys())[:3] if grouped_data_dict else 'Empty'}")
            
            # Convertir a objetos tipados
            projects_list = []
            for project_name, project_data in grouped_data_dict.items():
                print(f"🔍 DEBUG: Processing project: {project_name}")
                sessions_list = []
                for session_name, session_data in project_data.get('sessions', {}).items():
                    print(f"🔍 DEBUG: Processing session: {session_name}")
                    models_list = []
                    for model_dict in session_data.get('models', []):
                        model_info = ModelInfo(
                            model_name=model_dict.get('model_name', 'Unknown'),
                            model_count=model_dict.get('model_count', 0),
                            model_cost=float(model_dict.get('model_cost', 0.0)),
                            model_usage=float(model_dict.get('model_usage', 0.0)),
                            model_color=model_dict.get('model_color', 'gray')
                        )
                        models_list.append(model_info)
                    
                    session_info = SessionInfo(
                        session_name=session_name,
                        total_traces=session_data.get('total_traces', 0),
                        models=models_list
                    )
                    sessions_list.append(session_info)
                
                project_info = ProjectInfo(
                    project_name=project_name,
                    sessions=sessions_list
                )
                projects_list.append(project_info)
            
            self.projects_data = projects_list
            print(f"✅ DEBUG: Typed project data loaded: {len(self.projects_data)} projects with sessions")
            
        except Exception as e:
            print(f"❌ DEBUG: Error loading typed project data: {e}")
            import traceback
            traceback.print_exc()
            self.projects_data = []
    
    def load_performance_alerts(self):
        """Load performance alerts based on actual data."""
        try:
            alerts = db_manager.get_performance_alerts()
            self.performance_alerts = alerts
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.performance_alerts = []
    
    def load_real_time_stats(self):
        """Load real-time statistics."""
        try:
            real_time = db_manager.get_real_time_stats()
            self.real_time_stats = real_time
        except Exception as e:
            print(f"Error loading real-time stats: {e}")
            self.real_time_stats = {}
    
    def load_cost_analytics(self):
        """Load cost analytics data."""
        try:
            cost_data = db_manager.get_cost_analytics()
            self.cost_analytics = cost_data
        except Exception as e:
            print(f"Error loading cost analytics: {e}")
            self.cost_analytics = {}
    
    @rx.var
    def is_analytics_active(self) -> bool:
        """Check if analytics page is active."""
        return self.current_page == "analytics"
    
    @rx.var
    def is_usage_active(self) -> bool:
        """Check if usage page is active."""
        return self.current_page == "usage"
    
    def on_load(self):
        """Carga todos los datos al inicializar la página."""
        self.load_dashboard_data()
    
    def set_page_analytics(self):
        """Cambiar a la página de analytics."""
        self.current_page = "analytics"
    
    def set_page_usage(self):
        """Cambiar a la página de usage."""
        self.current_page = "usage"
    
    def get_filtered_real_time_stats(self, project_filter: str = None, session_filter: str = None, model_filter: str = None) -> dict:
        """Obtener métricas en tiempo real filtradas."""
        try:
            # Si no hay filtros, devolver stats globales
            if not project_filter and not session_filter and not model_filter:
                return self.real_time_stats
            
            # Aplicar filtros y calcular métricas específicas
            filtered_stats = db_manager.get_filtered_real_time_stats(
                project_filter=project_filter,
                session_filter=session_filter, 
                model_filter=model_filter
            )
            return filtered_stats
        except Exception as e:
            print(f"Error getting filtered real time stats: {e}")
            return {
                'active_requests': '0',
                'avg_response_time': '0s',
                'error_rate': '0.00%',
                'queue_length': 0
            }

    def get_filtered_cost_analytics(self, project_filter: str = None, session_filter: str = None, model_filter: str = None) -> dict:
        """Obtener análisis de costos filtrados."""
        try:
            # Si no hay filtros, devolver analytics globales
            if not project_filter and not session_filter and not model_filter:
                return self.cost_analytics
            
            # Aplicar filtros y calcular costos específicos
            filtered_costs = db_manager.get_filtered_cost_analytics(
                project_filter=project_filter,
                session_filter=session_filter,
                model_filter=model_filter
            )
            return filtered_costs
        except Exception as e:
            print(f"Error getting filtered cost analytics: {e}")
            return {
                'cost_per_1k': '$0.000',
                'daily_spend': '$0.00',
                'monthly_projection': '$0'
            }
