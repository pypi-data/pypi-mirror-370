"""
Common UI components and utilities for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *


def info_section(items: list, grid_cols: str = "sm:grid-cols-3"):
    """
    Create a generic information section with key-value pairs.

    Args:
        items: List of (label, value) tuples
        grid_cols: CSS grid columns class

    Returns:
        FastHTML component for information display
    """
    return Div(
        *[
            Div(
                Div(label, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="text-sm text-gray-900"),
                cls="py-2"
            )
            for label, value in items
        ],
        cls=f"grid grid-cols-1 gap-2 {grid_cols}"
    )


def entity_grid(entities: dict, schema_name: str, entity_type: str, icon: str, color: str):
    """
    Create a generic grid of entity cards.

    Args:
        entities: Dictionary of entities
        schema_name: Schema name for URL generation
        entity_type: Entity type for URL generation (tables, views, etc.)
        icon: UkIcon icon name
        color: CSS color class

    Returns:
        FastHTML component for entity grid
    """
    if not entities:
        return Div()

    entity_cards = []
    # Sort entities by name for consistent display
    for entity_name, entity in sorted(entities.items()):
        # Get entity-specific info
        info_text = get_entity_info_text(entity, entity_type)

        entity_cards.append(
            A(
                Div(
                    Div(
                        UkIcon(icon, height=20, cls=f"text-{color}-500"),
                        H3(entity_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(info_text, cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/{entity_type}/{entity_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *entity_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def get_entity_info_text(entity, entity_type: str) -> str:
    """Get descriptive text for entity based on its type."""
    if entity_type == "tables":
        column_count = len(entity.columns) if hasattr(entity, 'columns') else 0
        return f"{column_count} columns"
    elif entity_type == "views":
        return "SQL View"
    elif entity_type == "procedures":
        proc_type = "Function" if getattr(entity, 'is_function', False) else "Procedure"
        param_count = len(getattr(entity, 'parameters', []))
        return f"{proc_type} ({param_count} parameters)"
    elif entity_type == "triggers":
        timing = getattr(entity, 'timing', '')
        event = getattr(entity, 'event', '')
        table_name = getattr(entity, 'table_name', '')
        return f"{timing} {event} on {table_name}"
    else:
        return ""


def sql_section(sql_content: str, title: str = "SQL Definition"):
    """
    Create a SQL section with syntax highlighting.

    Args:
        sql_content: SQL code to display
        title: Section title

    Returns:
        FastHTML component for SQL display
    """
    if not sql_content:
        return P("No SQL definition available", cls="text-gray-500")

    markdown_content = f"""```sql
{sql_content}
```"""

    return Div(
        render_md(markdown_content),
        cls="prose prose-sm max-w-none"
    )


def notes_section(entity):
    """
    Create a notes section for entities.

    Args:
        entity: Entity object with notes attribute

    Returns:
        FastHTML component for notes display
    """
    notes = list(entity.notes) if hasattr(entity, 'notes') else []

    if not notes:
        return P("No notes available", cls="text-gray-500")

    return Div(
        *[note_card(note) for note in notes],
        cls="space-y-4"
    )


def note_card(note):
    """Create a note information card."""
    return Div(
        Div(
            H3(getattr(note, 'title', 'Note'), cls="text-base font-semibold text-blue-900 mb-2"),
            Div(
                render_md(getattr(note, 'content', '')),
                cls="prose prose-sm max-w-none text-gray-700"
            ),
            cls="p-4"
        ),
        cls="border border-blue-200 bg-blue-50 rounded-lg shadow-sm"
    )


def badge(text: str, style: str = "gray"):
    """
    Create a colored badge component.

    Args:
        text: Badge text
        style: Badge style (gray, blue, green, red, yellow, purple, orange)

    Returns:
        FastHTML span component with badge styling
    """
    style_classes = {
        "gray": "bg-gray-100 text-gray-800",
        "blue": "bg-blue-100 text-blue-800",
        "green": "bg-green-100 text-green-800",
        "red": "bg-red-100 text-red-800",
        "yellow": "bg-yellow-100 text-yellow-800",
        "purple": "bg-purple-100 text-purple-800",
        "orange": "bg-orange-100 text-orange-800",
    }

    return Span(
        text,
        cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {style_classes.get(style, style_classes['gray'])}"
    )


def data_table(headers: list, rows: list, table_classes: str = "min-w-full table-auto"):
    """
    Create a data table component.

    Args:
        headers: List of header texts
        rows: List of row components
        table_classes: CSS classes for table element

    Returns:
        FastHTML table component
    """
    return Div(
        Table(
            Thead(
                Tr(
                    *[
                        Th(
                            header,
                            cls="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50"
                        )
                        for header in headers
                    ]
                ),
                cls="bg-gray-50"
            ),
            Tbody(
                *rows,
                cls="bg-white divide-y divide-gray-200"
            ),
            cls=table_classes
        ),
        cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg"
    )


def card_grid(cards: list, grid_cols: str = "sm:grid-cols-2 lg:grid-cols-3"):
    """
    Create a grid of cards.

    Args:
        cards: List of card components
        grid_cols: CSS grid columns class

    Returns:
        FastHTML div component with card grid
    """
    return Div(
        *cards,
        cls=f"grid grid-cols-1 gap-4 {grid_cols}"
    )


def info_card(title: str, content, border_color: str = "border-gray-200"):
    """
    Create an information card.

    Args:
        title: Card title
        content: Card content
        border_color: Border color class

    Returns:
        FastHTML div component styled as a card
    """
    return Div(
        Div(
            H3(title, cls="text-lg font-medium text-gray-900 mb-2"),
            content,
            cls="p-4"
        ),
        cls=f"border {border_color} rounded-lg"
    )
