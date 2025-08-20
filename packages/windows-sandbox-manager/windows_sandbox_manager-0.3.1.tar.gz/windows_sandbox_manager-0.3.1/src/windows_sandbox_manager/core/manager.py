"""
Multi-sandbox manager with async operations and registry integration.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from .sandbox import Sandbox, SandboxState
from .registry import SandboxRegistry
from ..config.models import SandboxConfig
from ..exceptions import SandboxNotFoundError, SandboxError


class SandboxManager:
    """
    Manages multiple sandbox instances with lifecycle coordination.
    """

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self._sandboxes: Dict[str, Sandbox] = {}
        self._registry = SandboxRegistry()
        self._creation_semaphore = asyncio.Semaphore(max_concurrent)
        self._shutdown_event = asyncio.Event()

    async def create_sandbox(self, config: SandboxConfig) -> Sandbox:
        """Create and start a new sandbox instance."""
        async with self._creation_semaphore:
            # Check if sandbox with same name already exists
            existing = self.get_sandbox_by_name(config.name)
            if existing and existing.is_running:
                raise SandboxError(f"Sandbox '{config.name}' already running")

            # Create new sandbox
            sandbox = Sandbox(config)

            try:
                # Add to registry before creation
                self._sandboxes[sandbox.id] = sandbox
                await self._registry.register(sandbox)

                # Create and start sandbox
                await sandbox.create()

                return sandbox

            except Exception as e:
                # Remove from registry on failure
                await self._cleanup_failed_sandbox(sandbox.id)
                raise e

    async def shutdown_sandbox(self, sandbox_id: str, timeout: int = 30) -> None:
        """Shutdown a specific sandbox."""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise SandboxNotFoundError(f"Sandbox not found: {sandbox_id}")

        try:
            await sandbox.shutdown(timeout)
        finally:
            # Remove from registry
            await self._registry.unregister(sandbox_id)
            self._sandboxes.pop(sandbox_id, None)

    async def shutdown_all(self, timeout: int = 30) -> None:
        """Shutdown all sandboxes."""
        if not self._sandboxes:
            return

        # Create shutdown tasks for all sandboxes
        shutdown_tasks = []
        for sandbox_id in list(self._sandboxes.keys()):
            task = asyncio.create_task(self._safe_shutdown_sandbox(sandbox_id, timeout))
            shutdown_tasks.append(task)

        # Wait for all shutdowns to complete
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self._shutdown_event.set()

    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        """Get sandbox by ID."""
        return self._sandboxes.get(sandbox_id)

    def get_sandbox_by_name(self, name: str) -> Optional[Sandbox]:
        """Get sandbox by name."""
        for sandbox in self._sandboxes.values():
            if sandbox.config.name == name:
                return sandbox
        return None

    def list_sandboxes(self, state_filter: Optional[SandboxState] = None) -> List[Sandbox]:
        """List all sandboxes, optionally filtered by state."""
        sandboxes = list(self._sandboxes.values())

        if state_filter:
            sandboxes = [s for s in sandboxes if s.state == state_filter]

        # Sort by creation time
        return sorted(sandboxes, key=lambda s: s.created_at)

    def get_running_count(self) -> int:
        """Get count of running sandboxes."""
        return len([s for s in self._sandboxes.values() if s.is_running])

    def get_total_count(self) -> int:
        """Get total count of sandboxes."""
        return len(self._sandboxes)

    async def cleanup_stopped_sandboxes(self) -> int:
        """Remove stopped sandboxes from management. Returns count cleaned up."""
        cleanup_count = 0
        stopped_ids = []

        for sandbox_id, sandbox in self._sandboxes.items():
            if sandbox.state in [SandboxState.STOPPED, SandboxState.FAILED]:
                stopped_ids.append(sandbox_id)

        for sandbox_id in stopped_ids:
            await self._registry.unregister(sandbox_id)
            self._sandboxes.pop(sandbox_id, None)
            cleanup_count += 1

        return cleanup_count

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide sandbox statistics."""
        running_sandboxes = self.list_sandboxes(SandboxState.RUNNING)

        total_memory = sum(s.config.memory_mb for s in running_sandboxes)
        total_cpu_cores = sum(s.config.cpu_cores for s in running_sandboxes)

        # Calculate average uptime for running sandboxes
        avg_uptime = 0.0
        if running_sandboxes:
            total_uptime = sum(s.uptime for s in running_sandboxes)
            avg_uptime = total_uptime / len(running_sandboxes)

        return {
            "total_sandboxes": self.get_total_count(),
            "running_sandboxes": len(running_sandboxes),
            "total_memory_mb": total_memory,
            "total_cpu_cores": total_cpu_cores,
            "average_uptime_seconds": avg_uptime,
            "max_concurrent": self.max_concurrent,
            "registry_size": await self._registry.size(),
        }

    async def wait_for_shutdown(self) -> None:
        """Wait for manager shutdown."""
        await self._shutdown_event.wait()

    async def _safe_shutdown_sandbox(self, sandbox_id: str, timeout: int) -> None:
        """Safely shutdown a sandbox with error handling."""
        try:
            await self.shutdown_sandbox(sandbox_id, timeout)
        except Exception as e:
            logging.error(f"Error during sandbox shutdown {sandbox_id}: {e}")

    async def _cleanup_failed_sandbox(self, sandbox_id: str) -> None:
        """Clean up a failed sandbox creation."""
        try:
            await self._registry.unregister(sandbox_id)
            self._sandboxes.pop(sandbox_id, None)
        except Exception as e:
            logging.error(f"Error cleaning up failed sandbox {sandbox_id}: {e}")

    async def __aenter__(self) -> "SandboxManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        await self.shutdown_all()
