"""
Header component for DBGear Editor.
"""

from fasthtml.common import *
from monsterui.all import *

from ..project import get_current_project


def header_component():
    """
    Create the main header component with title and navigation menu.

    Returns:
        FastHTML component for the header
    """
    project = get_current_project()
    project_info = project.get_project_info() if project else {}
    project_name = project_info.get('name', 'No Project')

    return Header(
        Div(
            # Left side - Title and project info
            Div(
                H1("DBGear Editor", cls="text-2xl font-bold text-white"),
                Span(f"Project: {project_name}", cls="text-sm text-gray-300 ml-4"),
                project_stats_badges(),
                cls="flex items-center"
            ),

            # Right side - Navigation menu
            Nav(
                Div(
                    # Main navigation buttons
                    A("Dashboard", href="/", cls="text-white hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"),
                    A("Schemas", href="/schemas", cls="text-white hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"),
                    A("Data", href="/data", cls="text-white hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"),


                    cls="flex items-center space-x-1"
                ),
                cls="flex items-center"
            ),

            cls="flex justify-between items-center px-6 py-4"
        ),
        cls="bg-blue-600 shadow-lg"
    )


def project_stats_badges():
    """
    Create project statistics badges showing entity counts.

    Returns:
        FastHTML component for project statistics
    """
    project = get_current_project()

    if not project or not project.is_loaded():
        return Span(
            UkIcon("alert-circle", height=14, cls="mr-1"),
            "No Project",
            cls="inline-flex items-center px-2 py-1 rounded text-xs bg-red-500 text-white ml-4"
        )

    project_info = project.get_project_info()

    badges = []
    
    # Core entities
    if project_info.get('schemas_count', 0) > 0:
        badges.append(
            Span(f"{project_info.get('schemas_count', 0)} Schemas", cls="px-3 py-1 text-xs bg-blue-500 text-white rounded")
        )
    
    if project_info.get('tables_count', 0) > 0:
        badges.append(
            Span(f"{project_info.get('tables_count', 0)} Tables", cls="px-3 py-1 text-xs bg-green-500 text-white rounded")
        )
    
    if project_info.get('views_count', 0) > 0:
        badges.append(
            Span(f"{project_info.get('views_count', 0)} Views", cls="px-3 py-1 text-xs bg-purple-500 text-white rounded")
        )
    
    if project_info.get('procedures_count', 0) > 0:
        badges.append(
            Span(f"{project_info.get('procedures_count', 0)} Procedures", cls="px-3 py-1 text-xs bg-orange-500 text-white rounded")
        )
    
    if project_info.get('triggers_count', 0) > 0:
        badges.append(
            Span(f"{project_info.get('triggers_count', 0)} Triggers", cls="px-3 py-1 text-xs bg-yellow-500 text-white rounded")
        )

    if not badges:
        return Span("Empty Project", cls="px-2 py-1 text-xs bg-gray-500 text-white rounded ml-4")

    return Div(
        *badges,
        cls="flex items-center space-x-2 ml-4"
    )


def project_status_badge():
    """
    Create a project status badge showing current project information.

    Returns:
        FastHTML component for project status
    """
    project = get_current_project()

    if not project or not project.is_loaded():
        return Span(
            UkIcon("alert-circle", height=16, cls="mr-1"),
            "No Project Loaded",
            cls="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
        )

    project_info = project.get_project_info()

    return Span(
        UkIcon("check-circle", height=16, cls="mr-1"),
        f"{project_info.get('schemas_count', 0)} schemas, {project_info.get('tables_count', 0)} tables",
        cls="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
    )
