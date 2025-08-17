"""
View-related UI components for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from .common import info_section, sql_section


def view_grid(views: dict, schema_name: str):
    """Create a grid of view cards."""
    if not views:
        return Div()

    view_cards = []
    for view_name, view in views.items():
        view_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("eye", height=20, cls="text-purple-500"),
                        H3(view_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P("SQL View", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/views/{view_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *view_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def view_info_section(view, schema_name: str, view_name: str):
    """Create view information section."""
    info_items = [
        ("View Name", view_name),
        ("Display Name", getattr(view, 'display_name', view_name)),
        ("Schema", schema_name),
    ]

    # Add view type if available
    if hasattr(view, 'view_type'):
        info_items.append(("View Type", getattr(view, 'view_type', 'Standard')))

    # Add materialized info if available
    if hasattr(view, 'is_materialized'):
        info_items.append(("Materialized", "Yes" if getattr(view, 'is_materialized', False) else "No"))

    return info_section(info_items)


def view_sql_section(view):
    """Create view SQL section with syntax highlighting."""
    sql_statement = getattr(view, 'sql_statement', None) or getattr(view, 'select_statement', None)
    return sql_section(sql_statement, "SQL Definition")
