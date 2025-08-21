"""
YAML configuration generator for JTECH™ Installer
"""

from jtech_installer.core.models import InstallationConfig


class ConfigGenerator:
    """Gerador de configurações YAML"""

    def __init__(self, config: InstallationConfig):
        self.config = config

    def generate_core_config(self) -> str:
        """Gera o core-config.yml"""
        # TODO: Implementar geração de configuração
        return "# TODO: Implementar geração de core-config.yml"
