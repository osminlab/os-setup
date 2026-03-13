"""
OS Detection Module
====================
Detects the current operating system and Linux distribution:
  - windows
  - mac
  - Linux distros: ubuntu, debian, fedora, arch, …

On Linux the distro is resolved from /etc/os-release (standard on all
modern distributions, including WSL). The ID field is used first; if the
distro is not directly registered we fall back to the first token of
ID_LIKE so that derivatives work transparently (e.g. Pop!_OS → ubuntu,
Linux Mint → ubuntu, Rocky Linux → rhel → fedora).
"""

import platform
from pathlib import Path


# ── /etc/os-release parser ─────────────────────────────────────────────────

def _parse_os_release(path: str = "/etc/os-release") -> dict[str, str]:
    """
    Parse a key=value file (e.g. /etc/os-release) into a plain dict.
    Quoted values are unquoted automatically.
    Returns an empty dict if the file does not exist.
    """
    result: dict[str, str] = {}
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return result


# ── Registered package-manager families ────────────────────────────────────

# Maps a distro ID (as it appears in /etc/os-release ID or ID_LIKE) to the
# canonical name used by get_package_manager() in package_managers.py.
_DISTRO_FAMILY: dict[str, str] = {
    "ubuntu":   "ubuntu",
    "debian":   "debian",
    "linuxmint":"ubuntu",   # ID_LIKE=ubuntu
    "pop":      "ubuntu",   # Pop!_OS → ID_LIKE=ubuntu
    "elementary":"ubuntu",
    "kali":     "debian",
    "raspbian": "debian",
    "fedora":   "fedora",
    "rhel":     "fedora",   # Red Hat family
    "centos":   "fedora",
    "rocky":    "fedora",
    "almalinux":"fedora",
    "arch":     "arch",
    "manjaro":  "arch",
    "endeavouros": "arch",
}


def _detect_linux_distro() -> str:
    """
    Resolve the Linux distro by reading /etc/os-release.
    Falls back through ID → each token of ID_LIKE → raises RuntimeError.
    """
    info = _parse_os_release()

    # 1. Try exact ID first
    distro_id = info.get("ID", "").lower()
    if distro_id in _DISTRO_FAMILY:
        return _DISTRO_FAMILY[distro_id]

    # 2. Walk through ID_LIKE tokens (space-separated, ordered by closeness)
    for like in info.get("ID_LIKE", "").lower().split():
        if like in _DISTRO_FAMILY:
            return _DISTRO_FAMILY[like]

    # 3. Return the raw ID so the user gets a meaningful error from the factory
    if distro_id:
        return distro_id

    raise RuntimeError(
        "Could not determine Linux distribution from /etc/os-release. "
        "Please open an issue and include the contents of that file."
    )


# ── Public API ──────────────────────────────────────────────────────────────

def detect_os() -> str:
    """
    Detect the current operating system / Linux distribution.

    Returns one of: 'windows', 'mac', 'ubuntu', 'debian', 'fedora', 'arch', …
    Raises RuntimeError if the OS/distro cannot be identified.

    Note: WSL is handled transparently — it exposes a normal /etc/os-release
    for its guest distribution, so no special-casing is needed.
    """
    system = platform.system().lower()

    if system == "darwin":
        return "mac"

    if system == "windows":
        return "windows"

    if system == "linux":
        return _detect_linux_distro()

    raise RuntimeError(
        f"Unsupported operating system: {platform.system()} "
        f"({platform.platform()})"
    )


if __name__ == "__main__":
    print(f"Detected OS: {detect_os()}")
