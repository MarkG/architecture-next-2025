# -*- coding: utf-8 -*-
"""
Parses Python files using AST to extract information like imports.
"""

import ast
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass # Added import

# Define a structure to hold import details temporarily
@dataclass
class RawImport:
    module_name: str
    alias: Optional[str]
    line_number: int
    is_from_import: bool
    from_module: Optional[str] = None # Only used for 'from x import y'

class ImportVisitor(ast.NodeVisitor):
    """
    An AST NodeVisitor that collects import statements.
    """
    def __init__(self):
        self.imports: List[RawImport] = []

    def visit_Import(self, node: ast.Import):
        """Handles 'import x' or 'import x as y'."""
        for alias in node.names:
            raw_import = RawImport(
                module_name=alias.name,
                alias=alias.asname,
                line_number=node.lineno,
                is_from_import=False
            )
            self.imports.append(raw_import)
            logging.debug(f"Found import: {alias.name} (alias: {alias.asname}) at line {node.lineno}")
        self.generic_visit(node) # Continue traversing child nodes if any

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Handles 'from x import y' or 'from x import y as z'."""
        # node.module is the 'x' part (can be None for relative imports like 'from . import y')
        # node.level indicates relative import level (0 for absolute, 1 for 'from .', 2 for 'from ..')
        from_module_name = node.module if node.module else ""
        # Construct the full 'from' part including relative dots
        relative_prefix = "." * node.level
        full_from_module = relative_prefix + from_module_name

        for alias in node.names:
            # The 'module_name' here is the specific item being imported ('y')
            raw_import = RawImport(
                module_name=alias.name,
                alias=alias.asname,
                line_number=node.lineno,
                is_from_import=True,
                from_module=full_from_module
            )
            self.imports.append(raw_import)
            logging.debug(f"Found from-import: {alias.name} (alias: {alias.asname}) from {full_from_module} at line {node.lineno}")
        self.generic_visit(node) # Continue traversing child nodes if any

def parse_python_file(file_path: Path) -> List[RawImport]:
    """
    Parses a Python file and extracts import statements using AST.

    Args:
        file_path: Path to the Python file.

    Returns:
        A list of RawImport objects representing the found imports.
        Returns an empty list if parsing fails or the file is not found.
    """
    logging.debug(f"Attempting to parse Python file: {file_path}")
    imports_found: List[RawImport] = []
    try:
        # Read file content, trying common encodings
        content = None
        encodings_to_try = ['utf-8', 'latin-1'] # Add more if needed
        for encoding in encodings_to_try:
            try:
                content = file_path.read_text(encoding=encoding)
                logging.debug(f"Successfully read {file_path} with encoding {encoding}")
                break
            except UnicodeDecodeError:
                logging.debug(f"Failed to decode {file_path} with {encoding}")
            except Exception as e:
                logging.warning(f"Could not read file {file_path} due to error: {e}")
                return imports_found # Cannot proceed without content

        if content is None:
             logging.error(f"Could not decode file {file_path} with any tried encoding.")
             return imports_found

        # Parse the code into an AST
        tree = ast.parse(content, filename=str(file_path))

        # Visit the AST nodes to find imports
        visitor = ImportVisitor()
        visitor.visit(tree)
        imports_found = visitor.imports

    except FileNotFoundError:
        logging.error(f"Python file not found for parsing: {file_path}")
    except SyntaxError as e:
        logging.warning(f"Syntax error parsing Python file {file_path} at line {e.lineno}: {e.msg}")
        # Optionally, could try to recover or just skip the file
    except Exception as e:
        logging.error(f"Unexpected error parsing Python file {file_path}: {e}", exc_info=True)

    logging.debug(f"Found {len(imports_found)} imports in {file_path}")
    return imports_found