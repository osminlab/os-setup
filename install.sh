#!/usr/bin/env bash
# ──────────────────────────────────────────────────
# os-setup  ·  Bootstrap Installer
# ──────────────────────────────────────────────────
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/osminlab/os-setup/main/install.sh | bash
#
# This script:
#   1. Ensures Python 3 is available
#   2. Installs uv (the fast Python package manager)
#   3. Clones the os-setup repository
#   4. Installs Python dependencies via uv
#   5. Makes the `os-setup` command available globally
# ──────────────────────────────────────────────────

set -euo pipefail

REPO_URL="https://github.com/osminlab/os-setup.git"
INSTALL_DIR="$HOME/.os-setup"

# ── Colours ─────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}▶  $*${NC}"; }
warn()  { echo -e "${YELLOW}⚠  $*${NC}"; }
error() { echo -e "${RED}✖  $*${NC}"; exit 1; }

# ── 1. Check Python ────────────────────────────
info "Checking for Python 3…"
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    error "Python 3 is required but not found. Please install Python 3 first."
fi
info "Found: $($PYTHON --version)"

# ── 2. Check Git ───────────────────────────────
if ! command -v git &>/dev/null; then
    error "Git is required but not found. Please install Git first."
fi

# ── 3. Install uv ─────────────────────────────
if ! command -v uv &>/dev/null; then
    info "Installing uv (Python package manager)…"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for the current session
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
else
    info "uv is already installed: $(uv --version)"
fi

# ── 4. Clone the repository ───────────────────
if [ -d "$INSTALL_DIR" ]; then
    warn "Directory $INSTALL_DIR already exists — pulling latest…"
    git -C "$INSTALL_DIR" pull --ff-only
else
    info "Cloning os-setup into $INSTALL_DIR…"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# ── 5. Install Python dependencies via uv ─────
info "Installing Python dependencies via uv…"
(cd "$INSTALL_DIR" && uv sync)

# ── 6. Create global wrapper script ───────────
WRAPPER="$HOME/.local/bin/os-setup"
mkdir -p "$(dirname "$WRAPPER")"

cat > "$WRAPPER" << WRAPPER_EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec uv run python -m os_setup.cli "\$@"
WRAPPER_EOF
chmod +x "$WRAPPER"

# ── 7. Ensure ~/.local/bin is on PATH ─────────
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    warn "Add ~/.local/bin to your PATH to use 'os-setup' globally."
    warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
info "Installation complete! Run:"
echo ""
echo "    os-setup install"
echo ""
