"""
Table-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.requests import Request

from ..layout import layout, content_header, breadcrumb
from ..project import get_current_project
from ..ui.tables import (
    table_info_section, table_columns_section,
    table_indexes_section, table_relations_section
)
from ..ui.common import notes_section
from ..ui.dependencies import dependency_navigation_button
from ..components.right_sidebar import table_notes_sidebar


def register_table_routes(rt):
    """Register table-related routes."""

    @rt('/schemas/{schema_name}/tables/{table_name}')
    def table_detail(schema_name: str, table_name: str, request: Request = None):
        """Table detail page showing column definitions and constraints."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        tables = project.get_tables(schema_name).get(schema_name, {})
        table = tables.get(table_name)

        if not table:
            return NotFoundResponse("Table not found")

        content = Div(
            breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), table_name),

            content_header(
                f"Table: {table_name}",
                f"Schema: {schema_name}"
            ),

            # Dependencies navigation
            Div(
                dependency_navigation_button(schema_name, table_name),
                cls="mb-6"
            ),

            # Table information card
            Div(
                H2("Table Information", cls="text-lg font-medium text-gray-900 mb-4"),
                table_info_section(table, schema_name, table_name),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Columns section
            Div(
                H2("Columns", cls="text-lg font-medium text-gray-900 mb-4"),
                table_columns_section(table),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Indexes section (if any)
            *([
                Div(
                    H2("Indexes", cls="text-lg font-medium text-gray-900 mb-4"),
                    table_indexes_section(table),
                    cls="bg-white shadow rounded-lg p-6 mb-6"
                )
            ] if len(list(table.indexes)) > 0 else []),

            # Relations section (if any)
            *([
                Div(
                    H2("Relations", cls="text-lg font-medium text-gray-900 mb-4"),
                    table_relations_section(table),
                    cls="bg-white shadow rounded-lg p-6 mb-6"
                )
            ] if len(list(table.relations)) > 0 else []),

        )

        # Create right sidebar with notes
        sidebar_content = table_notes_sidebar(table)

        return layout(
            content, 
            f"{table_name} - {schema_name} - DBGear Editor", 
            str(request.url.path) if request else "",
            sidebar_content
        )
