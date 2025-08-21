"""
Data models for JTECH™ Installer
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class InstallationType(Enum):
    """Tipos de instalação"""

    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"


class TeamType(Enum):
    """Tipos de equipe"""

    ALL = "all"
    FULLSTACK = "fullstack"
    NO_UI = "no-ui"
    IDE_MINIMAL = "ide-minimal"


class OSType(Enum):
    """Tipos de sistema operacional"""

    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


@dataclass
class SystemInfo:
    """Informações do sistema"""

    os_type: OSType
    python_version: str
    git_available: bool
    vscode_available: bool
    current_directory: Path
    architecture: str = "x64"


@dataclass
class InstallationConfig:
    """Configuração da instalação"""

    project_path: Path
    install_type: InstallationType
    team_type: TeamType
    vs_code_integration: bool
    custom_config: Dict[str, Any]
    framework_source_path: Path | None = None


@dataclass
class InstallationResult:
    """Resultado da instalação"""

    success: bool
    installed_components: List[str]
    errors: List[str]
    warnings: List[str]
    duration: float
    config_generated: bool = False
    validation_passed: bool = False


@dataclass
class PerformanceMetrics:
    """Métricas de performance da instalação"""

    total_duration: float
    detection_time: float
    file_operations_time: float
    config_generation_time: float
    validation_time: float
    files_processed: int
    total_size_mb: float


@dataclass
class AssetInfo:
    """Informações sobre um asset do framework"""

    source_path: Path
    target_path: Path
    file_type: str
    required: bool = True
    checksum: str | None = None


@dataclass
class InstallationProgress:
    """Progresso da instalação"""

    current_phase: str
    total_phases: int
    current_phase_number: int
    files_processed: int
    total_files: int
    current_file: str | None = None
