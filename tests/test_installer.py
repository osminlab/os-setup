"""
Tests for os_setup.installer (Installer orchestrator)
======================================================
The PackageManager is fully mocked — no real installs happen.
We verify that: config is loaded correctly, each step calls the PM
with the right packages, and that the ZSH step is skipped on Windows.
"""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from os_setup.installer import Installer


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_installer(os_name: str, mode: str = "automatic") -> Installer:
    """Return an Installer with a mocked PackageManager."""
    with patch("os_setup.installer.get_package_manager") as mock_factory:
        mock_pm = MagicMock()
        mock_pm.is_installed.return_value = False
        mock_factory.return_value = mock_pm
        installer = Installer(os_name, mode)
        installer.pm = mock_pm  # keep reference for assertions
    return installer


# ── Config loading ───────────────────────────────────────────────────────────

class TestLoadConfig:
    def test_loads_ubuntu_config(self):
        installer = _make_installer("ubuntu")
        assert "essentials" in installer.config
        assert isinstance(installer.config["essentials"], list)
        assert len(installer.config["essentials"]) > 0

    def test_loads_windows_config(self):
        installer = _make_installer("windows")
        assert "essentials" in installer.config or "dev_tools" in installer.config

    def test_loads_mac_config(self):
        installer = _make_installer("mac")
        assert isinstance(installer.config, dict)

    def test_loads_fedora_config(self):
        installer = _make_installer("fedora")
        assert "essentials" in installer.config


# ── _should_run ──────────────────────────────────────────────────────────────

class TestShouldRun:
    def test_automatic_mode_always_returns_true(self):
        installer = _make_installer("ubuntu", mode="automatic")
        assert installer._should_run("anything") is True

    def test_interactive_mode_prompts(self):
        installer = _make_installer("ubuntu", mode="interactive")
        with patch("os_setup.installer.prompt_confirm", return_value=True) as mock_p:
            result = installer._should_run("essentials")
        mock_p.assert_called_once()
        assert result is True


# ── ZSH step ────────────────────────────────────────────────────────────────

class TestStepZsh:
    def test_zsh_skipped_on_windows(self):
        installer = _make_installer("windows", mode="automatic")
        # _step_zsh should return immediately without calling the PM
        installer._step_zsh()
        installer.pm.install_if_missing.assert_not_called()

    def test_zsh_runs_on_ubuntu(self):
        installer = _make_installer("ubuntu", mode="automatic")
        with patch("os_setup.installer.shutil.which", return_value="/usr/bin/zsh"), \
             patch("os_setup.installer.run_command"):
            installer._step_zsh()
        installer.pm.install_if_missing.assert_called_with("zsh")


# ── Package steps ────────────────────────────────────────────────────────────

class TestPackageSteps:
    def test_essentials_step_calls_install_for_each_package(self):
        installer = _make_installer("ubuntu", mode="automatic")
        pkgs = installer.config.get("essentials", [])
        installer._step_essentials()
        calls = [call(p) for p in pkgs]
        installer.pm.install_if_missing.assert_has_calls(calls, any_order=False)

    def test_step_skipped_when_config_section_empty(self):
        installer = _make_installer("ubuntu", mode="automatic")
        installer.config["essentials"] = []
        installer._step_essentials()
        installer.pm.install_if_missing.assert_not_called()
