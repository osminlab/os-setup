# 🛠️ os-setup

**Cross-platform developer environment setup CLI.**

Configure a new machine with **one command** — installs developer tools, GUI applications, shell configuration, dotfiles, and more.

---

## ✨ Features

| Feature | Windows | Linux | macOS |
|---|:---:|:---:|:---:|
| System packages (git, python, node…) | ✅ | ✅ | ✅ |
| GUI apps (VS Code, Docker Desktop, Chrome…) | ✅ | — | ✅ |
| CLI utilities (fzf, tree) | ✅ | ✅ | ✅ |
| ZSH + shell configuration | — | ✅ | ✅ |
| Dotfiles (.zshrc, .gitconfig, .aliases) | ✅ | ✅ | ✅ |
| VS Code extensions | ✅ | ✅ | ✅ |
| Git global config | ✅ | ✅ | ✅ |
| SSH key generation | ✅ | ✅ | ✅ |

---

## 📦 Prerequisites

- **Python 3.11** or higher.
- **Git** installed on the system.
- *(Optional for manual install)* **uv**, the extremely fast Python package manager. The automatic installation script will install it for you if you don't have it.

---

## 🚀 Quick Start

### One-Line Install (Linux / macOS / WSL)

```bash
curl -fsSL https://raw.githubusercontent.com/osminlab/os-setup/main/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/osminlab/os-setup.git
cd os-setup
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
uv sync
uv run python -m os_setup.cli install
```

---

## 📖 Usage

```bash
os-setup install
```

The CLI will:

1. **Detect your OS** automatically (Windows, Linux, or macOS). WSL is detected transparently as its underlying Linux distro.
2. **Ask for a mode**:
   - **Automatic** — installs everything without prompts.
   - **Interactive** — asks before each group.
3. Run through the full setup pipeline.

---

## 📁 Project Structure

```
os-setup/
├── os_setup/               # Python package
│   ├── cli.py              # CLI entry point (argparse)
│   ├── installer.py        # Main orchestrator
│   ├── os_detector.py      # OS detection logic
│   ├── package_managers.py # Unified package manager abstraction
│   ├── vscode.py           # VS Code extension installer
│   └── utils.py            # Helpers (output, prompts, file ops)
│
├── config/                 # YAML configuration files (per OS)
│   ├── windows.yaml        # winget package IDs
│   ├── ubuntu.yaml         # apt packages
│   ├── fedora.yaml         # dnf packages
│   └── mac.yaml            # Homebrew formulae & casks
│
├── dotfiles/               # Shell config files
│   ├── .zshrc
│   ├── .gitconfig
│   └── .aliases
│
├── vscode/
│   └── extensions.txt      # VS Code extension IDs
│
├── install.sh              # Curl bootstrap installer (installs uv)
├── pyproject.toml          # Project metadata and dependencies (uv)
└── README.md
```

> [!NOTE]
> The **`config/`** and **`dotfiles/`** directories contain **my personal workflow and preferences**.
> They reflect the tools, packages, and shell configuration that I use day to day.
> You are free to modify them to match your own setup — add, remove, or change anything you need.
> Think of them as a starting point, not a rigid template.

---

## ⚙️ Configuration System

Each OS has its own **YAML file** under `config/` with native package names/IDs.

| File | OS Family / Package Manager |
|---|---|
| `windows.yaml` | Windows (winget IDs) |
| `ubuntu.yaml` | Debian/Ubuntu family (apt packages) |
| `mac.yaml` | macOS (Homebrew formulae & casks) |
| `fedora.yaml` | RHEL/Fedora family (dnf packages) |

### YAML Categories

```yaml
# Core tools you'd want on every machine
essentials:
  - Git.Git
  - Python.PythonInstallManager

# Development-specific tools
dev_tools:
  - Docker.DockerDesktop

# Terminal enhancement utilities
cli_tools:
  - junegunn.fzf

# GUI applications
apps:
  - Microsoft.VisualStudioCode
  - Google.Chrome
```

---

## 🔧 Extending

### Add a new package

Edit the appropriate YAML file in `config/` and add the package name.

### Add a new VS Code extension

Append the extension ID to `vscode/extensions.txt`.

### Add a new dotfile

1. Place the file in `dotfiles/`.
2. It will be automatically copied to `$HOME` during setup.

### Support a new OS

1. Create `config/<os>.yaml`.
2. Add detection logic in `os_setup/os_detector.py`.
3. Register a package manager in `os_setup/package_managers.py`.

---

## 🔒 Safety

The tool is **idempotent** — safe to run multiple times:

- Checks if packages are already installed before re-installing.
- Skips existing dotfiles (prompts in interactive mode).
- Does not overwrite existing Git config or SSH keys without confirmation.

---

## 📋 Execution Flow

```
os-setup install
  │
  ├─ 1.  Detect OS
  ├─ 2.  Select mode (automatic / interactive)
  ├─ 3.  Load OS-specific YAML config
  ├─ 4.  Update package manager
  ├─ 5.  Install essentials
  ├─ 6.  Install dev tools
  ├─ 7.  Install CLI tools
  ├─ 8.  Install applications
  ├─ 9.  Configure ZSH
  ├─ 10. Install VS Code extensions
  ├─ 11. Copy dotfiles
  ├─ 12. Configure Git (user.name / email)
  ├─ 13. Generate SSH key (if missing)
  └─ 14. Done 🎉
```

---

## 📝 License

MIT
