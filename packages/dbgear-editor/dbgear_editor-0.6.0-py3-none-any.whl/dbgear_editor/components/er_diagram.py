"""
ER diagram component for rendering Cytoscape.js diagrams.
Converts dependency analysis data to Cytoscape.js JSON format.
"""

from typing import Dict, List, Any, Optional
import json


def generate_cytoscape_er_diagram(graph_data: Dict[str, Any], focus_table: Optional[str] = None, schema_name: Optional[str] = None) -> str:
    """
    Generate Cytoscape.js JSON data from dependency graph data.
    
    Args:
        graph_data: Graph data from TableDependencyAnalyzer
        focus_table: Optional table name to highlight as center of diagram
        schema_name: Schema name for click links
        
    Returns:
        JSON string containing cytoscape.js elements
    """
    elements = []
    processed_nodes = set()
    processed_edges = set()
    
    # Process nodes (tables and views)
    for node in graph_data.get('nodes', []):
        if node['type'] == 'table':
            table_name = node['table_name']
            node_id = _clean_identifier(table_name)
            
            if node_id not in processed_nodes:
                # Create table node
                node_element = {
                    'data': {
                        'id': node_id,
                        'label': table_name,
                        'type': 'table',
                        'focused': focus_table == table_name
                    },
                    'classes': 'table-node' + (' focused' if focus_table == table_name else '')
                }
                elements.append(node_element)
                processed_nodes.add(node_id)
    
    # Process edges (relationships)
    for edge in graph_data.get('edges', []):
        if edge['type'] == 'relation':
            source_table = _extract_table_name(edge['source'])
            target_table = _extract_table_name(edge['target'])
            
            if source_table and target_table:
                source_id = _clean_identifier(source_table)
                target_id = _clean_identifier(target_table)
                edge_id = f"{source_id}-{target_id}"
                
                if edge_id not in processed_edges:
                    # Ensure nodes exist
                    for node_id, table_name in [(source_id, source_table), (target_id, target_table)]:
                        if node_id not in processed_nodes:
                            node_element = {
                                'data': {
                                    'id': node_id,
                                    'label': table_name,
                                    'type': 'table'
                                },
                                'classes': 'table-node'
                            }
                            elements.append(node_element)
                            processed_nodes.add(node_id)
                    
                    # Create edge
                    edge_element = {
                        'data': {
                            'id': edge_id,
                            'source': source_id,
                            'target': target_id,
                            'label': edge.get('label', 'references'),
                            'type': 'relation'
                        },
                        'classes': 'relation-edge'
                    }
                    elements.append(edge_element)
                    processed_edges.add(edge_id)
    
    return json.dumps(elements, ensure_ascii=False)


