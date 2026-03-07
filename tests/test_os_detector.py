"""
Tests for os_setup.os_detector
================================
All tests run without touching the real filesystem or environment —
platform.system() and the /etc/os-release file are monkey-patched.
"""
from __future__ import annotations

import pytest
from unittest.mock import mock_open, patch

from os_setup.os_detector import _parse_os_release, _detect_linux_distro, detect_os


# ── _parse_os_release ───────────────────────────────────────────────────────

class TestParseOsRelease:
    def test_parses_simple_key_value(self, tmp_path):
        f = tmp_path / "os-release"
        f.write_text('ID=ubuntu\nNAME="Ubuntu"\nVERSION_ID="22.04"\n')
        result = _parse_os_release(str(f))
        assert result["ID"] == "ubuntu"
        assert result["NAME"] == "Ubuntu"
        assert result["VERSION_ID"] == "22.04"

    def test_ignores_comments_and_blank_lines(self, tmp_path):
        f = tmp_path / "os-release"
        f.write_text("# comment\n\nID=debian\n")
        result = _parse_os_release(str(f))
        assert result == {"ID": "debian"}

    def test_returns_empty_dict_for_missing_file(self):
        result = _parse_os_release("/nonexistent/os-release")
        assert result == {}

    def test_unquotes_single_and_double_quotes(self, tmp_path):
        f = tmp_path / "os-release"
        f.write_text("ID='arch'\nNAME=\"Arch Linux\"\n")
        result = _parse_os_release(str(f))
        assert result["ID"] == "arch"
        assert result["NAME"] == "Arch Linux"


# ── detect_os ───────────────────────────────────────────────────────────────

class TestDetectOs:
    def _patch(self, system: str, os_release_content: str = ""):
        """Helper: patch platform.system and the os-release file."""
        return (
            patch("os_setup.os_detector.platform.system", return_value=system),
            patch(
                "os_setup.os_detector._parse_os_release",
                return_value=self._parse(os_release_content),
            ),
        )

    @staticmethod
    def _parse(content: str) -> dict[str, str]:
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip().strip('"').strip("'")
        return result

    def test_detect_mac(self):
        with patch("os_setup.os_detector.platform.system", return_value="Darwin"):
            assert detect_os() == "mac"

    def test_detect_windows(self):
        with patch("os_setup.os_detector.platform.system", return_value="Windows"):
            assert detect_os() == "windows"

    def test_detect_ubuntu_via_id(self):
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "ubuntu", "ID_LIKE": "debian"}):
            assert detect_os() == "ubuntu"

    def test_detect_debian(self):
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "debian"}):
            assert detect_os() == "debian"

    def test_detect_fedora(self):
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "fedora"}):
            assert detect_os() == "fedora"

    def test_detect_arch(self):
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "arch"}):
            assert detect_os() == "arch"

    def test_detect_pop_os_via_id_like_fallback(self):
        """Pop!_OS has ID=pop, ID_LIKE=ubuntu — should resolve to ubuntu."""
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "pop", "ID_LIKE": "ubuntu"}):
            assert detect_os() == "ubuntu"

    def test_detect_rocky_via_id_like_rhel(self):
        """Rocky Linux has ID=rocky, ID_LIKE=rhel → fedora."""
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "rocky", "ID_LIKE": "rhel fedora"}):
            assert detect_os() == "fedora"

    def test_wsl_ubuntu_transparent(self):
        """WSL running Ubuntu should detect as 'ubuntu' with no special casing."""
        with patch("os_setup.os_detector.platform.system", return_value="Linux"), \
             patch("os_setup.os_detector._parse_os_release",
                   return_value={"ID": "ubuntu", "ID_LIKE": "debian"}):
            assert detect_os() == "ubuntu"

    def test_raises_for_unsupported_os(self):
        with patch("os_setup.os_detector.platform.system", return_value="FreeBSD"):
            with pytest.raises(RuntimeError, match="Unsupported operating system"):
                detect_os()
