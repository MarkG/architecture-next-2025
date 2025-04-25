# -*- coding: utf-8 -*-
"""
Finds potential use-cases in code using pattern matching (Regex).
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Pattern, Tuple
from dataclasses import dataclass

@dataclass
class UseCaseMatch:
    file_path: Path # Relative path
    line_number: int
    match_type: str # e.g., 'function_name', 'comment_tag'
    matched_text: str
    context: str # The full line where the match occurred

# --- Define Patterns ---
# These are initial, simple patterns and likely need refinement.

# Python Patterns
PYTHON_PATTERNS: Dict[str, Pattern] = {
    "function_name": re.compile(
        r"^\s*def\s+(handle_\w+|process_\w+|render_\w+|on_\w+|get_\w+|post_\w+|put_\w+|delete_\w+)\s*\("
    ),
    "class_method_name": re.compile( # Similar pattern but inside classes
         r"^\s+def\s+(handle_\w+|process_\w+|render_\w+|on_\w+|get_\w+|post_\w+|put_\w+|delete_\w+)\s*\("
    ),
    "comment_tag": re.compile(
        r"#\s*(?:TODO|FIXME|XXX|USECASE|SCENARIO|FEATURE|STORY)\b[:\s]*(.*)", re.IGNORECASE
    ),
    # Could add patterns for decorators like @app.route, @api.post etc. later
}

# JavaScript Patterns
JAVASCRIPT_PATTERNS: Dict[str, Pattern] = {
    "function_name": re.compile(
        r"^\s*(?:async\s+)?function\s+(handle[A-Z]\w*|process[A-Z]\w*|render[A-Z]\w*|on[A-Z]\w*|get[A-Z]\w*|post[A-Z]\w*|put[A-Z]\w*|delete[A-Z]\w*)\s*\("
    ),
    "arrow_function_variable": re.compile( # const handleRequest = (...) => { ... }
         r"^\s*(?:const|let|var)\s+(handle[A-Z]\w*|process[A-Z]\w*|render[A-Z]\w*|on[A-Z]\w*|get[A-Z]\w*|post[A-Z]\w*|put[A-Z]\w*|delete[A-Z]\w*)\s*=\s*\(.*\)\s*=>"
    ),
     "class_method_name": re.compile( # method() {..} or async method() {..} inside class
         r"^\s*(?:async\s+)?(handle[A-Z]\w*|process[A-Z]\w*|render[A-Z]\w*|on[A-Z]\w*|get[A-Z]\w*|post[A-Z]\w*|put[A-Z]\w*|delete[A-Z]\w*)\s*\("
     ),
    "comment_tag": re.compile(
        r"//\s*(?:TODO|FIXME|XXX|USECASE|SCENARIO|FEATURE|STORY)\b[:\s]*(.*)", re.IGNORECASE
    ),
    # Could add patterns for Express routes: app.get(...), router.post(...) etc. later
}

PATTERNS_BY_LANG: Dict[str, Dict[str, Pattern]] = {
    "python": PYTHON_PATTERNS,
    "javascript": JAVASCRIPT_PATTERNS,
}

def find_potential_usecases(
    file_content: str,
    file_path_rel: Path, # Relative path for reporting
    language: str
) -> List[UseCaseMatch]:
    """
    Scans file content using language-specific regex patterns to find potential use-cases.

    Args:
        file_content: The content of the file as a string.
        file_path_rel: The relative path of the file being scanned.
        language: The detected language ('python', 'javascript', etc.).

    Returns:
        A list of UseCaseMatch objects found in the file.
    """
    matches: List[UseCaseMatch] = []
    patterns = PATTERNS_BY_LANG.get(language)

    if not patterns:
        logging.debug(f"No use-case patterns defined for language: {language}")
        return matches

    lines = file_content.splitlines()
    for i, line in enumerate(lines):
        line_num = i + 1
        for match_type, pattern in patterns.items():
            for match in pattern.finditer(line):
                # Extract the most relevant part of the match
                # For function names, group 1 usually captures the name
                # For comments, group 1 captures the comment text
                matched_text = match.group(1) if match.groups() else match.group(0)
                use_case = UseCaseMatch(
                    file_path=file_path_rel,
                    line_number=line_num,
                    match_type=match_type,
                    matched_text=matched_text.strip(),
                    context=line.strip()
                )
                matches.append(use_case)
                logging.debug(f"Found potential use-case: {use_case}")
                # Stop checking other patterns on this line once one matches? Optional.
                # break # Uncomment to report only the first match type per line

    return matches