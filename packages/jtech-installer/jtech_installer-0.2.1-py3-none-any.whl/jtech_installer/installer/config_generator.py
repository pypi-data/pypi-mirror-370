"""Gerador de configuração core-config.yml personalizada."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..core.models import InstallationConfig, TeamType


class ConfigGenerator:
    """Gera configuração core-config.yml personalizada baseada no tipo de equipe."""

    def __init__(self, base_template_path: Optional[Path] = None):
        """
        Inicializa o gerador de configuração.

        Args:
            base_template_path: Caminho para template base do core-config.yml
        """
        self.base_template_path = base_template_path

    def generate_config(
        self, config: InstallationConfig, target_path: Path
    ) -> Dict[str, Any]:
        """
        Gera configuração personalizada baseada no tipo de equipe.

        Args:
            config: Configuração de instalação
            target_path: Caminho do projeto de destino

        Returns:
            Dicionário com configuração gerada
        """
        # Configuração base comum a todos os tipos
        base_config = self._get_base_config()

        # Personalizações por tipo de equipe
        team_config = self._get_team_specific_config(config.team_type)

        # Configurações específicas do projeto
        project_config = self._get_project_specific_config(target_path)

        # Merge das configurações
        final_config = {**base_config, **team_config, **project_config}

        return final_config

    def _get_base_config(self) -> Dict[str, Any]:
        """Retorna configuração base comum a todos os tipos."""
        return {
            "markdownExploder": True,
            "slashPrefix": "jtech",
            "qa": {"qaLocation": "docs/qa"},
            "prd": {
                "prdFile": "docs/prd.md",
                "prdVersion": "v2",
                "prdSharded": True,
                "prdShardedLocation": "docs/prd",
                "epicFilePattern": "epic-{n}*.md",
            },
            "architecture": {
                "architectureFile": "docs/architecture.md",
                "architectureVersion": "v2",
                "architectureSharded": True,
                "architectureShardedLocation": "docs/architecture",
            },
            "devDebugLog": ".ai/debug-log.md",
            "devStoryLocation": "docs/stories",
        }

    def _get_team_specific_config(self, team_type: TeamType) -> Dict[str, Any]:
        """Retorna configurações específicas por tipo de equipe."""
        configs = {
            TeamType.ALL: {
                "customTechnicalDocuments": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/source-tree.md",
                    "docs/architecture/deployment.md",
                    "docs/architecture/security.md",
                ],
                "devLoadAlwaysFiles": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/source-tree.md",
                    "docs/architecture/deployment.md",
                ],
            },
            TeamType.FULLSTACK: {
                "customTechnicalDocuments": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/source-tree.md",
                    "docs/architecture/deployment.md",
                ],
                "devLoadAlwaysFiles": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/source-tree.md",
                ],
            },
            TeamType.NO_UI: {
                "customTechnicalDocuments": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/api-design.md",
                ],
                "devLoadAlwaysFiles": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                    "docs/architecture/api-design.md",
                ],
            },
            TeamType.IDE_MINIMAL: {
                "customTechnicalDocuments": None,
                "devLoadAlwaysFiles": [
                    "docs/architecture/coding-standards.md",
                    "docs/architecture/tech-stack.md",
                ],
            },
        }

        return configs.get(team_type, {})

    def _get_project_specific_config(
        self, target_path: Path
    ) -> Dict[str, Any]:
        """Retorna configurações específicas do projeto."""
        config = {}

        # Detecta se é projeto existente (brownfield)
        if self._is_brownfield_project(target_path):
            config["projectType"] = "brownfield"

            # Ajusta caminhos para projetos existentes
            if (target_path / "documentation").exists():
                config["prd"]["prdFile"] = "documentation/prd.md"
                config["architecture"][
                    "architectureFile"
                ] = "documentation/architecture.md"
                config["qa"]["qaLocation"] = "documentation/qa"

        else:
            config["projectType"] = "greenfield"

        return config

    def _is_brownfield_project(self, target_path: Path) -> bool:
        """Verifica se é um projeto existente (brownfield)."""
        indicators = [
            target_path / "src",
            target_path / "lib",
            target_path / "app",
            target_path / "package.json",
            target_path / "requirements.txt",
            target_path / "Cargo.toml",
            target_path / "go.mod",
        ]

        return any(indicator.exists() for indicator in indicators)

    def write_config(
        self, config_dict: Dict[str, Any], target_path: Path
    ) -> Path:
        """
        Escreve a configuração no arquivo core-config.yml.

        Args:
            config_dict: Dicionário com configuração
            target_path: Caminho do projeto de destino

        Returns:
            Caminho do arquivo gerado
        """
        config_file = target_path / ".jtech-core" / "core-config.yml"

        # Garante que o diretório existe
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Escreve o arquivo YAML
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(
                config_dict,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        return config_file

    def validate_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        Valida a configuração gerada.

        Args:
            config_dict: Dicionário com configuração

        Returns:
            True se válida, False caso contrário
        """
        required_keys = ["prd", "architecture", "qa", "slashPrefix"]

        for key in required_keys:
            if key not in config_dict:
                return False

        # Valida estrutura do PRD
        prd_config = config_dict.get("prd", {})
        if not all(k in prd_config for k in ["prdFile", "prdVersion"]):
            return False

        # Valida estrutura da arquitetura
        arch_config = config_dict.get("architecture", {})
        if not all(
            k in arch_config
            for k in ["architectureFile", "architectureVersion"]
        ):
            return False

        return True
