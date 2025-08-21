"""
Prerequisites checker for JTECH™ Installer
"""

from packaging import version

from jtech_installer.core.exceptions import SystemRequirementError
from jtech_installer.core.models import SystemInfo


class PrerequisitesChecker:
    """Verifica pré-requisitos do sistema"""

    MINIMUM_PYTHON_VERSION = "3.12.0"

    def check_all(self, system_info: SystemInfo) -> None:
        """Verifica todos os pré-requisitos"""
        self._check_python_version(system_info.python_version)
        self._check_git(system_info.git_available)
        # VS Code é opcional

    def _check_python_version(self, python_version: str) -> None:
        """Verifica se a versão do Python é adequada"""
        if version.parse(python_version) < version.parse(
            self.MINIMUM_PYTHON_VERSION
        ):
            raise SystemRequirementError(
                f"Python {self.MINIMUM_PYTHON_VERSION}+ é obrigatório. "
                f"Versão atual: {python_version}"
            )

    def _check_git(self, git_available: bool) -> None:
        """Verifica se Git está disponível"""
        if not git_available:
            raise SystemRequirementError(
                "Git é obrigatório mas não foi encontrado. "
                "Por favor, instale Git antes de continuar."
            )
