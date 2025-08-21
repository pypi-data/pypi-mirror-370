import reflex as rx
from ..backend.states import format_number_compact

def recent_traces_table(State: callable) -> rx.Component:
    """Create a modern table showing recent traces."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("🔥 Recent Traces", size="6", color="var(--accent-11)"),
                rx.spacer(),
                rx.badge("Live", variant="soft", color_scheme="green", size="2"),
                width="100%",
                align="center",
            ),
            rx.cond(
                State.recent_traces.length() > 0,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    "Type", 
                                    style={"background": "var(--gray-3)", "font_weight": "600"}
                                ),
                                rx.table.column_header_cell(
                                    "Project", 
                                    style={"background": "var(--gray-3)", "font_weight": "600"}
                                ),
                                rx.table.column_header_cell(
                                    "Duration", 
                                    style={"background": "var(--gray-3)", "font_weight": "600"}
                                ),
                                rx.table.column_header_cell(
                                    "Tokens", 
                                    style={"background": "var(--gray-3)", "font_weight": "600"}
                                ),
                                rx.table.column_header_cell(
                                    "Cost", 
                                    style={"background": "var(--gray-3)", "font_weight": "600"}
                                ),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.recent_traces,
                                lambda trace: rx.table.row(
                                    rx.table.row_header_cell(
                                        rx.badge(
                                            trace["type_name"],
                                            variant="soft",
                                            color_scheme="blue",
                                            size="2",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(trace["project_name"], weight="medium"),
                                        style={"color": "var(--gray-11)"}
                                    ),
                                    rx.table.cell(
                                        rx.text(f"{trace['duration_ms']}ms", size="2"),
                                        style={"color": "var(--green-11)"}
                                    ),
                                    rx.table.cell(
                                        rx.text(trace['total_tokens'], size="2", weight="medium"),
                                        style={"color": "var(--orange-11)"}
                                    ),
                                    rx.table.cell(
                                        rx.text(trace['call_cost'], size="2", weight="bold"),
                                        style={"color": "var(--green-11)"}
                                    ),
                                    style={
                                        "_hover": {"background": "var(--gray-2)"},
                                        "transition": "background 0.2s ease",
                                    }
                                ),
                            ),
                        ),
                        style={
                            "border_radius": "8px",
                            "overflow": "hidden",
                        }
                    ),
                    style={
                        "border_radius": "8px",
                        "overflow": "hidden",
                        "border": "1px solid var(--gray-5)",
                    }
                ),
                rx.box(
                    rx.vstack(
                        rx.text("🤖", size="9", opacity="0.3"),
                        rx.text("No traces found", color="gray", size="4"),
                        rx.text("Start generating some AI traces to see them here!", size="2", color="gray", opacity="0.7"),
                        spacing="2",
                        align="center",
                    ),
                    padding="3rem",
                    style={"text_align": "center"}
                ),
            ),
            spacing="4",
            align="start",
        ),
        width="100%",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "box_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
        },
    )


def recent_projects_list(State: callable) -> rx.Component:
    """Create a modern list showing recent projects."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("📁 Recent Projects", size="6", color="var(--accent-11)"),
                rx.spacer(),
                rx.badge(f"{State.total_projects}", variant="outline", color_scheme="blue", size="2"),
                width="100%",
                align="center",
            ),
            rx.cond(
                State.recent_projects.length() > 0,
                rx.vstack(
                    rx.foreach(
                        State.recent_projects,
                        lambda project: rx.box(
                            rx.hstack(
                                rx.badge(
                                    "�",
                                    variant="soft",
                                    color_scheme="blue",
                                    size="3",
                                    radius="full",
                                ),
                                rx.vstack(
                                    rx.text(
                                        project["name"], 
                                        weight="bold", 
                                        size="4",
                                        color="var(--gray-12)"
                                    ),
                                    rx.text(
                                        project["created_at"], 
                                        size="2", 
                                        color="var(--gray-9)",
                                        opacity="0.8"
                                    ),
                                    spacing="1",
                                    align="start",
                                ),
                                rx.spacer(),
                                rx.badge(
                                    "Active",
                                    variant="soft",
                                    color_scheme="green",
                                    size="1",
                                ),
                                spacing="3",
                                align="center",
                                width="100%",
                            ),
                            padding="1rem",
                            style={
                                "border_radius": "8px",
                                "border": "1px solid var(--gray-4)",
                                "background": "var(--gray-2)",
                                "_hover": {
                                    "background": "var(--gray-3)",
                                    "border_color": "var(--blue-6)",
                                    "transform": "translateX(4px)",
                                    "transition": "all 0.2s ease",
                                },
                                "transition": "all 0.2s ease",
                                "cursor": "pointer",
                            }
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("📂", size="8", opacity="0.3"),
                        rx.text("No projects found", color="gray", size="4"),
                        rx.text("Create your first project to get started!", size="2", color="gray", opacity="0.7"),
                        spacing="2",
                        align="center",
                    ),
                    padding="2rem",
                    style={"text_align": "center"}
                ),
            ),
            spacing="4",
            align="start",
        ),
        width="100%",
        max_width="450px",
        style={
            "background": "var(--gray-1)",
            "border": "1px solid var(--gray-4)",
            "box_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
        },
    )