"""
View-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.requests import Request

from ..layout import layout, content_header, breadcrumb
from ..project import get_current_project
from ..ui.views import view_info_section, view_sql_section
from ..ui.common import notes_section
from ..components.right_sidebar import view_notes_sidebar


def register_view_routes(rt):
    """Register view-related routes."""

    @rt('/schemas/{schema_name}/views/{view_name}')
    def view_detail(schema_name: str, view_name: str, request: Request = None):
        """View detail page showing SQL definition and metadata."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        views = project.get_views(schema_name).get(schema_name, {})
        view = views.get(view_name)

        if not view:
            return NotFoundResponse("View not found")

        content = Div(
            breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), view_name),

            content_header(
                f"View: {view_name}",
                f"Schema: {schema_name}"
            ),

            # View information card
            Div(
                H2("View Information", cls="text-lg font-medium text-gray-900 mb-4"),
                view_info_section(view, schema_name, view_name),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # SQL Definition section
            Div(
                H2("SQL Definition", cls="text-lg font-medium text-gray-900 mb-4"),
                view_sql_section(view),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

        )

        # Create right sidebar with notes
        sidebar_content = view_notes_sidebar(view)

        return layout(
            content, 
            f"{view_name} - {schema_name} - DBGear Editor", 
            str(request.url.path) if request else "",
            sidebar_content
        )
