# -*- coding: utf-8 -*-
"""
Parses JavaScript files using Regex to extract require and import statements.

Note: Regex-based parsing is less robust than AST parsing and may miss
complex cases or produce false positives. This is an initial implementation.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# Define a structure similar to Python's RawImport
@dataclass
class JSRawImport:
    # Non-default fields first
    module_specifier: str # The string inside require() or from ''
    type: str # 'require', 'import_from', 'dynamic_import'
    # Default fields last
    imported_items: Optional[List[str]] = None # e.g., ['useState', 'useEffect'] in 'import { useState, useEffect } from "react"'
    line_number: Optional[int] = None # Regex doesn't easily provide line numbers without extra work

# Regex for CommonJS: require('module') or require("module")
# Handles single or double quotes. Captures the module specifier.
# Ignores lines starting with // or /* ... */ comments (basic attempt)
# Doesn't handle complex multi-line requires or requires inside comments perfectly.
REQUIRE_REGEX = re.compile(
    r"^\s*(?!\/\/)(?!\/\*.*\*\/)"  # Ignore lines starting with // or /*...*/
    r".*?\brequire\s*\(\s*['\"]"   # Match 'require(' with quotes
    r"([^'\"]+)"                  # Capture the module specifier (non-quote characters)
    r"['\"]\s*\)",                # Match closing quote and parenthesis
    re.MULTILINE
)

# Regex for ES6 Imports: import ... from 'module' or import ... from "module"
# Handles various import forms like:
# import defaultExport from 'module';
# import * as name from 'module';
# import { export1 } from 'module';
# import { export1 as alias1 } from 'module';
# import { export1 , export2 } from 'module';
# import defaultExport, { export1 } from 'module';
# import defaultExport, * as name from 'module';
# import 'module'; (for side effects) - This regex focuses on 'from' part
# Captures the module specifier.
# Basic comment ignoring.
IMPORT_FROM_REGEX = re.compile(
    r"^\s*(?!\/\/)(?!\/\*.*\*\/)"  # Ignore lines starting with // or /*...*/
    r"import(?:.+?from\s*)?['\"]" # Match 'import ... from ' or 'import ' with quotes
    r"([^'\"]+)"                  # Capture the module specifier
    r"['\"]\s*;?",                # Match closing quote and optional semicolon
    re.MULTILINE
)

# Regex for Dynamic Imports: import('module')
DYNAMIC_IMPORT_REGEX = re.compile(
    r"\bimport\s*\(\s*['\"]"      # Match 'import(' with quotes
    r"([^'\"]+)"                  # Capture the module specifier
    r"['\"]\s*\)",                # Match closing quote and parenthesis
)


def parse_javascript_file(file_path: Path) -> List[JSRawImport]:
    """
    Parses a JavaScript file using Regex and extracts require/import statements.

    Args:
        file_path: Path to the JavaScript file.

    Returns:
        A list of JSRawImport objects representing the found imports/requires.
        Returns an empty list if parsing fails or the file is not found.
    """
    logging.debug(f"Attempting to parse JavaScript file: {file_path}")
    imports_found: List[JSRawImport] = []
    try:
        # Read file content, trying common encodings
        content = None
        encodings_to_try = ['utf-8', 'latin-1']
        for encoding in encodings_to_try:
            try:
                content = file_path.read_text(encoding=encoding)
                logging.debug(f"Successfully read {file_path} with encoding {encoding}")
                break
            except UnicodeDecodeError:
                logging.debug(f"Failed to decode {file_path} with {encoding}")
            except Exception as e:
                logging.warning(f"Could not read file {file_path} due to error: {e}")
                return imports_found

        if content is None:
             logging.error(f"Could not decode file {file_path} with any tried encoding.")
             return imports_found

        # Find require() calls
        for match in REQUIRE_REGEX.finditer(content):
            module_specifier = match.group(1)
            imports_found.append(JSRawImport(module_specifier=module_specifier, type='require'))
            logging.debug(f"Found require: {module_specifier}")

        # Find import ... from statements
        for match in IMPORT_FROM_REGEX.finditer(content):
            module_specifier = match.group(1)
            # TODO: Could try to parse the part before 'from' to get imported_items, but complex with regex
            imports_found.append(JSRawImport(module_specifier=module_specifier, type='import_from'))
            logging.debug(f"Found import from: {module_specifier}")

        # Find dynamic import() calls
        for match in DYNAMIC_IMPORT_REGEX.finditer(content):
            module_specifier = match.group(1)
            imports_found.append(JSRawImport(module_specifier=module_specifier, type='dynamic_import'))
            logging.debug(f"Found dynamic import: {module_specifier}")

    except FileNotFoundError:
        logging.error(f"JavaScript file not found for parsing: {file_path}")
    except Exception as e:
        logging.error(f"Unexpected error parsing JavaScript file {file_path}: {e}", exc_info=True)

    # Remove duplicates that might arise if regex patterns overlap slightly
    # Note: This simple list(set()) won't work directly with dataclasses without __hash__
    # Using a more explicit deduplication based on specifier and type
    unique_imports = {}
    for imp in imports_found:
        key = (imp.module_specifier, imp.type)
        if key not in unique_imports:
            unique_imports[key] = imp
    imports_found = list(unique_imports.values())


    logging.debug(f"Found {len(imports_found)} unique imports/requires in {file_path}")
    return imports_found