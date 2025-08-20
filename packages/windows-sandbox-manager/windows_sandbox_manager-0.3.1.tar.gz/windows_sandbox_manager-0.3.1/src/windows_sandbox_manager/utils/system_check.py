"""
System requirements checker for Windows Sandbox.
"""

import sys
import platform
import subprocess
import ctypes
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class WindowsEdition(Enum):
    """Windows edition types."""
    HOME = "Home"
    PRO = "Pro"
    ENTERPRISE = "Enterprise"
    EDUCATION = "Education"
    PRO_WORKSTATION = "Pro for Workstations"
    UNKNOWN = "Unknown"


class RequirementStatus(Enum):
    """Status of a system requirement."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    UNKNOWN = "unknown"


@dataclass
class SystemRequirement:
    """Individual system requirement check result."""
    name: str
    status: RequirementStatus
    message: str
    details: Optional[str] = None
    fix_instructions: Optional[str] = None


@dataclass
class SystemCheckResult:
    """Complete system requirements check result."""
    can_run_sandbox: bool
    requirements: List[SystemRequirement]
    os_version: str
    os_edition: str
    is_admin: bool
    total_memory_gb: float
    cpu_cores: int


class SystemChecker:
    """Check system requirements for Windows Sandbox."""
    
    # Minimum Windows version for sandbox support (Windows 10 1903)
    MIN_WINDOWS_BUILD = 18362
    MIN_MEMORY_GB = 4.0
    MIN_CPU_CORES = 2
    REQUIRED_DISK_SPACE_GB = 1.0
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges."""
        if not SystemChecker.is_windows():
            return False
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    @staticmethod
    def get_windows_version() -> Tuple[str, int]:
        """Get Windows version and build number."""
        if not SystemChecker.is_windows():
            return "Not Windows", 0
            
        try:
            # Get detailed version info
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )
            
            version = winreg.QueryValueEx(key, "DisplayVersion")[0]
            build = int(winreg.QueryValueEx(key, "CurrentBuildNumber")[0])
            winreg.CloseKey(key)
            
            return f"Windows {version} (Build {build})", build
        except:
            # Fallback to platform module
            version = platform.version()
            try:
                build = int(version.split('.')[2])
            except:
                build = 0
            return f"Windows {platform.release()} ({version})", build
    
    @staticmethod
    def get_windows_edition() -> WindowsEdition:
        """Get Windows edition (Home, Pro, Enterprise, etc.)."""
        if not SystemChecker.is_windows():
            return WindowsEdition.UNKNOWN
            
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            )
            edition = winreg.QueryValueEx(key, "EditionID")[0].lower()
            winreg.CloseKey(key)
            
            if "home" in edition:
                return WindowsEdition.HOME
            elif "enterprise" in edition:
                return WindowsEdition.ENTERPRISE
            elif "education" in edition:
                return WindowsEdition.EDUCATION
            elif "professional" in edition or "pro" in edition:
                if "workstation" in edition:
                    return WindowsEdition.PRO_WORKSTATION
                return WindowsEdition.PRO
            else:
                return WindowsEdition.UNKNOWN
        except:
            return WindowsEdition.UNKNOWN
    
    @staticmethod
    def is_sandbox_feature_enabled() -> bool:
        """Check if Windows Sandbox feature is enabled."""
        if not SystemChecker.is_windows():
            return False
            
        try:
            # Check using DISM
            result = subprocess.run(
                ["dism", "/online", "/get-featureinfo", "/featurename:Containers-DisposableClientVM"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return "State : Enabled" in result.stdout
        except:
            # Fallback: check if WindowsSandbox.exe exists
            sandbox_exe = r"C:\Windows\System32\WindowsSandbox.exe"
            return os.path.exists(sandbox_exe)
    
    @staticmethod
    def is_virtualization_enabled() -> bool:
        """Check if CPU virtualization is enabled."""
        if not SystemChecker.is_windows():
            return False
            
        try:
            # Check using systeminfo
            result = subprocess.run(
                ["systeminfo"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Look for virtualization status
            for line in result.stdout.split('\n'):
                if "Virtualization Enabled In Firmware:" in line:
                    return "Yes" in line
                elif "Hyper-V Requirements:" in line:
                    # Alternative check
                    return True
                    
            return False
        except:
            return False
    
    @staticmethod
    def get_system_memory_gb() -> float:
        """Get total system memory in GB."""
        try:
            if SystemChecker.is_windows():
                import ctypes
                kernel32 = ctypes.windll.kernel32
                
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                
                memStatus = MEMORYSTATUSEX()
                memStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memStatus))
                
                return memStatus.ullTotalPhys / (1024 ** 3)
            else:
                # For non-Windows (testing/development)
                import psutil
                return psutil.virtual_memory().total / (1024 ** 3)
        except:
            return 0.0
    
    @staticmethod
    def get_cpu_cores() -> int:
        """Get number of CPU cores."""
        try:
            import os
            return os.cpu_count() or 0
        except:
            return 0
    
    @staticmethod
    def get_available_disk_space_gb() -> float:
        """Get available disk space on system drive in GB."""
        try:
            if SystemChecker.is_windows():
                import ctypes
                
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p("C:\\"),
                    ctypes.pointer(free_bytes),
                    ctypes.pointer(total_bytes),
                    None
                )
                
                return free_bytes.value / (1024 ** 3)
            else:
                import shutil
                stat = shutil.disk_usage("/")
                return stat.free / (1024 ** 3)
        except:
            return 0.0
    
    @classmethod
    def check_all_requirements(cls) -> SystemCheckResult:
        """Check all system requirements for Windows Sandbox."""
        requirements = []
        
        # Check OS
        if not cls.is_windows():
            requirements.append(SystemRequirement(
                name="Operating System",
                status=RequirementStatus.FAILED,
                message="Windows is required",
                details="Windows Sandbox only runs on Windows 10/11",
                fix_instructions="Install Windows 10 Pro/Enterprise/Education version 1903 or later"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Operating System",
                status=RequirementStatus.PASSED,
                message="Windows detected",
                details=platform.platform()
            ))
        
        # Check Windows version
        version_str, build = cls.get_windows_version()
        if build >= cls.MIN_WINDOWS_BUILD:
            requirements.append(SystemRequirement(
                name="Windows Version",
                status=RequirementStatus.PASSED,
                message=f"{version_str}",
                details=f"Build {build} meets minimum requirement ({cls.MIN_WINDOWS_BUILD})"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Windows Version",
                status=RequirementStatus.FAILED,
                message=f"{version_str} is too old",
                details=f"Build {build} is below minimum ({cls.MIN_WINDOWS_BUILD})",
                fix_instructions="Update to Windows 10 version 1903 (May 2019 Update) or later"
            ))
        
        # Check Windows edition
        edition = cls.get_windows_edition()
        if edition in [WindowsEdition.PRO, WindowsEdition.ENTERPRISE, 
                      WindowsEdition.EDUCATION, WindowsEdition.PRO_WORKSTATION]:
            requirements.append(SystemRequirement(
                name="Windows Edition",
                status=RequirementStatus.PASSED,
                message=f"Windows {edition.value}",
                details="Edition supports Windows Sandbox"
            ))
        elif edition == WindowsEdition.HOME:
            requirements.append(SystemRequirement(
                name="Windows Edition",
                status=RequirementStatus.FAILED,
                message="Windows Home edition detected",
                details="Windows Sandbox is not available on Home edition",
                fix_instructions="Upgrade to Windows Pro, Enterprise, or Education edition"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Windows Edition",
                status=RequirementStatus.WARNING,
                message=f"Unknown edition: {edition.value}",
                details="Could not determine if edition supports Windows Sandbox"
            ))
        
        # Check administrator privileges
        is_admin = cls.is_admin()
        if is_admin:
            requirements.append(SystemRequirement(
                name="Administrator Privileges",
                status=RequirementStatus.PASSED,
                message="Running as administrator",
                details="Has required privileges"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Administrator Privileges",
                status=RequirementStatus.WARNING,
                message="Not running as administrator",
                details="Administrator privileges may be required for some operations",
                fix_instructions="Run the application as Administrator (right-click > Run as administrator)"
            ))
        
        # Check if Windows Sandbox feature is enabled
        if cls.is_sandbox_feature_enabled():
            requirements.append(SystemRequirement(
                name="Windows Sandbox Feature",
                status=RequirementStatus.PASSED,
                message="Windows Sandbox is enabled",
                details="Feature is installed and ready"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Windows Sandbox Feature",
                status=RequirementStatus.FAILED,
                message="Windows Sandbox is not enabled",
                details="The Windows Sandbox optional feature must be enabled",
                fix_instructions=(
                    "Enable Windows Sandbox:\n"
                    "1. Open 'Turn Windows features on or off'\n"
                    "2. Check 'Windows Sandbox'\n"
                    "3. Click OK and restart\n"
                    "Or run in PowerShell as admin: Enable-WindowsOptionalFeature -Online -FeatureName 'Containers-DisposableClientVM'"
                )
            ))
        
        # Check virtualization
        if cls.is_virtualization_enabled():
            requirements.append(SystemRequirement(
                name="CPU Virtualization",
                status=RequirementStatus.PASSED,
                message="Virtualization is enabled",
                details="CPU virtualization support detected"
            ))
        else:
            requirements.append(SystemRequirement(
                name="CPU Virtualization",
                status=RequirementStatus.WARNING,
                message="Could not verify virtualization",
                details="Virtualization status unknown",
                fix_instructions="Enable virtualization in BIOS/UEFI settings (Intel VT-x or AMD-V)"
            ))
        
        # Check memory
        memory_gb = cls.get_system_memory_gb()
        if memory_gb >= cls.MIN_MEMORY_GB:
            requirements.append(SystemRequirement(
                name="System Memory",
                status=RequirementStatus.PASSED,
                message=f"{memory_gb:.1f} GB RAM",
                details=f"Meets minimum requirement ({cls.MIN_MEMORY_GB} GB)"
            ))
        else:
            requirements.append(SystemRequirement(
                name="System Memory",
                status=RequirementStatus.FAILED,
                message=f"{memory_gb:.1f} GB RAM is insufficient",
                details=f"Below minimum requirement ({cls.MIN_MEMORY_GB} GB)",
                fix_instructions=f"Add more RAM (minimum {cls.MIN_MEMORY_GB} GB required)"
            ))
        
        # Check CPU cores
        cpu_cores = cls.get_cpu_cores()
        if cpu_cores >= cls.MIN_CPU_CORES:
            requirements.append(SystemRequirement(
                name="CPU Cores",
                status=RequirementStatus.PASSED,
                message=f"{cpu_cores} CPU cores",
                details=f"Meets minimum requirement ({cls.MIN_CPU_CORES} cores)"
            ))
        else:
            requirements.append(SystemRequirement(
                name="CPU Cores",
                status=RequirementStatus.WARNING,
                message=f"{cpu_cores} CPU cores",
                details=f"Below recommended ({cls.MIN_CPU_CORES} cores)",
            ))
        
        # Check disk space
        disk_gb = cls.get_available_disk_space_gb()
        if disk_gb >= cls.REQUIRED_DISK_SPACE_GB:
            requirements.append(SystemRequirement(
                name="Disk Space",
                status=RequirementStatus.PASSED,
                message=f"{disk_gb:.1f} GB available",
                details=f"Sufficient space for sandbox operations"
            ))
        else:
            requirements.append(SystemRequirement(
                name="Disk Space",
                status=RequirementStatus.WARNING,
                message=f"{disk_gb:.1f} GB available",
                details=f"Low disk space may cause issues",
                fix_instructions=f"Free up disk space (at least {cls.REQUIRED_DISK_SPACE_GB} GB recommended)"
            ))
        
        # Determine if sandbox can run
        critical_failures = [
            r for r in requirements 
            if r.status == RequirementStatus.FAILED and 
            r.name in ["Operating System", "Windows Version", "Windows Edition", 
                      "Windows Sandbox Feature", "System Memory"]
        ]
        
        can_run = len(critical_failures) == 0
        
        return SystemCheckResult(
            can_run_sandbox=can_run,
            requirements=requirements,
            os_version=version_str,
            os_edition=edition.value,
            is_admin=is_admin,
            total_memory_gb=memory_gb,
            cpu_cores=cpu_cores
        )
    
    @staticmethod
    def print_requirements_report(result: SystemCheckResult) -> None:
        """Print a formatted requirements report."""
        print("\n" + "=" * 60)
        print("WINDOWS SANDBOX SYSTEM REQUIREMENTS CHECK")
        print("=" * 60)
        
        print(f"\nSystem: {result.os_version} - {result.os_edition}")
        print(f"Admin: {'Yes' if result.is_admin else 'No'}")
        print(f"Memory: {result.total_memory_gb:.1f} GB")
        print(f"CPU Cores: {result.cpu_cores}")
        
        print("\n" + "-" * 60)
        print("REQUIREMENTS STATUS:")
        print("-" * 60)
        
        # Group by status
        passed = [r for r in result.requirements if r.status == RequirementStatus.PASSED]
        failed = [r for r in result.requirements if r.status == RequirementStatus.FAILED]
        warnings = [r for r in result.requirements if r.status == RequirementStatus.WARNING]
        
        # Print failures first
        if failed:
            print("\n❌ FAILED:")
            for req in failed:
                print(f"  • {req.name}: {req.message}")
                if req.details:
                    print(f"    Details: {req.details}")
                if req.fix_instructions:
                    print(f"    Fix: {req.fix_instructions}")
        
        # Print warnings
        if warnings:
            print("\n⚠️  WARNINGS:")
            for req in warnings:
                print(f"  • {req.name}: {req.message}")
                if req.details:
                    print(f"    Details: {req.details}")
                if req.fix_instructions:
                    print(f"    Fix: {req.fix_instructions}")
        
        # Print passed
        if passed:
            print("\n✅ PASSED:")
            for req in passed:
                print(f"  • {req.name}: {req.message}")
        
        # Final verdict
        print("\n" + "=" * 60)
        if result.can_run_sandbox:
            print("✅ SYSTEM IS READY FOR WINDOWS SANDBOX")
        else:
            print("❌ SYSTEM DOES NOT MEET REQUIREMENTS FOR WINDOWS SANDBOX")
            print("\nPlease address the failed requirements above.")
        print("=" * 60 + "\n")


def check_requirements() -> SystemCheckResult:
    """Convenience function to check system requirements."""
    return SystemChecker.check_all_requirements()


def verify_sandbox_ready() -> bool:
    """Quick check if Windows Sandbox can run."""
    result = check_requirements()
    return result.can_run_sandbox


if __name__ == "__main__":
    # Run system check when module is executed directly
    result = check_requirements()
    SystemChecker.print_requirements_report(result)
    
    # Exit with error code if requirements not met
    sys.exit(0 if result.can_run_sandbox else 1)