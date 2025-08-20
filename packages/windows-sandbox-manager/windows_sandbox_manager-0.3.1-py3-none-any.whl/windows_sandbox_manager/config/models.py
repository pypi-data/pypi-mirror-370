"""
Pydantic models for configuration management.
"""

from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict
import yaml
import json


class FolderMapping(BaseModel):
    """Configuration for folder mapping between host and guest."""

    host: Path
    guest: Path
    readonly: bool = False

    @field_validator("host", "guest")
    @classmethod
    def validate_paths(cls, v: Any) -> Path:
        if isinstance(v, str):
            return Path(v)
        return Path(v)  # Ensure we always return Path


class NetworkRestriction(BaseModel):
    """Network access restriction configuration."""

    allow: Optional[List[str]] = None
    deny: Optional[List[str]] = None


class SecurityConfig(BaseModel):
    """Security configuration for sandbox."""

    # Fixed: using pattern instead of regex for Pydantic v2 compatibility
    isolation_level: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    network_restrictions: Optional[NetworkRestriction] = None
    file_access: Dict[str, bool] = Field(default_factory=dict)


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""

    metrics_enabled: bool = True
    # Fixed: using pattern instead of regex for Pydantic v2 compatibility
    log_level: str = Field(default="info", pattern=r"^(debug|info|warning|error|critical)$")
    health_check_interval: int = Field(default=30, ge=1, le=3600)


class PluginConfig(BaseModel):
    """Plugin configuration."""

    name: str
    enabled: bool = True
    config: Dict[str, Union[str, int, bool, float]] = Field(default_factory=dict)


class SandboxConfig(BaseModel):
    """Complete sandbox configuration."""

    name: str
    description: str = ""
    memory_mb: int = Field(default=4096, ge=512, le=32768)
    cpu_cores: int = Field(default=2, ge=1, le=16)
    networking: bool = True
    gpu_acceleration: bool = False

    folders: List[FolderMapping] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    startup_commands: List[str] = Field(default_factory=list)

    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    plugins: List[PluginConfig] = Field(default_factory=list)

    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "SandboxConfig":
        """Load configuration from YAML or JSON file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        if file_path.suffix.lower() in [".yml", ".yaml"]:
            data = yaml.safe_load(content)
        elif file_path.suffix.lower() == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        return cls(**data)

    def to_file(self, file_path: Union[str, Path], format: str = "yaml") -> None:
        """Save configuration to file."""
        file_path = Path(file_path)

        data = self.model_dump()

        if format.lower() in ["yml", "yaml"]:
            content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        elif format.lower() == "json":
            content = json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        file_path.write_text(content, encoding="utf-8")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        """Validate sandbox name."""
        if not v or not v.strip():
            raise ValueError("Sandbox name cannot be empty")
        if len(v) > 50:
            raise ValueError("Sandbox name too long (max 50 characters)")
        return str(v).strip()

    @field_validator("folders")
    @classmethod
    def validate_folders(cls, v: Any) -> Any:
        """Validate folder mappings."""
        guest_paths = set()
        for folder in v:
            if folder.guest in guest_paths:
                raise ValueError(f"Duplicate guest path: {folder.guest}")
            guest_paths.add(folder.guest)
        return v
