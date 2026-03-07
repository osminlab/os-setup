# ──────────────────────────────────────────────────
# os-setup  ·  Windows Bootstrap Installer
# ──────────────────────────────────────────────────
# Usage:
#   powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/osminlab/os-setup/main/install.ps1 | iex"
#
# This script:
#   1. Ensures Python 3 is available
#   2. Installs uv (the fast Python package manager)
#   3. Clones the os-setup repository
#   4. Installs Python dependencies via uv
#   5. Makes the `os-setup` command available globally
# ──────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

$REPO_URL = "https://github.com/osminlab/os-setup.git"
$INSTALL_DIR = "$HOME\.os-setup"

# ── Colours ─────────────────────────────────────
function Write-Info { param([string]$msg) Write-Host "▶  $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "⚠  $msg" -ForegroundColor Yellow }
function Write-Error { param([string]$msg) Write-Host "✖  $msg" -ForegroundColor Red; exit 1 }

# ── 1. Check Python ────────────────────────────
Write-Info "Checking for Python 3…"
$PYTHON = "python"
if (-Not (Get-Command $PYTHON -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3 is required but not found. Please install Python 3 first."
}
$pythonVersion = & $PYTHON --version 2>&1
Write-Info "Found: $pythonVersion"

# ── 2. Check Git ───────────────────────────────
Write-Info "Checking for Git…"
if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is required but not found. Please install Git first."
}

# ── 3. Install uv ─────────────────────────────
Write-Info "Checking for uv…"
if (-Not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Info "Installing uv (Python package manager)…"
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    
    # Temporarily add uv to the current session's PATH
    $env:PATH = "$HOME\.cargo\bin;$env:PATH"
} else {
    $uvVersion = & uv --version 2>&1
    Write-Info "uv is already installed: $uvVersion"
}

# ── 4. Clone the repository ───────────────────
if (Test-Path $INSTALL_DIR) {
    Write-Warn "Directory $INSTALL_DIR already exists — pulling latest…"
    Set-Location $INSTALL_DIR
    git pull --ff-only
} else {
    Write-Info "Cloning os-setup into $INSTALL_DIR…"
    git clone $REPO_URL $INSTALL_DIR
    Set-Location $INSTALL_DIR
}

# ── 5. Install Python dependencies via uv ─────
Write-Info "Installing Python dependencies via uv…"
uv sync

# ── 6. Create global wrapper scripts ──────────
$BIN_DIR = "$HOME\.local\bin"
if (-Not (Test-Path $BIN_DIR)) {
    New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null
}

$WRAPPER_PS1 = "$BIN_DIR\os-setup.ps1"
@"
#!/usr/bin/env pwsh
Set-Location "$INSTALL_DIR"
uv run python -m os_setup.cli `$args
"@ | Out-File -FilePath $WRAPPER_PS1 -Encoding utf8

$WRAPPER_CMD = "$BIN_DIR\os-setup.cmd"
@"
@echo off
pushd "%USERPROFILE%\.os-setup"
uv run python -m os_setup.cli %*
popd
"@ | Out-File -FilePath $WRAPPER_CMD -Encoding utf8

# ── 7. Ensure ~/.local/bin is on PATH ─────────
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$BIN_DIR*") {
    Write-Warn "Add ~/.local/bin to your PATH to use 'os-setup' globally."
    Write-Warn "  [Environment]::SetEnvironmentVariable('PATH', `"`$userPath;$BIN_DIR`", 'User')"
}

Write-Host ""
Write-Info "Installation complete! Run:"
Write-Host ""
Write-Host "    os-setup install"
Write-Host ""
