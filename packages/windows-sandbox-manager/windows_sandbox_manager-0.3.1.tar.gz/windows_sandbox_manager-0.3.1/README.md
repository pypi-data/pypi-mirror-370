# Windows Sandbox Manager

Python library for managing Windows Sandbox instances programmatically. Useful for running untrusted code, testing applications, or executing AI agents in isolated environments.

## Installation

```bash
pip install windows-sandbox-manager
```

## Usage

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig

async def main():
    # Create sandbox manager
    manager = SandboxManager()
    
    # Create sandbox configuration
    config = SandboxConfig(
        name="my-sandbox",
        memory_mb=4096,
        cpu_cores=2,
        networking=True
    )
    
    # Create and start sandbox
    sandbox = await manager.create_sandbox(config)
    
    # Execute commands
    result = await sandbox.execute("python --version")
    print(f"Output: {result.stdout}")
    
    # Cleanup
    await sandbox.shutdown()

asyncio.run(main())
```

### CLI

```bash
wsb create sandbox.yaml
wsb list
wsb exec <sandbox-id> "python script.py"
wsb shutdown <sandbox-id>
```

## Configuration

```yaml
name: "dev-sandbox"
memory_mb: 4096
cpu_cores: 2
networking: true

folders:
  - host: "C:\\Projects\\MyApp"
    guest: "C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"
    readonly: false

startup_commands:
  - "python --version"
```

## AI Agent Execution

Windows Sandbox provides a secure environment for running AI agents that need to execute untrusted code or interact with the file system without risking the host machine.

### Example: Running an AI Code Agent

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig, FolderMapping
from pathlib import Path

async def run_ai_agent():
    config = SandboxConfig(
        name="ai-agent-sandbox",
        memory_mb=8192,
        cpu_cores=4,
        networking=True,
        folders=[
            FolderMapping(
                host=Path("C:/agent_workspace"),
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/workspace"),
                readonly=False
            )
        ],
        startup_commands=[
            "python -m pip install requests openai",
            "python -c \"print('AI Agent environment ready')\""
        ]
    )
    
    async with SandboxManager() as manager:
        sandbox = await manager.create_sandbox(config)
        
        # Execute AI agent code safely
        agent_code = '''
import os
import requests

# AI agent can safely write files, make network requests, etc.
with open("output.txt", "w") as f:
    f.write("AI agent executed safely in sandbox")

# Network access is isolated
response = requests.get("https://api.github.com")
print(f"API Status: {response.status_code}")
'''
        
        # Write agent code to sandbox
        result = await sandbox.execute(f'echo "{agent_code}" > agent.py')
        
        # Run the agent (now uses real PowerShell Direct communication)
        result = await sandbox.execute("python agent.py")
        print(f"Agent output: {result.stdout}")
        print(f"Exit code: {result.returncode}")
        
        # Monitor resource usage
        stats = await sandbox.get_resource_stats()
        print(f"Memory usage: {stats.memory_mb}MB")
        print(f"CPU usage: {stats.cpu_percent}%")
        
        # Check results
        result = await sandbox.execute("type output.txt")
        print(f"Agent created file: {result.stdout}")

asyncio.run(run_ai_agent())
```

### Use Cases for AI Agents

- **Code Generation & Execution**: Let AI agents write and test code without affecting your system
- **File System Operations**: Allow agents to create, modify, and organize files safely
- **Web Scraping**: Run web scraping agents with network isolation
- **Data Processing**: Process untrusted data files in a contained environment
- **Testing & Validation**: Test AI-generated scripts before running on production systems

## Features

- **Real Sandbox Execution**: Execute commands directly in Windows Sandbox VMs using PowerShell Direct
- **Enhanced Resource Monitoring**: Real-time monitoring of CPU, memory, disk I/O, and network usage with configurable alerts
- **Async API**: Full async/await support for non-blocking sandbox operations
- **Secure Isolation**: Complete isolation from host system for running untrusted code
- **Folder Mapping**: Share folders between host and sandbox with configurable permissions
- **CLI Interface**: Command-line tools for managing sandboxes
- **Configuration Management**: YAML/JSON based configuration with validation

## Feature Examples

### Real Sandbox Execution

Execute commands directly in Windows Sandbox using PowerShell Direct communication:

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig

