"""
Async sandbox lifecycle manager with state management and resource monitoring.
"""

import asyncio
import uuid
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import asyncio.subprocess
import xml.etree.ElementTree as ET

from ..config.models import SandboxConfig
from ..exceptions import SandboxCreationError, SandboxError, ResourceError
from ..monitoring.resources import ResourceMonitor, ResourceStats
from ..utils.system_check import SystemChecker, RequirementStatus


class SandboxState(Enum):
    """Sandbox lifecycle states."""

    PENDING = "pending"
    CREATING = "creating"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ExecutionResult:
    """Result of command execution in sandbox."""

    def __init__(self, stdout: str, stderr: str, returncode: int, execution_time: float):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.execution_time = execution_time
        self.success = returncode == 0


class Sandbox:
    """
    Async sandbox instance with lifecycle management.
    """

    def __init__(self, config: SandboxConfig):
        self.id = str(uuid.uuid4())
        self.config = config
        self.state = SandboxState.PENDING
        self.created_at = datetime.utcnow()
        self.process: Optional[asyncio.subprocess.Process] = None
        self.wsb_file_path: Optional[Path] = None
        self._shutdown_event = asyncio.Event()
        self._resource_monitor: Optional[ResourceMonitor] = None

    async def create(self) -> None:
        """Create and start the sandbox."""
        try:
            self.state = SandboxState.CREATING
            
            # Validate system requirements
            await self._validate_system_requirements()

            # Generate WSB configuration file
            self.wsb_file_path = await self._generate_wsb_file()

            # Start Windows Sandbox
            await self._start_sandbox()

            # Initialize resource monitoring
            if self.config.monitoring.metrics_enabled:
                self._resource_monitor = ResourceMonitor(self.id)
                await self._resource_monitor.start()

            # Execute startup commands
            if self.config.startup_commands:
                await self._execute_startup_commands()

            self.state = SandboxState.RUNNING

        except Exception as e:
            self.state = SandboxState.FAILED
            raise SandboxCreationError(f"Failed to create sandbox: {e}") from e

    async def shutdown(self, timeout: int = 30) -> None:
        """Gracefully shutdown the sandbox."""
        if self.state in [SandboxState.STOPPED, SandboxState.FAILED]:
            return

        self.state = SandboxState.STOPPING

        try:
            # Stop resource monitoring
            if self._resource_monitor:
                await self._resource_monitor.stop()

            # Terminate sandbox process
            if self.process:
                self.process.terminate()

                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process()), timeout=timeout
                    )
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown failed
                    self.process.kill()
                    await self._wait_for_process()

            # Cleanup temporary files
            await self._cleanup()

            self.state = SandboxState.STOPPED
            self._shutdown_event.set()

        except Exception as e:
            self.state = SandboxState.FAILED
            raise SandboxError(f"Failed to shutdown sandbox: {e}") from e

    async def execute(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a command in the sandbox."""
        if self.state != SandboxState.RUNNING:
            raise SandboxError(f"Cannot execute command, sandbox state: {self.state}")

        start_time = asyncio.get_event_loop().time()

        try:
            # Execute command in Windows Sandbox via PowerShell remoting
            # Using PowerShell Direct to communicate with the sandbox VM
            ps_command = self._build_powershell_command(command)
            
            proc = await asyncio.create_subprocess_shell(
                ps_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            execution_time = asyncio.get_event_loop().time() - start_time

            return ExecutionResult(
                stdout=stdout.decode("utf-8", errors="ignore"),
                stderr=stderr.decode("utf-8", errors="ignore"),
                returncode=proc.returncode or 0,
                execution_time=execution_time,
            )

        except asyncio.TimeoutError:
            raise SandboxError(f"Command execution timed out after {timeout} seconds")
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            raise SandboxError(f"Command execution failed: {e}") from e

    async def get_resource_stats(self) -> ResourceStats:
        """Get current resource usage statistics."""
        if not self._resource_monitor:
            raise ResourceError("Resource monitoring not enabled")

        return await self._resource_monitor.get_stats()
    
    async def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed resource usage statistics as a dictionary."""
        stats = await self.get_resource_stats()
        return stats.to_dict()

    async def wait_for_shutdown(self) -> None:
        """Wait for sandbox to shutdown."""
        await self._shutdown_event.wait()

    @property
    def is_running(self) -> bool:
        """Check if sandbox is running."""
        return self.state == SandboxState.RUNNING

    @property
    def uptime(self) -> float:
        """Get sandbox uptime in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()

    async def _generate_wsb_file(self) -> Path:
        """Generate Windows Sandbox configuration file."""
        wsb_content = self._build_wsb_xml()

        # Create temporary WSB file
        temp_dir = Path.cwd() / "temp"
        temp_dir.mkdir(exist_ok=True)

        wsb_file = temp_dir / f"{self.config.name}_{self.id[:8]}.wsb"
        wsb_file.write_text(wsb_content, encoding="utf-8")

        return wsb_file

    def _build_wsb_xml(self) -> str:
        """Build Windows Sandbox XML configuration."""
        root = ET.Element("Configuration")

        # Memory configuration
        memory = ET.SubElement(root, "MemoryInMB")
        memory.text = str(self.config.memory_mb)

        # CPU configuration
        cpu = ET.SubElement(root, "VCpu")
        cpu.text = str(self.config.cpu_cores)

        # Networking
        networking = ET.SubElement(root, "Networking")
        networking.text = "Enable" if self.config.networking else "Disable"

        # GPU acceleration
        if self.config.gpu_acceleration:
            gpu = ET.SubElement(root, "VGpu")
            gpu.text = "Enable"

        # Folder mappings
        if self.config.folders:
            mapped_folders = ET.SubElement(root, "MappedFolders")
            for folder in self.config.folders:
                mapped_folder = ET.SubElement(mapped_folders, "MappedFolder")

                host_folder = ET.SubElement(mapped_folder, "HostFolder")
                host_folder.text = str(folder.host)

                sandbox_folder = ET.SubElement(mapped_folder, "SandboxFolder")
                sandbox_folder.text = str(folder.guest)

                readonly = ET.SubElement(mapped_folder, "ReadOnly")
                readonly.text = "true" if folder.readonly else "false"

        # Convert to string
        return ET.tostring(root, encoding="unicode", xml_declaration=True)

    async def _start_sandbox(self) -> None:
        """Start the Windows Sandbox process."""
        if not self.wsb_file_path:
            raise SandboxError("WSB file not generated")

        try:
            # Start Windows Sandbox with the configuration file
            self.process = await asyncio.create_subprocess_exec(
                "WindowsSandbox.exe",
                str(self.wsb_file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Give sandbox time to initialize
            await asyncio.sleep(5)

        except FileNotFoundError:
            raise SandboxCreationError(
                "Windows Sandbox not found. Ensure Windows Sandbox feature is enabled."
            )
        except Exception as e:
            raise SandboxCreationError(f"Failed to start sandbox process: {e}") from e

    async def _execute_startup_commands(self) -> None:
        """Execute startup commands in the sandbox."""
        for command in self.config.startup_commands:
            try:
                result = await self.execute(command, timeout=60)
                if not result.success:
                    logging.warning(f"Startup command failed: {command} - {result.stderr}")
            except Exception as e:
                logging.error(f"Error executing startup command '{command}': {e}")

    async def _wait_for_process(self) -> None:
        """Wait for sandbox process to terminate."""
        if self.process:
            await self.process.wait()

    def _build_powershell_command(self, command: str) -> str:
        """Build PowerShell command to execute in Windows Sandbox."""
        # Escape the command for PowerShell
        escaped_command = command.replace('"', '""').replace("'", "''")
        
        # Use PowerShell Direct to execute command in sandbox VM
        # This requires the sandbox to be running and accessible
        ps_script = f'''
        $VMName = "WindowsSandbox_{self.id[:8]}"
        $Session = New-PSSession -VMName $VMName -Credential (Get-Credential -Message "Sandbox Access")
        try {{
            $Result = Invoke-Command -Session $Session -ScriptBlock {{
                cmd.exe /c "{escaped_command}" 2>&1
            }}
            $ExitCode = Invoke-Command -Session $Session -ScriptBlock {{ $LASTEXITCODE }}
            Write-Output "STDOUT:$Result"
            Write-Output "EXITCODE:$ExitCode"
        }} finally {{
            Remove-PSSession -Session $Session -ErrorAction SilentlyContinue
        }}
        '''
        
        escaped_script = ps_script.replace('"', '""')
        return f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{escaped_script}"'
    
    async def _cleanup(self) -> None:
        """Clean up temporary files and resources."""
        if self.wsb_file_path and self.wsb_file_path.exists():
            try:
                self.wsb_file_path.unlink()
            except Exception as e:
                logging.warning(f"Failed to cleanup WSB file {self.wsb_file_path}: {e}")
    
    async def _validate_system_requirements(self) -> None:
        """Validate system meets requirements for Windows Sandbox."""
        result = SystemChecker.check_all_requirements()
        
        if not result.can_run_sandbox:
            # Build detailed error message
            error_msg = "System does not meet Windows Sandbox requirements:\n"
            
            for req in result.requirements:
                if req.status == RequirementStatus.FAILED:
                    error_msg += f"\n❌ {req.name}: {req.message}"
                    if req.details:
                        error_msg += f"\n   Details: {req.details}"
                    if req.fix_instructions:
                        error_msg += f"\n   Fix: {req.fix_instructions}"
            
            error_msg += "\n\nPlease see SETUP_AND_TROUBLESHOOTING.md for detailed instructions."
            
            raise SandboxCreationError(error_msg)
        
        # Log warnings if any
        warnings = [r for r in result.requirements if r.status == RequirementStatus.WARNING]
        if warnings:
            for req in warnings:
                logging.warning(f"{req.name}: {req.message}")
        
        logging.info(f"System validation passed. OS: {result.os_version}, Edition: {result.os_edition}")
