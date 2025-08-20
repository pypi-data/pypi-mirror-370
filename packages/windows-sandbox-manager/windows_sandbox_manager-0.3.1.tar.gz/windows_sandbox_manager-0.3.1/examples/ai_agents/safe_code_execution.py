"""
Example: Safe AI agent code execution in Windows Sandbox.
Demonstrates how to run potentially untrusted AI-generated code safely.
"""

import asyncio
from pathlib import Path
from windows_sandbox_manager import SandboxManager, SandboxConfig, FolderMapping


async def run_ai_code_agent():
    """Run an AI agent that generates and executes code safely."""
    
    # Create workspace directory
    workspace = Path("C:/temp/ai_workspace")
    workspace.mkdir(exist_ok=True)
    
    # Configure sandbox for AI agent
    config = SandboxConfig(
        name="ai-code-agent",
        memory_mb=4096,
        cpu_cores=2,
        networking=True,
        folders=[
            FolderMapping(
                host=workspace,
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/workspace"),
                readonly=False
            )
        ],
        startup_commands=[
            "python -m pip install requests beautifulsoup4 pandas",
            "cd C:/Users/WDAGUtilityAccount/Desktop/workspace"
        ]
    )
    
    async with SandboxManager() as manager:
        print("Creating sandbox for AI agent...")
        sandbox = await manager.create_sandbox(config)
        
        # Simulate AI-generated code (potentially untrusted)
        ai_generated_code = '''
import requests
import json
from pathlib import Path

def analyze_github_repo(repo_url):
    """Analyze a GitHub repository safely."""
    # Extract repo info from URL
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1]
    
    # Make API request
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Create analysis report
        report = {
            "name": data["name"],
            "language": data["language"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "description": data["description"]
        }
        
        # Save report to file
        with open("analysis_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Analysis complete for {repo}")
        print(f"Language: {report['language']}")
        print(f"Stars: {report['stars']}")
        
        return report
    else:
        print(f"Error: {response.status_code}")
        return None

# Run analysis
if __name__ == "__main__":
    result = analyze_github_repo("https://github.com/microsoft/vscode")
    if result:
        print("Report saved to analysis_report.json")
'''
        
        print("Executing AI-generated code in sandbox...")
        
        # Write the AI code to a file in the sandbox
        write_result = await sandbox.execute(
            f'echo "{ai_generated_code}" > ai_script.py'
        )
        
        if write_result.success:
            # Execute the AI-generated code
            exec_result = await sandbox.execute("python ai_script.py")
            
            print("AI Agent Output:")
            print(exec_result.stdout)
            
            if exec_result.stderr:
                print("Errors:")
                print(exec_result.stderr)
            
            # Check if report was created
            check_result = await sandbox.execute("dir analysis_report.json")
            if "analysis_report.json" in check_result.stdout:
                # Read the report
                report_result = await sandbox.execute("type analysis_report.json")
                print("\nGenerated Report:")
                print(report_result.stdout)
            
        print("\nAI agent execution completed safely!")


async def run_data_processing_agent():
    """Example of AI agent processing data files safely."""
    
    config = SandboxConfig(
        name="data-processing-agent",
        memory_mb=2048,
        cpu_cores=1,
        networking=False,  # No network needed for local processing
        startup_commands=[
            "python -m pip install pandas numpy"
        ]
    )
    
    async with SandboxManager() as manager:
        print("Creating sandbox for data processing...")
        sandbox = await manager.create_sandbox(config)
        
        # Simulate AI agent processing untrusted data
        data_processor = '''
import pandas as pd
import numpy as np

# Create sample data (simulating untrusted input)
data = {
    "id": range(1, 101),
    "value": np.random.randn(100),
    "category": np.random.choice(["A", "B", "C"], 100)
}

df = pd.DataFrame(data)

# Process data
summary = df.groupby("category").agg({
    "value": ["mean", "std", "count"]
}).round(3)

print("Data processing completed:")
print(summary)

# Save results
df.to_csv("processed_data.csv", index=False)
summary.to_csv("summary_stats.csv")

print("Files saved: processed_data.csv, summary_stats.csv")
'''
        
        print("Running data processing agent...")
        
        # Execute data processing
        write_result = await sandbox.execute(f'echo "{data_processor}" > process_data.py')
        exec_result = await sandbox.execute("python process_data.py")
        
        print("Data Processing Output:")
        print(exec_result.stdout)
        
        # Verify files were created
        files_result = await sandbox.execute("dir *.csv")
        print("\nCreated files:")
        print(files_result.stdout)


async def main():
    """Run AI agent examples."""
    print("=== AI Agent Safe Execution Examples ===\n")
    
    print("1. Running Code Generation Agent...")
    await run_ai_code_agent()
    
    print("\n" + "="*50 + "\n")
    
    print("2. Running Data Processing Agent...")
    await run_data_processing_agent()
    
    print("\nAll AI agents completed safely in isolated sandboxes!")


if __name__ == "__main__":
    asyncio.run(main())