async def execute_commands():
    config = SandboxConfig(name="command-sandbox")
    
    async with SandboxManager() as manager:
        sandbox = await manager.create_sandbox(config)
        
        # Execute single command
        result = await sandbox.execute("dir C:\\")
        print(f"Directory listing: {result.stdout}")
        print(f"Exit code: {result.returncode}")
        
        # Execute multiple commands
        commands = [
            "python --version",
            "pip install requests",
            "python -c \"import requests; print('Requests installed')\"",
        ]
        
        for cmd in commands:
            result = await sandbox.execute(cmd, timeout=120)
            if result.success:
                print(f"✓ {cmd}: {result.stdout.strip()}")
            else:
                print(f"✗ {cmd}: {result.stderr.strip()}")

asyncio.run(execute_commands())
```

### Enhanced Resource Monitoring

Monitor sandbox resource usage in real-time with detailed metrics:

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig
from windows_sandbox_manager.monitoring import ResourceMonitor

async def monitor_resources():
    config = SandboxConfig(
        name="monitored-sandbox",
        monitoring={"metrics_enabled": True}
    )
    
    async with SandboxManager() as manager:
        sandbox = await manager.create_sandbox(config)
        monitor = ResourceMonitor(sandbox)
        
        # Start monitoring
        await monitor.start()
        
        # Start resource-intensive task
        await sandbox.execute("python -c \"import time; [i**2 for i in range(100000) for _ in range(1000)]\"")
        
        # Get detailed metrics
        for i in range(5):
            metrics = await monitor.get_metrics()
            print(f"CPU: {metrics.cpu_percent:.1f}%")
            print(f"Memory: {metrics.memory_mb:.1f}MB (Peak: {metrics.memory_peak_mb:.1f}MB)")
            print(f"Disk Read: {metrics.disk_read_mb:.2f}MB/s")
            print(f"Disk Write: {metrics.disk_write_mb:.2f}MB/s")
            print(f"Network In: {metrics.network_recv_mbps:.2f}Mbps")
            print(f"Network Out: {metrics.network_sent_mbps:.2f}Mbps")
            print("---")
            await asyncio.sleep(2)
        
        # Stop monitoring
        await monitor.stop()

asyncio.run(monitor_resources())
```

Configure resource alerts:

```python
from windows_sandbox_manager import SandboxConfig, MonitoringConfig

config = SandboxConfig(
    name="alert-sandbox",
    monitoring=MonitoringConfig(
        metrics_enabled=True,
        alert_thresholds={
            "cpu_percent": 80.0,
            "memory_mb": 6144,
            "disk_write_mb_per_sec": 100.0
        },
        health_check_interval=30
    )
)
```

### Async API Operations

Perform multiple sandbox operations concurrently:

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig

async def concurrent_operations():
    config1 = SandboxConfig(name="sandbox-1")
    config2 = SandboxConfig(name="sandbox-2") 
    config3 = SandboxConfig(name="sandbox-3")
    
    async with SandboxManager() as manager:
        # Create multiple sandboxes concurrently
        sandbox1, sandbox2, sandbox3 = await asyncio.gather(
            manager.create_sandbox(config1),
            manager.create_sandbox(config2),
            manager.create_sandbox(config3)
        )
        
        # Execute commands in parallel
        results = await asyncio.gather(
            sandbox1.execute("python -c \"import time; time.sleep(2); print('Task 1 done')\""),
            sandbox2.execute("python -c \"import time; time.sleep(2); print('Task 2 done')\""),
            sandbox3.execute("python -c \"import time; time.sleep(2); print('Task 3 done')\""),
            return_exceptions=True
        )
        
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"Sandbox {i} failed: {result}")
            else:
                print(f"Sandbox {i}: {result.stdout.strip()}")

asyncio.run(concurrent_operations())
```

### Folder Mapping

Share folders between host and sandbox with different permissions:

```python
import asyncio
from pathlib import Path
from windows_sandbox_manager import SandboxManager, SandboxConfig, FolderMapping

