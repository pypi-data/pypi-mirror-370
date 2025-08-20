"""
Resource monitoring for sandbox instances.
"""

import asyncio
import psutil
from datetime import datetime
from typing import Optional, Dict, Any


class ResourceStats:
    """Resource usage statistics."""

    def __init__(self, memory_mb: int, cpu_percent: float, disk_mb: int,
                 memory_percent: float = 0.0, disk_io_read_mb: float = 0.0,
                 disk_io_write_mb: float = 0.0, network_sent_mb: float = 0.0,
                 network_recv_mb: float = 0.0, process_count: int = 0):
        self.memory_mb = memory_mb
        self.cpu_percent = cpu_percent
        self.disk_mb = disk_mb
        self.memory_percent = memory_percent
        self.disk_io_read_mb = disk_io_read_mb
        self.disk_io_write_mb = disk_io_write_mb
        self.network_sent_mb = network_sent_mb
        self.network_recv_mb = network_recv_mb
        self.process_count = process_count
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'memory_mb': self.memory_mb,
            'memory_percent': self.memory_percent,
            'cpu_percent': self.cpu_percent,
            'disk_mb': self.disk_mb,
            'disk_io_read_mb': self.disk_io_read_mb,
            'disk_io_write_mb': self.disk_io_write_mb,
            'network_sent_mb': self.network_sent_mb,
            'network_recv_mb': self.network_recv_mb,
            'process_count': self.process_count,
            'timestamp': self.timestamp.isoformat()
        }


class ResourceMonitor:
    """
    Monitors resource usage for sandbox instances.
    """

    def __init__(self, sandbox_id: str, interval: int = 30):
        self.sandbox_id = sandbox_id
        self.interval = interval
        self._monitoring = False
        self._task: Optional[asyncio.Task] = None
        self._latest_stats: Optional[ResourceStats] = None
        self._initial_io_counters: Optional[Dict[str, Any]] = None
        self._initial_net_counters: Optional[Dict[str, Any]] = None

    async def start(self) -> None:
        """Start resource monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Stop resource monitoring."""
        self._monitoring = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def get_stats(self) -> ResourceStats:
        """Get latest resource statistics."""
        if self._latest_stats is None:
            # Collect stats once if not monitoring
            return await self._collect_stats()
        return self._latest_stats

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                stats = await self._collect_stats()
                self._latest_stats = stats
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue monitoring
                await asyncio.sleep(self.interval)

    async def _collect_stats(self) -> ResourceStats:
        """Collect current resource statistics for sandbox process and system."""
        try:
            # System-wide statistics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if self._initial_net_counters is None:
                self._initial_net_counters = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                }
            
            network_sent_mb = (net_io.bytes_sent - self._initial_net_counters['bytes_sent']) / (1024 * 1024)
            network_recv_mb = (net_io.bytes_recv - self._initial_net_counters['bytes_recv']) / (1024 * 1024)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if self._initial_io_counters is None:
                self._initial_io_counters = {
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                }
            
            disk_io_read_mb = (disk_io.read_bytes - self._initial_io_counters['read_bytes']) / (1024 * 1024)
            disk_io_write_mb = (disk_io.write_bytes - self._initial_io_counters['write_bytes']) / (1024 * 1024)
            
            # Find sandbox-specific processes
            sandbox_processes = []
            total_sandbox_memory = 0
            total_sandbox_cpu = 0.0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['name'] and 'sandbox' in proc_info['name'].lower():
                        sandbox_processes.append(proc)
                        # Get memory for this process
                        if proc_info['memory_info']:
                            total_sandbox_memory += proc_info['memory_info'].rss
                        # Get CPU for this process (needs interval for accurate reading)
                        try:
                            total_sandbox_cpu += proc.cpu_percent(interval=0.01)
                        except:
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue
            
            # If sandbox processes found, use their stats; otherwise use system stats
            if sandbox_processes:
                memory_mb = total_sandbox_memory // (1024 * 1024)
                cpu_percent_used = total_sandbox_cpu
                process_count = len(sandbox_processes)
            else:
                # Use system-wide stats as fallback
                memory_mb = memory.used // (1024 * 1024)
                cpu_percent_used = cpu_percent
                process_count = len(psutil.pids())
            
            return ResourceStats(
                memory_mb=int(memory_mb),
                cpu_percent=round(cpu_percent_used, 2),
                disk_mb=int(disk.used // (1024 * 1024)),
                memory_percent=round(memory.percent, 2),
                disk_io_read_mb=round(disk_io_read_mb, 2),
                disk_io_write_mb=round(disk_io_write_mb, 2),
                network_sent_mb=round(network_sent_mb, 2),
                network_recv_mb=round(network_recv_mb, 2),
                process_count=process_count
            )
            
        except Exception:
            # If monitoring fails, return basic stats
            try:
                # Try to at least get basic system stats
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=0.1)
                disk = psutil.disk_usage('/')
                
                return ResourceStats(
                    memory_mb=int(memory.used // (1024 * 1024)),
                    cpu_percent=round(cpu, 2),
                    disk_mb=int(disk.used // (1024 * 1024)),
                    memory_percent=round(memory.percent, 2)
                )
            except:
                # Complete fallback
                return ResourceStats(memory_mb=0, cpu_percent=0.0, disk_mb=0)
