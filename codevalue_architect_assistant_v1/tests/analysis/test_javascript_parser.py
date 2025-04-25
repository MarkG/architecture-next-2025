# -*- coding: utf-8 -*-
"""Tests for JavaScript Regex parsing."""

import pytest
from pathlib import Path
from codevalue_architect_assistant.analysis.javascript_parser import parse_javascript_file, JSRawImport

# Helper function to create a temp file and parse it
def _parse_js_content(tmp_path: Path, content: str, filename: str = "test_script.js") -> list[JSRawImport]:
    file_path = tmp_path / filename
    file_path.write_text(content, encoding='utf-8')
    parsed_imports = parse_javascript_file(file_path)
    # Sort for consistent comparison, as regex order isn't guaranteed
    return sorted(parsed_imports, key=lambda x: (x.type, x.module_specifier))

def test_parse_require(tmp_path: Path):
    """Test basic require('module')."""
    content = """
const fs = require('fs');
let utils = require("./utils");
var path = require("path"); // Double quotes
"""
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 3
    assert imports[0] == JSRawImport(module_specifier='./utils', type='require')
    assert imports[1] == JSRawImport(module_specifier='fs', type='require')
    assert imports[2] == JSRawImport(module_specifier='path', type='require')

def test_parse_import_from(tmp_path: Path):
    """Test basic import ... from 'module'."""
    content = """
import React from 'react';
import { useState, useEffect } from "react"; // Double quotes
import * as utils from './utils.js';
import Default, { named } from './another';
import './styles.css'; // Side effect import
"""
    imports = _parse_js_content(tmp_path, content)
    # Regex currently captures the module specifier for all 'import ... from' forms
    assert len(imports) == 5
    assert imports[0] == JSRawImport(module_specifier='./another', type='import_from')
    assert imports[1] == JSRawImport(module_specifier='./styles.css', type='import_from')
    assert imports[2] == JSRawImport(module_specifier='./utils.js', type='import_from')
    assert imports[3] == JSRawImport(module_specifier='react', type='import_from') # Found twice, deduplicated
    # Note: The regex doesn't distinguish the two 'react' imports, deduplication handles it.

def test_parse_dynamic_import(tmp_path: Path):
    """Test dynamic import('module')."""
    content = """
function loadModule() {
  import('./lazy').then(module => {
    // ...
  });
}
const data = await import("config/data.json");
"""
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 2
    assert imports[0] == JSRawImport(module_specifier='./lazy', type='dynamic_import')
    assert imports[1] == JSRawImport(module_specifier='config/data.json', type='dynamic_import')

def test_parse_mixed_imports(tmp_path: Path):
    """Test file with require, import from, and dynamic import."""
    content = """
const fs = require('fs');
import { Component } from 'react';
import util from './util';

async function load() {
  const dynamicMod = await import('./dynamic');
  console.log(dynamicMod);
}
require('../config'); // Relative require
"""
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 5
    assert JSRawImport(module_specifier='./dynamic', type='dynamic_import') in imports
    assert JSRawImport(module_specifier='./util', type='import_from') in imports
    assert JSRawImport(module_specifier='react', type='import_from') in imports
    assert JSRawImport(module_specifier='../config', type='require') in imports
    assert JSRawImport(module_specifier='fs', type='require') in imports

def test_parse_ignores_comments(tmp_path: Path):
    """Test that commented out imports/requires are ignored."""
    content = """
// const fs = require('fs');
/* import React from 'react'; */
const path = require('path'); // This one should be found
// import { x } from './ignored';
"""
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 1
    assert imports[0] == JSRawImport(module_specifier='path', type='require')

def test_parse_complex_cases_potential_failures(tmp_path: Path):
    """Highlight cases where simple regex might fail."""
    content = """
const complex = require('module' + VERSION); // Concatenated string - WILL FAIL
const tricky = require(/* comment */ 'tricky'); // Comment inside - Might fail depending on regex
import(\`./templates/${name}.html\`); // Template literal - WILL FAIL
"""
    # We expect these to NOT be found by the current simple regex
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 1 # Only 'tricky' might be found
    assert imports[0] == JSRawImport(module_specifier='tricky', type='require')
    # This test confirms the limitations of the regex approach

def test_parse_empty_file_js(tmp_path: Path):
    """Test parsing an empty JS file."""
    imports = _parse_js_content(tmp_path, "")
    assert len(imports) == 0

def test_parse_no_imports_js(tmp_path: Path):
    """Test parsing a JS file with no imports."""
    content = "console.log('Hello');\nconst x = 1;"
    imports = _parse_js_content(tmp_path, content)
    assert len(imports) == 0