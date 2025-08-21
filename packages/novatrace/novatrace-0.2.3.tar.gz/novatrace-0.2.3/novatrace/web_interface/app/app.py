"""NovaTrace Dashboard - Web interface for monitoring AI traces."""
import reflex as rx
from novatrace.web_interface.components.foot import footer
from novatrace.web_interface.components import page
from novatrace.web_interface.components.recent_projects import recent_traces_table, recent_projects_list
from novatrace.web_interface.components import metrics
from novatrace.web_interface.backend.states import State
from novatrace.web_interface.connect import *

def usage() -> rx.Component:
    return rx.vstack(
        metrics.detailed_model_usage(State),
        spacing="6",
        width="100%",
    )

def analytics() -> rx.Component:
    return rx.vstack(
        # Métricas en tiempo real y costos encapsuladas (datos globales)
        metrics.metrics_overview(State),
        
        # Recent Traces and Performance Alerts
        rx.grid(
            recent_traces_table(State),
            metrics.performance_alerts(State),
            columns="2",
            spacing="6",
            width="100%",
            style={
                "@media (max-width: 1024px)": {"columns": "1"},
            }
        ),
        spacing="6",
        width="100%",
    )

def content() -> rx.Component:
    return rx.vstack(
        # rx.color_mode.button(position="top-right"),
        
        # Dynamic content based on current page
        rx.cond(
            State.is_analytics_active,
            analytics(),
            usage()
        ),

        footer(),

        align_items='center',
        spacing="6",
        width="100%",
        padding="0",  # Sin padding extra ya que el scroll_area ya tiene padding
        on_mount=State.load_dashboard_data,
    )

def index() -> rx.Component:
    """NovaTrace Dashboard main page with advanced LLM monitoring."""
    return page.page(State, content)

app = rx.App()
app.add_page(index)
