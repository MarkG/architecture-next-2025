# -*- coding: utf-8 -*-
"""Tests for Mermaid diagram generator."""

import pytest
import networkx as nx
from pathlib import Path
from codevalue_architect_assistant.models import DependencyMap, Dependency
from codevalue_architect_assistant.diagrams.mermaid_generator import generate_mermaid_diagram, _sanitize_mermaid_id

# Helper to create a basic DependencyMap for testing
def create_test_dep_map(edges=None, nodes=None, unresolved=None) -> DependencyMap:
    dep_map = DependencyMap(repository_root=Path("/fake/repo"))
    if nodes:
        dep_map.graph.add_nodes_from(nodes)
    if edges:
        for u, v in edges:
            # Add edge with minimal data for testing structure
            dep_map.graph.add_edge(u, v, type='static_import') # Assuming Dependency object handled by add_dependency
    if unresolved:
        dep_map.unresolved_dependencies = unresolved
    return dep_map

def test_generate_mermaid_empty_graph():
    """Test generating Mermaid for an empty graph."""
    dep_map = create_test_dep_map()
    output = generate_mermaid_diagram(dep_map, direction="TD")
    assert output.strip() == "graph TD;\n    %% Empty Graph"

def test_generate_mermaid_simple_graph_lr():
    """Test a simple graph with LR direction."""
    edges = [("a.py", "b.py"), ("b.py", "c.py")]
    nodes = ["a.py", "b.py", "c.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_mermaid_diagram(dep_map, direction="LR")

    assert "graph LR;" in output
    # Check for edges (allow for sanitized IDs)
    assert "a_py --> b_py;" in output
    assert "b_py --> c_py;" in output
    # Check nodes are implicitly present via edges

def test_generate_mermaid_simple_graph_td():
    """Test a simple graph with TD direction."""
    edges = [("a.py", "b.py"), ("a.py", "c.py")]
    nodes = ["a.py", "b.py", "c.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_mermaid_diagram(dep_map, direction="TD")

    assert "graph TD;" in output
    assert "a_py --> b_py;" in output
    assert "a_py --> c_py;" in output

def test_generate_mermaid_with_paths():
    """Test graph with nodes containing path separators."""
    edges = [("src/main.py", "src/utils/helper.py"), ("src/utils/helper.py", "common/config.py")]
    nodes = ["src/main.py", "src/utils/helper.py", "common/config.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_mermaid_diagram(dep_map) # Default LR

    assert "graph LR;" in output
    # Check sanitized IDs in edges
    assert "src_main_py --> src_utils_helper_py;" in output
    assert "src_utils_helper_py --> common_config_py;" in output

def test_generate_mermaid_isolated_node():
    """Test graph with a node that has no edges."""
    nodes = ["a.py", "b.py", "isolated.py"]
    edges = [("a.py", "b.py")]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_mermaid_diagram(dep_map)

    assert "graph LR;" in output
    assert "a_py --> b_py;" in output
    # Check that the isolated node is explicitly defined
    assert 'isolated_py["isolated.py"];' in output
    # Check that the connected nodes are also defined (or implicitly via edge)
    assert "a_py" in output # Check presence, definition format might vary
    assert "b_py" in output

def test_sanitize_mermaid_id():
    """Test the ID sanitization function."""
    assert _sanitize_mermaid_id("a.py") == "a_py"
    assert _sanitize_mermaid_id("src/main.py") == "src/main_py"
    assert _sanitize_mermaid_id("path\\to\\file.js") == "path/to/file_js" # Backslashes replaced
    assert _sanitize_mermaid_id("node-module.mjs") == "node_module_mjs" # Hyphen replaced
    assert _sanitize_mermaid_id("a b c.txt") == "a_b_c_txt" # Spaces replaced
    assert _sanitize_mermaid_id("weird!@#$%^&*.py") == "weird__________py" # Special chars replaced
    assert _sanitize_mermaid_id("") == "" # Empty input

def test_generate_mermaid_invalid_direction():
    """Test providing an invalid direction defaults to LR."""
    edges = [("a.py", "b.py")]
    nodes = ["a.py", "b.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_mermaid_diagram(dep_map, direction="UPDOWN") # Invalid direction
    assert "graph LR;" in output # Should default to LR
    assert "a_py --> b_py;" in output

# Optional: Test with unresolved dependencies if that visualization is added
# def test_generate_mermaid_with_unresolved(tmp_path: Path):
#     """Test visualization of unresolved dependencies."""
#     nodes = ["main.py"]
#     edges = []
#     unresolved = [
#         Dependency(source_file=Path("main.py"), target_module="requests", target_file=None, type="static_import"),
#         Dependency(source_file=Path("main.py"), target_module="./missing", target_file=None, type="require")
#     ]
#     dep_map = create_test_dep_map(edges=edges, nodes=nodes, unresolved=unresolved)
#     output = generate_mermaid_diagram(dep_map)
#
#     assert 'requests_ext_0[("requests")];' in output # Check external node definition
#     assert 'missing_ext_1[("./missing")];' in output
#     assert "main_py -.-> requests_ext_0;" in output # Check dashed line for external
#     assert "main_py -.-> missing_ext_1;" in output