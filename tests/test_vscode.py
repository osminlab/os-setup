"""
Tests for os_setup.vscode (VS Code extension installer)
=========================================================
All file I/O uses temporary files — no real VS Code or extension
installations are performed.
"""
from __future__ import annotations

import pytest
from pathlib import Path

from os_setup.vscode import load_extensions


class TestLoadExtensions:
    def test_reads_valid_extension_ids(self, tmp_path):
        f = tmp_path / "extensions.txt"
        f.write_text("ms-python.python\ndbaeumer.vscode-eslint\n")
        result = load_extensions(f)
        assert result == ["ms-python.python", "dbaeumer.vscode-eslint"]

    def test_ignores_blank_lines(self, tmp_path):
        f = tmp_path / "extensions.txt"
        f.write_text("ms-python.python\n\n\ndbaeumer.vscode-eslint\n")
        result = load_extensions(f)
        assert len(result) == 2

    def test_ignores_comment_lines(self, tmp_path):
        f = tmp_path / "extensions.txt"
        f.write_text(
            "# Python\n"
            "ms-python.python\n"
            "# Linting\n"
            "dbaeumer.vscode-eslint\n"
        )
        result = load_extensions(f)
        assert result == ["ms-python.python", "dbaeumer.vscode-eslint"]

    def test_returns_empty_list_for_missing_file(self, tmp_path):
        result = load_extensions(tmp_path / "nonexistent.txt")
        assert result == []

    def test_strips_trailing_whitespace(self, tmp_path):
        f = tmp_path / "extensions.txt"
        f.write_text("  ms-python.python  \n  \n")
        result = load_extensions(f)
        assert result == ["ms-python.python"]
