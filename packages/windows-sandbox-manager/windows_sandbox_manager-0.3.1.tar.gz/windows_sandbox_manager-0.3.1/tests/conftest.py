"""
Pytest configuration and fixtures.
"""

import asyncio
import pytest
from pathlib import Path
from typing import Generator, AsyncGenerator

from windows_sandbox_manager.config.models import SandboxConfig
from windows_sandbox_manager.core.manager import SandboxManager


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> SandboxConfig:
    """Create a test sandbox configuration."""
    return SandboxConfig(
        name="test-sandbox",
        memory_mb=2048,
        cpu_cores=1,
        networking=False,
        gpu_acceleration=False
    )


@pytest.fixture
async def sandbox_manager() -> AsyncGenerator[SandboxManager, None]:
    """Create a sandbox manager for testing."""
    manager = SandboxManager(max_concurrent=2)
    yield manager
    await manager.shutdown_all()


@pytest.fixture
def temp_config_file(tmp_path: Path, test_config: SandboxConfig) -> Path:
    """Create a temporary configuration file."""
    config_file = tmp_path / "test_config.yaml"
    test_config.to_file(config_file)
    return config_file


@pytest.fixture
def mock_windows_env(monkeypatch):
    """Mock Windows environment for testing."""
    monkeypatch.setattr("platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "windows_sandbox_manager.utils.windows.WindowsUtils.check_sandbox_support",
        lambda: True
    )