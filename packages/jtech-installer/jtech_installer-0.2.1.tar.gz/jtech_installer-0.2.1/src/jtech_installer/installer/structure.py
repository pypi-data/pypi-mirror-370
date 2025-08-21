"""
Criador de estrutura de diretórios para JTECH™ Installer
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from ..core.exceptions import JTechInstallerException
from ..core.models import InstallationConfig, InstallationType


class DirectoryPermission(Enum):
    """Permissões de diretório por sistema operacional."""

    STANDARD = 0o755
    RESTRICTED = 0o750
    PUBLIC = 0o755


@dataclass
class DirectoryInfo:
    """Informações sobre um diretório a ser criado."""

    path: str
    description: str
    required: bool = True
    permission: DirectoryPermission = DirectoryPermission.STANDARD
    create_gitkeep: bool = False


class StructureCreator:
    """Criador da estrutura completa de diretórios do JTECH™ Core Framework."""

    # Estrutura completa de diretórios do framework
    JTECH_STRUCTURE = [
        DirectoryInfo(
            ".jtech-core",
            "Diretório raiz do framework JTECH™ Core",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".jtech-core/agents",
            "Agentes especializados do framework",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".jtech-core/templates",
            "Templates para geração de documentos",
            required=True,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            ".jtech-core/workflows",
            "Workflows automatizados",
            required=True,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            ".jtech-core/tasks",
            "Tarefas e automações específicas",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".jtech-core/checklists",
            "Checklists para processos",
            required=True,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            ".jtech-core/utils",
            "Utilitários e ferramentas auxiliares",
            required=True,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            ".jtech-core/data",
            "Dados de configuração e cache",
            required=True,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            ".jtech-core/agents-teams",
            "Agentes específicos por tipo de equipe",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".jtech-core/chatmodes",
            "Definições de chatmodes para GitHub Copilot",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".jtech-core/backups",
            "Backups e pontos de rollback",
            required=True,
            permission=DirectoryPermission.RESTRICTED,
        ),
        DirectoryInfo(
            ".github",
            "Configurações específicas do GitHub",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".github/chatmodes",
            "ChatModes para integração com GitHub Copilot",
            required=True,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            ".vscode",
            "Configurações do Visual Studio Code",
            required=False,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            "docs",
            "Documentação do projeto",
            required=False,
            permission=DirectoryPermission.STANDARD,
        ),
        DirectoryInfo(
            "docs/architecture",
            "Documentação de arquitetura",
            required=False,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
        DirectoryInfo(
            "docs/qa",
            "Documentação de quality assurance",
            required=False,
            permission=DirectoryPermission.STANDARD,
            create_gitkeep=True,
        ),
    ]

    def __init__(self, config: InstallationConfig, dry_run: bool = False):
        """
        Inicializa o criador de estrutura.

        Args:
            config: Configuração da instalação
            dry_run: Se True, simula a criação sem criar os diretórios
        """
        self.config = config
        self.dry_run = dry_run
        self.created_directories: List[str] = []
        self.skipped_directories: List[str] = []
        self.failed_directories: List[str] = []

    def create_structure(self) -> Dict[str, Any]:
        """
        Cria toda a estrutura de diretórios necessária.

        Returns:
            Dicionário com resultados da criação
        """
        results = {
            "success": True,
            "created_directories": [],
            "skipped_directories": [],
            "failed_directories": [],
            "total_directories": len(self.JTECH_STRUCTURE),
            "errors": [],
        }

        try:
            for dir_info in self.JTECH_STRUCTURE:
                try:
                    result = self._create_directory(dir_info)

                    if result["created"]:
                        results["created_directories"].append(
                            {
                                "path": dir_info.path,
                                "description": dir_info.description,
                            }
                        )
                    elif result["existed"]:
                        results["skipped_directories"].append(
                            {"path": dir_info.path, "reason": "Already exists"}
                        )

                except Exception as e:
                    error_msg = (
                        f"Falha ao criar diretório {dir_info.path}: {e}"
                    )
                    results["errors"].append(error_msg)
                    results["failed_directories"].append(dir_info.path)

                    if dir_info.required:
                        results["success"] = False

            # Criar arquivos .gitkeep necessários
            if results["success"]:
                self._create_gitkeep_files(results)

            return results

        except Exception as e:
            raise JTechInstallerException(
                f"Erro crítico na criação da estrutura: {e}"
            )

    def _create_directory(self, dir_info: DirectoryInfo) -> Dict[str, bool]:
        """
        Cria um diretório individual.

        Args:
            dir_info: Informações do diretório

        Returns:
            Dicionário com resultado da operação
        """
        full_path = self.config.project_path / dir_info.path

        # Verificar se já existe
        if full_path.exists():
            if full_path.is_dir():
                return {"created": False, "existed": True}
            else:
                raise JTechInstallerException(
                    f"Conflito: {full_path} existe mas não é um diretório"
                )

        # Verificar modo brownfield
        if (
            self.config.install_type == InstallationType.BROWNFIELD
            and not self._should_create_in_brownfield(dir_info)
        ):
            return {"created": False, "existed": False, "skipped": True}

        # Criar diretório se não for dry run
        if not self.dry_run:
            full_path.mkdir(parents=True, exist_ok=True)

            # Aplicar permissões (apenas em sistemas Unix)
            if os.name != "nt":  # Não Windows
                os.chmod(full_path, dir_info.permission.value)

        return {"created": True, "existed": False}

    def _should_create_in_brownfield(self, dir_info: DirectoryInfo) -> bool:
        """
        Determina se um diretório deve ser criado em projeto brownfield.

        Args:
            dir_info: Informações do diretório

        Returns:
            True se deve criar o diretório
        """
        # Sempre criar diretórios essenciais do framework
        essential_dirs = [".jtech-core", ".github/chatmodes"]

        if any(
            dir_info.path.startswith(essential) for essential in essential_dirs
        ):
            return True

        # Não criar diretórios opcionais em brownfield se já existir estrutura
        optional_dirs = ["docs", ".vscode"]
        if any(
            dir_info.path.startswith(optional) for optional in optional_dirs
        ):
            return not self._has_existing_structure()

        return True

    def _has_existing_structure(self) -> bool:
        """
        Verifica se já existe uma estrutura de projeto.

        Returns:
            True se existe estrutura estabelecida
        """
        structure_indicators = [
            "src",
            "lib",
            "app",
            "components",
            "pages",
            "docs",
            "documentation",
            "README.md",
            "readme.md",
        ]

        for indicator in structure_indicators:
            if (self.config.project_path / indicator).exists():
                return True

        return False

    def _create_gitkeep_files(self, results: Dict[str, Any]) -> None:
        """
        Cria arquivos .gitkeep em diretórios vazios que precisam ser versionados.

        Args:
            results: Resultados da criação de diretórios
        """
        gitkeep_count = 0

        for dir_info in self.JTECH_STRUCTURE:
            if not dir_info.create_gitkeep:
                continue

            full_path = self.config.project_path / dir_info.path
            gitkeep_file = full_path / ".gitkeep"

            # Criar .gitkeep apenas se diretório estiver vazio
            if (
                full_path.exists()
                and not gitkeep_file.exists()
                and not any(full_path.iterdir())
            ):

                if not self.dry_run:
                    gitkeep_file.write_text(
                        "# This file ensures the directory is tracked by Git\n"
                        f"# Directory: {dir_info.description}\n"
                    )
                gitkeep_count += 1

        if gitkeep_count > 0:
            results["gitkeep_files_created"] = gitkeep_count

    def validate_structure(self) -> Dict[str, Any]:
        """
        Valida se a estrutura foi criada corretamente.

        Returns:
            Resultados da validação
        """
        validation_results = {
            "valid": True,
            "missing_required": [],
            "permission_issues": [],
            "total_validated": 0,
            "errors": [],
        }

        try:
            for dir_info in self.JTECH_STRUCTURE:
                validation_results["total_validated"] += 1
                full_path = self.config.project_path / dir_info.path

                # Verificar existência de diretórios obrigatórios
                if dir_info.required and not full_path.exists():
                    validation_results["missing_required"].append(
                        dir_info.path
                    )
                    validation_results["valid"] = False

                # Verificar permissões (apenas em sistemas Unix)
                if full_path.exists() and os.name != "nt":
                    try:
                        current_permissions = oct(full_path.stat().st_mode)[
                            -3:
                        ]
                        expected_permissions = oct(dir_info.permission.value)[
                            -3:
                        ]

                        if current_permissions != expected_permissions:
                            validation_results["permission_issues"].append(
                                {
                                    "path": dir_info.path,
                                    "expected": expected_permissions,
                                    "actual": current_permissions,
                                }
                            )
                    except Exception as e:
                        validation_results["errors"].append(
                            f"Erro ao verificar permissões de {dir_info.path}: {e}"
                        )

            return validation_results

        except Exception as e:
            raise JTechInstallerException(
                f"Erro durante validação da estrutura: {e}"
            )

    def get_structure_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre a estrutura que será criada.

        Returns:
            Informações detalhadas da estrutura
        """
        return {
            "total_directories": len(self.JTECH_STRUCTURE),
            "required_directories": len(
                [d for d in self.JTECH_STRUCTURE if d.required]
            ),
            "optional_directories": len(
                [d for d in self.JTECH_STRUCTURE if not d.required]
            ),
            "directories_with_gitkeep": len(
                [d for d in self.JTECH_STRUCTURE if d.create_gitkeep]
            ),
            "structure_details": [
                {
                    "path": dir_info.path,
                    "description": dir_info.description,
                    "required": dir_info.required,
                    "permission": dir_info.permission.name,
                    "create_gitkeep": dir_info.create_gitkeep,
                }
                for dir_info in self.JTECH_STRUCTURE
            ],
        }
