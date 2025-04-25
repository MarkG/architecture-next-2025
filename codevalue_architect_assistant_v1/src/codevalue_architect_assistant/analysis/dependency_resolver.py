# -*- coding: utf-8 -*-
"""
Resolves raw import statements to specific files within the project
or marks them as external/unresolved.
"""

import logging
from pathlib import Path
from typing import List, Set, Optional, ForwardRef

from ..models import Dependency, ProjectFile, AnalysisResult # Added AnalysisResult
from .python_parser import RawImport, parse_python_file # Added parse_python_file
from .javascript_parser import JSRawImport, parse_javascript_file # Added JS parser imports

# --- Python Import Resolution ---

def resolve_python_import(
    raw_import: RawImport,
    source_file_rel_path: Path, # Relative path of the file containing the import
    project_root: Path,
    project_py_files_rel: Set[Path] # Set of all known .py file relative paths
) -> Dependency:
    """
    Attempts to resolve a single Python RawImport to a specific file within the project.
    (Implementation details omitted for brevity - assume it's the same as before)
    """
    target_file: Optional[Path] = None
    target_module_str: str = ""

    if raw_import.is_from_import:
        base_module = raw_import.from_module
        imported_item = raw_import.module_name
        target_module_str = (base_module or "") + "." + imported_item # Simplified representation

        if base_module and base_module.startswith('.'):
            # Relative Import Logic (Simplified for brevity)
            level = base_module.count('.')
            module_part = base_module.lstrip('.')
            current_dir = source_file_rel_path.parent
            for _ in range(level - 1):
                current_dir = current_dir.parent

            potential_target_dir = current_dir # Directory calculated based on level
            potential_target_name = module_part # Name part after dots (e.g., 'utils', or '' for 'from . import X')

            target_file = None # Reset target_file before checking

            if potential_target_name:
                # Case 1: from .module import X OR from .package import X
                # Check for module: current_dir / module.py
                potential_module_file_abs = (potential_target_dir / potential_target_name).with_suffix(".py")
                potential_module_file_rel = potential_module_file_abs.relative_to(project_root) if potential_module_file_abs.is_relative_to(project_root) else None
                if potential_module_file_rel and potential_module_file_rel in project_py_files_rel:
                    target_file = potential_module_file_rel

                # Check for package: current_dir / module / __init__.py
                potential_pkg_init_abs = potential_target_dir / potential_target_name / "__init__.py"
                potential_pkg_init_rel = potential_pkg_init_abs.relative_to(project_root) if potential_pkg_init_abs.is_relative_to(project_root) else None
                if not target_file and potential_pkg_init_rel and potential_pkg_init_rel in project_py_files_rel:
                     target_file = potential_pkg_init_rel
            else:
                # Case 2: from . import name OR from .. import name
                # Here, 'name' is in raw_import.module_name, not base_module/module_part
                imported_item_name = raw_import.module_name

                # Check for module: current_dir / name.py
                potential_module_file_abs = (potential_target_dir / imported_item_name).with_suffix(".py")
                potential_module_file_rel = potential_module_file_abs.relative_to(project_root) if potential_module_file_abs.is_relative_to(project_root) else None
                if potential_module_file_rel and potential_module_file_rel in project_py_files_rel:
                    target_file = potential_module_file_rel

                # Check for package: current_dir / name / __init__.py
                potential_pkg_init_abs = potential_target_dir / imported_item_name / "__init__.py"
                potential_pkg_init_rel = potential_pkg_init_abs.relative_to(project_root) if potential_pkg_init_abs.is_relative_to(project_root) else None
                if not target_file and potential_pkg_init_rel and potential_pkg_init_rel in project_py_files_rel:
                     target_file = potential_pkg_init_rel

        elif base_module:
            # Absolute Import Logic (Simplified for brevity)
            module_path_parts = base_module.split('.')
            potential_pkg_init = Path(*module_path_parts) / "__init__.py"
            potential_module_file = Path(*module_path_parts[:-1]) / (module_path_parts[-1] + ".py") if len(module_path_parts) > 0 else Path(module_path_parts[0]).with_suffix(".py")

            if potential_pkg_init in project_py_files_rel:
                 target_file = potential_pkg_init
            elif potential_module_file in project_py_files_rel:
                 target_file = potential_module_file
        # else: from . import x case handled by relative logic

    else: # Direct import: import x.y.z
        target_module_str = raw_import.module_name
        module_path_parts = target_module_str.split('.')
        potential_pkg_init = Path(*module_path_parts) / "__init__.py"
        potential_module_file = Path(*module_path_parts[:-1]) / (module_path_parts[-1] + ".py") if len(module_path_parts) > 1 else Path(module_path_parts[0]).with_suffix(".py")
        potential_top_pkg_init = Path(module_path_parts[0]) / "__init__.py" # Check top level package too

        if potential_pkg_init in project_py_files_rel:
            target_file = potential_pkg_init
        elif potential_module_file in project_py_files_rel:
             target_file = potential_module_file
        elif potential_top_pkg_init in project_py_files_rel:
             target_file = potential_top_pkg_init # Link to top package if sub-module/pkg not found directly

    dependency = Dependency(
        source_file=source_file_rel_path,
        target_module=target_module_str,
        target_file=target_file,
        line_number=raw_import.line_number,
        type="static_import" # Python imports are generally static
    )
    return dependency

# --- JavaScript Import Resolution ---

