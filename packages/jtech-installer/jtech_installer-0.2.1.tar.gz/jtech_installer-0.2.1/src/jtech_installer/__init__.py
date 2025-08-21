"""
JTECH™ Core Framework Installer

Instalador de ambiente automatizado para o JTECH™ Core Framework.
Fornece configuração rápida e consistente de ambientes de desenvolvimento.
"""

__version__ = "0.1.0"
__author__ = "JTECH™ Core Team"
__email__ = "team@jtech.dev"

from jtech_installer.core.engine import InstallerEngine
from jtech_installer.core.exceptions import JTechInstallerException

__all__ = [
    "InstallerEngine",
    "JTechInstallerException",
    "__version__",
]
