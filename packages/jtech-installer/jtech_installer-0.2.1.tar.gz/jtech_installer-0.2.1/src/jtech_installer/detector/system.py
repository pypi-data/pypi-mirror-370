"""
System detection module for JTECH™ Installer
"""

import platform
import subprocess
import sys
from pathlib import Path

from jtech_installer.core.models import OSType, SystemInfo


class SystemDetector:
    """Detecta informações do sistema operacional"""

    def detect(self) -> SystemInfo:
        """Detecta todas as informações do sistema"""
        return SystemInfo(
            os_type=self._detect_os(),
            python_version=self._get_python_version(),
            git_available=self._check_git(),
            vscode_available=self._check_vscode(),
            current_directory=Path.cwd(),
            architecture=self._get_architecture(),
        )

    def _detect_os(self) -> OSType:
        """Detecta o sistema operacional"""
        system = platform.system().lower()
        if system == "linux":
            return OSType.LINUX
        elif system == "darwin":
            return OSType.MACOS
        elif system == "windows":
            return OSType.WINDOWS
        else:
            raise ValueError(f"Sistema operacional não suportado: {system}")

    def _get_python_version(self) -> str:
        """Obtém a versão do Python"""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def _get_architecture(self) -> str:
        """Detecta a arquitetura do sistema"""
        arch = platform.machine().lower()
        if arch in ["x86_64", "amd64"]:
            return "x64"
        elif arch in ["arm64", "aarch64"]:
            return "arm64"
        else:
            return arch

    def _check_git(self) -> bool:
        """Verifica se Git está disponível"""
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_vscode(self) -> bool:
        """Verifica se VS Code está disponível"""
        try:
            subprocess.run(
                ["code", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
