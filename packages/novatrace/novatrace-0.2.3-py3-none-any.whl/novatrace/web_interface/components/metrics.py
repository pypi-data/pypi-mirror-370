import reflex as rx

def real_time_metrics(State: callable, project_filter: str = None, session_filter: str = None, model_filter: str = None) -> rx.Component:
    """Métricas en tiempo real basadas en datos reales - con filtros opcionales."""
    
    # Por ahora usar solo datos globales, los filtros se implementarán después
    stats_data = State.real_time_stats
    
    # Título dinámico basado en filtros
    title_text = "⚡ Real-Time Metrics"
    if project_filter:
        title_text = f"⚡ Real-Time Metrics - {project_filter}"
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(title_text, size="5"),
                rx.badge("LIVE", color_scheme="green", variant="solid"),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Active requests", size="2", color="gray"),
                    rx.text(
                        stats_data.get("active_requests", "0"),
                        size="7", weight="bold", color="blue"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Avg response", size="2", color="gray"),
                    rx.text(
                        stats_data.get("avg_response_time", "0s"),
                        size="7", weight="bold", color="green"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Error rate", size="2", color="gray"),
                    rx.text(
                        stats_data.get("error_rate", "0%"),
                        size="7", weight="bold", color="red"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Queue length", size="2", color="gray"),
                    rx.text(
                        stats_data.get("queue_length", "0"),
                        size="7", weight="bold", color="orange"
                    ),
                    spacing="1",
                    align="center",
                ),
                columns="4",
                spacing="4",
            ),
            spacing="3",
        ),
        style={
            "padding": "1.5rem",
            "background": "linear-gradient(135deg, var(--indigo-1) 0%, var(--indigo-2) 100%)",
            "border": "1px solid var(--indigo-5)",
            "border_radius": "16px",
            "box_shadow": "0 8px 32px rgba(99, 102, 241, 0.12)",
            "flex": "1",
            "min_width": "400px",
            "max_width": "600px"
        }
    )

