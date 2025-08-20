"""
Windows Sandbox Manager - A modern, secure Python library for Windows Sandbox management.
"""

from .core.manager import SandboxManager
from .core.sandbox import Sandbox, SandboxState, ExecutionResult
from .config.models import SandboxConfig, FolderMapping, SecurityConfig, MonitoringConfig
from .monitoring.resources import ResourceMonitor, ResourceStats
from .exceptions import (
    SandboxError,
    SandboxCreationError,
    SandboxNotFoundError,
    ConfigurationError,
    SecurityError,
)

__version__ = "0.3.0"
__author__ = "Amal David"
__email__ = "labuka@duck.com"

__all__ = [
    "SandboxManager",
    "Sandbox",
    "SandboxState",
    "ExecutionResult",
    "SandboxConfig",
    "FolderMapping",
    "SecurityConfig",
    "MonitoringConfig",
    "ResourceMonitor",
    "ResourceStats",
    "SandboxError",
    "SandboxCreationError",
    "SandboxNotFoundError",
    "ConfigurationError",
    "SecurityError",
]
