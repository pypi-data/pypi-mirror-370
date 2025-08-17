"""
Table-related UI components for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from .common import info_section, badge, data_table, info_card


def table_grid(tables: dict, schema_name: str):
    """Create a grid of table cards."""
    if not tables:
        return Div()

    table_cards = []
    # Sort tables by name for consistent display
    for table_name, table in sorted(tables.items()):
        column_count = len(table.columns) if hasattr(table, 'columns') else 0

        table_cards.append(
            A(
                Div(
                    Div(
                        UkIcon("table", height=20, cls="text-green-500"),
                        H3(table_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    P(f"{column_count} columns", cls="text-sm text-gray-500"),
                    cls="p-4"
                ),
                href=f"/schemas/{schema_name}/tables/{table_name}",
                cls="block bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors duration-150"
            )
        )

    return Div(
        *table_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )


def table_info_section(table, schema_name: str, table_name: str):
    """Create table information section."""
    mysql_options = table.mysql_options

    info_items = [
        ("Table Name", table_name),
        ("Display Name", table.display_name),
        ("Schema", schema_name),
    ]

    if mysql_options:
        info_items.extend([
            ("Engine", mysql_options.engine or "InnoDB"),
            ("Charset", mysql_options.charset or "Default"),
            ("Collation", mysql_options.collation or "Default"),
        ])

        if mysql_options.auto_increment:
            info_items.append(("Auto Increment", str(mysql_options.auto_increment)))

        if mysql_options.row_format:
            info_items.append(("Row Format", mysql_options.row_format))

    return info_section(info_items)


def table_columns_section(table):
    """Create table columns section with detailed information."""
    columns = list(table.columns)

    if not columns:
        return P("No columns defined", cls="text-gray-500")

    headers = [
        "Column Name", "Data Type", "Nullable", "Default",
        "Auto Inc", "Primary Key", "Description"
    ]

    rows = [column_row(column) for column in columns]

    return data_table(headers, rows)


def column_row(column):
    """Create a table row for a column."""
    # Format column type
    col_type = column.column_type
    type_display = col_type.base_type if col_type else "Unknown"

    if col_type and col_type.length:
        type_display += f"({col_type.length}"
        if col_type.precision:
            type_display += f",{col_type.precision}"
        type_display += ")"

    # Create badges for boolean values
    nullable_badge = badge("Yes", "green") if column.nullable else badge("No", "red")
    auto_inc_badge = badge("Yes", "blue") if column.auto_increment else ""
    primary_key_badge = badge(str(column.primary_key + 1), "purple") if column.primary_key is not None else ""

    return Tr(
        Td(
            Code(column.column_name, cls="text-sm font-mono text-blue-600"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(
            Code(type_display, cls="text-sm font-mono text-gray-900"),
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(nullable_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(
            Code(column.default_value or "", cls="text-sm font-mono text-gray-500") if column.default_value else "",
            cls="px-6 py-4 whitespace-nowrap"
        ),
        Td(auto_inc_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(primary_key_badge, cls="px-6 py-4 whitespace-nowrap"),
        Td(
            column.display_name or "",
            cls="px-6 py-4 text-sm text-gray-900"
        ),
        cls="hover:bg-gray-50"
    )


def table_indexes_section(table):
    """Create table indexes section."""
    indexes = list(table.indexes)

    if not indexes:
        return P("No indexes defined", cls="text-gray-500")

    return Div(
        *[index_card(index) for index in indexes],
        cls="space-y-4"
    )


def index_card(index):
    """Create an index information card."""
    index_type_badge_styles = {
        "PRIMARY": "red",
        "UNIQUE": "yellow",
        "INDEX": "blue",
        "FULLTEXT": "green",
        "SPATIAL": "purple",
    }

    badge_style = index_type_badge_styles.get(index.index_type, "gray")

    content = Div(
        Div(
            H3(index.index_name, cls="text-lg font-medium text-gray-900"),
            badge(index.index_type, badge_style),
            cls="flex items-center justify-between"
        ),
        Div(
            Span("Columns: ", cls="font-medium text-gray-700"),
            Span(", ".join(index.columns), cls="text-gray-900"),
            cls="mt-2"
        ),
        *([
            Div(
                Span("Unique: ", cls="font-medium text-gray-700"),
                Span("Yes" if index.is_unique else "No", cls="text-gray-900"),
                cls="mt-1"
            )
        ] if hasattr(index, 'is_unique') else [])
    )

    return info_card(f"Index: {index.index_name}", content)


def table_relations_section(table):
    """Create table relations section."""
    relations = list(table.relations)

    if not relations:
        return P("No relations defined", cls="text-gray-500")

    return Div(
        *[relation_card(relation) for relation in relations],
        cls="space-y-4"
    )


def relation_card(relation):
    """Create a relation information card."""
    relation_name = getattr(relation, 'constraint_name', None) or "Foreign Key"

    content = Div(
        Div(
            Span("Target Table: ", cls="font-medium text-gray-700"),
            Span(f"{relation.target.schema_name}.{relation.target.table_name}", cls="text-gray-900"),
            cls="mb-1"
        ),
        Div(
            Span("Columns: ", cls="font-medium text-gray-700"),
            Span(
                " → ".join([
                    f"{bind.source_column} → {bind.target_column}"
                    for bind in relation.bind_columns
                ]),
                cls="text-gray-900"
            ),
            cls="mb-1"
        ),
        Div(
            Span("Cardinality: ", cls="font-medium text-gray-700"),
            Span(f"{relation.cardinarity_source} : {relation.cardinarity_target}", cls="text-gray-900"),
            cls="mb-1"
        ),
        Div(
            Span("On Delete: ", cls="font-medium text-gray-700"),
            Span(relation.on_delete, cls="text-gray-900"),
            cls="mb-1"
        ),
        Div(
            Span("On Update: ", cls="font-medium text-gray-700"),
            Span(relation.on_update, cls="text-gray-900"),
            cls="mb-1"
        ),
        *([
            Div(
                Span("Description: ", cls="font-medium text-gray-700"),
                Span(relation.description, cls="text-gray-900"),
            )
        ] if relation.description else [])
    )

    return info_card(relation_name, content)
