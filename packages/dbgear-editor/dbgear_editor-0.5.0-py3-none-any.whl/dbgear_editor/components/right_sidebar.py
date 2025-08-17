"""
Right sidebar component for displaying notes and additional information.
"""

from fasthtml.common import *
from monsterui.all import *
from ..ui.common import notes_section


def right_sidebar_component(entity=None, title="Notes"):
    """
    Create right sidebar with notes display.
    
    Args:
        entity: Entity object with notes attribute
        title: Sidebar title (default: "Notes")
        
    Returns:
        FastHTML component for right sidebar content
    """
    if not entity:
        return Div(
            Div(
                H2(title, cls="text-sm font-semibold text-gray-700 mb-3"),
                P("No notes available", cls="text-sm text-gray-500 italic"),
                cls="p-4"
            )
        )
    
    return Div(
        # Header - smaller and less prominent
        Div(
            H2(title, cls="text-sm font-semibold text-gray-700 mb-3"),
            cls="p-4 border-b border-gray-200"
        ),
        
        # Notes content
        Div(
            notes_section(entity),
            cls="p-4"
        )
    )


def notes_sidebar_for_entity(entity, entity_type="Entity"):
    """
    Create notes sidebar specifically for an entity.
    
    Args:
        entity: Entity object with notes
        entity_type: Type of entity (Table, View, etc.)
        
    Returns:
        FastHTML component for entity notes sidebar
    """
    notes_count = len(list(entity.notes)) if hasattr(entity, 'notes') else 0
    
    # Show just "Notes" or entity type + "Notes" without count
    title = "Notes"
    
    return right_sidebar_component(entity, title)


def schema_notes_sidebar(schema):
    """
    Create notes sidebar for schema.
    
    Args:
        schema: Schema object with notes
        
    Returns:
        FastHTML component for schema notes sidebar
    """
    return notes_sidebar_for_entity(schema, "Schema")


def table_notes_sidebar(table):
    """
    Create notes sidebar for table.
    
    Args:
        table: Table object with notes
        
    Returns:
        FastHTML component for table notes sidebar
    """
    return notes_sidebar_for_entity(table, "Table")


def view_notes_sidebar(view):
    """
    Create notes sidebar for view.
    
    Args:
        view: View object with notes
        
    Returns:
        FastHTML component for view notes sidebar
    """
    return notes_sidebar_for_entity(view, "View")


def procedure_notes_sidebar(procedure):
    """
    Create notes sidebar for procedure.
    
    Args:
        procedure: Procedure object with notes
        
    Returns:
        FastHTML component for procedure notes sidebar
    """
    return notes_sidebar_for_entity(procedure, "Procedure")


def trigger_notes_sidebar(trigger):
    """
    Create notes sidebar for trigger.
    
    Args:
        trigger: Trigger object with notes
        
    Returns:
        FastHTML component for trigger notes sidebar
    """
    return notes_sidebar_for_entity(trigger, "Trigger")