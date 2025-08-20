"""
Input validation and sanitization for security.
"""

import re
import os
from pathlib import Path
from typing import Union, Set
from urllib.parse import urlparse

from ..exceptions import SecurityError


class InputValidator:
    """
    Base input validator with common security checks.
    """

    @staticmethod
    def validate_string_length(value: str, max_length: int = 1000) -> str:
        """Validate string length to prevent buffer overflow attacks."""
        if len(value) > max_length:
            raise SecurityError(f"Input too long: {len(value)} > {max_length}")
        return value

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string by removing dangerous characters."""
        # Remove null bytes and control characters
        sanitized = "".join(char for char in value if ord(char) >= 32 or char in "\t\n\r")
        return sanitized.strip()

    @staticmethod
    def validate_alphanumeric(value: str, allow_spaces: bool = False) -> str:
        """Validate that string contains only alphanumeric characters."""
        pattern = r"^[a-zA-Z0-9\s]+$" if allow_spaces else r"^[a-zA-Z0-9]+$"
        if not re.match(pattern, value):
            raise SecurityError("Input contains invalid characters")
        return value

    @staticmethod
    def validate_name(value: str) -> str:
        """Validate sandbox/resource names."""
        if not value or not value.strip():
            raise SecurityError("Name cannot be empty")

        # Remove whitespace
        value = value.strip()

        # Check length
        if len(value) > 50:
            raise SecurityError("Name too long (max 50 characters)")

        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise SecurityError("Name contains invalid characters")

        return value


class PathValidator:
    """
    Path validation to prevent directory traversal and unauthorized access.
    """

    DANGEROUS_PATHS = {
        "windows": {
            "C:\\Windows",
            "C:\\System32",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
        },
        "patterns": {"..", ".\\..", "../", "..\\", "\\..\\", "/../"},
    }

    @classmethod
    def validate_host_path(cls, path: Union[str, Path]) -> Path:
        """Validate host system path for security."""
        if isinstance(path, str):
            path = Path(path)

        # Convert to absolute path
        try:
            abs_path = path.resolve()
        except (OSError, ValueError) as e:
            raise SecurityError(f"Invalid path: {e}")

        # Check for path traversal attempts
        path_str = str(abs_path).lower()
        for pattern in cls.DANGEROUS_PATHS["patterns"]:
            if pattern.lower() in path_str:
                raise SecurityError(f"Path traversal attempt detected: {pattern}")

        # Check against protected system directories
        for protected in cls.DANGEROUS_PATHS["windows"]:
            if path_str.startswith(protected.lower()):
                raise SecurityError(f"Access to protected directory denied: {protected}")

        # Ensure path exists and is accessible
        if not abs_path.exists():
            raise SecurityError(f"Path does not exist: {abs_path}")

        # Check if path is readable
        if not os.access(abs_path, os.R_OK):
            raise SecurityError(f"Path not accessible: {abs_path}")

        return abs_path

    @classmethod
    def validate_guest_path(cls, path: Union[str, Path]) -> Path:
        """Validate guest (sandbox) path."""
        if isinstance(path, str):
            path = Path(path)

        path_str = str(path)

        # Check for path traversal attempts
        for pattern in cls.DANGEROUS_PATHS["patterns"]:
            if pattern in path_str:
                raise SecurityError(f"Path traversal attempt in guest path: {pattern}")

        # Ensure it's an absolute Windows path (check for drive letter pattern)
        if not (len(path_str) >= 3 and path_str[1] == ":" and path_str[0].isalpha()):
            raise SecurityError("Guest path must be absolute Windows path (e.g., C:/...)")

        return path

    @classmethod
    def validate_file_extension(cls, path: Path, allowed_extensions: Set[str]) -> bool:
        """Validate file extension against allowed list."""
        if not allowed_extensions:
            return True

        extension = path.suffix.lower()
        return extension in {ext.lower() for ext in allowed_extensions}


class CommandValidator:
    """
    Command validation to prevent injection attacks.
    """

    # Commands that could be dangerous even in sandbox (system manipulation)
    DANGEROUS_COMMANDS = {
        "format",
        "diskpart",
        "shutdown",
        "restart",
        "reboot",
    }

    DANGEROUS_PATTERNS = [
        r"&\s+\w",  # Command chaining with &
        r"\|\s+\w",  # Pipe to another command
        r";\s*\w",  # Command separator ;
        r"`[^`]+`",  # Command substitution
        r"\$\([^)]+\)",  # Command substitution $()
        r">\s*\S",  # Output redirection
        r"<\s*\S",  # Input redirection
    ]

    @classmethod
    def validate_command(cls, command: str) -> str:
        """Validate command for security issues."""
        if not command or not command.strip():
            raise SecurityError("Command cannot be empty")

        command = command.strip()

        # Check length
        if len(command) > 2000:
            raise SecurityError("Command too long")

        # Check for dangerous command patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError(f"Dangerous command pattern detected: {pattern}")

        # Check for dangerous commands
        command_parts = command.split()
        if command_parts:
            base_command = command_parts[0].lower()
            # Remove file extension if present
            base_command = base_command.split(".")[0]

            if base_command in cls.DANGEROUS_COMMANDS:
                raise SecurityError(f"Dangerous command not allowed: {base_command}")

        return command

    @classmethod
    def sanitize_argument(cls, arg: str) -> str:
        """Sanitize command argument."""
        # Remove dangerous characters
        dangerous_chars = ["&", "|", ";", "`", "$", ">", "<", "\\", "%"]
        for char in dangerous_chars:
            arg = arg.replace(char, "")

        return arg.strip()

    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate URL for security."""
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise SecurityError(f"Invalid URL: {e}")

        # Only allow http/https
        if parsed.scheme not in ["http", "https"]:
            raise SecurityError(f"Unsupported URL scheme: {parsed.scheme}")

        # Prevent local network access
        hostname = parsed.hostname
        if hostname:
            # Block localhost and local IPs
            if hostname.lower() in ["localhost", "127.0.0.1", "::1"]:
                raise SecurityError("Local network access not allowed")

            # Block private IP ranges (basic check)
            if hostname.startswith(("192.168.", "10.", "172.")):
                raise SecurityError("Private network access not allowed")

        return url


class SecurityConfig:
    """
    Security configuration and policy enforcement.
    """

    def __init__(self) -> None:
        self.allowed_file_extensions: Set[str] = {
            ".txt",
            ".py",
            ".js",
            ".json",
            ".yaml",
            ".yml",
            ".md",
            ".csv",
            ".xml",
            ".html",
            ".css",
            ".sql",
            ".log",
        }
        self.max_file_size_mb: int = 100
        self.max_command_length: int = 1000
        self.enable_path_validation: bool = True
        self.enable_command_validation: bool = True

    def validate_file_access(self, path: Path) -> bool:
        """Validate file access according to security policy."""
        if self.enable_path_validation:
            PathValidator.validate_host_path(path)

        # Check file size
        if path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                raise SecurityError(f"File too large: {size_mb:.1f}MB > {self.max_file_size_mb}MB")

        # Check file extension
        if not PathValidator.validate_file_extension(path, self.allowed_file_extensions):
            raise SecurityError(f"File extension not allowed: {path.suffix}")

        return True
