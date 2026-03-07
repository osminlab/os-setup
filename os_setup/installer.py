"""
Installer — Main Orchestrator
===============================
Loads the OS-specific YAML config, then walks through every setup phase:
  1. Essentials
  2. Dev tools
  3. CLI tools
  4. GUI applications
  5. ZSH configuration
  6. VS Code extensions
  7. Dotfiles
  8. Git global config
  9. SSH key generation
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import yaml

from os_setup.package_managers import PackageManager, get_package_manager
from os_setup.utils import (
    copy_dotfile,
    get_repo_root,
    print_error,
    print_header,
    print_info,
    print_step,
    print_success,
    print_warning,
    prompt_confirm,
    prompt_input,
    resolve_config_path,
    run_command,
)
from os_setup.vscode import install_extensions


class Installer:
    """
    Orchestrates the full environment setup.

    Parameters
    ----------
    os_name : One of ``'windows'``, ``'ubuntu'``, ``'wsl'``, ``'mac'``.
    mode    : ``'automatic'`` or ``'interactive'``.
    """

    def __init__(self, os_name: str, mode: str) -> None:
        self.os_name = os_name
        self.mode = mode
        self.pm: PackageManager = get_package_manager(os_name)
        self.config: dict[str, Any] = self._load_config()

    # ── Config loading ──────────────────────────────────────────────────

    def _load_config(self) -> dict[str, Any]:
        """Load the OS-specific YAML configuration file.

        The filename is derived directly from the OS name, so any new distro
        registered in os_detector.py + package_managers.py automatically gets
        config loaded without touching this file.
        """
        return self._read_yaml(f"{self.os_name}.yaml")

    @staticmethod
    def _read_yaml(filename: str) -> dict[str, Any]:
        path = resolve_config_path(filename)
        if not path.exists():
            print_warning(f"Config file not found: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    # ── Interactive helper ──────────────────────────────────────────────

    def _should_run(self, group_label: str) -> bool:
        """In interactive mode, ask before running a group."""
        if self.mode == "automatic":
            return True
        return prompt_confirm(f"Install/configure {group_label}?")

    # ── Public entry point ──────────────────────────────────────────────

    def run(self) -> None:
        """Execute the full installation pipeline."""
        print_header(f"os-setup  ·  {self.os_name.upper()}")
        print_info(f"Mode: {self.mode}")
        print()

        self._step_update_pm()
        self._step_essentials()
        self._step_dev_tools()
        self._step_cli_tools()
        self._step_apps()
        self._step_zsh()
        self._step_vscode_extensions()
        self._step_dotfiles()
        self._step_git_config()
        self._step_ssh_keys()

        print_header("Setup complete! 🎉")
        print_success("Your development environment is ready.")

    # ── Individual steps ────────────────────────────────────────────────

    def _step_update_pm(self) -> None:
        if self._should_run("package manager update"):
            print_header("Updating Package Manager")
            self.pm.update()

    def _step_essentials(self) -> None:
        packages: list[str] = self.config.get("essentials", [])
        if not packages:
            return
        if self._should_run("essentials"):
            print_header("Essentials")
            for pkg in packages:
                self.pm.install_if_missing(pkg)

    def _step_dev_tools(self) -> None:
        tools: list[str] = self.config.get("dev_tools", [])
        if not tools:
            return
        if self._should_run("dev tools"):
            print_header("Dev Tools")
            for tool in tools:
                self.pm.install_if_missing(tool)

    def _step_cli_tools(self) -> None:
        tools: list[str] = self.config.get("cli_tools", [])
        if not tools:
            return
        if self._should_run("CLI tools"):
            print_header("CLI Tools")
            for tool in tools:
                self.pm.install_if_missing(tool)

    def _step_apps(self) -> None:
        apps: list[str] = self.config.get("apps", [])
        if not apps:
            return
        if self._should_run("applications"):
            print_header("Applications")
            for app in apps:
                if self.os_name == "mac" and hasattr(self.pm, "install_cask"):
                    self.pm.install_cask(app)
                else:
                    self.pm.install_if_missing(app)

    def _step_zsh(self) -> None:
        if self.os_name == "windows":
            return  # ZSH not applicable on native Windows (use WSL or a Linux VM)
        if self._should_run("ZSH configuration"):
            print_header("ZSH Configuration")
            # 1. Install zsh
            self.pm.install_if_missing("zsh")
            # 2. Set zsh as default shell
            zsh_path = shutil.which("zsh")
            if zsh_path:
                current_shell = os.environ.get("SHELL", "")
                if "zsh" not in current_shell:
                    print_step("Changing default shell to zsh…")
                    run_command(f"chsh -s {zsh_path}", check=False)
                else:
                    print_success("ZSH is already the default shell")
            # 3. The .zshrc is handled in the dotfiles step

    def _step_vscode_extensions(self) -> None:
        if self._should_run("VS Code extensions"):
            print_header("VS Code Extensions")
            install_extensions()

    def _step_dotfiles(self) -> None:
        if self._should_run("dotfiles"):
            print_header("Dotfiles")
            dotfiles_dir = get_repo_root() / "dotfiles"
            home = Path.home()
            interactive = self.mode == "interactive"

            if not dotfiles_dir.exists():
                print_warning("dotfiles/ directory not found — skipping")
                return

            for src in dotfiles_dir.iterdir():
                if src.is_file():
                    dest = home / src.name
                    copy_dotfile(src, dest, interactive=interactive)

    def _step_git_config(self) -> None:
        if self._should_run("Git global configuration"):
            print_header("Git Configuration")
            # Check user.name
            result = run_command(
                "git config --global user.name",
                check=False,
                capture=True,
            )
            if not result.stdout.strip():
                name = prompt_input("Enter your Git user.name")
                if name:
                    run_command(f'git config --global user.name "{name}"')
            else:
                print_success(f"Git user.name = {result.stdout.strip()}")

            # Check user.email
            result = run_command(
                "git config --global user.email",
                check=False,
                capture=True,
            )
            if not result.stdout.strip():
                email = prompt_input("Enter your Git user.email")
                if email:
                    run_command(f'git config --global user.email "{email}"')
            else:
                print_success(f"Git user.email = {result.stdout.strip()}")

    def _step_ssh_keys(self) -> None:
        if self._should_run("SSH key generation"):
            print_header("SSH Keys")
            key_path = Path.home() / ".ssh" / "id_ed25519"
            if key_path.exists():
                print_success(f"SSH key already exists: {key_path}")
            else:
                if self.mode == "automatic" or prompt_confirm(
                    "Generate a new ed25519 SSH key?"
                ):
                    print_step("Generating SSH key…")
                    key_path.parent.mkdir(parents=True, exist_ok=True)
                    run_command(
                        f'ssh-keygen -t ed25519 -f "{key_path}" -N ""',
                    )
                    print_success(f"SSH key generated: {key_path}")
