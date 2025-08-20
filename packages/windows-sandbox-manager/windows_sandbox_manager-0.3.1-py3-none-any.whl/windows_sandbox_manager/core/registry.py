"""
Sandbox registry for tracking and persistence.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .sandbox import Sandbox, SandboxState
from ..exceptions import SandboxError


@dataclass
class SandboxInfo:
    """Sandbox information for registry storage."""

    id: str
    name: str
    state: str
    created_at: str
    config_snapshot: Dict
    last_seen: str


class SandboxRegistry:
    """
    Registry for tracking sandbox instances and state persistence.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path.cwd() / ".sandbox_registry.json"
        self._registry: Dict[str, SandboxInfo] = {}
        self._lock = asyncio.Lock()

    async def register(self, sandbox: Sandbox) -> None:
        """Register a sandbox in the registry."""
        async with self._lock:
            info = SandboxInfo(
                id=sandbox.id,
                name=sandbox.config.name,
                state=sandbox.state.value,
                created_at=sandbox.created_at.isoformat(),
                config_snapshot=sandbox.config.model_dump(),
                last_seen=datetime.utcnow().isoformat(),
            )

            self._registry[sandbox.id] = info
            await self._persist()

    async def unregister(self, sandbox_id: str) -> bool:
        """Unregister a sandbox from the registry."""
        async with self._lock:
            if sandbox_id in self._registry:
                del self._registry[sandbox_id]
                await self._persist()
                return True
            return False

    async def update_state(self, sandbox_id: str, state: SandboxState) -> None:
        """Update sandbox state in registry."""
        async with self._lock:
            if sandbox_id in self._registry:
                self._registry[sandbox_id].state = state.value
                self._registry[sandbox_id].last_seen = datetime.utcnow().isoformat()
                await self._persist()

    async def get_info(self, sandbox_id: str) -> Optional[SandboxInfo]:
        """Get sandbox information from registry."""
        async with self._lock:
            return self._registry.get(sandbox_id)

    async def list_all(self) -> List[SandboxInfo]:
        """List all registered sandboxes."""
        async with self._lock:
            return list(self._registry.values())

    async def list_by_state(self, state: SandboxState) -> List[SandboxInfo]:
        """List sandboxes by state."""
        async with self._lock:
            return [info for info in self._registry.values() if info.state == state.value]

    async def find_by_name(self, name: str) -> List[SandboxInfo]:
        """Find sandboxes by name."""
        async with self._lock:
            return [info for info in self._registry.values() if info.name == name]

    async def size(self) -> int:
        """Get registry size."""
        async with self._lock:
            return len(self._registry)

    async def cleanup_stale(self, max_age_hours: int = 24) -> int:
        """Clean up stale registry entries. Returns count of cleaned entries."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        cleanup_count = 0

        async with self._lock:
            stale_ids = []

            for sandbox_id, info in self._registry.items():
                try:
                    last_seen = datetime.fromisoformat(info.last_seen)
                    if last_seen.timestamp() < cutoff_time:
                        stale_ids.append(sandbox_id)
                except (ValueError, TypeError):
                    # Invalid timestamp, mark for cleanup
                    stale_ids.append(sandbox_id)

            for sandbox_id in stale_ids:
                del self._registry[sandbox_id]
                cleanup_count += 1

            if cleanup_count > 0:
                await self._persist()

        return cleanup_count

    async def clear(self) -> None:
        """Clear all registry entries."""
        async with self._lock:
            self._registry.clear()
            await self._persist()

    async def load(self) -> None:
        """Load registry from persistent storage."""
        if not self.registry_path.exists():
            return

        try:
            async with self._lock:
                content = self.registry_path.read_text(encoding="utf-8")
                data = json.loads(content)

                self._registry = {k: SandboxInfo(**v) for k, v in data.items()}
        except (json.JSONDecodeError, TypeError, ValueError):
            # Log error and start with empty registry
            self._registry = {}

    async def _persist(self) -> None:
        """Persist registry to storage."""
        try:
            # Convert to JSON-serializable format
            data = {k: asdict(v) for k, v in self._registry.items()}

            # Write to temporary file first, then rename for atomicity
            temp_path = self.registry_path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            temp_path.rename(self.registry_path)

        except Exception as e:
            raise SandboxError(f"Failed to persist registry: {e}") from e

    async def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        async with self._lock:
            stats = {"total": len(self._registry)}

            # Count by state
            for state in SandboxState:
                count = len([info for info in self._registry.values() if info.state == state.value])
                stats[f"state_{state.value}"] = count

            return stats