def generate_table_dependency_cytoscape(dependencies: Dict[str, Any]) -> str:
    """
    Generate Cytoscape.js JSON for individual table dependencies.
    
    Args:
        dependencies: Output from TableDependencyAnalyzer.analyze()
        
    Returns:
        JSON string containing cytoscape.js elements
    """
    elements = []
    processed_nodes = set()
    processed_edges = set()
    
    # Central table
    target_table = dependencies.get('target_table', {})
    center_table_name = target_table.get('table_name', 'Unknown')
    center_id = _clean_identifier(center_table_name)
    
    # Add central table node
    center_element = {
        'data': {
            'id': center_id,
            'label': center_table_name,
            'type': 'table',
            'central': True
        },
        'classes': 'table-node central'
    }
    elements.append(center_element)
    processed_nodes.add(center_id)
    
    # Process left dependencies (tables referencing this one)
    for level_key, deps in dependencies.get('left', {}).items():
        for dep in deps:
            if dep['type'] == 'relation' and dep.get('table_name'):
                ref_table_name = dep['table_name']
                ref_id = _clean_identifier(ref_table_name)
                
                # Add referencing table node
                if ref_id not in processed_nodes:
                    ref_element = {
                        'data': {
                            'id': ref_id,
                            'label': ref_table_name,
                            'type': 'table'
                        },
                        'classes': 'table-node'
                    }
                    elements.append(ref_element)
                    processed_nodes.add(ref_id)
                
                # Add edge (referenced by) - direction: ref_table -> center_table
                edge_id = f"{ref_id}-{center_id}"
                if edge_id not in processed_edges:
                    edge_element = {
                        'data': {
                            'id': edge_id,
                            'source': ref_id,
                            'target': center_id,
                            'label': 'references',
                            'type': 'referenced_by'
                        },
                        'classes': 'relation-edge referenced-by'
                    }
                    elements.append(edge_element)
                    processed_edges.add(edge_id)
    
    # Process right dependencies (tables this one references)
    for level_key, deps in dependencies.get('right', {}).items():
        for dep in deps:
            if dep['type'] == 'relation' and dep.get('table_name'):
                target_table_name = dep['table_name']
                target_id = _clean_identifier(target_table_name)
                
                # Add target table node
                if target_id not in processed_nodes:
                    target_element = {
                        'data': {
                            'id': target_id,
                            'label': target_table_name,
                            'type': 'table'
                        },
                        'classes': 'table-node'
                    }
                    elements.append(target_element)
                    processed_nodes.add(target_id)
                
                # Add edge (references)
                edge_id = f"{center_id}-{target_id}"
                if edge_id not in processed_edges:
                    edge_element = {
                        'data': {
                            'id': edge_id,
                            'source': center_id,
                            'target': target_id,
                            'label': 'references',
                            'type': 'references'
                        },
                        'classes': 'relation-edge references'
                    }
                    elements.append(edge_element)
                    processed_edges.add(edge_id)
    
    return json.dumps(elements, ensure_ascii=False)


def _clean_identifier(identifier: str) -> str:
    """Clean identifier for Mermaid syntax compatibility."""
    if not identifier:
        return "Unknown"
    
    # Replace special characters with underscores
    cleaned = identifier.replace('-', '_').replace(' ', '_').replace('.', '_')
    
    # Ensure it starts with a letter or underscore
    if cleaned and not (cleaned[0].isalpha() or cleaned[0] == '_'):
        cleaned = f"T_{cleaned}"
    
    return cleaned or "Unknown"


def _extract_table_name(node_id: str) -> Optional[str]:
    """Extract table name from node ID (format: schema.table)."""
    if '.' in node_id:
        return node_id.split('.', 1)[1]
    return node_id


# Legacy mermaid generation functions - kept for backward compatibility
def generate_mermaid_er_diagram(graph_data: Dict[str, Any], focus_table: Optional[str] = None, schema_name: Optional[str] = None) -> str:
    """
    Legacy function - use generate_cytoscape_er_diagram instead.
    """
    return "Legacy mermaid function - use cytoscape version"

def generate_table_dependency_diagram(dependencies: Dict[str, Any]) -> str:
    """
    Legacy function - use generate_table_dependency_cytoscape instead.
    """
    return "Legacy mermaid function - use cytoscape version"


def create_dependency_summary_text(dependencies: Dict[str, Any]) -> List[str]:
    """
    Create a text summary of dependencies for display.
    
    Args:
        dependencies: Output from TableDependencyAnalyzer.analyze()
        
    Returns:
        List of summary strings
    """
    summary = []
    target_table = dependencies.get('target_table', {})
    table_name = target_table.get('table_name', 'Unknown')
    
    # Count dependencies
    left_count = sum(len(deps) for deps in dependencies.get('left', {}).values())
    right_count = sum(len(deps) for deps in dependencies.get('right', {}).values())
    
    summary.append(f"Table: {table_name}")
    summary.append(f"Referenced by: {left_count} objects")
    summary.append(f"References: {right_count} objects")
    
    # Detail breakdown
    for side, label in [('left', 'Referenced by'), ('right', 'References')]:
        deps_by_type = {}
        for level_deps in dependencies.get(side, {}).values():
            for dep in level_deps:
                dep_type = dep['type']
                if dep_type not in deps_by_type:
                    deps_by_type[dep_type] = 0
                deps_by_type[dep_type] += 1
        
        if deps_by_type:
            type_summary = ", ".join([f"{count} {dep_type}(s)" for dep_type, count in deps_by_type.items()])
            summary.append(f"  {label}: {type_summary}")
    
    return summary