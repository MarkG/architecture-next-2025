# -*- coding: utf-8 -*-
"""Tests for PlantUML diagram generator."""

import pytest
import networkx as nx
from pathlib import Path
from codevalue_architect_assistant.models import DependencyMap, Dependency
from codevalue_architect_assistant.diagrams.plantuml_generator import generate_plantuml_diagram, _sanitize_plantuml_alias

# Helper to create a basic DependencyMap for testing
def create_test_dep_map(edges=None, nodes=None, unresolved=None) -> DependencyMap:
    dep_map = DependencyMap(repository_root=Path("/fake/repo"))
    if nodes:
        dep_map.graph.add_nodes_from(nodes)
    if edges:
        for u, v in edges:
            dep_map.graph.add_edge(u, v, type='static_import')
    if unresolved:
        dep_map.unresolved_dependencies = unresolved
    return dep_map

def test_generate_plantuml_empty_graph():
    """Test generating PlantUML for an empty graph."""
    dep_map = create_test_dep_map()
    output = generate_plantuml_diagram(dep_map)
    expected = "@startuml\n' Empty Graph\n@enduml"
    assert output.strip() == expected

def test_generate_plantuml_simple_graph():
    """Test a simple graph."""
    edges = [("a.py", "b.py"), ("b.py", "c.py")]
    nodes = ["a.py", "b.py", "c.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_plantuml_diagram(dep_map)

    assert "@startuml" in output
    assert "@enduml" in output
    assert 'component "a.py" as a_py' in output
    assert 'component "b.py" as b_py' in output
    assert 'component "c.py" as c_py' in output
    assert "a_py --> b_py" in output
    assert "b_py --> c_py" in output

def test_generate_plantuml_with_paths():
    """Test graph with nodes containing path separators."""
    edges = [("src/main.py", "src/utils/helper.py"), ("src/utils/helper.py", "common/config.py")]
    nodes = ["src/main.py", "src/utils/helper.py", "common/config.py"]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_plantuml_diagram(dep_map)

    # Check component definitions with sanitized aliases
    assert 'component "src/main.py" as src_main_py' in output
    assert 'component "src/utils/helper.py" as src_utils_helper_py' in output
    assert 'component "common/config.py" as common_config_py' in output
    # Check relationships using aliases
    assert "src_main_py --> src_utils_helper_py" in output
    assert "src_utils_helper_py --> common_config_py" in output

def test_generate_plantuml_isolated_node():
    """Test graph with a node that has no edges."""
    nodes = ["a.py", "b.py", "isolated.py"]
    edges = [("a.py", "b.py")]
    dep_map = create_test_dep_map(edges=edges, nodes=nodes)
    output = generate_plantuml_diagram(dep_map)

    assert 'component "a.py" as a_py' in output
    assert 'component "b.py" as b_py' in output
    assert 'component "isolated.py" as isolated_py' in output
    assert "a_py --> b_py" in output
    # Ensure isolated_py is defined but has no arrows pointing to/from it in this simple case

def test_sanitize_plantuml_alias():
    """Test the alias sanitization function."""
    assert _sanitize_plantuml_alias("a.py") == "a_py"
    assert _sanitize_plantuml_alias("src/main.py") == "src_main_py"
    assert _sanitize_plantuml_alias("path\\to\\file.js") == "path_to_file_js"
    assert _sanitize_plantuml_alias("node-module.mjs") == "node_module_mjs"
    assert _sanitize_plantuml_alias("a b c.txt") == "a_b_c_txt"
    assert _sanitize_plantuml_alias("weird!@#$%^&*.py") == "weird__________py"
    assert _sanitize_plantuml_alias("123file.py") == "_123file_py" # Prepends underscore if starts with digit
    assert _sanitize_plantuml_alias("") == "node_" + str(hash("")) # Fallback for empty

# Optional: Test with unresolved dependencies if that visualization is added
# def test_generate_plantuml_with_unresolved(tmp_path: Path):
#     """Test visualization of unresolved dependencies."""
#     nodes = ["main.py"]
#     edges = []
#     unresolved = [
#         Dependency(source_file=Path("main.py"), target_module="requests", target_file=None, type="static_import"),
#         Dependency(source_file=Path("main.py"), target_module="./missing", target_file=None, type="require")
#     ]
#     dep_map = create_test_dep_map(edges=edges, nodes=nodes, unresolved=unresolved)
#     output = generate_plantuml_diagram(dep_map)
#
#     assert 'component "main.py" as main_py' in output
#     assert 'component "requests" as requests_ext <<external>>' in output
#     assert 'component "./missing" as _missing_ext <<external>>' in output # Alias sanitized
#     assert "main_py ..> requests_ext" in output # Dashed line
#     assert "main_py ..> _missing_ext" in output