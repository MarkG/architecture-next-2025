# -*- coding: utf-8 -*-
"""
Tests for the main CLI functionality.
"""

import pytest
from click.testing import CliRunner
from codevalue_architect_assistant.cli import cli

def test_cli_entrypoint():
    """Test the main CLI entry point runs without error."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert "CodeValue Architect Assistant" in result.output

# Add more tests for specific commands later
# def test_analyze_command(...): ...