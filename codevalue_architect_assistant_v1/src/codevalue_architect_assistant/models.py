# -*- coding: utf-8 -*-
"""
Core data structures (models) for representing project information.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
import networkx as nx

@dataclass
class ProjectFile:
    """Represents a single file within the analyzed project."""
    path: Path
    relative_path: Path # Path relative to the repository root
    language: Optional[str] = None
    size_bytes: Optional[int] = None
    # Add more attributes as needed, e.g., last modified, hash

@dataclass
class Dependency:
    """Represents a dependency link between two entities."""
    source_file: Path # Relative path of the file containing the dependency
    target_module: str # The imported/required module string
    target_file: Optional[Path] = None # Resolved relative path of the target file, if found within the project
    line_number: Optional[int] = None
    type: str = "static_import" # e.g., static_import, dynamic_import, require

@dataclass
class AnalysisResult:
    """Holds the results of the initial repository analysis."""
    repository_root: Path
    files: List[ProjectFile] = field(default_factory=list)
    languages_detected: Dict[str, int] = field(default_factory=dict) # Language name -> count
    # Add more fields like detected frameworks, total lines of code, etc.

@dataclass
class DependencyMap:
    """Holds the dependency graph and related information."""
    repository_root: Path
    graph: nx.DiGraph = field(default_factory=nx.DiGraph) # Nodes are relative file paths (str), edges have Dependency attributes
    unresolved_dependencies: List[Dependency] = field(default_factory=list)

    def add_dependency(self, dep: Dependency):
        """Adds a dependency to the graph."""
        source_str = str(dep.source_file)
        target_str = str(dep.target_file) if dep.target_file else dep.target_module

        # Ensure nodes exist
        if not self.graph.has_node(source_str):
            self.graph.add_node(source_str) # Add attributes later if needed

        # Add target node only if it's resolved within the project
        if dep.target_file and not self.graph.has_node(target_str):
             self.graph.add_node(target_str)

        # Add edge if target is resolved, otherwise track as unresolved
        if dep.target_file:
            # Store dependency details on the edge
            self.graph.add_edge(source_str, target_str, type=dep.type, line=dep.line_number)
        else:
            self.unresolved_dependencies.append(dep)