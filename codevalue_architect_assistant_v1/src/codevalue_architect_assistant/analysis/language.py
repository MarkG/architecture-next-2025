# -*- coding: utf-8 -*-
"""
Language detection utilities.
"""

import logging
from pathlib import Path
from typing import Optional, Dict

# Mapping from lowercase file extensions to language names
# Add more mappings as needed
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    # Python
    ".py": "python",
    ".pyw": "python",
    # JavaScript
    ".js": "javascript",
    ".mjs": "javascript", # ES Modules
    ".cjs": "javascript", # CommonJS
    # Add other common languages if desired for basic detection
    # ".java": "java",
    ".cs": "csharp",
    # ".go": "go",
    # ".rb": "ruby",
    # ".php": "php",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    # ".yaml": "yaml",
    # ".yml": "yaml",
    # ".md": "markdown",
    # ".sh": "shell",
    # ".bash": "shell",
    # ".zsh": "shell",
}

def detect_language(file_path: Path) -> Optional[str]:
    """
    Detects the programming language of a file based on its extension.

    Args:
        file_path: The Path object representing the file.

    Returns:
        The detected language name (e.g., 'python', 'javascript') or None
        if the language cannot be determined from the extension.
    """
    if not file_path or not file_path.is_file():
        logging.warning(f"Cannot detect language for non-file path: {file_path}")
        return None

    extension = file_path.suffix.lower()
    language = LANGUAGE_EXTENSIONS.get(extension)

    if language:
        logging.debug(f"Detected language '{language}' for file: {file_path}")
    else:
        logging.debug(f"Could not detect language for file extension '{extension}' in file: {file_path}")

    return language