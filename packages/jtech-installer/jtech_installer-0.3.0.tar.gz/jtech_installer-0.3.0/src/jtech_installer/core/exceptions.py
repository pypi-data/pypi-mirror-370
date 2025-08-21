"""
Custom exceptions for JTECH™ Installer
"""


class JTechInstallerException(Exception):
    """Base exception for JTECH™ Installer"""


class SystemRequirementError(JTechInstallerException):
    """Erro de pré-requisitos do sistema"""


class PermissionError(JTechInstallerException):
    """Erro de permissões"""


class FileOperationError(JTechInstallerException):
    """Erro em operações de arquivo"""


class ConfigurationError(JTechInstallerException):
    """Erro de configuração"""


class ValidationError(JTechInstallerException):
    """Erro de validação"""


class RollbackError(JTechInstallerException):
    """Erro durante rollback"""
