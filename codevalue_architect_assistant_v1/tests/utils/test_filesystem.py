# -*- coding: utf-8 -*-
"""Tests for filesystem utilities."""

import pytest
from pathlib import Path
from codevalue_architect_assistant.utils.filesystem import scan_repository, DEFAULT_IGNORE_DIRS, DEFAULT_IGNORE_FILES

def test_scan_repository_basic(tmp_path: Path):
    """Test basic scanning of a simple directory structure."""
    # Create test structure
    (tmp_path / "file1.py").touch()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file2.js").touch()
    (tmp_path / "subdir" / "ignored_file.log").touch() # Assume .log isn't ignored by default

    # Scan
    found_files = list(scan_repository(tmp_path))
    found_relative_paths = {f.relative_to(tmp_path) for f in found_files}

    # Assert
    assert len(found_files) == 3
    assert Path("file1.py") in found_relative_paths
    assert Path("subdir/file2.js") in found_relative_paths
    assert Path("subdir/ignored_file.log") in found_relative_paths

def test_scan_repository_with_ignores(tmp_path: Path):
    """Test scanning with default ignored directories and files."""
    # Create test structure including ignored items
    (tmp_path / "file1.py").touch()
    (tmp_path / ".git").mkdir() # Ignored dir
    (tmp_path / ".git" / "config").touch()
    (tmp_path / "node_modules").mkdir() # Ignored dir
    (tmp_path / "node_modules" / "package.json").touch()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").touch()
    (tmp_path / "src" / "__pycache__").mkdir() # Ignored dir
    (tmp_path / "src" / "__pycache__" / "cache.pyc").touch()
    (tmp_path / ".gitignore").touch() # Ignored file

    # Scan using default ignores
    found_files = list(scan_repository(tmp_path))
    found_relative_paths = {f.relative_to(tmp_path) for f in found_files}

    # Assert - only non-ignored files should be found
    assert len(found_files) == 2
    assert Path("file1.py") in found_relative_paths
    assert Path("src/main.py") in found_relative_paths
    assert Path(".gitignore") not in found_relative_paths
    assert not any(p.parts[0] == ".git" for p in found_relative_paths)
    assert not any(p.parts[0] == "node_modules" for p in found_relative_paths)
    assert not any("__pycache__" in p.parts for p in found_relative_paths)

def test_scan_repository_custom_ignores(tmp_path: Path):
    """Test scanning with custom ignore sets."""
    # Create test structure
    (tmp_path / "config.yaml").touch()
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "input.csv").touch()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run.py").touch()

    custom_ignore_dirs = {"data"}
    custom_ignore_files = {"config.yaml"}

    # Scan with custom ignores
    found_files = list(scan_repository(
        tmp_path,
        ignore_dirs=custom_ignore_dirs,
        ignore_files=custom_ignore_files
    ))
    found_relative_paths = {f.relative_to(tmp_path) for f in found_files}

    # Assert
    assert len(found_files) == 1
    assert Path("scripts/run.py") in found_relative_paths
    assert Path("config.yaml") not in found_relative_paths
    assert not any(p.parts[0] == "data" for p in found_relative_paths)

def test_scan_empty_directory(tmp_path: Path):
    """Test scanning an empty directory."""
    found_files = list(scan_repository(tmp_path))
    assert len(found_files) == 0

def test_scan_non_existent_directory(tmp_path: Path):
    """Test scanning a non-existent directory."""
    non_existent_path = tmp_path / "does_not_exist"
    found_files = list(scan_repository(non_existent_path))
    assert len(found_files) == 0 # Should not raise error, just yield nothing

def test_scan_file_path(tmp_path: Path):
    """Test scanning when given a file path instead of a directory."""
    file_path = tmp_path / "a_file.txt"
    file_path.touch()
    found_files = list(scan_repository(file_path))
    assert len(found_files) == 0 # Should not raise error, just yield nothing