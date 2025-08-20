"""
Simple sandbox creation and management example.
"""

import asyncio
from pathlib import Path
from windows_sandbox_manager import SandboxManager, SandboxConfig


async def main():
    """Create and manage a simple sandbox."""
    
    # Create sandbox configuration
    config = SandboxConfig(
        name="simple-example",
        memory_mb=2048,
        cpu_cores=1,
        networking=True,
        folders=[],
        startup_commands=[
            "echo Hello from Windows Sandbox!",
            "python --version"
        ]
    )
    
    # Create sandbox manager
    async with SandboxManager() as manager:
        print("Creating sandbox...")
        
        # Create and start the sandbox
        sandbox = await manager.create_sandbox(config)
        
        print(f"Sandbox '{sandbox.config.name}' created successfully!")
        print(f"Sandbox ID: {sandbox.id}")
        print(f"State: {sandbox.state.value}")
        
        # Wait a moment for startup
        await asyncio.sleep(5)
        
        # Execute a command
        print("\nExecuting command...")
        result = await sandbox.execute("dir C:\\")
        
        if result.success:
            print("Command output:")
            print(result.stdout)
        else:
            print(f"Command failed with exit code: {result.returncode}")
            print(f"Error: {result.stderr}")
        
        # Get resource stats
        print("\nResource usage:")
        stats = await sandbox.get_resource_stats()
        print(f"Memory: {stats.memory_mb}MB")
        print(f"CPU: {stats.cpu_percent}%")
        
        print("\nShutting down sandbox...")
        await sandbox.shutdown()
        print("Sandbox shut down successfully!")


if __name__ == "__main__":
    asyncio.run(main())