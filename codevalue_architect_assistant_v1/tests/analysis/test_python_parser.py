# -*- coding: utf-8 -*-
"""Tests for Python AST parsing."""

import pytest
from pathlib import Path
from codevalue_architect_assistant.analysis.python_parser import parse_python_file, RawImport

# Helper function to create a temp file and parse it
def _parse_content(tmp_path: Path, content: str, filename: str = "test_module.py") -> list[RawImport]:
    file_path = tmp_path / filename
    file_path.write_text(content, encoding='utf-8')
    return parse_python_file(file_path)

def test_parse_simple_import(tmp_path: Path):
    """Test 'import module'."""
    content = "import os\nimport sys"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 2
    assert imports[0] == RawImport(module_name='os', alias=None, line_number=1, is_from_import=False)
    assert imports[1] == RawImport(module_name='sys', alias=None, line_number=2, is_from_import=False)

def test_parse_import_with_alias(tmp_path: Path):
    """Test 'import module as alias'."""
    content = "import pandas as pd"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='pandas', alias='pd', line_number=1, is_from_import=False)

def test_parse_multiple_imports_on_line(tmp_path: Path):
    """Test 'import mod1, mod2'."""
    content = "import json, logging" # Less common, but valid syntax
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 2
    # Note: AST nodes might represent this differently, check visitor logic if fails
    # Assuming ImportVisitor handles node.names correctly
    assert imports[0] == RawImport(module_name='json', alias=None, line_number=1, is_from_import=False)
    assert imports[1] == RawImport(module_name='logging', alias=None, line_number=1, is_from_import=False)


def test_parse_from_import(tmp_path: Path):
    """Test 'from module import name'."""
    content = "from collections import defaultdict\nfrom pathlib import Path"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 2
    assert imports[0] == RawImport(module_name='defaultdict', alias=None, line_number=1, is_from_import=True, from_module='collections')
    assert imports[1] == RawImport(module_name='Path', alias=None, line_number=2, is_from_import=True, from_module='pathlib')

def test_parse_from_import_with_alias(tmp_path: Path):
    """Test 'from module import name as alias'."""
    content = "from os import path as osp"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='path', alias='osp', line_number=1, is_from_import=True, from_module='os')

def test_parse_from_import_multiple(tmp_path: Path):
    """Test 'from module import name1, name2'."""
    content = "from typing import List, Dict, Optional"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 3
    assert imports[0] == RawImport(module_name='List', alias=None, line_number=1, is_from_import=True, from_module='typing')
    assert imports[1] == RawImport(module_name='Dict', alias=None, line_number=1, is_from_import=True, from_module='typing')
    assert imports[2] == RawImport(module_name='Optional', alias=None, line_number=1, is_from_import=True, from_module='typing')

def test_parse_from_import_star(tmp_path: Path):
    """Test 'from module import *'."""
    content = "from utils import *"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='*', alias=None, line_number=1, is_from_import=True, from_module='utils')

def test_parse_relative_import_dot(tmp_path: Path):
    """Test 'from . import sibling'."""
    content = "from . import models"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='models', alias=None, line_number=1, is_from_import=True, from_module='.')

def test_parse_relative_import_dot_module(tmp_path: Path):
    """Test 'from .module import name'."""
    content = "from .utils import helper_function"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='helper_function', alias=None, line_number=1, is_from_import=True, from_module='.utils')

def test_parse_relative_import_dots(tmp_path: Path):
    """Test 'from ..package import name'."""
    content = "from ..common import config"
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == RawImport(module_name='config', alias=None, line_number=1, is_from_import=True, from_module='..common')

def test_parse_mixed_imports(tmp_path: Path):
    """Test a file with various import types."""
    content = """
import os
import logging as log
from . import utils
from ..common import constants as c
from typing import List, Tuple
"""
    imports = _parse_content(tmp_path, content)
    assert len(imports) == 6
    # Check a few examples
    assert any(imp == RawImport(module_name='os', alias=None, line_number=2, is_from_import=False) for imp in imports)
    assert any(imp == RawImport(module_name='logging', alias='log', line_number=3, is_from_import=False) for imp in imports)
    assert any(imp == RawImport(module_name='utils', alias=None, line_number=4, is_from_import=True, from_module='.') for imp in imports)
    assert any(imp == RawImport(module_name='constants', alias='c', line_number=5, is_from_import=True, from_module='..common') for imp in imports)
    assert any(imp == RawImport(module_name='List', alias=None, line_number=6, is_from_import=True, from_module='typing') for imp in imports)
    assert any(imp == RawImport(module_name='Tuple', alias=None, line_number=6, is_from_import=True, from_module='typing') for imp in imports)


def test_parse_file_with_syntax_error(tmp_path: Path):
    """Test parsing a file containing a syntax error."""
    content = "import sys\ndef func(\n    print('hello')\nimport os" # Syntax error - unexpected import
    imports = _parse_content(tmp_path, content)
    # Should ideally log a warning but return successfully parsed imports before the error
    # Depending on AST parser behavior, it might return partial results or none.
    # Let's assume it parses up to the error.
    assert len(imports) == 1
    assert imports[0].module_name == 'sys'

def test_parse_non_existent_file(tmp_path: Path):
    """Test parsing a file that doesn't exist."""
    imports = parse_python_file(tmp_path / "non_existent.py")
    assert len(imports) == 0

def test_parse_empty_file(tmp_path: Path):
    """Test parsing an empty file."""
    imports = _parse_content(tmp_path, "")
    assert len(imports) == 0

def test_parse_file_with_encoding_issues(tmp_path: Path):
    """Test parsing a file with non-utf8 encoding (if handled)."""
    # Python's ast.parse usually handles encoding declarations or defaults,
    # but file reading might fail first. Our reader tries utf-8 then latin-1.
    try:
        content_bytes = b'# -*- coding: latin-1 -*-\nimport os\nx = "\xe9"' # é in latin-1
        file_path = tmp_path / "encoded.py"
        file_path.write_bytes(content_bytes)
        imports = parse_python_file(file_path)
        assert len(imports) == 1
        assert imports[0].module_name == 'os'
    except UnicodeEncodeError:
        pytest.skip("System locale might not support writing latin-1 easily for test setup")