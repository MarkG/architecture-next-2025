# -*- coding: utf-8 -*-
"""Tests for Python and JavaScript dependency resolution."""

import pytest
from pathlib import Path
from typing import Set

# Assuming RawImport/JSRawImport are defined and Dependency in models
from codevalue_architect_assistant.analysis.python_parser import RawImport
from codevalue_architect_assistant.analysis.javascript_parser import JSRawImport # Added
from codevalue_architect_assistant.models import Dependency
from codevalue_architect_assistant.analysis.dependency_resolver import ( # Updated imports
    resolve_python_import,
    resolve_javascript_import
)

# --- Test Setup ---

# Helper to create a mock Python project structure
def setup_mock_py_project(tmp_path: Path) -> Set[Path]:
    """Creates a mock Python project structure and returns relative paths of .py files."""
    root = tmp_path / "py_project"
    root.mkdir()
    (root / "main.py").touch()
    (root / "utils.py").touch()
    (root / "package").mkdir()
    (root / "package" / "__init__.py").touch()
    (root / "package" / "mod1.py").touch()
    (root / "package" / "subpackage").mkdir()
    (root / "package" / "subpackage" / "__init__.py").touch()
    (root / "package" / "subpackage" / "mod2.py").touch()
    (root / "other").mkdir()
    (root / "other" / "script.py").touch()

    # Files relative to tmp_path/py_project
    return {
        Path("main.py"), Path("utils.py"), Path("package/__init__.py"),
        Path("package/mod1.py"), Path("package/subpackage/__init__.py"),
        Path("package/subpackage/mod2.py"), Path("other/script.py"),
    }

# Helper to create a mock JavaScript project structure
def setup_mock_js_project(tmp_path: Path) -> Set[Path]:
    """Creates a mock JS project structure and returns relative paths of JS files."""
    root = tmp_path / "js_project"
    root.mkdir()
    (root / "app.js").touch()
    (root / "utils.js").touch()
    (root / "config.json").touch() # Often required
    (root / "lib").mkdir()
    (root / "lib" / "helper.mjs").touch()
    (root / "lib" / "constants.cjs").touch()
    (root / "components").mkdir()
    (root / "components" / "button").mkdir()
    (root / "components" / "button" / "index.js").touch() # Index file
    (root / "components" / "modal.js").touch()
    (root / "data").mkdir()
    (root / "data" / "users.json").touch()

    # Files relative to tmp_path/js_project
    # Include .json files as they might be targets of resolution
    return {
        Path("app.js"), Path("utils.js"), Path("config.json"),
        Path("lib/helper.mjs"), Path("lib/constants.cjs"),
        Path("components/button/index.js"), Path("components/modal.js"),
        Path("data/users.json"),
    }


# --- Python Test Cases ---

def test_resolve_absolute_import_module(tmp_path: Path):
    """Test 'import utils' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='utils', alias=None, line_number=1, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'utils'
    assert dep.target_file == Path("utils.py") # Resolved to utils.py
    assert dep.line_number == 1

def test_resolve_absolute_import_package(tmp_path: Path):
    """Test 'import package' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='package', alias=None, line_number=2, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'package'
    assert dep.target_file == Path("package/__init__.py") # Resolved to package/__init__.py

def test_resolve_absolute_import_submodule(tmp_path: Path):
    """Test 'import package.mod1' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='package.mod1', alias=None, line_number=3, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'package.mod1'
    assert dep.target_file == Path("package/__init__.py") # Resolved to top-level package

def test_resolve_absolute_import_subpackage(tmp_path: Path):
    """Test 'import package.subpackage' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='package.subpackage', alias=None, line_number=4, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'package.subpackage'
    assert dep.target_file == Path("package/__init__.py") # Resolved to top-level package

def test_resolve_from_absolute_import_module(tmp_path: Path):
    """Test 'from package import mod1' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='mod1', alias=None, line_number=5, is_from_import=True, from_module='package')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'package.mod1'
    assert dep.target_file == Path("package/__init__.py") # Resolved to package containing mod1

def test_resolve_from_absolute_import_submodule(tmp_path: Path):
    """Test 'from package.subpackage import mod2' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='mod2', alias=None, line_number=6, is_from_import=True, from_module='package.subpackage')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'package.subpackage.mod2'
    assert dep.target_file == Path("package/subpackage/__init__.py")

def test_resolve_relative_import_sibling_module(tmp_path: Path):
    """Test 'from . import utils' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py") # In root
    raw_import = RawImport(module_name='utils', alias=None, line_number=7, is_from_import=True, from_module='.')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '.utils'
    assert dep.target_file == Path("utils.py") # Resolved to sibling utils.py

def test_resolve_relative_import_sibling_package(tmp_path: Path):
    """Test 'from . import package' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py") # In root
    raw_import = RawImport(module_name='package', alias=None, line_number=8, is_from_import=True, from_module='.')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '.package'
    assert dep.target_file == Path("package/__init__.py") # Resolved to sibling package

