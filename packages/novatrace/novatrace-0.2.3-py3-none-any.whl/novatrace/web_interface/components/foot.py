import reflex as rx

def footer() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("Powered by", size="2", color="gray"),
            rx.text("NovaTrace", weight="bold", size="2", color="var(--blue-11)"),
            rx.text("•", size="2", color="gray"),
        rx.text("Built with Reflex", size="2", color="gray"),
        spacing="2",
        justify="center",
    ),
    padding="2rem",
    style={"border_top": "1px solid var(--gray-4)"}
),