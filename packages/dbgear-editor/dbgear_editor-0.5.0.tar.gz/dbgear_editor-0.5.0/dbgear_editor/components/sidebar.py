"""
Sidebar component for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from ..project import get_current_project


def sidebar_component(current_path: str = ""):
    """
    Create the main sidebar component with schema and table navigation.

    Returns:
        FastHTML component for the sidebar
    """
    project = get_current_project()

    if not project or not project.is_loaded():
        return Aside(
            Div(
                Div(
                    UkIcon("folder-open", height=48, cls="mx-auto text-gray-400"),
                    H3("No Project Loaded", cls="mt-4 text-lg font-medium text-gray-900 text-center"),
                    P("Load a project to view schemas and tables", cls="mt-2 text-sm text-gray-500 text-center"),
                    P("Use 'dbgear-editor --project /path/to/project' to load a project.", cls="text-sm text-gray-500 mt-4"),
                    cls="text-center py-8"
                ),
                cls="px-4"
            ),
            cls="w-64 bg-gray-50 h-full border-r border-gray-200 overflow-y-auto"
        )

    schemas = project.get_schemas()
    tables = project.get_tables()
    views = project.get_views()
    procedures = project.get_procedures()
    triggers = project.get_triggers()

    return Aside(
        Div(

            # Schema navigation
            Div(
                *[schema_section(schema_name, schema, tables.get(schema_name, {}), views.get(schema_name, {}), procedures.get(schema_name, {}), triggers.get(schema_name, {}), current_path)
                  for schema_name, schema in schemas.items()],
                cls="px-2 py-4"
            ) if schemas else Div(
                P("No schemas found", cls="text-sm text-gray-500 px-4 py-8 text-center"),
                cls="px-2 py-4"
            ),

            cls="overflow-y-auto"
        ),
        cls="w-64 bg-gray-50 h-full border-r border-gray-200 flex flex-col"
    )



def schema_section(schema_name: str, schema, schema_tables: dict, schema_views: dict, schema_procedures: dict, schema_triggers: dict, current_path: str = ""):
    """
    Create a collapsible schema section with tables, views, procedures, and triggers.

    Args:
        schema_name: Name of the schema
        schema: Schema object
        schema_tables: Tables in this schema
        schema_views: Views in this schema
        schema_procedures: Procedures in this schema
        schema_triggers: Triggers in this schema

    Returns:
        FastHTML component for schema section
    """
    schema_id = f"schema-{schema_name}"

    # Check if current URL matches this schema to keep it expanded

    # Determine if this schema section should be expanded
    is_current_schema = f"/schemas/{schema_name}/" in current_path
    section_class = "ml-4 mt-1" + ("" if is_current_schema else " hidden")
    chevron_rotation = "rotate(90deg)" if is_current_schema else "rotate(0deg)"

    return Div(
        # Schema header (collapsible)
        Button(
            Div(
                UkIcon("database", height=16, cls="mr-2"),
                Span(schema_name, cls="font-medium text-gray-900"),
                Span(f"({len(schema_tables)}T, {len(schema_views)}V, {len(schema_procedures)}P, {len(schema_triggers)}Tr)", cls="text-xs text-gray-500 ml-1"),
                cls="flex items-center flex-1"
            ),
            UkIcon("chevron-right", height=16, cls="text-gray-400 transform transition-transform duration-200", style=f"transform: {chevron_rotation}", **{"data-chevron": schema_id}),
            cls="w-full flex items-center justify-between px-2 py-2 text-left text-sm rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500",
            **{"data-toggle": schema_id}
        ),

        # Schema content (tables and views)
        Div(
            # Tables section
            *([
                Div(
                    Div(
                        UkIcon("table", height=14, cls="mr-1 text-gray-400"),
                        Span("Tables", cls="text-xs font-medium text-gray-700"),
                        cls="flex items-center px-3 py-1"
                    ),
                    *[table_item(table_name, table, schema_name, current_path) for table_name, table in sorted(schema_tables.items())],
                    cls="mb-2"
                )
            ] if schema_tables else []),

            # Views section
            *([
                Div(
                    Div(
                        UkIcon("eye", height=14, cls="mr-1 text-gray-400"),
                        Span("Views", cls="text-xs font-medium text-gray-700"),
                        cls="flex items-center px-3 py-1"
                    ),
                    *[view_item(view_name, view, schema_name, current_path) for view_name, view in sorted(schema_views.items())],
                    cls="mb-2"
                )
            ] if schema_views else []),

            # Procedures section
            *([
                Div(
                    Div(
                        UkIcon("zap", height=14, cls="mr-1 text-gray-400"),
                        Span("Procedures", cls="text-xs font-medium text-gray-700"),
                        cls="flex items-center px-3 py-1"
                    ),
                    *[procedure_item(procedure_name, procedure, schema_name, current_path) for procedure_name, procedure in sorted(schema_procedures.items())],
                    cls="mb-2"
                )
            ] if schema_procedures else []),

            # Triggers section
            *([
                Div(
                    Div(
                        UkIcon("flash", height=14, cls="mr-1 text-gray-400"),
                        Span("Triggers", cls="text-xs font-medium text-gray-700"),
                        cls="flex items-center px-3 py-1"
                    ),
                    *[trigger_item(trigger_name, trigger, schema_name, current_path) for trigger_name, trigger in sorted(schema_triggers.items())],
                    cls="mb-2"
                )
            ] if schema_triggers else []),

            cls=section_class,
            id=schema_id
        ),

        cls="mb-1"
    )


def table_item(table_name: str, table, schema_name: str, current_path: str = ""):
    """
    Create a table item link.

    Args:
        table_name: Name of the table
        table: Table object
        schema_name: Name of the parent schema

    Returns:
        FastHTML component for table item
    """
    column_count = len(table.columns) if hasattr(table, 'columns') else 0

    # Check if this is the current active item
    table_base_path = f"/schemas/{schema_name}/tables/{table_name}"
    is_active = current_path == table_base_path or current_path.startswith(table_base_path + "/")
    item_class = "block px-3 py-1 rounded text-sm transition-colors duration-150"
    if is_active:
        item_class += " bg-blue-100 text-blue-800 font-medium"
    else:
        item_class += " hover:bg-blue-50 hover:text-blue-700"

    return A(
        Div(
            UkIcon("table", height=14, cls="mr-2 text-blue-500"),
            Span(table_name, cls="text-sm"),
            Span(f"({column_count})", cls="text-xs text-gray-500 ml-1"),
            cls="flex items-center"
        ),
        href=f"/schemas/{schema_name}/tables/{table_name}",
        cls=item_class
    )


def view_item(view_name: str, view, schema_name: str, current_path: str = ""):
    """
    Create a view item link.

    Args:
        view_name: Name of the view
        view: View object
        schema_name: Name of the parent schema

    Returns:
        FastHTML component for view item
    """
    # Check if this is the current active item
    view_base_path = f"/schemas/{schema_name}/views/{view_name}"
    is_active = current_path == view_base_path or current_path.startswith(view_base_path + "/")
    item_class = "block px-3 py-1 rounded text-sm transition-colors duration-150"
    if is_active:
        item_class += " bg-purple-100 text-purple-800 font-medium"
    else:
        item_class += " hover:bg-purple-50 hover:text-purple-700"

    return A(
        Div(
            UkIcon("eye", height=14, cls="mr-2 text-purple-500"),
            Span(view_name, cls="text-sm"),
            cls="flex items-center"
        ),
        href=f"/schemas/{schema_name}/views/{view_name}",
        cls=item_class
    )


def procedure_item(procedure_name: str, procedure, schema_name: str, current_path: str = ""):
    """
    Create a procedure item link.

    Args:
        procedure_name: Name of the procedure
        procedure: Procedure object
        schema_name: Name of the parent schema

    Returns:
        FastHTML component for procedure item
    """
    proc_type = "F" if getattr(procedure, 'is_function', False) else "P"

    # Check if this is the current active item
    procedure_base_path = f"/schemas/{schema_name}/procedures/{procedure_name}"
    is_active = current_path == procedure_base_path or current_path.startswith(procedure_base_path + "/")
    item_class = "block px-3 py-1 rounded text-sm transition-colors duration-150"
    if is_active:
        item_class += " bg-orange-100 text-orange-800 font-medium"
    else:
        item_class += " hover:bg-orange-50 hover:text-orange-700"

    return A(
        Div(
            UkIcon("zap", height=14, cls="mr-2 text-orange-500"),
            Span(procedure_name, cls="text-sm"),
            Span(f"({proc_type})", cls="text-xs text-gray-500 ml-1"),
            cls="flex items-center"
        ),
        href=f"/schemas/{schema_name}/procedures/{procedure_name}",
        cls=item_class
    )


def trigger_item(trigger_name: str, trigger, schema_name: str, current_path: str = ""):
    """
    Create a trigger item link.

    Args:
        trigger_name: Name of the trigger
        trigger: Trigger object
        schema_name: Name of the parent schema

    Returns:
        FastHTML component for trigger item
    """
    # Get trigger timing and event for display
    timing = getattr(trigger, 'timing', '')[:1]  # B/A for BEFORE/AFTER
    event = getattr(trigger, 'event', '')[:1]    # I/U/D for INSERT/UPDATE/DELETE

    # Check if this is the current active item
    trigger_base_path = f"/schemas/{schema_name}/triggers/{trigger_name}"
    is_active = current_path == trigger_base_path or current_path.startswith(trigger_base_path + "/")
    item_class = "block px-3 py-1 rounded text-sm transition-colors duration-150"
    if is_active:
        item_class += " bg-yellow-100 text-yellow-800 font-medium"
    else:
        item_class += " hover:bg-yellow-50 hover:text-yellow-700"

    return A(
        Div(
            UkIcon("flash", height=14, cls="mr-2 text-yellow-500"),
            Span(trigger_name, cls="text-sm"),
            Span(f"({timing}{event})", cls="text-xs text-gray-500 ml-1"),
            cls="flex items-center"
        ),
        href=f"/schemas/{schema_name}/triggers/{trigger_name}",
        cls=item_class
    )