def test_resolve_relative_import_from_sibling_module(tmp_path: Path):
    """Test 'from .utils import helper' from main.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py") # In root
    raw_import = RawImport(module_name='helper', alias=None, line_number=9, is_from_import=True, from_module='.utils')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '.utils.helper'
    assert dep.target_file == Path("utils.py") # Resolved to the module containing 'helper'

def test_resolve_relative_import_parent_module(tmp_path: Path):
    """Test 'from .. import common' from package/mod1.py."""
    project_files = setup_mock_py_project(tmp_path)
    # Add a common file at the root for this test
    (tmp_path / "py_project" / "common.py").touch()
    project_files.add(Path("common.py"))

    project_root = tmp_path / "py_project"
    source_file = Path("package/mod1.py")
    raw_import = RawImport(module_name='common', alias=None, line_number=1, is_from_import=True, from_module='..')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '..common'
    assert dep.target_file == Path("common.py") # Resolved to common.py in parent dir

def test_resolve_relative_import_parent_package_module(tmp_path: Path):
    """Test 'from ..other import script' from package/mod1.py."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("package/mod1.py")
    raw_import = RawImport(module_name='script', alias=None, line_number=2, is_from_import=True, from_module='..other')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '..other.script'
    assert dep.target_file == Path("other/script.py") # Resolved to other/script.py

def test_resolve_unresolved_absolute(tmp_path: Path):
    """Test 'import non_existent_module'."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='non_existent_module', alias=None, line_number=10, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'non_existent_module'
    assert dep.target_file is None # Not resolved

def test_resolve_unresolved_relative(tmp_path: Path):
    """Test 'from . import non_existent_sibling'."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='non_existent_sibling', alias=None, line_number=11, is_from_import=True, from_module='.')
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '.non_existent_sibling'
    assert dep.target_file is None # Not resolved

def test_resolve_stdlib_import(tmp_path: Path):
    """Test 'import os'."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='os', alias=None, line_number=12, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'os'
    assert dep.target_file is None # Not resolved (stdlib)

def test_resolve_py_third_party_import(tmp_path: Path): # Renamed slightly
    """Test 'import requests'."""
    project_files = setup_mock_py_project(tmp_path)
    project_root = tmp_path / "py_project"
    source_file = Path("main.py")
    raw_import = RawImport(module_name='requests', alias=None, line_number=13, is_from_import=False)
    dep = resolve_python_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'requests'
    assert dep.target_file is None # Not resolved (third-party)


# --- JavaScript Test Cases ---

def test_resolve_js_relative_sibling_js(tmp_path: Path):
    """Test require('./utils') from app.js."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='./utils', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == './utils'
    assert dep.target_file == Path("utils.js") # Resolved to utils.js

def test_resolve_js_relative_sibling_mjs(tmp_path: Path):
    """Test import helper from './helper.mjs' from constants.cjs in lib/."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("lib/constants.cjs")
    raw_import = JSRawImport(module_specifier='./helper.mjs', type='import_from')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == './helper.mjs'
    assert dep.target_file == Path("lib/helper.mjs")

def test_resolve_js_relative_sibling_no_ext(tmp_path: Path):
    """Test require('./utils') without extension."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='./utils', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.target_file == Path("utils.js") # Should resolve by trying .js

def test_resolve_js_relative_to_dir_index(tmp_path: Path):
    """Test import Button from './button' from components/modal.js."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("components/modal.js")
    raw_import = JSRawImport(module_specifier='./button', type='import_from')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == './button'
    assert dep.target_file == Path("components/button/index.js")

def test_resolve_js_relative_parent(tmp_path: Path):
    """Test require('../utils') from lib/helper.mjs."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("lib/helper.mjs")
    raw_import = JSRawImport(module_specifier='../utils', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '../utils'
    assert dep.target_file == Path("utils.js") # Resolved to utils.js in parent

def test_resolve_js_absolute_from_root(tmp_path: Path):
    """Test import config from '/config.json' (treating / as project root)."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='/config.json', type='import_from')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == '/config.json'
    assert dep.target_file == Path("config.json")

def test_resolve_js_absolute_no_ext(tmp_path: Path):
    """Test require('/lib/constants')"""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='/lib/constants', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.target_file == Path("lib/constants.cjs") # Resolved by trying extensions

def test_resolve_js_bare_specifier(tmp_path: Path):
    """Test import React from 'react'."""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='react', type='import_from')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.source_file == source_file
    assert dep.target_module == 'react'
    assert dep.target_file is None # Unresolved (external/node_modules)

def test_resolve_js_unresolved_relative(tmp_path: Path):
    """Test require('./nonexistent')"""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='./nonexistent', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.target_file is None

def test_resolve_js_unresolved_absolute(tmp_path: Path):
    """Test import '/nonexistent.js'"""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("app.js")
    raw_import = JSRawImport(module_specifier='/nonexistent.js', type='import_from')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.target_file is None

def test_resolve_js_json_import(tmp_path: Path):
    """Test require('../data/users.json')"""
    project_files = setup_mock_js_project(tmp_path)
    project_root = tmp_path / "js_project"
    source_file = Path("lib/helper.mjs") # Source file is in lib/
    raw_import = JSRawImport(module_specifier='../data/users.json', type='require')
    dep = resolve_javascript_import(raw_import, source_file, project_root, project_files)
    assert dep.target_file == Path("data/users.json") # Resolved to users.json