def cost_efficiency_metrics(State: callable, project_filter: str = None, session_filter: str = None, model_filter: str = None) -> rx.Component:
    """Métricas de eficiencia de costos basadas en datos reales - con filtros opcionales."""
    
    # Por ahora usar solo datos globales, los filtros se implementarán después
    cost_data = State.cost_analytics
    
    # Título dinámico basado en filtros
    title_text = "💰 Cost Efficiency"
    if project_filter:
        title_text = f"💰 Cost Efficiency - {project_filter}"
    
    return rx.card(
        rx.vstack(
            rx.heading(title_text, size="5"),
            rx.grid(
                rx.vstack(
                    rx.text("Cost per 1K tokens", size="2", weight="bold", color="gray"),
                    rx.text(
                        cost_data.get("cost_per_1k", "$0.000"),
                        size="6", weight="bold", color="green"
                    ),
                    rx.text(
                        "↓ 15% vs last week",
                        size="1", color="green"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Daily spend", size="2", weight="bold", color="gray"),
                    rx.text(
                        cost_data.get("daily_spend", "$0.00"),
                        size="6", weight="bold", color="blue"
                    ),
                    rx.text(
                        "Based on current usage",
                        size="1", color="gray"
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Monthly projection", size="2", weight="bold", color="gray"),
                    rx.text(
                        cost_data.get("monthly_projection", "$0"),
                        size="6", weight="bold", color="purple"
                    ),
                    rx.text("Estimated monthly cost", size="1", color="green"),
                    spacing="1",
                    align="center",
                ),
                columns="3",
                spacing="4",
            ),
            spacing="3",
        ),
        style={
            "padding": "1.5rem",
            "background": "linear-gradient(135deg, var(--emerald-1) 0%, var(--emerald-2) 100%)",
            "border": "1px solid var(--emerald-5)",
            "border_radius": "16px",
            "box_shadow": "0 8px 32px rgba(16, 185, 129, 0.12)",
            "flex": "1",
            "min_width": "400px",
            "max_width": "600px"
        }
    )

def metrics_overview(State: callable, project_filter: str = None, session_filter: str = None, model_filter: str = None) -> rx.Component:
    """
    Componente que encapsula las métricas en tiempo real y de costos.
    
    Args:
        State: El estado de Reflex
        project_filter: Filtro por proyecto específico (None = todos los proyectos)
        session_filter: Filtro por sesión específica (None = todas las sesiones)
        model_filter: Filtro por modelo específico (None = todos los modelos)
    """
    return rx.hstack(
        real_time_metrics(State, project_filter, session_filter, model_filter),
        cost_efficiency_metrics(State, project_filter, session_filter, model_filter),
        spacing="6",
        width="100%",
        align="stretch",  # Para que ambas tarjetas tengan la misma altura
        justify="center"  # Centrar horizontalmente
    )

def model_usage_breakdown(State: callable) -> rx.Component:
    """Uso de modelos por proyecto basado en datos reales."""
    return rx.card(
        rx.vstack(
            rx.heading("🤖 Model Usage by Project", size="5"),
            rx.cond(
                State.model_usage_by_project.length() > 0,
                rx.vstack(
                    rx.foreach(
                        State.model_usage_by_project,
                        lambda project: rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("📁", size="4"),
                                    rx.heading(
                                        project["project_name"],
                                        size="4",
                                        color="var(--blue-11)"
                                    ),
                                    rx.spacer(),
                                    rx.badge(
                                        f"{project['total_traces']} traces",
                                        color_scheme="blue",
                                        variant="soft"
                                    ),
                                    align="center",
                                    width="100%",
                                ),
                                # Mostrar modelo principal y estadísticas
                                rx.vstack(
                                    rx.hstack(
                                        rx.badge(
                                            project["primary_model"],
                                            color_scheme=project["primary_model_color"],
                                            variant="soft"
                                        ),
                                        rx.text(
                                            project["primary_model_usage"],
                                            size="2",
                                            weight="bold",
                                            color="blue"
                                        ),
                                        rx.text("%", size="2", color="blue"),
                                        rx.spacer(),
                                        rx.text(
                                            "$",
                                            size="2",
                                            color="green"
                                        ),
                                        rx.text(
                                            project["primary_model_cost"],
                                            size="2",
                                            color="green"
                                        ),
                                        spacing="1",
                                        align="center",
                                        width="100%"
                                    ),
                                    rx.hstack(
                                        rx.text("+", size="2", color="gray"),
                                        rx.text(
                                            project["models_count"],
                                            size="2",
                                            color="gray"
                                        ),
                                        rx.text("models", size="2", color="gray"),
                                        spacing="1"
                                    ),
                                    spacing="1",
                                    width="100%"
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            style={
                                "padding": "1rem",
                                "background": "var(--gray-2)",
                                "border": "1px solid var(--gray-4)",
                                "margin_bottom": "0.5rem"
                            }
                        )
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.text(
                    "No model usage data available",
                    size="3",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="3",
        ),
        style={
            "padding": "1.5rem",
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        }
    )

def detalles(item) -> rx.Component:
    return rx.card(
            rx.hstack(
                # Número del modelo
                rx.box(
                    rx.text(
                        item["model_number"],
                        size="2",
                        weight="bold",
                        color="white"
                    ),
                    style={
                        "width": "32px",
                        "height": "32px",
                        "border_radius": "50%",
                        "background": f"var(--{item['model_color']}-9)",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "flex_shrink": "0"
                    }
                ),
                # Información del modelo
                rx.vstack(
                    rx.hstack(
                        rx.badge(
                            item["model_name"],
                            color_scheme=item["model_color"],
                            variant="soft",
                            size="2"
                        ),
                        rx.spacer(),
                        rx.text(
                            f"{item['model_usage']}%",
                            size="3",
                            weight="bold",
                            color="var(--green-11)"
                        ),
                        spacing="2",
                        align="center",
                        width="100%"
                    ),
                    rx.hstack(
                        rx.text(
                            f"{item['model_count']} traces",
                            size="2",
                            color="var(--gray-11)"
                        ),
                        rx.text("•", size="2", color="var(--gray-9)"),
                        rx.text(
                            f"${item['model_cost']}",
                            size="2",
                            color="var(--green-11)",
                            weight="medium"
                        ),
                        spacing="2",
                        align="center"
                    ),
                    spacing="1",
                    align="start",
                    width="100%"
                ),
                spacing="3",
                align="center",
                width="100%"
            ),
            style={
                "padding": "1rem",
                "background": "var(--gray-1)",
                "border": "1px solid var(--gray-5)",
                "border_radius": "8px",
                "margin_bottom": "0.5rem",
                "margin_left": "2rem",  # Indentación para mostrar jerarquía
                "margin_right": "0.5rem",
                "transition": "all 0.2s ease",
                "width": "calc(100% - 2.5rem)",  # Ancho consistente considerando la indentación
                ":hover": {
                    "background": "var(--gray-2)",
                    "border_color": "var(--blue-6)",
                    "transform": "translateX(4px)"
                }
            }
        )

def detailed_model_usage(State: callable) -> rx.Component:
    """Detailed Model Usage with Project > Session > Model hierarchy in 2 columns."""
    return rx.card(
        rx.vstack(
            rx.heading("Model Usage by Project and Session", size="5"),
            rx.text(State.debug_message, size="2", color="cyan"),
            rx.cond(
                State.projects_data.length() > 0,
                # 2-column grid for projects
                rx.box(
                    rx.grid(
                        # FOREACH sobre PROYECTOS tipados (cada proyecto es una tarjeta ROJA)
                        rx.foreach(
                            State.projects_data,
                            lambda project: rx.card(
                                rx.vstack(
                                    # HEADER del proyecto (parte superior de la tarjeta ROJA)
                                    rx.hstack(
                                        rx.text("📁", size="5"),
                                        rx.vstack(
                                            rx.heading(
                                                project.project_name,
                                                size="4",
                                                color="var(--red-11)",
                                                weight="bold"
                                            ),
                                            rx.hstack(
                                                rx.badge(
                                                    project.sessions.length(),
                                                    color_scheme="red",
                                                    variant="soft",
                                                    size="2"
                                                ),
                                                rx.text("sessions", size="2", color="var(--gray-11)"),
                                                spacing="1",
                                                align="center"
                                            ),
                                            spacing="1",
                                            align="start"
                                        ),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                    ),
                                    
                                    # FOREACH sobre SESIONES tipadas dentro del proyecto (tarjetas AZULES)
                                    rx.vstack(
                                        rx.foreach(
                                            project.sessions,
                                            lambda session: rx.card(
                                                rx.vstack(
                                                    # Header de la sesión
                                                    rx.hstack(
                                                        rx.text("📊", size="4"),
                                                        rx.vstack(
                                                            rx.heading(
                                                                f"Session: {session.session_name}",
                                                                size="3",
                                                                color="var(--blue-11)",
                                                                weight="bold"
                                                            ),
                                                            rx.hstack(
                                                                rx.badge(
                                                                    session.total_traces,
                                                                    color_scheme="blue",
                                                                    variant="soft",
                                                                    size="1"
                                                                ),
                                                                rx.text("traces", size="1", color="var(--gray-11)"),
                                                                spacing="1",
                                                                align="center"
                                                            ),
                                                            spacing="1",
                                                            align="start"
                                                        ),
                                                        spacing="2",
                                                        align="center",
                                                        width="100%",
                                                    ),
                                                    
                                                    # FOREACH sobre MODELOS tipados dentro de la sesión (tarjetas VERDES en 2 columnas)
                                                    rx.grid(
                                                        rx.foreach(
                                                            session.models,
                                                            lambda model: rx.card(
                                                                rx.hstack(
                                                                    # Información del modelo
                                                                    rx.vstack(
                                                                        rx.text(
                                                                            model.model_name,
                                                                            size="2",
                                                                            weight="bold",
                                                                            color="var(--green-11)"
                                                                        ),
                                                                        rx.hstack(
                                                                            rx.text(
                                                                                f"{model.model_count}",
                                                                                size="1",
                                                                                color="var(--gray-11)"
                                                                            ),
                                                                            rx.text("•", size="1", color="var(--gray-9)"),
                                                                            rx.text(
                                                                                f"${model.model_cost}",
                                                                                size="1",
                                                                                color="var(--green-11)",
                                                                                weight="medium"
                                                                            ),
                                                                            spacing="1",
                                                                            align="center"
                                                                        ),
                                                                        spacing="1",
                                                                        align="start",
                                                                        width="100%"
                                                                    ),
                                                                    spacing="2",
                                                                    align="center",
                                                                    width="100%"
                                                                ),
                                                                style={
                                                                    "padding": "0.5rem",
                                                                    "background": "linear-gradient(135deg, var(--green-2) 0%, var(--green-1) 100%)",
                                                                    "border": "1px solid var(--green-5)",
                                                                    "border_radius": "8px",
                                                                    "transition": "all 0.2s ease",
                                                                    "width": "100%",
                                                                    ":hover": {
                                                                        "background": "linear-gradient(135deg, var(--green-3) 0%, var(--green-2) 100%)",
                                                                        "border_color": "var(--green-7)",
                                                                        "transform": "translateX(2px)",
                                                                    }
                                                                }
                                                            )
                                                        ),
                                                        columns="2",  # 2 columns for models
                                                        spacing="2",
                                                        width="100%"
                                                    ),
                                                    
                                                    spacing="2",
                                                    width="100%"
                                                ),
                                                style={
                                                    "padding": "1rem",
                                                    "background": "linear-gradient(135deg, var(--blue-2) 0%, var(--blue-1) 100%)",
                                                    "border": "1px solid var(--blue-6)",
                                                    "border_radius": "12px",
                                                    "margin_bottom": "0.5rem",
                                                    "transition": "all 0.3s ease",
                                                    "width": "100%",
                                                    ":hover": {
                                                        "box_shadow": "0 8px 24px rgba(59, 130, 246, 0.15)",
                                                        "transform": "translateY(-1px)"
                                                    }
                                                }
                                            )
                                        ),
                                        spacing="2",
                                        width="100%"
                                    ),
                                    
                                    spacing="3",
                                    width="100%"
                                ),
                                style={
                                    "padding": "1.5rem",
                                    "background": "linear-gradient(135deg, var(--purple-1) 0%, var(--purple-2) 100%)",
                                    "border": "2px solid var(--purple-6)",
                                    "border_radius": "16px",
                                    "transition": "all 0.3s ease",
                                    "width": "100%",
                                    ":hover": {
                                        "box_shadow": "0 12px 48px rgba(147, 51, 234, 0.25)",
                                        "transform": "translateY(-2px)"
                                    }
                                }
                            )
                        ),
                        columns="2",  # 2 columns for projects
                        spacing="4",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.text(
                    "No model data available",
                    size="3",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="4",
            width="100%"
        ),
        style={
            "padding": "1.5rem",
            "background": "linear-gradient(135deg, var(--gray-1) 0%, var(--gray-2) 100%)",
            "border": "1px solid var(--gray-5)",
            "border_radius": "16px",
            "box_shadow": "0 8px 32px rgba(0, 0, 0, 0.12)",
            "width": "100%"
        }
    )

def performance_alerts(State: callable) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("🤖 Model Usage by Project and Session", size="5"),
            # Debug info
            rx.text(f"Projects loaded: {State.projects_data.length()}", size="2", color="orange"),
            rx.cond(
                State.projects_data.length() > 0,
                # 2-column grid for projects
                rx.box(
                    rx.grid(
                        # FOREACH sobre PROYECTOS tipados (cada proyecto es una tarjeta ROJA)
                        rx.foreach(
                            State.projects_data,
                            lambda project: rx.card(
                                rx.vstack(
                                    # HEADER del proyecto (parte superior de la tarjeta ROJA)
                                    rx.hstack(
                                        rx.text("📁", size="5"),
                                        rx.vstack(
                                            rx.heading(
                                                project.project_name,
                                                size="4",
                                                color="var(--red-11)",
                                                weight="bold"
                                            ),
                                            rx.hstack(
                                                rx.badge(
                                                    project.sessions.length(),
                                                    color_scheme="red",
                                                    variant="soft",
                                                    size="2"
                                                ),
                                                rx.text("sessions", size="2", color="var(--gray-11)"),
                                                spacing="1",
                                                align="center"
                                            ),
                                            spacing="1",
                                            align="start"
                                        ),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                    ),
                                    
                                    # FOREACH sobre SESIONES tipadas dentro del proyecto (tarjetas AZULES)
                                    rx.vstack(
                                        rx.foreach(
                                            project.sessions,
                                            lambda session: rx.card(
                                                rx.vstack(
                                                    # Header de la sesión
                                                    rx.hstack(
                                                        rx.text("📊", size="4"),
                                                        rx.vstack(
                                                            rx.heading(
                                                                f"Session: {session.session_name}",
                                                                size="3",
                                                                color="var(--blue-11)",
                                                                weight="bold"
                                                            ),
                                                            rx.hstack(
                                                                rx.badge(
                                                                    session.total_traces,
                                                                    color_scheme="blue",
                                                                    variant="soft",
                                                                    size="1"
                                                                ),
                                                                rx.text("traces", size="1", color="var(--gray-11)"),
                                                                spacing="1",
                                                                align="center"
                                                            ),
                                                            spacing="1",
                                                            align="start"
                                                        ),
                                                        spacing="2",
                                                        align="center",
                                                        width="100%",
                                                    ),
                                                    
                                                    # FOREACH sobre MODELOS tipados dentro de la sesión (tarjetas VERDES en 2 columnas)
                                                    rx.grid(
                                                        rx.foreach(
                                                            session.models,
                                                            lambda model: rx.card(
                                                                rx.hstack(
                                                                    # Círculo del modelo
                                                                    rx.box(
                                                                        rx.text(
                                                                            "●",
                                                                            size="2",
                                                                            weight="bold",
                                                                            color="white"
                                                                        ),
                                                                        style={
                                                                            "width": "20px",
                                                                            "height": "20px",
                                                                            "border_radius": "50%",
                                                                            "background": model.model_color,
                                                                            "display": "flex",
                                                                            "align_items": "center",
                                                                            "justify_content": "center",
                                                                            "flex_shrink": "0"
                                                                        }
                                                                    ),
                                                                    # Información del modelo
                                                                    rx.vstack(
                                                                        rx.text(
                                                                            model.model_name,
                                                                            size="2",
                                                                            weight="bold",
                                                                            color="var(--green-11)"
                                                                        ),
                                                                        rx.hstack(
                                                                            rx.text(
                                                                                f"{model.model_count}",
                                                                                size="1",
                                                                                color="var(--gray-11)"
                                                                            ),
                                                                            rx.text("•", size="1", color="var(--gray-9)"),
                                                                            rx.text(
                                                                                f"${model.model_cost}",
                                                                                size="1",
                                                                                color="var(--green-11)",
                                                                                weight="medium"
                                                                            ),
                                                                            spacing="1",
                                                                            align="center"
                                                                        ),
                                                                        spacing="1",
                                                                        align="start",
                                                                        width="100%"
                                                                    ),
                                                                    spacing="2",
                                                                    align="center",
                                                                    width="100%"
                                                                ),
                                                                style={
                                                                    "padding": "0.5rem",
                                                                    "background": "linear-gradient(135deg, var(--green-2) 0%, var(--green-1) 100%)",
                                                                    "border": "1px solid var(--green-5)",
                                                                    "border_radius": "8px",
                                                                    "transition": "all 0.2s ease",
                                                                    "width": "100%",
                                                                    ":hover": {
                                                                        "background": "linear-gradient(135deg, var(--green-3) 0%, var(--green-2) 100%)",
                                                                        "border_color": "var(--green-7)",
                                                                        "transform": "translateX(2px)",
                                                                    }
                                                                }
                                                            )
                                                        ),
                                                        columns="2",  # 2 columns for models
                                                        spacing="2",
                                                        width="100%"
                                                    ),
                                                    
                                                    spacing="2",
                                                    width="100%"
                                                ),
                                                style={
                                                    "padding": "1rem",
                                                    "background": "linear-gradient(135deg, var(--blue-2) 0%, var(--blue-1) 100%)",
                                                    "border": "1px solid var(--blue-6)",
                                                    "border_radius": "12px",
                                                    "margin_bottom": "0.5rem",
                                                    "transition": "all 0.3s ease",
                                                    "width": "100%",
                                                    ":hover": {
                                                        "box_shadow": "0 8px 24px rgba(59, 130, 246, 0.15)",
                                                        "transform": "translateY(-1px)"
                                                    }
                                                }
                                            )
                                        ),
                                        spacing="2",
                                        width="100%"
                                    ),
                                    
                                    spacing="3",
                                    width="100%"
                                ),
                                style={
                                    "padding": "1.5rem",
                                    "background": "linear-gradient(135deg, var(--red-2) 0%, var(--red-1) 100%)",
                                    "border": "2px solid var(--red-6)",
                                    "border_radius": "16px",
                                    "transition": "all 0.3s ease",
                                    "width": "100%",
                                    ":hover": {
                                        "box_shadow": "0 12px 48px rgba(239, 68, 68, 0.25)",
                                        "transform": "translateY(-2px)"
                                    }
                                }
                            )
                        ),
                        columns="2",  # 2 columns for projects
                        spacing="4",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.text(
                    "No model data available",
                    size="3",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="4",
            width="100%"
        ),
        style={
            "padding": "1.5rem",
            "background": "linear-gradient(135deg, var(--gray-1) 0%, var(--gray-2) 100%)",
            "border": "1px solid var(--gray-5)",
            "border_radius": "16px",
            "box_shadow": "0 8px 32px rgba(0, 0, 0, 0.12)",
            "width": "100%"
        }
    )

def performance_alerts(State: callable) -> rx.Component:
    """Sistema de alertas basado en datos reales."""
    return rx.card(
        rx.vstack(
            rx.heading("🚨 Performance Alerts", size="5"),
            rx.cond(
                State.performance_alerts.length() > 0,
                rx.vstack(
                    rx.foreach(
                        State.performance_alerts,
                        lambda alert: rx.hstack(
                            rx.badge(
                                alert["icon"],
                                variant="solid",
                                color_scheme=rx.cond(
                                    alert["type"] == "error", "red",
                                    rx.cond(alert["type"] == "warning", "yellow", "green")
                                )
                            ),
                            rx.text(alert["message"], size="3"),
                            rx.spacer(),
                            rx.text(alert["time"], size="2", color="gray"),
                            width="100%",
                            align="center",
                        )
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.text(
                    "No alerts - All systems operational",
                    size="3",
                    color="green",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="3",
        ),
        style={
            "padding": "1.5rem",
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        }
    )