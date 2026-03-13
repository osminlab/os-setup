"""
Tests for os_setup.package_managers
======================================
The factory and install_if_missing logic are tested without any real
shell calls by using a FakePackageManager that records method invocations.
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, call

from os_setup.package_managers import (
    AptManager,
    BrewManager,
    DnfManager,
    PacmanManager,
    WingetManager,
    get_package_manager,
    PackageManager,
)


# ── get_package_manager factory ─────────────────────────────────────────────

class TestGetPackageManager:
    def test_windows_returns_winget(self):
        assert isinstance(get_package_manager("windows"), WingetManager)

    def test_ubuntu_returns_apt(self):
        assert isinstance(get_package_manager("ubuntu"), AptManager)

    def test_debian_returns_apt(self):
        """Debian is explicitly registered and should also use AptManager."""
        assert isinstance(get_package_manager("debian"), AptManager)

    def test_mac_returns_brew(self):
        assert isinstance(get_package_manager("mac"), BrewManager)

    def test_fedora_returns_dnf(self):
        assert isinstance(get_package_manager("fedora"), DnfManager)

    def test_arch_returns_pacman(self):
        assert isinstance(get_package_manager("arch"), PacmanManager)

    def test_unknown_os_raises_value_error(self):
        with pytest.raises(ValueError, match="No package manager registered"):
            get_package_manager("haiku")

    def test_wsl_no_longer_registered(self):
        """'wsl' was removed as a target — should raise ValueError."""
        with pytest.raises(ValueError):
            get_package_manager("wsl")


# ── install_if_missing ───────────────────────────────────────────────────────

class FakePackageManager(PackageManager):
    """Concrete PackageManager that records calls without running any commands."""

    def __init__(self, already_installed: bool = False):
        self._installed = already_installed
        self.install_calls: list[str] = []

    def update(self) -> None:
        pass

    def install(self, package: str) -> None:
        self.install_calls.append(package)

    def is_installed(self, package: str) -> bool:
        return self._installed


class TestInstallIfMissing:
    def test_installs_when_not_present(self):
        pm = FakePackageManager(already_installed=False)
        pm.install_if_missing("fzf")
        assert pm.install_calls == ["fzf"]

    def test_skips_when_already_installed(self):
        pm = FakePackageManager(already_installed=True)
        pm.install_if_missing("fzf")
        assert pm.install_calls == []

    def test_handles_install_exception_gracefully(self):
        """install_if_missing should catch exceptions and not propagate them."""
        pm = FakePackageManager(already_installed=False)
        pm.install = MagicMock(side_effect=RuntimeError("command failed"))
        # Should NOT raise — errors are printed, not thrown
        pm.install_if_missing("bad-pkg")
