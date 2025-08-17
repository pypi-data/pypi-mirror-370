"""
UI components for dependency visualization.
Provides FastHTML components for rendering ER diagrams and dependency information.
"""

from typing import Dict, List, Any, Optional
from fasthtml.common import *
from monsterui.all import *

from ..components.er_diagram import (
    generate_cytoscape_er_diagram,
    generate_table_dependency_cytoscape,
    create_dependency_summary_text
)


def render_schema_er_diagram(schema_name: str, graph_data: Dict[str, Any]) -> FT:
    """
    Render complete schema ER diagram page.
    
    Args:
        schema_name: Name of the schema
        graph_data: Graph data from dependency analyzer
        
    Returns:
        FastHTML component tree
    """
    cytoscape_data = generate_cytoscape_er_diagram(graph_data, schema_name=schema_name)
    
    # Statistics
    node_count = len(graph_data.get('nodes', []))
    edge_count = len(graph_data.get('edges', []))
    
    return Div(
        # Header section
        Div(
            H1(f"ER Diagram - {schema_name}", cls="text-3xl font-bold text-gray-900 mb-4"),
            Div(
                Span(f"{node_count} tables", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2"),
                Span(f"{edge_count} relationships", cls="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"),
                cls="mb-6"
            ),
            cls="mb-8"
        ),
        
        # ER Diagram section
        Div(
            H2("Entity Relationship Diagram", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(
                # SVG display in a container with fixed height
                Div(
                    Img(
                        src=f"/schemas/{schema_name}/er-diagram",
                        alt=f"ER Diagram for {schema_name}",
                        cls="border border-gray-200 rounded-lg bg-white",
                        style="width: 100%; height: 100%; object-fit: scale-down;"
                    ),
                    cls="w-full flex justify-center items-center",
                    style="height: 600px; overflow: hidden;"
                ),
                cls="mb-6"
            ),
            cls="mb-8"
        ),
        
        # Table list section
        Div(
            H2("Tables in Schema", cls="text-xl font-semibold text-gray-900 mb-4"),
            P("Click on any table name below to view details:", cls="text-sm text-gray-600 mb-4"),
            render_table_list(graph_data.get('nodes', []), schema_name),
            cls="mb-8"
        ),
        
        cls="container mx-auto px-4 py-8"
    )


def render_table_dependency_view(schema_name: str, table_name: str, dependencies: Dict[str, Any]) -> FT:
    """
    Render table-specific dependency view.
    
    Args:
        schema_name: Name of the schema
        table_name: Name of the table
        dependencies: Dependency data from analyzer
        
    Returns:
        FastHTML component tree
    """
    cytoscape_data = generate_table_dependency_cytoscape(dependencies)
    summary_text = create_dependency_summary_text(dependencies)
    
    return Div(
        # Header
        Div(
            H1(f"Dependencies - {table_name}", cls="text-3xl font-bold text-gray-900 mb-2"),
            P(f"Schema: {schema_name}", cls="text-gray-600 mb-6"),
            cls="mb-8"
        ),
        
        # Summary stats
        Div(
            H2("Dependency Summary", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(
                *[P(line, cls="text-sm text-gray-700") for line in summary_text],
                cls="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6"
            ),
            cls="mb-8"
        ),
        
        # Dependency Diagram
        Div(
            H2("Dependency Diagram", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(
                # SVG display in a container with fixed height
                Div(
                    Img(
                        src=f"/schemas/{schema_name}/tables/{table_name}/diagram",
                        alt=f"Dependency Diagram for {table_name}",
                        cls="border border-gray-200 rounded-lg bg-white",
                        style="width: 100%; height: 100%; object-fit: scale-down;"
                    ),
                    cls="w-full flex justify-center items-center",
                    style="height: 500px; overflow: hidden;"
                ),
                cls="mb-6"
            ),
            cls="mb-8"
        ),
        
        # Detailed dependency lists
        render_dependency_details(dependencies),
        
        cls="container mx-auto px-4 py-8"
    )


def render_table_list(nodes: List[Dict[str, Any]], schema_name: str) -> FT:
    """
    Render list of tables with links to dependency views.
    
    Args:
        nodes: List of node data from graph
        schema_name: Name of the schema
        
    Returns:
        FastHTML component
    """
    tables = sorted([node for node in nodes if node.get('type') == 'table'], key=lambda x: x.get('table_name', ''))
    views = sorted([node for node in nodes if node.get('type') == 'view'], key=lambda x: x.get('label', ''))
    
    return Div(
        # Tables section
        Div(
            H3("Tables", cls="text-lg font-medium text-gray-900 mb-3"),
            Div(
                *[
                    A(
                        Div(
                            Div(
                                UkIcon("table", height=16, cls="text-blue-500 mr-2"),
                                Strong(table['table_name'], cls="text-gray-900"),
                                cls="flex items-center mb-1"
                            ),
                            P("View table details", cls="text-xs text-gray-500"),
                            cls="p-3"
                        ),
                        href=f"/schemas/{schema_name}/tables/{table['table_name']}",
                        cls="block bg-white border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm hover:shadow-md"
                    )
                    for table in tables
                ],
                cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-6"
            ) if tables else P("No tables found", cls="text-gray-500 italic"),
            cls="mb-6"
        ),
        
        # Views section
        Div(
            H3("Views", cls="text-lg font-medium text-gray-900 mb-3"),
            Div(
                *[
                    Div(
                        Span(view['label'], cls="text-gray-700"),
                        cls="bg-blue-50 border border-blue-200 rounded-lg p-3"
                    )
                    for view in views
                ],
                cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3"
            ) if views else P("No views found", cls="text-gray-500 italic"),
            cls="mb-6"
        ) if views else None
    )


def render_dependency_details(dependencies: Dict[str, Any]) -> FT:
    """
    Render detailed dependency information in 3-column layout.
    
    Args:
        dependencies: Dependency data from analyzer
        
    Returns:
        FastHTML component
    """
    target_table = dependencies.get('target_table', {})
    center_table_name = target_table.get('table_name', 'Unknown')
    
    return Div(
        H2("Detailed Dependencies", cls="text-xl font-semibold text-gray-900 mb-4"),
        
        Div(
            # Left column: Referenced By (tables that reference this table)
            Div(
                H3("Referenced By", cls="text-lg font-medium text-gray-900 mb-3 text-center"),
                P("Tables that reference this table", cls="text-sm text-gray-600 mb-4 text-center"),
                render_dependency_list(dependencies.get('left', {}), 'left'),
                Div(
                    Div(cls="h-0 w-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-t-[15px] border-t-blue-500 mx-auto"),
                    P("→", cls="text-2xl text-blue-500 text-center mt-2"),
                    cls="mt-4"
                ),
                cls="bg-blue-50 border border-blue-200 rounded-lg p-4"
            ),
            
            # Center column: Current table
            Div(
                H3("Current Table", cls="text-lg font-medium text-gray-900 mb-3 text-center"),
                Div(
                    Div(
                        UkIcon("table", height=24, cls="text-yellow-600 mx-auto mb-2"),
                        H4(center_table_name, cls="text-xl font-bold text-gray-900 text-center"),
                        P("Focus table", cls="text-sm text-gray-600 text-center"),
                        cls="p-6 bg-white border-2 border-yellow-400 rounded-lg shadow-md"
                    ),
                    cls="flex justify-center items-center"
                ),
                cls="flex flex-col justify-center"
            ),
            
            # Right column: References (tables this table references)
            Div(
                Div(
                    Div(cls="h-0 w-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-t-[15px] border-t-green-500 mx-auto"),
                    P("→", cls="text-2xl text-green-500 text-center mt-2"),
                    cls="mb-4"
                ),
                H3("References", cls="text-lg font-medium text-gray-900 mb-3 text-center"),
                P("Tables this table references", cls="text-sm text-gray-600 mb-4 text-center"),
                render_dependency_list(dependencies.get('right', {}), 'right'),
                cls="bg-green-50 border border-green-200 rounded-lg p-4"
            ),
            
            cls="grid grid-cols-1 lg:grid-cols-3 gap-6"
        ),
        
        cls="mb-8"
    )


def render_dependency_list(dep_levels: Dict[str, List[Dict[str, Any]]], side: str) -> FT:
    """
    Render dependency list for one side (left or right).
    
    Args:
        dep_levels: Dependency levels data
        side: 'left' or 'right'
        
    Returns:
        FastHTML component
    """
    if not dep_levels:
        return P("No dependencies", cls="text-gray-500 italic")
    
    return Div(
        *[
            Div(
                H4(f"Level {level_key.split('_')[1]}", cls="text-md font-medium text-gray-800 mb-2"),
                Div(
                    *[render_dependency_item(dep) for dep in deps],
                    cls="space-y-2"
                ),
                cls="mb-4"
            )
            for level_key, deps in dep_levels.items() if deps
        ]
    )


def render_dependency_item(dep: Dict[str, Any]) -> FT:
    """
    Render individual dependency item.
    
    Args:
        dep: Dependency item data
        
    Returns:
        FastHTML component
    """
    dep_type = dep.get('type', 'unknown')
    object_name = dep.get('object_name', 'Unknown')
    table_name = dep.get('table_name')
    schema_name = dep.get('schema_name', '')
    
    # Icon based on type
    type_icons = {
        'relation': '🔗',
        'view': '👁️',
        'trigger': '⚡',
        'index': '📇'
    }
    icon = type_icons.get(dep_type, '❓')
    
    # Type color
    type_colors = {
        'relation': 'bg-blue-100 text-blue-800',
        'view': 'bg-green-100 text-green-800',
        'trigger': 'bg-yellow-100 text-yellow-800',
        'index': 'bg-purple-100 text-purple-800'
    }
    color_class = type_colors.get(dep_type, 'bg-gray-100 text-gray-800')
    
    return Div(
        Div(
            Span(icon, cls="mr-2"),
            Span(dep_type.title(), cls=f"inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {color_class} mr-2"),
            Strong(object_name, cls="text-gray-900"),
            cls="flex items-center mb-1"
        ),
        Div(
            P(f"Schema: {schema_name}" + (f" • Table: {table_name}" if table_name else ""), cls="text-xs text-gray-600"),
            # Add path information if available
            Div(
                *[P(f"via {path_item.get('table_name', 'Unknown')}", cls="text-xs text-gray-500") 
                 for path_item in dep.get('path', [])],
                cls="ml-4"
            ) if dep.get('path') else None,
            cls="ml-6"
        ),
        cls="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
    )


def dependency_navigation_button(schema_name: str, table_name: Optional[str] = None) -> FT:
    """
    Create navigation button to dependency views.
    
    Args:
        schema_name: Name of the schema
        table_name: Optional table name for table-specific view
        
    Returns:
        FastHTML component
    """
    if table_name:
        href = f"/schemas/{schema_name}/tables/{table_name}/dependencies"
        text = "View Dependencies"
        icon = "🔗"
    else:
        href = f"/schemas/{schema_name}/dependencies"
        text = "View ER Diagram"
        icon = "📊"
    
    return A(
        Span(icon, cls="mr-2"),
        text,
        href=href,
        cls="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
    )