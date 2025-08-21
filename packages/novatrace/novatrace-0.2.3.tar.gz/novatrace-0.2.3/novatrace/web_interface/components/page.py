import reflex as rx
from novatrace.web_interface.components.card import stat_card
from novatrace.web_interface.backend.states import State

def header() -> rx.Component:
    """Create the header component for the dashboard."""
    return rx.hstack(
        # rx.text("🚀", size="9"),
        rx.heading(
            "NovaTrace", 
            size="9", 
            style={
                "background": "linear-gradient(45deg, var(--blue-11), var(--purple-11))",
                "background_clip": "text",
                "color": "transparent",
                "font_weight": "900",
            }
        ),
        rx.badge(
            "LLM Monitor",
            variant="soft",
            color_scheme="blue",
            size="3",
            style={"margin_left": "1rem"}
        ),
        rx.box(width="5rem"),  # Spacer
        rx.spacer(),
        cards(),
        width='100vw',
        align_items='center',
        padding='1rem 1rem 1rem 1rem',
        spacing="2",
        border_bottom="1px solid var(--gray-4)",
    )

def button_builder(icon: str, text: str, color_scheme: str, on_click: callable = None) -> rx.Component:
    return rx.button(
        rx.hstack(
            icon,
            text,
            spacing='2',
        ),
        variant="outline",
        color_scheme=color_scheme,
        on_click=on_click,
        size="3",
        width="100%",
    )

def side_bar(State: callable, content: callable) -> rx.Component:
    """Create the side bar component for the dashboard."""
    return rx.vstack(
        header(),
        rx.hstack(
            # Sidebar
            rx.vstack(
                rx.text("Navigation", size="5", weight="bold"),
                rx.vstack(
                    button_builder(
                        icon=rx.text("📊"),
                        text=rx.text("Analytics"),
                        color_scheme="purple",
                        on_click=State.set_page_analytics
                    ),
                    button_builder(
                        icon=rx.text("🔧"),
                        text=rx.text("Usage"),
                        color_scheme="yellow",
                        on_click=State.set_page_usage
                    ),
                    button_builder(
                        icon=rx.text("⚙️"),
                        text=rx.text("Settings"),
                        color_scheme="blue"
                    ),
                    button_builder(
                        icon=rx.text("❓"),
                        text=rx.text("Help"),
                        color_scheme="green"
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="4",
                width="200px",  # Ancho fijo
                min_width="200px",
                border_right="1px solid var(--gray-4)",
                padding="1rem",
                height="calc(100vh - 120px)",  # Altura fija
                overflow="hidden"  # Sin scroll en sidebar
            ),
            # Contenido principal con scroll_area
            rx.scroll_area(
                rx.box(
                    content(),
                    padding="1rem",
                    width="100%"
                ),
                height="calc(100vh - 120px)",  # Altura fija
                width="100%",
                style={
                    "flex": "1",
                    "overflow": "auto"
                }
            ),
            width="100%",
            height="calc(100vh - 120px)",
            spacing="0"
        ),
        width="100%",
        spacing="0",
        height="100vh",  # Altura total de la pantalla
        overflow="hidden"  # Sin scroll global
    )

def cards() -> rx.Component:
    """Create the cards component for the dashboard."""
    return rx.box(
    rx.grid(
        stat_card("Sessions", State.total_sessions, "👥", "blue"),
        stat_card("Projects", State.total_projects, "📁", "green"),
        stat_card("Traces", State.total_traces_formatted, "⚡", "purple"),
        stat_card("Cost", State.total_cost_formatted, "💰", "orange"),
        stat_card("Tokens", State.total_tokens_formatted, "🔤", "red"),
        columns="5",
        spacing="0",
        width="100%",
        style={
            "@media (max-width: 200px)": {"columns": "3"},
            "@media (max-width: 200px)": {"columns": "2"},
            "@media (max-width: 200px)": {"columns": "1"},
        }
    ),
    width="100%",
),

def page(State: callable, content: callable) -> rx.Component:
    """Create the main page component for the dashboard."""
    return rx.box(
        rx.box(
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "bottom": "0",
                "background": "linear-gradient(135deg, var(--gray-1) 0%, var(--blue-2) 100%)",
                "z_index": "-1",
            }
        ),
        side_bar(State, content),
        rx.script("""
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                body, html {
                    overflow: hidden !important;
                    height: 100vh !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
            `;
            document.head.appendChild(style);
        """),

        width="100vw",
        height="100vh",
        overflow="hidden",  # Sin scroll global
        style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "right": "0",
            "bottom": "0"
        }
    )