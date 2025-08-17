"""
Procedure-related route handlers for DBGear Editor.
"""

from fasthtml.common import *
from starlette.requests import Request

from ..layout import layout, content_header, breadcrumb
from ..project import get_current_project
from ..ui.procedures import (
    procedure_info_section, procedure_parameters_section, procedure_sql_section
)
from ..ui.common import notes_section
from ..components.right_sidebar import procedure_notes_sidebar


def register_procedure_routes(rt):
    """Register procedure-related routes."""

    @rt('/schemas/{schema_name}/procedures/{procedure_name}')
    def procedure_detail(schema_name: str, procedure_name: str, request: Request):
        """Procedure detail page showing SQL definition and parameters."""
        project = get_current_project()

        if not project or not project.is_loaded():
            return RedirectResponse(url="/")

        schemas = project.get_schemas()
        schema = schemas.get(schema_name)

        if not schema:
            return NotFoundResponse("Schema not found")

        procedures = project.get_procedures(schema_name).get(schema_name, {})
        procedure = procedures.get(procedure_name)

        if not procedure:
            return NotFoundResponse("Procedure not found")

        content = Div(
            breadcrumb(("Schemas", "/schemas"), (schema_name, f"/schemas/{schema_name}"), procedure_name),

            content_header(
                f"{'Function' if procedure.is_function else 'Procedure'}: {procedure_name}",
                f"Schema: {schema_name}"
            ),

            # Procedure information card
            Div(
                H2("Procedure Information", cls="text-lg font-medium text-gray-900 mb-4"),
                procedure_info_section(procedure, schema_name, procedure_name),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

            # Parameters section (if any)
            *([
                Div(
                    H2("Parameters", cls="text-lg font-medium text-gray-900 mb-4"),
                    procedure_parameters_section(procedure),
                    cls="bg-white shadow rounded-lg p-6 mb-6"
                )
            ] if len(procedure.parameters) > 0 else []),

            # SQL Body section
            Div(
                H2("SQL Body", cls="text-lg font-medium text-gray-900 mb-4"),
                procedure_sql_section(procedure),
                cls="bg-white shadow rounded-lg p-6 mb-6"
            ),

        )

        # Create right sidebar with notes
        sidebar_content = procedure_notes_sidebar(procedure)

        return layout(
            content, 
            f"{procedure_name} - {schema_name} - DBGear Editor", 
            str(request.url.path),
            sidebar_content
        )
