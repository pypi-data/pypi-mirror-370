"""
Trigger-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.requests import Request

from ..layout import layout, content_header, breadcrumb
from ..project import get_current_project
from ..ui.triggers import trigger_info_section, trigger_sql_section
from ..ui.common import notes_section
from ..components.right_sidebar import trigger_notes_sidebar


def register_trigger_routes(rt):
    """Register trigger-related routes."""

    @rt('/schemas/{schema_name}/triggers/{trigger_name}')
    def trigger_detail(schema_name: str, trigger_name: str, request: Request = None):
        """Trigger detail page showing SQL definition and metadata."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        triggers = project.get_triggers(schema_name).get(schema_name, {})
        trigger = triggers.get(trigger_name)

        if not trigger:
            return NotFoundResponse("Trigger not found")

        content = Div(
            breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), trigger_name),

            content_header(
                f"Trigger: {trigger_name}",
                f"Schema: {schema_name}"
            ),

            # Trigger information card
            Div(
                H2("Trigger Information", cls="text-lg font-medium text-gray-900 mb-4"),
                trigger_info_section(trigger, schema_name, trigger_name),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # SQL Body section
            Div(
                H2("SQL Body", cls="text-lg font-medium text-gray-900 mb-4"),
                trigger_sql_section(trigger),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

        )

        # Create right sidebar with notes
        sidebar_content = trigger_notes_sidebar(trigger)

        return layout(
            content, 
            f"{trigger_name} - {schema_name} - DBGear Editor", 
            str(request.url.path) if request else "",
            sidebar_content
        )
