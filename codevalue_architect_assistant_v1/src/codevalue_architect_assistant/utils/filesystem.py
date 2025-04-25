# -*- coding: utf-8 -*-
"""
Filesystem scanning utilities.
"""

import os
import logging
from pathlib import Path
from typing import Iterable, List, Set

# Default directories and files to ignore during scanning
DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".env",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".vscode",
    ".idea",
}
DEFAULT_IGNORE_FILES: Set[str] = {
    ".gitignore",
    ".gitattributes",
    # Add specific file names if needed
}
# Consider adding support for .gitignore parsing later

def scan_repository(
    root_path: Path,
    ignore_dirs: Set[str] = DEFAULT_IGNORE_DIRS,
    ignore_files: Set[str] = DEFAULT_IGNORE_FILES,
    # TODO: Add support for custom ignore patterns (e.g., from .gitignore)
) -> Iterable[Path]:
    """
    Recursively scans a directory, yielding paths to files.

    Skips directories and files specified in the ignore sets.

    Args:
        root_path: The root directory path to start scanning from.
        ignore_dirs: A set of directory names to ignore.
        ignore_files: A set of file names to ignore.

    Yields:
        Path objects for each non-ignored file found.
    """
    logging.info(f"Scanning directory: {root_path}")
    if not root_path.is_dir():
        logging.error(f"Provided path is not a directory: {root_path}")
        return

    for dirpath, dirnames, filenames in os.walk(str(root_path), topdown=True):
        current_dir_path = Path(dirpath)
        logging.debug(f"Scanning in: {current_dir_path}")

        # Modify dirnames in-place to prevent os.walk from descending into ignored directories
        dirs_to_remove = []
        for i, dirname in enumerate(dirnames):
            if dirname in ignore_dirs:
                logging.debug(f"Ignoring directory: {current_dir_path / dirname}")
                dirs_to_remove.append(dirname)
        # Remove ignored directories by modifying the list os.walk iterates over
        # Must iterate backwards or use a copy to avoid index issues when removing
        for d in dirs_to_remove:
             dirnames.remove(d) # This modifies the list used by os.walk for recursion

        # Yield non-ignored files
        for filename in filenames:
            if filename not in ignore_files:
                file_path = current_dir_path / filename
                logging.debug(f"Found file: {file_path}")
                yield file_path
            else:
                logging.debug(f"Ignoring file: {current_dir_path / filename}")

    logging.info(f"Finished scanning directory: {root_path}")