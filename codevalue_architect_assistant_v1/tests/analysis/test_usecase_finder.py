# -*- coding: utf-8 -*-
"""Tests for use-case finder."""

import pytest
from pathlib import Path
from codevalue_architect_assistant.analysis.usecase_finder import find_potential_usecases, UseCaseMatch

# Helper function to run finder on content
def _find_in_content(content: str, language: str, filename: str = "test_file") -> list[UseCaseMatch]:
    # Use a dummy relative path for testing
    file_path_rel = Path(f"{filename}.{'py' if language == 'python' else 'js'}")
    matches = find_potential_usecases(content, file_path_rel, language)
    # Sort by line number for consistent testing
    return sorted(matches, key=lambda m: m.line_number)

# --- Python Tests ---

def test_find_python_function_names():
    """Test finding Python functions matching patterns."""
    content = """
def handle_request(req):
    pass

class Processor:
    def process_data(self, data):
        pass

    def _internal_helper(self):
        pass

def unrelated_function():
    pass

async def post_update(update): # Check async def
    pass
"""
    matches = _find_in_content(content, "python")
    assert len(matches) == 3
    assert matches[0].match_type == "function_name"
    assert matches[0].matched_text == "handle_request"
    assert matches[0].line_number == 2
    assert matches[1].match_type == "class_method_name" # Inside class
    assert matches[1].matched_text == "process_data"
    assert matches[1].line_number == 6
    assert matches[2].match_type == "function_name" # async def
    assert matches[2].matched_text == "post_update"
    assert matches[2].line_number == 15


def test_find_python_comment_tags():
    """Test finding Python comment tags."""
    content = """
# TODO: Refactor this later
def some_func():
    # FIXME: Handle edge case
    pass
# USECASE: User login flow
# feature: Add new reporting endpoint
"""
    matches = _find_in_content(content, "python")
    assert len(matches) == 4
    assert matches[0].match_type == "comment_tag"
    assert matches[0].matched_text == "Refactor this later"
    assert matches[0].line_number == 2
    assert matches[1].match_type == "comment_tag"
    assert matches[1].matched_text == "Handle edge case"
    assert matches[1].line_number == 4
    assert matches[2].match_type == "comment_tag"
    assert matches[2].matched_text == "User login flow"
    assert matches[2].line_number == 6
    assert matches[3].match_type == "comment_tag"
    assert matches[3].matched_text == "Add new reporting endpoint" # Case insensitive tag
    assert matches[3].line_number == 7

# --- JavaScript Tests ---

def test_find_javascript_function_names():
    """Test finding JS functions matching patterns."""
    content = """
function handleRequest(req, res) { }
async function processOrder(orderId) { }

const renderPage = () => { }; // Arrow function variable

class UserAPI {
  getUserProfile(id) { } // Normal method
  async postMessage(msg) { } // Async method
}

function unrelated() {}
"""
    matches = _find_in_content(content, "javascript")
    assert len(matches) == 4 # handleRequest, processOrder, renderPage (arrow var), postMessage (async method)
    assert matches[0].match_type == "function_name"
    assert matches[0].matched_text == "handleRequest"
    assert matches[0].line_number == 2
    assert matches[1].match_type == "function_name"
    assert matches[1].matched_text == "processOrder"
    assert matches[1].line_number == 3
    assert matches[2].match_type == "arrow_function_variable"
    assert matches[2].matched_text == "renderPage"
    assert matches[2].line_number == 5
    assert matches[3].match_type == "class_method_name" # Inside class
    assert matches[3].matched_text == "postMessage"
    assert matches[3].line_number == 9


def test_find_javascript_comment_tags():
    """Test finding JavaScript comment tags."""
    content = """
// TODO: Add validation
function submitForm() {
  // FIXME handle errors properly
}
// USECASE: Process payment transaction
// story : User registration
"""
    matches = _find_in_content(content, "javascript")
    assert len(matches) == 4
    assert matches[0].match_type == "comment_tag"
    assert matches[0].matched_text == "Add validation"
    assert matches[0].line_number == 2
    assert matches[1].match_type == "comment_tag"
    assert matches[1].matched_text == "handle errors properly"
    assert matches[1].line_number == 4
    assert matches[2].match_type == "comment_tag"
    assert matches[2].matched_text == "Process payment transaction"
    assert matches[2].line_number == 6
    assert matches[3].match_type == "comment_tag"
    assert matches[3].matched_text == "User registration" # Case insensitive tag
    assert matches[3].line_number == 7

# --- General Tests ---

def test_find_no_matches():
    """Test content with no matching patterns."""
    content_py = "x = 1\nprint('hello')"
    content_js = "const y = 2;\nconsole.log('world');"
    matches_py = _find_in_content(content_py, "python")
    matches_js = _find_in_content(content_js, "javascript")
    assert len(matches_py) == 0
    assert len(matches_js) == 0

def test_find_unsupported_language():
    """Test with an unsupported language."""
    content = "public class HelloWorld {}"
    matches = _find_in_content(content, "java")
    assert len(matches) == 0

def test_find_empty_content():
    """Test with empty file content."""
    matches_py = _find_in_content("", "python")
    matches_js = _find_in_content("", "javascript")
    assert len(matches_py) == 0
    assert len(matches_js) == 0