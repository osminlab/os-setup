"""
Package Manager Abstraction
=============================
Provides a unified ``install_package(name)`` interface backed by the
native package manager for each supported OS / Linux distribution.

Supported backends:
  - **winget**   (Windows)
  - **apt**      (Ubuntu, Debian, and Debian-family derivatives)
  - **dnf**      (Fedora, RHEL, CentOS, Rocky, AlmaLinux)
  - **pacman**   (Arch Linux, Manjaro, EndeavourOS)
  - **Homebrew** (macOS)

To add a new distro:
  1. Implement a subclass of PackageManager below.
  2. Register it in _MANAGERS at the bottom of this file.
  3. Create the corresponding config/<distro>.yaml.
"""

from __future__ import annotations

import shutil
from abc import ABC, abstractmethod

from os_setup.utils import print_error, print_step, print_success, print_warning, run_command


# ── Abstract base ───────────────────────────────────────────────────────────

class PackageManager(ABC):
    """Interface every OS-specific package manager must implement."""

    @abstractmethod
    def update(self) -> None:
        """Refresh the local package index / ensure the tool is available."""

    @abstractmethod
    def install(self, package: str) -> None:
        """Install a single package by name (or winget ID, brew formula…)."""

    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """Return True if *package* is already present."""

    def install_if_missing(self, package: str) -> None:
        """Install only when the package is not already present."""
        try:
            if self.is_installed(package):
                print_success(f"{package} is already installed")
            else:
                print_step(f"Installing {package}…")
                self.install(package)
                print_success(f"{package} installed")
        except Exception as exc:
            print_error(f"Failed to install {package}: {exc}")


# ── Winget (Windows) ────────────────────────────────────────────────────────

class WingetManager(PackageManager):
    def update(self) -> None:
        print_step("Updating winget sources…")
        run_command(["winget", "source", "update"], check=False)

    def install(self, package: str) -> None:
        run_command([
            "winget", "install", "-e", "--id", package,
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--disable-interactivity",
        ])

    def is_installed(self, package: str) -> bool:
        result = run_command(
            ["winget", "list", "-e", "--id", package, "--disable-interactivity"],
            check=False,
            capture=True,
        )
        return result.returncode == 0 and package.lower() in result.stdout.lower()


# ── APT (Ubuntu / Debian family) ────────────────────────────────────────────

class AptManager(PackageManager):
    def update(self) -> None:
        print_step("Updating apt package lists…")
        # shell=True required: uses && to chain two commands
        run_command("sudo apt update && sudo apt upgrade -y", shell=True)

    def install(self, package: str) -> None:
        run_command(["sudo", "apt", "install", "-y", package])

    def is_installed(self, package: str) -> bool:
        result = run_command(
            ["dpkg", "-s", package],
            check=False,
            capture=True,
        )
        return result.returncode == 0


# ── DNF (Fedora / RHEL family) ──────────────────────────────────────────────

class DnfManager(PackageManager):
    def update(self) -> None:
        print_step("Updating dnf package lists…")
        run_command(["sudo", "dnf", "upgrade", "-y"])

    def install(self, package: str) -> None:
        run_command(["sudo", "dnf", "install", "-y", package])

    def is_installed(self, package: str) -> bool:
        result = run_command(
            ["rpm", "-q", package],
            check=False,
            capture=True,
        )
        return result.returncode == 0


# ── Pacman (Arch Linux family) ──────────────────────────────────────────────

class PacmanManager(PackageManager):
    def update(self) -> None:
        print_step("Updating pacman package lists…")
        run_command(["sudo", "pacman", "-Syu", "--noconfirm"])

    def install(self, package: str) -> None:
        run_command(["sudo", "pacman", "-S", "--noconfirm", package])

    def is_installed(self, package: str) -> bool:
        result = run_command(
            ["pacman", "-Q", package],
            check=False,
            capture=True,
        )
        return result.returncode == 0


# ── Homebrew (macOS) ────────────────────────────────────────────────────────

class BrewManager(PackageManager):
    _BREW_INSTALL_URL = (
        "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
    )

    def update(self) -> None:
        if not shutil.which("brew"):
            print_step("Homebrew not found — installing…")
            # shell=True required: Homebrew installer uses shell eval
            run_command(
                f'NONINTERACTIVE=1 /bin/bash -c '
                f'"$(curl -fsSL {self._BREW_INSTALL_URL})"',
                shell=True,
            )
        print_step("Updating Homebrew…")
        run_command(["brew", "update"])

    def install(self, package: str) -> None:
        run_command(["brew", "install", package])

    def install_cask(self, cask: str) -> None:
        """Install a Homebrew Cask (GUI application) if not already installed."""
        try:
            result = run_command(["brew", "list", "--cask", cask], check=False, capture=True)
            if result.returncode == 0:
                print_success(f"Cask '{cask}' is already installed")
                return

            print_step(f"Installing cask {cask}…")
            run_command(["brew", "install", "--cask", cask])
            print_success(f"Cask '{cask}' installed")
        except Exception as exc:
            print_error(f"Failed to install cask {cask}: {exc}")

    def is_installed(self, package: str) -> bool:
        result = run_command(
            ["brew", "list", package],
            check=False,
            capture=True,
        )
        return result.returncode == 0


# ── Factory ─────────────────────────────────────────────────────────────────

# Maps the canonical distro/OS name returned by detect_os() to a manager.
# To support a new distro: add a new entry here and create config/<name>.yaml.
_MANAGERS: dict[str, type[PackageManager]] = {
    # Windows
    "windows": WingetManager,
    # Debian family (Ubuntu, Debian, Mint, Pop!_OS, …)
    "ubuntu":  AptManager,
    "debian":  AptManager,
    # Fedora / RHEL family
    "fedora":  DnfManager,
    # Arch family
    "arch":    PacmanManager,
    # macOS
    "mac":     BrewManager,
}


def get_package_manager(os_name: str) -> PackageManager:
    """
    Return a PackageManager instance appropriate for *os_name*.

    Raises ValueError for unknown OS names.
    """
    cls = _MANAGERS.get(os_name)
    if cls is None:
        raise ValueError(
            f"No package manager registered for OS '{os_name}'. "
            f"Supported: {', '.join(_MANAGERS)}"
        )
    return cls()
