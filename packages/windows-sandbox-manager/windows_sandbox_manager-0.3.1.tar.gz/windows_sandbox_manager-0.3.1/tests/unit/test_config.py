"""
Unit tests for configuration models.
"""

import pytest
from pathlib import Path
from pydantic import ValidationError

from windows_sandbox_manager.config.models import (
    SandboxConfig, FolderMapping, SecurityConfig, MonitoringConfig
)


class TestSandboxConfig:
    """Test SandboxConfig model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SandboxConfig(name="test")
        
        assert config.name == "test"
        assert config.memory_mb == 4096
        assert config.cpu_cores == 2
        assert config.networking is True
        assert config.gpu_acceleration is False
        assert len(config.folders) == 0
        assert len(config.environment) == 0
        assert len(config.startup_commands) == 0
    
    def test_validation_memory_limits(self):
        """Test memory validation limits."""
        # Valid memory
        config = SandboxConfig(name="test", memory_mb=2048)
        assert config.memory_mb == 2048
        
        # Too low
        with pytest.raises(ValidationError):
            SandboxConfig(name="test", memory_mb=256)
        
        # Too high
        with pytest.raises(ValidationError):
            SandboxConfig(name="test", memory_mb=50000)
    
    def test_validation_cpu_limits(self):
        """Test CPU validation limits."""
        # Valid CPU count
        config = SandboxConfig(name="test", cpu_cores=4)
        assert config.cpu_cores == 4
        
        # Too low
        with pytest.raises(ValidationError):
            SandboxConfig(name="test", cpu_cores=0)
        
        # Too high
        with pytest.raises(ValidationError):
            SandboxConfig(name="test", cpu_cores=32)
    
    def test_name_validation(self):
        """Test name validation."""
        # Valid names
        config = SandboxConfig(name="test-sandbox")
        assert config.name == "test-sandbox"
        
        config = SandboxConfig(name="  test  ")
        assert config.name == "test"
        
        # Invalid names
        with pytest.raises(ValidationError):
            SandboxConfig(name="")
        
        with pytest.raises(ValidationError):
            SandboxConfig(name="   ")
        
        with pytest.raises(ValidationError):
            SandboxConfig(name="a" * 60)  # Too long
    
    def test_folder_mapping_validation(self):
        """Test folder mapping validation."""
        folders = [
            FolderMapping(host=Path("C:/test1"), guest=Path("C:/guest1")),
            FolderMapping(host=Path("C:/test2"), guest=Path("C:/guest2"))
        ]
        
        config = SandboxConfig(name="test", folders=folders)
        assert len(config.folders) == 2
        
        # Duplicate guest paths should fail
        duplicate_folders = [
            FolderMapping(host=Path("C:/test1"), guest=Path("C:/guest1")),
            FolderMapping(host=Path("C:/test2"), guest=Path("C:/guest1"))
        ]
        
        with pytest.raises(ValidationError):
            SandboxConfig(name="test", folders=duplicate_folders)


class TestFolderMapping:
    """Test FolderMapping model."""
    
    def test_path_conversion(self):
        """Test automatic path conversion."""
        mapping = FolderMapping(host="C:/test", guest="C:/guest")
        
        assert isinstance(mapping.host, Path)
        assert isinstance(mapping.guest, Path)
        assert mapping.readonly is False
    
    def test_readonly_flag(self):
        """Test readonly flag."""
        mapping = FolderMapping(
            host=Path("C:/test"),
            guest=Path("C:/guest"),
            readonly=True
        )
        
        assert mapping.readonly is True


class TestSecurityConfig:
    """Test SecurityConfig model."""
    
    def test_default_security_config(self):
        """Test default security configuration."""
        config = SecurityConfig()
        
        assert config.isolation_level == "medium"
        assert config.network_restrictions is None
        assert len(config.file_access) == 0
    
    def test_isolation_level_validation(self):
        """Test isolation level validation."""
        # Valid levels
        for level in ["low", "medium", "high"]:
            config = SecurityConfig(isolation_level=level)
            assert config.isolation_level == level
        
        # Invalid level
        with pytest.raises(ValidationError):
            SecurityConfig(isolation_level="extreme")


class TestMonitoringConfig:
    """Test MonitoringConfig model."""
    
    def test_default_monitoring_config(self):
        """Test default monitoring configuration."""
        config = MonitoringConfig()
        
        assert config.metrics_enabled is True
        assert config.log_level == "info"
        assert config.health_check_interval == 30
    
    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid levels
        for level in ["debug", "info", "warning", "error", "critical"]:
            config = MonitoringConfig(log_level=level)
            assert config.log_level == level
        
        # Invalid level
        with pytest.raises(ValidationError):
            MonitoringConfig(log_level="verbose")
    
    def test_health_check_interval_validation(self):
        """Test health check interval validation."""
        # Valid intervals
        config = MonitoringConfig(health_check_interval=60)
        assert config.health_check_interval == 60
        
        # Too low
        with pytest.raises(ValidationError):
            MonitoringConfig(health_check_interval=0)
        
        # Too high
        with pytest.raises(ValidationError):
            MonitoringConfig(health_check_interval=5000)