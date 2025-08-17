"""
Dependency visualization routes.
Handles ER diagram and dependency analysis endpoints.
"""

from fasthtml.common import *
from starlette.requests import Request
from starlette.responses import Response
from graphviz import Digraph
from dbgear.misc.dependencies import TableDependencyAnalyzer
from dbgear.models.exceptions import DBGearError

from ..layout import layout
from ..project import get_current_project
from ..ui.dependencies import (
    render_schema_er_diagram,
    render_table_dependency_view
)


def register_dependency_routes(rt):
    """Register dependency visualization routes."""

    @rt('/schemas/{schema_name}/dependencies')
    def schema_dependencies(schema_name: str, request: Request):
        """Display ER diagram for entire schema."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return RedirectResponse(url="/")

            # Validate schema exists
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return layout(
                    title="Schema Not Found",
                    content=Div(
                        H1("Schema Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Schema '{schema_name}' does not exist in this project.", cls="text-gray-700 mb-4"),
                        A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    )
                )

            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )

            # Get schema object
            schema = project.schema_manager.schemas[schema_name]

            # Build graph data structure
            nodes = []
            edges = []

            # Add all tables as nodes
            for table_name, table_obj in schema.tables.tables.items():
                nodes.append({
                    "id": f"{schema_name}.{table_name}",
                    "type": "table",
                    "schema_name": schema_name,
                    "table_name": table_name,
                    "label": table_name
                })

            # Add all views as nodes
            for view_name, view_obj in schema.views.views.items():
                nodes.append({
                    "id": f"{schema_name}.{view_name}",
                    "type": "view",
                    "schema_name": schema_name,
                    "view_name": view_name,
                    "label": view_name
                })

            # Analyze dependencies for each table to create edges
            for table_name in schema.tables.tables.keys():
                try:
                    deps = analyzer.analyze(
                        schema_name=schema_name,
                        table_name=table_name,
                        left_level=0,  # We only need right side for schema graph
                        right_level=2
                    )

                    # Create edges from dependencies
                    for level_key, level_deps in deps["right"].items():
                        for dep in level_deps:
                            if dep["type"] == "relation" and dep["table_name"]:
                                # Foreign key relationship
                                edges.append({
                                    "source": f"{schema_name}.{table_name}",
                                    "target": f"{dep['schema_name']}.{dep['table_name']}",
                                    "type": "relation",
                                    "label": dep["object_name"],
                                    "details": dep["details"]
                                })

                except Exception as e:
                    # Skip tables that can't be analyzed
                    print(f"Warning: Could not analyze dependencies for {table_name}: {e}")
                    continue

            graph_data = {
                "nodes": nodes,
                "edges": edges,
                "schema_name": schema_name,
                "max_level": 2
            }

            # Render ER diagram page
            content = render_schema_er_diagram(schema_name, graph_data)

            return layout(
                content,
                f"ER Diagram - {schema_name} - DBGear Editor",
                str(request.url.path)
            )

        except DBGearError as e:
            return layout(
                Div(
                    H1("Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Error - DBGear Editor",
                str(request.url.path)
            )
        except Exception as e:
            return layout(
                Div(
                    H1("Internal Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An unexpected error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Internal Error - DBGear Editor",
                str(request.url.path)
            )

    @rt('/schemas/{schema_name}/tables/{table_name}/dependencies')
    def table_dependencies(schema_name: str, table_name: str, request: Request):
        """Display dependency analysis for specific table."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return RedirectResponse(url="/")

            # Validate schema and table exist
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return layout(
                    Div(
                        H1("Schema Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Schema '{schema_name}' does not exist in this project.", cls="text-gray-700 mb-4"),
                        A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    ),
                    "Schema Not Found - DBGear Editor",
                    str(request.url.path)
                )

            schema = project.schema_manager.schemas[schema_name]
            if table_name not in schema.tables.tables:
                return layout(
                    Div(
                        H1("Table Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Table '{table_name}' does not exist in schema '{schema_name}'.", cls="text-gray-700 mb-4"),
                        A(f"← Back to Schema", href=f"/schemas/{schema_name}", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    ),
                    "Table Not Found - DBGear Editor",
                    str(request.url.path)
                )

            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )

            # Analyze table dependencies
            dependencies = analyzer.analyze(
                schema_name=schema_name,
                table_name=table_name,
                left_level=3,
                right_level=3
            )

            # Render dependency view
            content = render_table_dependency_view(schema_name, table_name, dependencies)

            return layout(
                content,
                f"Dependencies - {table_name} - DBGear Editor",
                str(request.url.path)
            )

        except DBGearError as e:
            return layout(
                Div(
                    H1("Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A(f"← Back to Table", href=f"/schemas/{schema_name}/tables/{table_name}", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Error - DBGear Editor",
                str(request.url.path)
            )
        except Exception as e:
            return layout(
                Div(
                    H1("Internal Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An unexpected error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A(f"← Back to Table", href=f"/schemas/{schema_name}/tables/{table_name}", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Internal Error - DBGear Editor",
                str(request.url.path)
            )

    @rt('/schemas/{schema_name}/er-diagram')
    def schema_er_diagram_svg(schema_name: str):
        """Return SVG ER diagram for entire schema using graphviz."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return Response("Project not loaded", status_code=400)

            # Validate schema exists
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return Response(f"Schema '{schema_name}' not found", status_code=404)

            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )

            # Get schema object
            schema = project.schema_manager.schemas[schema_name]

            # Create graphviz digraph with smaller dimensions
            graph = Digraph(comment=f'ER Diagram for {schema_name}', format='svg')
            graph.attr(rankdir='TB', bgcolor='white', dpi='72', 
                      size='8,6!', margin='0.1', pad='0.2', 
                      ranksep='0.3', nodesep='0.2')
            graph.attr('node', shape='box', style='rounded,filled', 
                      fontname='Arial', fontsize='9', width='1.0', 
                      height='0.5', margin='0.1')
            graph.attr('edge', fontname='Arial', fontsize='7')

            # Add all tables as nodes
            for table_name, table_obj in schema.tables.tables.items():
                graph.node(
                    f"{schema_name}.{table_name}",
                    label=table_name,
                    fillcolor='lightblue',
                    color='blue'
                )

            # Add all views as nodes
            for view_name, view_obj in schema.views.views.items():
                graph.node(
                    f"{schema_name}.{view_name}",
                    label=view_name,
                    fillcolor='lightgreen',
                    color='green',
                    shape='ellipse'
                )

            # Analyze dependencies for each table to create edges
            for table_name in schema.tables.tables.keys():
                try:
                    deps = analyzer.analyze(
                        schema_name=schema_name,
                        table_name=table_name,
                        left_level=0,
                        right_level=2
                    )

                    # Create edges from dependencies
                    for level_key, level_deps in deps["right"].items():
                        for dep in level_deps:
                            if dep["type"] == "relation" and dep["table_name"]:
                                # Foreign key relationship
                                graph.edge(
                                    f"{schema_name}.{table_name}",
                                    f"{dep['schema_name']}.{dep['table_name']}",
                                    label=dep["object_name"],
                                    color='red'
                                )

                except Exception:
                    # Skip tables that can't be analyzed
                    continue

            # Generate SVG
            svg_content = graph.pipe(format='svg', encoding='utf-8')

            return Response(
                content=svg_content,
                media_type="image/svg+xml",
                headers={"Cache-Control": "no-cache"}
            )

        except Exception as e:
            return Response(f"Error generating SVG: {str(e)}", status_code=500)

    @rt('/schemas/{schema_name}/tables/{table_name}/diagram')
    def table_dependency_diagram_svg(schema_name: str, table_name: str):
        """Return SVG dependency diagram for specific table using graphviz."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return Response("Project not loaded", status_code=400)

            # Validate schema exists
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return Response(f"Schema '{schema_name}' not found", status_code=404)

            # Validate table exists
            schema = project.schema_manager.schemas[schema_name]
            if table_name not in schema.tables.tables:
                return Response(f"Table '{table_name}' not found", status_code=404)

            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )

            # Analyze table dependencies
            dependencies = analyzer.analyze(
                schema_name=schema_name,
                table_name=table_name,
                left_level=3,
                right_level=3
            )

            # Create graphviz digraph for table dependencies with compact size
            graph = Digraph(comment=f'Dependency Diagram for {table_name}', format='svg')
            graph.attr(rankdir='LR', bgcolor='white', dpi='72', splines='ortho',
                      size='10,6!', margin='0.2', pad='0.2', 
                      nodesep='0.4', ranksep='0.8')
            graph.attr('node', shape='box', style='rounded,filled', 
                      fontname='Arial', fontsize='9', width='1.2', 
                      height='0.6', margin='0.05')
            graph.attr('edge', fontname='Arial', fontsize='7')

            # Add central table (target table)
            target_table = dependencies.get('target_table', {})
            center_table_name = target_table.get('table_name', table_name)
            graph.node(
                f"center_{center_table_name}",
                label=center_table_name,
                fillcolor='gold',
                color='orange',
                style='rounded,filled,bold',
                fontsize='12'
            )

            # Add left side tables (referenced by)
            left_deps = dependencies.get('left', {})
            for level_key, level_deps in left_deps.items():
                for dep in level_deps:
                    if dep.get('table_name'):
                        node_id = f"left_{dep['schema_name']}_{dep['table_name']}"
                        graph.node(
                            node_id,
                            label=dep['table_name'],
                            fillcolor='lightblue',
                            color='blue'
                        )
                        # Add edge from left table to center
                        graph.edge(
                            node_id,
                            f"center_{center_table_name}",
                            label=dep.get('object_name', ''),
                            color='blue',
                            dir='forward'
                        )

            # Add right side tables (references)
            right_deps = dependencies.get('right', {})
            for level_key, level_deps in right_deps.items():
                for dep in level_deps:
                    if dep.get('table_name'):
                        node_id = f"right_{dep['schema_name']}_{dep['table_name']}"
                        graph.node(
                            node_id,
                            label=dep['table_name'],
                            fillcolor='lightgreen',
                            color='green'
                        )
                        # Add edge from center to right table
                        graph.edge(
                            f"center_{center_table_name}",
                            node_id,
                            label=dep.get('object_name', ''),
                            color='green',
                            dir='forward'
                        )

            # Generate SVG
            svg_content = graph.pipe(format='svg', encoding='utf-8')

            return Response(
                content=svg_content,
                media_type="image/svg+xml",
                headers={"Cache-Control": "no-cache"}
            )

        except Exception as e:
            return Response(f"Error generating table dependency SVG: {str(e)}", status_code=500)
