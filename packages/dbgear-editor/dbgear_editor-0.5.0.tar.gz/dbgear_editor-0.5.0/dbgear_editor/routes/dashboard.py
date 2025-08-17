"""
Dashboard and schema-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *
from starlette.requests import Request

from ..layout import layout, content_header, empty_state, breadcrumb
from ..project import get_current_project
from ..ui.tables import table_grid
from ..ui.views import view_grid
from ..ui.procedures import procedure_grid
from ..ui.triggers import trigger_grid
from ..ui.dependencies import dependency_navigation_button
from ..components.right_sidebar import schema_notes_sidebar


def register_dashboard_routes(rt):
    """Register dashboard and schema-related routes."""

    @rt('/')
    def index(request: Request):
        """Dashboard page showing project overview."""
        project = get_current_project()

        if not project or not project.is_loaded():
            content = Div(
                content_header(
                    "DBGear Editor",
                    "No project loaded. Please start the application with --project argument."
                ),
                empty_state(
                    "folder-open",
                    "No Project Loaded",
                    "Use 'dbgear-editor --project /path/to/project' to load a project."
                )
            )
        else:
            project_info = project.get_project_info()
            schemas = project.get_schemas()

            content = Div(
                content_header(
                    f"Project: {project_info.get('name', 'Unknown')}",
                    f"Located at: {project_info.get('path', 'Unknown')}"
                ),

                # Project statistics
                Div(
                    Div(
                        Div(
                            UkIcon("database", height=24, cls="text-blue-500"),
                            Div(
                                H3(str(project_info.get('schemas_count', 0)), cls="text-2xl font-bold text-gray-900"),
                                P("Schemas", cls="text-sm text-gray-500"),
                                cls="ml-3"
                            ),
                            cls="flex items-center"
                        ),
                        cls="bg-white overflow-hidden shadow rounded-lg p-5"
                    ),

                    Div(
                        Div(
                            UkIcon("table", height=24, cls="text-green-500"),
                            Div(
                                H3(str(project_info.get('tables_count', 0)), cls="text-2xl font-bold text-gray-900"),
                                P("Tables", cls="text-sm text-gray-500"),
                                cls="ml-3"
                            ),
                            cls="flex items-center"
                        ),
                        cls="bg-white overflow-hidden shadow rounded-lg p-5"
                    ),

                    Div(
                        Div(
                            UkIcon("eye", height=24, cls="text-purple-500"),
                            Div(
                                H3(str(project_info.get('views_count', 0)), cls="text-2xl font-bold text-gray-900"),
                                P("Views", cls="text-sm text-gray-500"),
                                cls="ml-3"
                            ),
                            cls="flex items-center"
                        ),
                        cls="bg-white overflow-hidden shadow rounded-lg p-5"
                    ),

                    Div(
                        Div(
                            UkIcon("zap", height=24, cls="text-orange-500"),
                            Div(
                                H3(str(project_info.get('procedures_count', 0)), cls="text-2xl font-bold text-gray-900"),
                                P("Procedures", cls="text-sm text-gray-500"),
                                cls="ml-3"
                            ),
                            cls="flex items-center"
                        ),
                        cls="bg-white overflow-hidden shadow rounded-lg p-5"
                    ),

                    Div(
                        Div(
                            UkIcon("flash", height=24, cls="text-yellow-500"),
                            Div(
                                H3(str(project_info.get('triggers_count', 0)), cls="text-2xl font-bold text-gray-900"),
                                P("Triggers", cls="text-sm text-gray-500"),
                                cls="ml-3"
                            ),
                            cls="flex items-center"
                        ),
                        cls="bg-white overflow-hidden shadow rounded-lg p-5"
                    ),

                    cls="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5 mb-8"
                ),

                # Recent schemas section
                Div(
                    H2("Schemas", cls="text-lg font-medium text-gray-900 mb-4"),
                    schema_grid(schemas) if schemas else empty_state(
                        "database",
                        "No Schemas Found",
                        "This project doesn't contain any database schemas yet."
                    ),
                    cls="bg-white shadow rounded-lg p-6"
                )
            )

        return layout(content, current_path=str(request.url.path))

    @rt('/schemas')
    def schemas(request: Request):
        """Schemas overview page."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()

        content = Div(
            content_header(
                "Database Schemas",
                "Manage your database schemas, tables, and views"
            ),

            schema_grid(schemas) if schemas else empty_state(
                "database",
                "No Schemas Found",
                "This project doesn't contain any database schemas yet."
            )
        )

        return layout(content, "Schemas - DBGear Editor", str(request.url.path))

    @rt('/schemas/{schema_name}')
    def schema_detail(schema_name: str, request: Request):
        """Schema detail page showing tables and views."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        tables = project.get_tables(schema_name).get(schema_name, {})
        views = project.get_views(schema_name).get(schema_name, {})
        procedures = project.get_procedures(schema_name).get(schema_name, {})
        triggers = project.get_triggers(schema_name).get(schema_name, {})

        content = Div(
            breadcrumb(("Schemas", "/schemas"), schema_name),

            content_header(
                f"Schema: {schema_name}",
                f"{len(tables)} tables, {len(views)} views, {len(procedures)} procedures, {len(triggers)} triggers"
            ),

            # ER Diagram navigation
            Div(
                dependency_navigation_button(schema_name),
                cls="mb-6"
            ),

            # Tables section
            Div(
                H2("Tables", cls="text-lg font-medium text-gray-900 mb-4"),
                table_grid(tables, schema_name) if tables else P("No tables in this schema", cls="text-gray-500"),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Views section
            Div(
                H2("Views", cls="text-lg font-medium text-gray-900 mb-4"),
                view_grid(views, schema_name) if views else P("No views in this schema", cls="text-gray-500"),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Procedures section
            Div(
                H2("Stored Procedures", cls="text-lg font-medium text-gray-900 mb-4"),
                procedure_grid(procedures, schema_name) if procedures else P("No procedures in this schema", cls="text-gray-500"),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Triggers section
            Div(
                H2("Triggers", cls="text-lg font-medium text-gray-900 mb-4"),
                trigger_grid(triggers, schema_name) if triggers else P("No triggers in this schema", cls="text-gray-500"),
                cls="bg-white shadow rounded-lg p-6"
            )
        )

        # Create right sidebar with schema notes
        sidebar_content = schema_notes_sidebar(schema)

        return layout(
            content, 
            f"{schema_name} - Schemas - DBGear Editor", 
            str(request.url.path),
            sidebar_content
        )


def schema_grid(schemas: dict):
    """Create a grid of schema cards."""
    if not schemas:
        return Div()

    schema_cards = []
    for schema_name, schema in schemas.items():
        table_count = len(schema.tables) if hasattr(schema, 'tables') else 0
        view_count = len(schema.views) if hasattr(schema, 'views') else 0
        procedure_count = len(schema.procedures) if hasattr(schema, 'procedures') else 0
        trigger_count = len(schema.triggers) if hasattr(schema, 'triggers') else 0

        schema_cards.append(
            Div(
                A(
                    Div(
                        UkIcon("database", height=20, cls="text-blue-500"),
                        H3(schema_name, cls="text-lg font-medium text-gray-900"),
                        cls="flex items-center mb-2"
                    ),
                    Div(
                        Span(f"{table_count} tables", cls="text-sm text-gray-500 mr-2"),
                        Span(f"{view_count} views", cls="text-sm text-gray-500 mr-2"),
                        cls="flex mb-1"
                    ),
                    Div(
                        Span(f"{procedure_count} procedures", cls="text-sm text-gray-500 mr-2"),
                        Span(f"{trigger_count} triggers", cls="text-sm text-gray-500"),
                        cls="flex mb-2"
                    ),
                    href=f"/schemas/{schema_name}",
                    cls="block hover:bg-gray-100 transition-colors duration-150 flex-1"
                ),
                Div(
                    dependency_navigation_button(schema_name),
                    cls="px-4 pb-4"
                ),
                cls="bg-gray-50 rounded-lg border border-gray-200 flex flex-col"
            )
        )

    return Div(
        *schema_cards,
        cls="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
    )