def _try_resolve_js_path(
    base_path: Path,
    project_root: Path,
    project_js_files_rel: Set[Path]
) -> Optional[Path]:
    """Helper to check variations of a JS path against known project files."""
    # 1. Try exact path + extensions
    for ext in ['.js', '.mjs', '.cjs', '.json']: # Add .json as it's often required
        potential_file = base_path.with_suffix(ext)
        if potential_file.is_relative_to(project_root):
             rel_path = potential_file.relative_to(project_root)
             if rel_path in project_js_files_rel:
                 return rel_path

    # 2. Try as directory + index + extensions
    for ext in ['index.js', 'index.mjs', 'index.cjs']:
        potential_file = base_path / ext
        if potential_file.is_relative_to(project_root):
            rel_path = potential_file.relative_to(project_root)
            if rel_path in project_js_files_rel:
                return rel_path

    return None


def resolve_javascript_import(
    raw_import: JSRawImport,
    source_file_rel_path: Path, # Relative path of the file containing the import
    project_root: Path,
    project_js_files_rel: Set[Path] # Set of all known .js/.mjs/.cjs file relative paths
) -> Dependency:
    """
    Attempts to resolve a single JSRawImport to a specific file within the project.
    Handles relative paths and basic absolute paths from root. Bare specifiers are unresolved.
    """
    specifier = raw_import.module_specifier
    target_file: Optional[Path] = None

    if specifier.startswith('.'):
        # --- Relative Import ---
        # Resolve relative to the source file's directory
        base_dir = (project_root / source_file_rel_path).parent
        try:
            # Use os.path.normpath or similar logic if Path.resolve causes issues with '..'
            # Path.resolve() might go outside project root, handle carefully
            potential_target_abs = (base_dir / specifier).resolve()

            # Check variations (.js, /index.js, etc.) relative to project root
            target_file = _try_resolve_js_path(potential_target_abs, project_root, project_js_files_rel)

            if target_file:
                logging.debug(f"Resolved relative JS import '{specifier}' to {target_file}")
            else:
                logging.debug(f"Could not resolve relative JS import '{specifier}' from {source_file_rel_path}")

        except Exception as e: # Broad exception for path resolution issues
             logging.warning(f"Error resolving relative JS path '{specifier}' from {source_file_rel_path}: {e}")


    elif specifier.startswith('/'):
         # --- Absolute path from root? (Less common for imports, maybe config paths) ---
         # Treat '/' as relative to project_root
         potential_target_abs = (project_root / specifier.lstrip('/')).resolve()
         target_file = _try_resolve_js_path(potential_target_abs, project_root, project_js_files_rel)
         if target_file:
             logging.debug(f"Resolved absolute JS import '{specifier}' to {target_file}")
         else:
             logging.debug(f"Could not resolve absolute JS import '{specifier}' from {source_file_rel_path}")

    # Add check for windows absolute paths C:\... if necessary, treat as unresolved

    else:
        # --- Bare specifier (e.g., 'react', 'lodash', 'my-module') ---
        # Assume external or node_modules (unresolved for now)
        # TODO: Could add logic to check node_modules later
        logging.debug(f"Treating bare JS specifier '{specifier}' as external/unresolved.")


    dependency = Dependency(
        source_file=source_file_rel_path,
        target_module=specifier, # The original specifier string
        target_file=target_file, # Resolved relative path or None
        line_number=raw_import.line_number, # May be None from regex parser
        type=raw_import.type # 'require', 'import_from', 'dynamic_import'
    )
    return dependency


# --- Combined Dependency Resolution ---

def resolve_all_dependencies(
    analysis_result: AnalysisResult,
    project_root: Path
) -> List[Dependency]:
    """
    Parses all supported files found in the analysis result and resolves their dependencies.

    Args:
        analysis_result: The result object from the initial scan.
        project_root: Absolute path to the project root.

    Returns:
        A list of all resolved Dependency objects from all languages.
    """
    all_dependencies: List[Dependency] = []

    # Prepare sets of known files for efficient lookup
    project_py_files_rel: Set[Path] = {
        pf.relative_path for pf in analysis_result.files if pf.language == 'python'
    }
    project_js_files_rel: Set[Path] = {
        pf.relative_path for pf in analysis_result.files if pf.language == 'javascript'
    }
    # Add other language file sets here if needed

    logging.info("Starting dependency resolution for all supported languages...")

    for project_file in analysis_result.files:
        if project_file.language == 'python':
            logging.debug(f"Processing Python file for imports: {project_file.relative_path}")
            raw_imports = parse_python_file(project_file.path)
            for raw_import in raw_imports:
                resolved_dep = resolve_python_import(
                    raw_import,
                    project_file.relative_path,
                    project_root,
                    project_py_files_rel
                )
                all_dependencies.append(resolved_dep)

        elif project_file.language == 'javascript':
            logging.debug(f"Processing JavaScript file for imports/requires: {project_file.relative_path}")
            raw_imports = parse_javascript_file(project_file.path)
            for raw_import in raw_imports:
                resolved_dep = resolve_javascript_import(
                    raw_import,
                    project_file.relative_path,
                    project_root,
                    project_js_files_rel # Pass the set of JS files
                )
                all_dependencies.append(resolved_dep)

        # Add elif blocks for other supported languages here

    logging.info(f"Finished dependency resolution. Found {len(all_dependencies)} total potential dependencies.")
    return all_dependencies


# Need dataclasses import
from dataclasses import dataclass