"""
CLI Entry Point
================
Provides the ``os-setup install`` command using argparse.
"""

from __future__ import annotations

import argparse
import sys

from os_setup import __version__
from os_setup.installer import Installer
from os_setup.os_detector import detect_os
from os_setup.utils import print_error, print_header, print_info, print_success


def _select_mode() -> str:
    """Prompt the user to choose automatic or interactive mode."""
    print()
    print("Select installation mode:")
    print()
    print("  1. Automatic   — install everything without prompts")
    print("  2. Interactive  — confirm each group before installing")
    print()
    while True:
        try:
            choice = input("Enter 1 or 2: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print_error("Operation cancelled by user.")
            sys.exit(130)
        if choice == "1":
            return "automatic"
        if choice == "2":
            return "interactive"
        print("  Invalid selection. Please enter 1 or 2.")


def cmd_install(args: argparse.Namespace) -> None:
    """Handler for the ``install`` subcommand."""
    print_header("os-setup  ·  Developer Environment Setup")

    # 1. Detect OS
    try:
        os_name = detect_os()
    except RuntimeError as exc:
        print_error(str(exc))
        sys.exit(1)
    print_success(f"Detected OS: {os_name}")

    # 2. Select mode
    mode = _select_mode()
    print_info(f"Mode selected: {mode}")

    # 3. Run installation
    installer = Installer(os_name, mode)
    try:
        installer.run()
    except KeyboardInterrupt:
        print()
        print_error("Installation cancelled by user.")
        sys.exit(130)


def main() -> None:
    """Build the argument parser and dispatch subcommands."""
    parser = argparse.ArgumentParser(
        prog="os-setup",
        description="Cross-platform developer environment setup tool.",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # install subcommand
    subparsers.add_parser(
        "install",
        help="Detect the OS and install the full development environment.",
    )

    args = parser.parse_args()

    if args.command == "install":
        cmd_install(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