async def folder_mapping_example():
    config = SandboxConfig(
        name="file-sandbox",
        folders=[
            # Read-only source code
            FolderMapping(
                host=Path("C:/MyProject/src"),
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/src"),
                readonly=True
            ),
            # Read-write workspace
            FolderMapping(
                host=Path("C:/SandboxWorkspace"),
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/workspace"),
                readonly=False
            ),
            # Read-only tools
            FolderMapping(
                host=Path("C:/Tools"),
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/tools"),
                readonly=True
            )
        ]
    )
    
    async with SandboxManager() as manager:
        sandbox = await manager.create_sandbox(config)
        
        # List shared folders
        result = await sandbox.execute("dir C:\\Users\\WDAGUtilityAccount\\Desktop")
        print("Shared folders:")
        print(result.stdout)
        
        # Read from read-only folder
        result = await sandbox.execute("type C:\\Users\\WDAGUtilityAccount\\Desktop\\src\\main.py")
        print("Source file content:")
        print(result.stdout)
        
        # Write to read-write workspace
        await sandbox.execute('echo "Output from sandbox" > C:\\Users\\WDAGUtilityAccount\\Desktop\\workspace\\output.txt')
        
        # Verify file was created on host
        result = await sandbox.execute("type C:\\Users\\WDAGUtilityAccount\\Desktop\\workspace\\output.txt")
        print("Created file content:")
        print(result.stdout)

asyncio.run(folder_mapping_example())
```

### CLI Interface

Use command-line tools for sandbox management:

```bash
# Create sandbox from configuration file
wsb create --config sandbox.yaml

# List active sandboxes
wsb list

# Execute command in specific sandbox
wsb exec sandbox-abc123 "python --version"

# Monitor sandbox resources
wsb monitor sandbox-abc123

# Copy files to/from sandbox
wsb copy local_file.txt sandbox-abc123:/path/in/sandbox/
wsb copy sandbox-abc123:/path/in/sandbox/output.txt ./local_output.txt

# Get sandbox logs
wsb logs sandbox-abc123

# Shutdown specific sandbox
wsb shutdown sandbox-abc123

# Cleanup all stopped sandboxes
wsb cleanup
```

Advanced CLI usage with configuration file:

```yaml
# sandbox.yaml
name: "development-sandbox"
memory_mb: 8192
cpu_cores: 4
networking: true

folders:
  - host: "C:\\Projects\\MyApp"
    guest: "C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"
    readonly: false
  - host: "C:\\Tools"
    guest: "C:\\Users\\WDAGUtilityAccount\\Desktop\\tools"
    readonly: true

startup_commands:
  - "python -m pip install --upgrade pip"
  - "python -m pip install -r C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp\\requirements.txt"
  - "cd C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"

monitoring:
  metrics_enabled: true
  alert_thresholds:
    memory_mb: 6144
    cpu_percent: 80.0
```

```bash
# Create and start sandbox with configuration
wsb create --config sandbox.yaml

# Execute interactive session
wsb shell sandbox-development --working-dir "C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"
```

## Requirements

- Windows 10 Pro/Enterprise/Education (version 1903+) 
- Windows Sandbox feature enabled
- Python 3.9+
- PowerShell 5.0+ (for sandbox communication)
- 4 GB RAM minimum (8 GB recommended)
- Virtualization enabled in BIOS

### Quick System Check

```bash
# Check if your system meets requirements
wsb check-system

# Detailed check with fix instructions
wsb check-system --verbose --fix-instructions
```

**Having issues? See [SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md) for detailed setup instructions and solutions to common problems.**

## Development

```bash
git clone https://github.com/Amal-David/python-windows-sandbox.git
cd python-windows-sandbox
pip install -e ".[dev]"
pytest
```

## Changelog

### Version 0.3.1
- Fixed missing `description` attribute in SandboxConfig
- Enhanced resource monitoring with detailed metrics (CPU, memory, disk I/O, network)
- Added ResourceMonitor class for advanced monitoring capabilities
- Improved memory peak tracking and resource metrics
- Added comprehensive system requirements checker
- Added automatic validation before sandbox creation
- Added CLI commands: `check-system` and `validate`
- Created detailed setup and troubleshooting documentation
- Improved error messages with actionable fix instructions
- Added psutil dependency for better system metrics

### Version 0.3.0
- Initial public release
- Real Windows Sandbox execution via PowerShell Direct
- Async/await API support
- CLI interface
- Folder mapping capabilities
- Basic resource monitoring

## License

MIT