# -*- coding: utf-8 -*-
"""Tests for language detection utilities."""

import pytest
from pathlib import Path
from codevalue_architect_assistant.analysis.language import detect_language

# Use parametrize to test multiple extensions efficiently
@pytest.mark.parametrize(
    "filename, expected_language",
    [
        # Python
        ("script.py", "python"),
        ("main.pyw", "python"),
        ("module/__init__.py", "python"),
        # JavaScript
        ("app.js", "javascript"),
        ("server.mjs", "javascript"),
        ("config.cjs", "javascript"),
        # Other known extensions (if added to LANGUAGE_EXTENSIONS)
        # ("index.html", "html"),
        # ("style.css", "css"),
        # ("README.md", "markdown"),
        # ("config.yaml", "yaml"),
        # ("data.json", "json"),
        # Unknown/Unsupported extensions
        ("document.txt", None),
        ("archive.zip", None),
        ("image.jpg", None),
        ("no_extension", None),
        (".dotfile", None), # Files starting with dot without extension
        ("weird.extension", None),
        # Case insensitivity
        ("SCRIPT.PY", "python"),
        ("App.JS", "javascript"),
    ],
)
def test_detect_language_extensions(tmp_path: Path, filename: str, expected_language: str | None):
    """Test language detection for various file extensions."""
    file_path = tmp_path / filename
    # Create nested dirs if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()

    detected = detect_language(file_path)
    assert detected == expected_language

def test_detect_language_non_existent_file(tmp_path: Path):
    """Test detection on a non-existent file."""
    file_path = tmp_path / "not_real.py"
    detected = detect_language(file_path)
    assert detected is None

def test_detect_language_directory(tmp_path: Path):
    """Test detection on a directory path."""
    dir_path = tmp_path / "a_directory"
    dir_path.mkdir()
    detected = detect_language(dir_path)
    assert detected is None

def test_detect_language_none_path():
    """Test detection with None input."""
    detected = detect_language(None)
    assert detected is None