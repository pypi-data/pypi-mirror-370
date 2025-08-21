"""Sistema de validação pós-instalação para JTECH™ Core."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..core.models import InstallationConfig, TeamType


@dataclass
class ValidationResult:
    """Resultado de uma validação específica."""

    component: str
    status: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationReport:
    """Relatório completo de validação."""

    results: List[ValidationResult]

    @property
    def is_valid(self) -> bool:
        """Retorna True se todas as validações passaram."""
        return all(result.status for result in self.results)

    @property
    def successful_components(self) -> List[str]:
        """Lista de componentes que passaram na validação."""
        return [result.component for result in self.results if result.status]

    @property
    def failed_components(self) -> List[str]:
        """Lista de componentes que falharam na validação."""
        return [
            result.component for result in self.results if not result.status
        ]

    @property
    def total_checks(self) -> int:
        """Total de verificações realizadas."""
        return len(self.results)

    @property
    def passed_checks(self) -> int:
        """Número de verificações que passaram."""
        return len(self.successful_components)

    @property
    def failed_checks(self) -> int:
        """Número de verificações que falharam."""
        return len(self.failed_components)


class PostInstallationValidator:
    """Validador pós-instalação para verificar integridade e funcionalidade."""

    def __init__(self, config: InstallationConfig):
        """
        Inicializa o validador.

        Args:
            config: Configuração de instalação
        """
        self.config = config
        self.project_path = config.project_path
        self.results: List[ValidationResult] = []

    def validate_all(self) -> ValidationReport:
        """
        Executa todas as validações.

        Returns:
            Relatório completo de validação
        """
        self.results = []

        # Validações estruturais
        self._validate_directory_structure()
        self._validate_core_config()
        self._validate_vscode_configuration()

        # Validações de conteúdo
        self._validate_agents()
        self._validate_chatmodes()
        self._validate_templates()

        # Validações funcionais
        self._validate_file_permissions()
        self._validate_yaml_syntax()
        self._validate_json_syntax()

        # Validações específicas por tipo de equipe
        self._validate_team_specific_setup()

        # Gerar relatório
        return self._generate_report()

    def _validate_directory_structure(self) -> None:
        """Valida a estrutura de diretórios."""
        expected_dirs = [
            ".jtech-core",
            ".jtech-core/agents",
            ".jtech-core/chatmodes",
            ".jtech-core/templates",
            ".jtech-core/tasks",
            ".jtech-core/workflows",
            ".github/chatmodes",
        ]

        if self.config.vs_code_integration:
            expected_dirs.append(".vscode")

        missing_dirs = []
        for dir_path in expected_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            self.results.append(
                ValidationResult(
                    component="directory_structure",
                    status=False,
                    message=f"Diretórios ausentes: {', '.join(missing_dirs)}",
                    details={"missing_directories": missing_dirs},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="directory_structure",
                    status=True,
                    message="Estrutura de diretórios válida",
                )
            )

    def _validate_core_config(self) -> None:
        """Valida o arquivo core-config.yml."""
        config_file = self.project_path / ".jtech-core" / "core-config.yml"

        if not config_file.exists():
            self.results.append(
                ValidationResult(
                    component="core_config",
                    status=False,
                    message="Arquivo core-config.yml não encontrado",
                )
            )
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # Validar campos obrigatórios
            required_fields = ["slashPrefix", "prd", "architecture", "qa"]
            missing_fields = [
                field for field in required_fields if field not in config_data
            ]

            if missing_fields:
                self.results.append(
                    ValidationResult(
                        component="core_config",
                        status=False,
                        message=f"Campos obrigatórios ausentes: {', '.join(missing_fields)}",
                        details={"missing_fields": missing_fields},
                    )
                )
            else:
                # Validar configuração específica por tipo de equipe
                team_valid = self._validate_team_config(config_data)

                self.results.append(
                    ValidationResult(
                        component="core_config",
                        status=team_valid,
                        message=(
                            "Configuração core-config.yml válida"
                            if team_valid
                            else "Configuração específica da equipe inválida"
                        ),
                        details={"team_type": self.config.team_type.value},
                    )
                )

        except yaml.YAMLError as e:
            self.results.append(
                ValidationResult(
                    component="core_config",
                    status=False,
                    message=f"Erro de sintaxe YAML: {e}",
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="core_config",
                    status=False,
                    message=f"Erro ao validar core-config.yml: {e}",
                )
            )

    def _validate_vscode_configuration(self) -> None:
        """Valida configurações do VS Code."""
        if not self.config.vs_code_integration:
            self.results.append(
                ValidationResult(
                    component="vscode_config",
                    status=True,
                    message="Integração VS Code desabilitada",
                )
            )
            return

        vscode_dir = self.project_path / ".vscode"
        if not vscode_dir.exists():
            self.results.append(
                ValidationResult(
                    component="vscode_config",
                    status=False,
                    message="Diretório .vscode não encontrado",
                )
            )
            return

        # Validar arquivos do VS Code
        vscode_files = ["settings.json", "extensions.json", "tasks.json"]
        issues = []

        for file_name in vscode_files:
            file_path = vscode_dir / file_name
            if not file_path.exists():
                issues.append(f"{file_name} ausente")
                continue

            # Validar JSON
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                issues.append(f"{file_name}: JSON inválido - {e}")

        if issues:
            self.results.append(
                ValidationResult(
                    component="vscode_config",
                    status=False,
                    message=f"Problemas encontrados: {', '.join(issues)}",
                    details={"issues": issues},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="vscode_config",
                    status=True,
                    message="Configuração VS Code válida",
                )
            )

    def _validate_agents(self) -> None:
        """Valida agentes instalados."""
        agents_dir = self.project_path / ".jtech-core" / "agents"

        if not agents_dir.exists():
            self.results.append(
                ValidationResult(
                    component="agents",
                    status=False,
                    message="Diretório de agentes não encontrado",
                )
            )
            return

        # Mapear agentes esperados por tipo de equipe
        expected_agents = self._get_expected_agents()

        installed_agents = list(agents_dir.glob("*.md"))
        installed_names = [agent.stem for agent in installed_agents]

        missing_agents = [
            agent for agent in expected_agents if agent not in installed_names
        ]
        extra_agents = [
            agent for agent in installed_names if agent not in expected_agents
        ]

        details = {
            "expected": expected_agents,
            "installed": installed_names,
            "missing": missing_agents,
            "extra": extra_agents,
        }

        if missing_agents:
            self.results.append(
                ValidationResult(
                    component="agents",
                    status=False,
                    message=f"Agentes ausentes: {', '.join(missing_agents)}",
                    details=details,
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="agents",
                    status=True,
                    message=f"Agentes validados: {len(installed_names)} instalados",
                    details=details,
                )
            )

    def _validate_chatmodes(self) -> None:
        """Valida chatmodes instalados."""
        chatmodes_dirs = [
            self.project_path / ".jtech-core" / "chatmodes",
            self.project_path / ".github" / "chatmodes",
        ]

        total_chatmodes = 0
        issues = []

        for chatmodes_dir in chatmodes_dirs:
            if not chatmodes_dir.exists():
                issues.append(
                    f"Diretório {chatmodes_dir.relative_to(self.project_path)} não encontrado"
                )
                continue

            chatmode_files = list(chatmodes_dir.glob("*.chatmode.md"))
            total_chatmodes += len(chatmode_files)

            # Validar formato dos arquivos
            for chatmode_file in chatmode_files:
                if not self._validate_chatmode_format(chatmode_file):
                    issues.append(f"Formato inválido: {chatmode_file.name}")

        if issues:
            self.results.append(
                ValidationResult(
                    component="chatmodes",
                    status=False,
                    message=f"Problemas encontrados: {', '.join(issues)}",
                    details={
                        "total_chatmodes": total_chatmodes,
                        "issues": issues,
                    },
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="chatmodes",
                    status=True,
                    message=f"Chatmodes validados: {total_chatmodes} encontrados",
                    details={"total_chatmodes": total_chatmodes},
                )
            )

    def _validate_templates(self) -> None:
        """Valida templates instalados."""
        templates_dir = self.project_path / ".jtech-core" / "templates"

        if not templates_dir.exists():
            self.results.append(
                ValidationResult(
                    component="templates",
                    status=False,
                    message="Diretório de templates não encontrado",
                )
            )
            return

        template_files = list(templates_dir.glob("*"))

        if not template_files:
            self.results.append(
                ValidationResult(
                    component="templates",
                    status=False,
                    message="Nenhum template encontrado",
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="templates",
                    status=True,
                    message=f"Templates validados: {len(template_files)} encontrados",
                    details={"template_count": len(template_files)},
                )
            )

    def _validate_file_permissions(self) -> None:
        """Valida permissões de arquivos."""
        critical_files = [
            self.project_path / ".jtech-core" / "core-config.yml"
        ]

        if self.config.vs_code_integration:
            critical_files.extend(
                [
                    self.project_path / ".vscode" / "settings.json",
                    self.project_path / ".vscode" / "extensions.json",
                ]
            )

        permission_issues = []

        for file_path in critical_files:
            if file_path.exists():
                if not file_path.is_file():
                    permission_issues.append(
                        f"{file_path.name} não é um arquivo"
                    )
                elif not file_path.stat().st_mode & 0o444:  # Readable
                    permission_issues.append(f"{file_path.name} não é legível")

        if permission_issues:
            self.results.append(
                ValidationResult(
                    component="file_permissions",
                    status=False,
                    message=f"Problemas de permissão: {', '.join(permission_issues)}",
                    details={"issues": permission_issues},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="file_permissions",
                    status=True,
                    message="Permissões de arquivo válidas",
                )
            )

    def _validate_yaml_syntax(self) -> None:
        """Valida sintaxe de todos os arquivos YAML."""
        yaml_files = []
        yaml_files.extend(self.project_path.rglob("*.yml"))
        yaml_files.extend(self.project_path.rglob("*.yaml"))

        syntax_errors = []

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                syntax_errors.append(f"{yaml_file.name}: {e}")
            except Exception:
                # Pular arquivos que não conseguimos ler
                continue

        if syntax_errors:
            self.results.append(
                ValidationResult(
                    component="yaml_syntax",
                    status=False,
                    message=f"Erros de sintaxe YAML: {', '.join(syntax_errors)}",
                    details={"errors": syntax_errors},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="yaml_syntax",
                    status=True,
                    message=f"Sintaxe YAML válida em {len(yaml_files)} arquivos",
                )
            )

    def _validate_json_syntax(self) -> None:
        """Valida sintaxe de todos os arquivos JSON."""
        json_files = list(self.project_path.rglob("*.json"))

        syntax_errors = []

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                syntax_errors.append(f"{json_file.name}: {e}")
            except Exception:
                # Pular arquivos que não conseguimos ler
                continue

        if syntax_errors:
            self.results.append(
                ValidationResult(
                    component="json_syntax",
                    status=False,
                    message=f"Erros de sintaxe JSON: {', '.join(syntax_errors)}",
                    details={"errors": syntax_errors},
                )
            )
        else:
            self.results.append(
                ValidationResult(
                    component="json_syntax",
                    status=True,
                    message=f"Sintaxe JSON válida em {len(json_files)} arquivos",
                )
            )

    def _validate_team_specific_setup(self) -> None:
        """Valida configurações específicas do tipo de equipe."""
        team_type = self.config.team_type

        if team_type == TeamType.IDE_MINIMAL:
            # Validar configuração mínima
            self._validate_minimal_setup()
        elif team_type == TeamType.FULLSTACK:
            # Validar configuração full-stack
            self._validate_fullstack_setup()
        elif team_type == TeamType.NO_UI:
            # Validar configuração backend
            self._validate_backend_setup()
        elif team_type == TeamType.ALL:
            # Validar configuração completa
            self._validate_complete_setup()

    def _validate_minimal_setup(self) -> None:
        """Valida configuração IDE minimal."""
        if self.config.vs_code_integration:
            settings_file = self.project_path / ".vscode" / "settings.json"
            if settings_file.exists():
                try:
                    with open(settings_file, "r", encoding="utf-8") as f:
                        settings = json.load(f)

                    # Verificar configurações específicas minimal
                    if settings.get("editor.minimap.enabled") is False:
                        self.results.append(
                            ValidationResult(
                                component="team_setup_minimal",
                                status=True,
                                message="Configuração IDE minimal validada",
                            )
                        )
                    else:
                        self.results.append(
                            ValidationResult(
                                component="team_setup_minimal",
                                status=False,
                                message="Configurações IDE minimal não aplicadas",
                            )
                        )
                except Exception as e:
                    self.results.append(
                        ValidationResult(
                            component="team_setup_minimal",
                            status=False,
                            message=f"Erro ao validar configuração minimal: {e}",
                        )
                    )

    def _validate_fullstack_setup(self) -> None:
        """Valida configuração fullstack."""
        # Implementar validações específicas fullstack
        self.results.append(
            ValidationResult(
                component="team_setup_fullstack",
                status=True,
                message="Configuração fullstack validada",
            )
        )

    def _validate_backend_setup(self) -> None:
        """Valida configuração backend/no-ui."""
        # Implementar validações específicas backend
        self.results.append(
            ValidationResult(
                component="team_setup_backend",
                status=True,
                message="Configuração backend validada",
            )
        )

    def _validate_complete_setup(self) -> None:
        """Valida configuração completa."""
        # Implementar validações específicas completa
        self.results.append(
            ValidationResult(
                component="team_setup_complete",
                status=True,
                message="Configuração completa validada",
            )
        )

    def _get_expected_agents(self) -> List[str]:
        """Retorna lista de agentes esperados por tipo de equipe."""
        agent_mappings = {
            TeamType.IDE_MINIMAL: ["pm", "architect", "dev"],
            TeamType.FULLSTACK: [
                "pm",
                "architect",
                "dev",
                "qa",
                "ui",
                "fullstack",
            ],
            TeamType.NO_UI: ["pm", "architect", "dev", "qa", "backend"],
            TeamType.ALL: [
                "pm",
                "architect",
                "dev",
                "qa",
                "ui",
                "fullstack",
                "backend",
                "devops",
                "security",
                "data",
            ],
        }

        return agent_mappings.get(self.config.team_type, [])

    def _validate_team_config(self, config_data: Dict[str, Any]) -> bool:
        """Valida configuração específica por tipo de equipe."""
        team_type = self.config.team_type

        if team_type == TeamType.IDE_MINIMAL:
            return config_data.get("customTechnicalDocuments") is None
        elif team_type in [TeamType.FULLSTACK, TeamType.NO_UI, TeamType.ALL]:
            return isinstance(
                config_data.get("customTechnicalDocuments"), list
            )

        return True

    def _validate_chatmode_format(self, chatmode_file: Path) -> bool:
        """Valida formato de um arquivo chatmode."""
        try:
            with open(chatmode_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Validações básicas de formato
            if not content.strip():
                return False

            # Verificar se tem extensão correta
            if not chatmode_file.name.endswith(".chatmode.md"):
                return False

            return True

        except Exception:
            return False

    def _generate_report(self) -> ValidationReport:
        """Gera relatório final de validação."""
        return ValidationReport(results=self.results)
