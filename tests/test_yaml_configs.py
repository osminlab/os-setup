"""
Tests for config/ YAML files
==============================
Validates that every OS config file:
  - Is parseable as valid YAML
  - Contains at least one known top-level section
  - Has no duplicate package IDs within the same section or across sections
"""
from __future__ import annotations

import pytest
import yaml
from pathlib import Path

# Root of the repository (two levels up from this file)
REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"

# All config files currently tracked
CONFIG_FILES = ["windows.yaml", "ubuntu.yaml", "mac.yaml", "fedora.yaml"]

# Expected top-level sections (at least one must be present)
KNOWN_SECTIONS = {"essentials", "dev_tools", "cli_tools", "apps"}


# ── Parametrized per-file tests ──────────────────────────────────────────────

@pytest.mark.parametrize("filename", CONFIG_FILES)
class TestYamlConfigs:
    def _load(self, filename: str) -> dict:
        path = CONFIG_DIR / filename
        assert path.exists(), f"Config file not found: {path}"
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def test_is_valid_yaml(self, filename: str):
        """File must be parseable without errors."""
        data = self._load(filename)
        assert isinstance(data, dict), f"{filename}: root element must be a mapping"

    def test_has_at_least_one_known_section(self, filename: str):
        data = self._load(filename)
        found = KNOWN_SECTIONS & set(data.keys())
        assert found, (
            f"{filename}: must have at least one of {KNOWN_SECTIONS}, "
            f"got {list(data.keys())}"
        )

    def test_all_sections_are_lists(self, filename: str):
        data = self._load(filename)
        for section, items in data.items():
            if section in KNOWN_SECTIONS:
                assert isinstance(items, list), (
                    f"{filename}[{section}]: expected list, got {type(items).__name__}"
                )

    def test_no_duplicate_ids_within_file(self, filename: str):
        data = self._load(filename)
        all_ids: list[str] = []
        for section in KNOWN_SECTIONS:
            all_ids.extend(data.get(section, []))
        duplicates = {x for x in all_ids if all_ids.count(x) > 1}
        assert not duplicates, (
            f"{filename}: duplicate package IDs found: {duplicates}"
        )

    def test_no_empty_string_ids(self, filename: str):
        data = self._load(filename)
        for section in KNOWN_SECTIONS:
            for pkg in data.get(section, []):
                assert pkg and pkg.strip(), (
                    f"{filename}[{section}]: contains empty or whitespace-only ID"
                )
