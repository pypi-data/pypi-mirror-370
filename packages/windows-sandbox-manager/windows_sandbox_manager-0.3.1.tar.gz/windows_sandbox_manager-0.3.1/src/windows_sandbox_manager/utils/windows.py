"""
Windows-specific utility functions.
"""

import platform
import subprocess
from typing import Dict, Tuple

from ..exceptions import SandboxError


class WindowsUtils:
    """Windows-specific utilities."""

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system().lower() == "windows"

    @staticmethod
    def check_sandbox_support() -> bool:
        """Check if Windows Sandbox is supported and enabled."""
        if not WindowsUtils.is_windows():
            return False

        try:
            # Check if Windows Sandbox executable exists
            result = subprocess.run(
                ["where", "WindowsSandbox.exe"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def get_windows_version() -> Tuple[int, int, int]:
        """Get Windows version as (major, minor, build)."""
        if not WindowsUtils.is_windows():
            raise SandboxError("Not running on Windows")

        try:
            version_string = platform.version()
            parts = version_string.split(".")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError) as e:
            raise SandboxError(f"Unable to parse Windows version: {e}")

    @staticmethod
    def check_minimum_version() -> bool:
        """Check if Windows version supports Sandbox (Windows 10 Pro/Enterprise 1903+)."""
        try:
            major, minor, build = WindowsUtils.get_windows_version()
            # Windows 10 build 1903 is build 18362
            return major >= 10 and build >= 18362
        except SandboxError:
            return False

    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system information."""
        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
        }

        if WindowsUtils.is_windows():
            info.update(
                {
                    "windows_version": platform.version(),
                    "windows_edition": WindowsUtils._get_windows_edition(),
                    "sandbox_supported": str(WindowsUtils.check_sandbox_support()),
                    "minimum_version": str(WindowsUtils.check_minimum_version()),
                }
            )

        return info

    @staticmethod
    def _get_windows_edition() -> str:
        """Get Windows edition (Pro, Enterprise, etc.)."""
        try:
            result = subprocess.run(
                ["wmic", "os", "get", "Caption", "/value"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("Caption="):
                        return line.split("=", 1)[1].strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return "Unknown"
