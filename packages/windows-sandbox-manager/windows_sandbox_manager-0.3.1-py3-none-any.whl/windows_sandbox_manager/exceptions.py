"""
Custom exceptions for Windows Sandbox Manager.
"""


class SandboxError(Exception):
    """Base exception for all sandbox-related errors."""

    pass


class SandboxCreationError(SandboxError):
    """Raised when sandbox creation fails."""

    pass


class SandboxNotFoundError(SandboxError):
    """Raised when a requested sandbox is not found."""

    pass


class ConfigurationError(SandboxError):
    """Raised when configuration is invalid or missing."""

    pass


class SecurityError(SandboxError):
    """Raised when security validation fails."""

    pass


class CommunicationError(SandboxError):
    """Raised when communication with sandbox fails."""

    pass


class ResourceError(SandboxError):
    """Raised when resource allocation or monitoring fails."""

    pass


class PluginError(SandboxError):
    """Raised when plugin operations fail."""

    pass
