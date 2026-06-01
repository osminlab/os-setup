"""
Utility Helpers
================
Coloured console output, command runner, confirmation prompts,
dotfile copying, and config-path resolution.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


# ── Colour helpers ──────────────────────────────────────────────────────────

class Colors:
    """ANSI colour codes (disabled automatically on non-TTY)."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BLUE   = "\033[94m"
    DIM    = "\033[2m"


def _c(color: str, text: str) -> str:
    """Wrap *text* in an ANSI colour if stdout is a terminal."""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.RESET}"


def print_header(text: str) -> None:
    width = 50
    print()
    print(_c(Colors.CYAN, "=" * width))
    print(_c(Colors.CYAN + Colors.BOLD, f"  {text}"))
    print(_c(Colors.CYAN, "=" * width))
    print()


def print_step(text: str) -> None:
    print(_c(Colors.BLUE, f"▶  {text}"))


def print_success(text: str) -> None:
    print(_c(Colors.GREEN, f"✔  {text}"))


def print_warning(text: str) -> None:
    print(_c(Colors.YELLOW, f"⚠  {text}"))


def print_error(text: str) -> None:
    print(_c(Colors.RED, f"✖  {text}"))


def print_info(text: str) -> None:
    print(_c(Colors.DIM, f"   {text}"))


# ── Command runner ──────────────────────────────────────────────────────────

def run_command(
    cmd: list[str] | str,
    check: bool = True,
    capture: bool = False,
    shell: bool = False,
) -> subprocess.CompletedProcess:
    """
    Execute a command.

    Parameters
    ----------
    cmd     : The command as a list of arguments (preferred) or a shell string.
    check   : Raise on non-zero exit code.
    capture : Capture stdout/stderr instead of printing.
    shell   : Run through the system shell (only when *cmd* is a string
              that requires shell operators like ``&&`` or ``|``).
    """
    display = cmd if isinstance(cmd, str) else " ".join(cmd)
    print_info(f"$ {display}")
    return subprocess.run(
        cmd,
        shell=shell,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


# ── Prompts ─────────────────────────────────────────────────────────────────

def prompt_confirm(message: str, default: bool = True) -> bool:
    """Ask a yes/no question and return the boolean answer."""
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"{message} {suffix}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    if answer == "":
        return default
    return answer in ("y", "yes")


def prompt_input(message: str) -> str:
    """Prompt the user for free-text input."""
    try:
        return input(f"{message}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


# ── File helpers ────────────────────────────────────────────────────────────

def copy_dotfile(src: Path, dest: Path, interactive: bool = True) -> None:
    """
    Copy *src* to *dest*.  If *dest* already exists and *interactive* is True,
    ask before overwriting.
    """
    if dest.exists():
        if interactive:
            if not prompt_confirm(f"  {dest} already exists. Overwrite?", default=False):
                print_warning(f"Skipped {dest.name}")
                return
        else:
            print_warning(f"Skipped {dest.name} (already exists)")
            return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print_success(f"Copied {dest.name} → {dest}")


# ── Path helpers ────────────────────────────────────────────────────────────

def get_repo_root() -> Path:
    """Return the root directory of the os-setup repository."""
    return Path(__file__).resolve().parent.parent


def resolve_config_path(filename: str) -> Path:
    """Return the absolute path to a file in the config/ directory."""
    return get_repo_root() / "config" / filename
