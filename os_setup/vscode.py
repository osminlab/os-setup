"""
VSCode Extension Installer
============================
Reads extension IDs from ``vscode/extensions.txt`` and installs them
via the ``code`` CLI.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from os_setup.utils import (
    get_repo_root,
    print_error,
    print_step,
    print_success,
    print_warning,
    run_command,
)


def _extensions_file() -> Path:
    return get_repo_root() / "vscode" / "extensions.txt"


def _code_is_available() -> bool:
    return shutil.which("code") is not None


def load_extensions(path: Path | None = None) -> list[str]:
    """
    Read extension IDs from *path* (default: ``vscode/extensions.txt``).
    Blank lines and ``#``-comments are ignored.
    """
    path = path or _extensions_file()
    if not path.exists():
        print_warning(f"Extensions file not found: {path}")
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def install_extensions(path: Path | None = None) -> None:
    """Install every VS Code extension listed in *path*."""
    if not _code_is_available():
        print_error(
            "'code' CLI not found. Please install Visual Studio Code first."
        )
        return

    extensions = load_extensions(path)
    if not extensions:
        print_warning("No extensions to install.")
        return

    print_step(f"Installing {len(extensions)} VS Code extension(s)…")
    for ext_id in extensions:
        result = run_command(
            ["code", "--install-extension", ext_id, "--force"],
            check=False,
            capture=True,
        )
        if result.returncode == 0:
            print_success(f"  {ext_id}")
        else:
            print_warning(f"  Failed to install {ext_id}")
