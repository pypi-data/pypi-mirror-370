import reflex as rx

def stat_card(title: str, value: str, icon: str = "📊", color: str = "blue", trend: str = None) -> rx.Component:
    """Create a modern statistics card component with gradient background."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(icon, size="3"),
                rx.text(title, size="3", color="gray", weight="medium"),
                spacing="2",
                align="start",
                width="100%"
            ),
            rx.text(
                value, 
                size="6", 
                weight="bold", 
                color=f"var(--{color}-11)",
            ),
            spacing="2",
            align="start",
            justify="center",
            width="100%",
            height="100%"
        ),
        width="100%",
        max_width="200px",
        min_width="150px",
        height="80px",
        style={
            "background": f"linear-gradient(135deg, var(--{color}-2), var(--{color}-3))",
            "border": f"1px solid var(--{color}-5)",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "padding": "1rem",
            "_hover": {
                "transform": "translateY(-2px)",
                "box_shadow": "0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "transition": "all 0.2s ease-in-out",
            },
            "transition": "all 0.2s ease-in-out",
        },
    )