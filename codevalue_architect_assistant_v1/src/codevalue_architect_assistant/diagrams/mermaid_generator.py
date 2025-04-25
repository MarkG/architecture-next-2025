# -*- coding: utf-8 -*-
"""
Generates Mermaid syntax for dependency graphs.
"""

import logging
import networkx as nx
from ..models import DependencyMap
from pathlib import Path

def _sanitize_mermaid_id(node_id: str) -> str:
    """
    Sanitizes a node ID (like a file path) for use in Mermaid.
    Replaces potentially problematic characters.
    Using Path objects directly often works, but explicit sanitization is safer.
    """
    # Replace backslashes with forward slashes (common issue)
    sanitized = str(node_id).replace("\\", "/")
    # Replace characters that might break Mermaid syntax or are hard to read
    # Example: replace periods, hyphens in node names if needed, but often okay.
    # For simplicity, we'll just ensure basic structure.
    # Mermaid IDs typically shouldn't contain spaces, quotes, etc.
    # Let's replace common problematic chars with underscores.
    sanitized = "".join(c if c.isalnum() or c in ['/', '_'] else '_' for c in sanitized)
    # Ensure it doesn't start or end with problematic chars if necessary
    return sanitized

def generate_mermaid_diagram(dep_map: DependencyMap, direction: str = "LR") -> str:
    """
    Generates a Mermaid diagram string from a DependencyMap.

    Args:
        dep_map: The DependencyMap containing the networkx graph.
        direction: The graph direction ('LR' for Left-to-Right, 'TD' for Top-Down).

    Returns:
        A string containing the Mermaid diagram syntax.
    """
    if not isinstance(dep_map, DependencyMap) or not isinstance(dep_map.graph, nx.DiGraph):
        logging.error("Invalid DependencyMap or graph provided to Mermaid generator.")
        return ""

    graph = dep_map.graph
    if not graph: # Handles empty graph case
        logging.warning("Dependency graph is empty. Generating empty Mermaid diagram.")
        return f"graph {direction};\n    %% Empty Graph"

    mermaid_lines = []
    # Ensure direction is valid
    valid_directions = ["TD", "TB", "BT", "RL", "LR"]
    if direction.upper() not in valid_directions:
        logging.warning(f"Invalid Mermaid direction '{direction}'. Defaulting to 'LR'.")
        direction = "LR"
    mermaid_lines.append(f"graph {direction.upper()};")

    # Add nodes and edges
    nodes_added = set()
    edges_added = set()

    for u, v, data in graph.edges(data=True):
        # Sanitize node IDs (file paths)
        u_id = _sanitize_mermaid_id(str(u))
        v_id = _sanitize_mermaid_id(str(v))

        # Add node definitions if not already added (optional, Mermaid creates nodes from edges)
        # Explicit definition allows styling later if needed.
        # if u_id not in nodes_added:
        #     mermaid_lines.append(f'    {u_id}["{str(u)}"];') # Display original path in label
        #     nodes_added.add(u_id)
        # if v_id not in nodes_added:
        #     mermaid_lines.append(f'    {v_id}["{str(v)}"];') # Display original path in label
        #     nodes_added.add(v_id)

        # Add edge
        edge_str = f'    {u_id} --> {v_id};'
        # Prevent duplicate edges in output if graph has parallel edges (unlikely here)
        if edge_str not in edges_added:
             mermaid_lines.append(edge_str)
             edges_added.add(edge_str)

    # Add nodes that might not have edges (isolated files)
    for node in graph.nodes():
        node_id_sanitized = _sanitize_mermaid_id(str(node))
        # Check if the node participated in any added edge
        participated = any(node_id_sanitized in edge for edge in edges_added)
        if not participated:
             # Add node explicitly if it had no edges
             mermaid_lines.append(f'    {node_id_sanitized}["{str(node)}"];')


    # Add unresolved dependencies as separate nodes (optional visualization choice)
    # for i, unresolved in enumerate(dep_map.unresolved_dependencies):
    #     source_id = _sanitize_mermaid_id(str(unresolved.source_file))
    #     target_id = _sanitize_mermaid_id(unresolved.target_module) + f"_ext_{i}" # Make unique external ID
    #     target_label = unresolved.target_module # Label for the external node
    #     mermaid_lines.append(f'    {target_id}[("{target_label}")];') # Style external nodes differently
    #     mermaid_lines.append(f'    {source_id} -.-> {target_id};') # Dashed line for external

    if not mermaid_lines[1:]: # Check if only the 'graph TD/LR;' line exists
         mermaid_lines.append("    %% No dependencies found to visualize")

    return "\n".join(mermaid_lines)