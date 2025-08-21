"""Configurador automático do VS Code para JTECH™ Core."""

import json
from typing import Any, Dict, List

from ..core.models import InstallationConfig, TeamType


class VSCodeConfigurator:
    """Configura automaticamente o VS Code para o framework JTECH™ Core."""

    def __init__(self, config: InstallationConfig, dry_run: bool = False):
        """
        Inicializa o configurador do VS Code.

        Args:
            config: Configuração de instalação
            dry_run: Se True, simula operações sem modificar arquivos
        """
        self.config = config
        self.dry_run = dry_run
        self.vscode_dir = config.project_path / ".vscode"

    def configure_all(self) -> Dict[str, bool]:
        """
        Executa todas as configurações do VS Code.

        Returns:
            Dict com status de cada configuração aplicada
        """
        results = {}

        # Criar diretório .vscode se não existir
        if not self.dry_run:
            self.vscode_dir.mkdir(parents=True, exist_ok=True)

        # Configurar settings.json
        results["settings"] = self._configure_settings()

        # Configurar extensões recomendadas
        results["extensions"] = self._configure_extensions()

        # Configurar tasks.json para framework
        results["tasks"] = self._configure_tasks()

        # Configurar launch.json se aplicável
        results["launch"] = self._configure_launch()

        return results

    def _configure_settings(self) -> bool:
        """
        Configura o arquivo settings.json do VS Code.

        Returns:
            True se configurado com sucesso
        """
        try:
            # Garantir que o diretório existe
            if not self.dry_run:
                self.vscode_dir.mkdir(parents=True, exist_ok=True)

            settings_file = self.vscode_dir / "settings.json"

            # Configurações base para JTECH™ Core
            base_settings = {
                # GitHub Copilot Chat
                "github.copilot.enable": {
                    "*": True,
                    "yaml": True,
                    "markdown": True,
                    "python": True,
                    "javascript": True,
                    "typescript": True,
                },
                "github.copilot.chat.enable": True,
                "github.copilot.chat.localeOverride": "pt-BR",
                # Markdown
                "markdown.preview.scrollEditorWithPreview": True,
                "markdown.preview.scrollPreviewWithEditor": True,
                "markdown.extension.toc.levels": "2..6",
                # Files
                "files.associations": {
                    "*.chatmode.md": "markdown",
                    "core-config.yml": "yaml",
                    "*.jtech.yml": "yaml",
                },
                # Explorer
                "explorer.fileNesting.enabled": True,
                "explorer.fileNesting.patterns": {
                    "*.md": "${capture}.*.md",
                    "core-config.yml": "core-*.yml,*.core.yml",
                },
                # Terminal
                "terminal.integrated.defaultProfile.linux": "bash",
                "terminal.integrated.cwd": "${workspaceFolder}",
                # JTECH™ Core específico
                "jtech.framework.autoload": True,
                "jtech.chatmodes.enabled": True,
                "jtech.agents.autodetect": True,
            }

            # Configurações específicas por tipo de equipe
            team_settings = self._get_team_specific_settings()
            base_settings.update(team_settings)

            # Merge com configurações existentes se o arquivo já existir
            if settings_file.exists() and not self.dry_run:
                with open(settings_file, "r", encoding="utf-8") as f:
                    try:
                        existing_settings = json.load(f)
                        # Merge inteligente - preserva configurações existentes
                        base_settings = {**existing_settings, **base_settings}
                    except json.JSONDecodeError:
                        # Se arquivo está corrompido, usar apenas nossas configurações
                        pass

            if not self.dry_run:
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(base_settings, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Erro ao configurar settings.json: {e}")
            return False

    def _configure_extensions(self) -> bool:
        """
        Configura extensões recomendadas no extensions.json.

        Returns:
            True se configurado com sucesso
        """
        try:
            # Garantir que o diretório existe
            if not self.dry_run:
                self.vscode_dir.mkdir(parents=True, exist_ok=True)

            extensions_file = self.vscode_dir / "extensions.json"

            # Extensões base para JTECH™ Core
            base_extensions = [
                # GitHub Copilot
                "github.copilot",
                "github.copilot-chat",
                # Markdown
                "yzhang.markdown-all-in-one",
                "davidanson.vscode-markdownlint",
                "bierner.markdown-mermaid",
                # YAML
                "redhat.vscode-yaml",
                # Git
                "eamodio.gitlens",
                # Formatação
                "esbenp.prettier-vscode",
                "ms-vscode.vscode-json",
                # Úteis gerais
                "ms-vscode.remote-containers",
                "ms-vscode-remote.remote-ssh",
            ]

            # Extensões específicas por tipo de equipe
            team_extensions = self._get_team_specific_extensions()
            all_extensions = base_extensions + team_extensions

            extensions_config = {
                "recommendations": all_extensions,
                "unwantedRecommendations": [
                    "ms-vscode.vscode-typescript-next",
                    "hookyqr.beautify",
                ],
            }

            # Merge com recomendações existentes
            if extensions_file.exists() and not self.dry_run:
                with open(extensions_file, "r", encoding="utf-8") as f:
                    try:
                        existing_config = json.load(f)
                        existing_recs = existing_config.get(
                            "recommendations", []
                        )
                        # Combinar sem duplicatas
                        combined_recs = list(
                            set(existing_recs + all_extensions)
                        )
                        extensions_config["recommendations"] = combined_recs
                    except json.JSONDecodeError:
                        pass

            if not self.dry_run:
                with open(extensions_file, "w", encoding="utf-8") as f:
                    json.dump(
                        extensions_config, f, indent=2, ensure_ascii=False
                    )

            return True

        except Exception as e:
            print(f"Erro ao configurar extensions.json: {e}")
            return False

    def _configure_tasks(self) -> bool:
        """
        Configura tarefas do VS Code no tasks.json.

        Returns:
            True se configurado com sucesso
        """
        try:
            # Garantir que o diretório existe
            if not self.dry_run:
                self.vscode_dir.mkdir(parents=True, exist_ok=True)

            tasks_file = self.vscode_dir / "tasks.json"

            tasks_config = {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "JTECH: Validate Framework",
                        "type": "shell",
                        "command": "echo",
                        "args": ["Framework validation would run here"],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "shared",
                        },
                        "problemMatcher": [],
                    },
                    {
                        "label": "JTECH: Generate Documentation",
                        "type": "shell",
                        "command": "echo",
                        "args": ["Documentation generation would run here"],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "shared",
                        },
                    },
                ],
            }

            # Adicionar tarefas específicas por tipo de equipe
            team_tasks = self._get_team_specific_tasks()
            tasks_config["tasks"].extend(team_tasks)

            if not self.dry_run:
                with open(tasks_file, "w", encoding="utf-8") as f:
                    json.dump(tasks_config, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Erro ao configurar tasks.json: {e}")
            return False

    def _configure_launch(self) -> bool:
        """
        Configura launch.json se aplicável.

        Returns:
            True se configurado com sucesso
        """
        try:
            # Garantir que o diretório existe
            if not self.dry_run:
                self.vscode_dir.mkdir(parents=True, exist_ok=True)

            # Por enquanto, apenas criar estrutura básica
            launch_file = self.vscode_dir / "launch.json"

            launch_config = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "JTECH Debug Mode",
                        "type": "node",
                        "request": "launch",
                        "program": "${workspaceFolder}/debug.js",
                        "console": "integratedTerminal",
                        "skipFiles": ["<node_internals>/**"],
                    }
                ],
            }

            # Só criar se não existir (não sobrescrever configurações de debug)
            if not launch_file.exists() and not self.dry_run:
                with open(launch_file, "w", encoding="utf-8") as f:
                    json.dump(launch_config, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Erro ao configurar launch.json: {e}")
            return False

    def _get_team_specific_settings(self) -> Dict[str, Any]:
        """Retorna configurações específicas por tipo de equipe."""
        team_settings = {
            TeamType.ALL: {
                "python.defaultInterpreterPath": "./venv/bin/python",
                "python.formatting.provider": "black",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": True,
                "javascript.preferences.includePackageJsonAutoImports": "auto",
                "typescript.preferences.includePackageJsonAutoImports": "auto",
            },
            TeamType.FULLSTACK: {
                "python.defaultInterpreterPath": "./venv/bin/python",
                "python.formatting.provider": "black",
                "javascript.preferences.includePackageJsonAutoImports": "auto",
                "typescript.preferences.includePackageJsonAutoImports": "auto",
                "emmet.includeLanguages": {
                    "javascript": "javascriptreact",
                    "typescript": "typescriptreact",
                },
            },
            TeamType.NO_UI: {
                "python.defaultInterpreterPath": "./venv/bin/python",
                "python.formatting.provider": "black",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": True,
                "rest-client.requestTimeout": 30000,
            },
            TeamType.IDE_MINIMAL: {
                "editor.minimap.enabled": False,
                "workbench.activityBar.visible": True,
                "editor.wordWrap": "on",
            },
        }

        return team_settings.get(self.config.team_type, {})

    def _get_team_specific_extensions(self) -> List[str]:
        """Retorna extensões específicas por tipo de equipe."""
        team_extensions = {
            TeamType.ALL: [
                "ms-python.python",
                "ms-python.black-formatter",
                "ms-python.pylint",
                "ms-vscode.vscode-typescript-next",
                "bradlc.vscode-tailwindcss",
                "ms-vscode.vscode-docker",
            ],
            TeamType.FULLSTACK: [
                "ms-python.python",
                "ms-python.black-formatter",
                "ms-vscode.vscode-typescript-next",
                "bradlc.vscode-tailwindcss",
                "ms-vscode.vscode-react-native",
                "formulahendry.auto-rename-tag",
            ],
            TeamType.NO_UI: [
                "ms-python.python",
                "ms-python.black-formatter",
                "ms-python.pylint",
                "humao.rest-client",
                "ms-vscode.vscode-docker",
                "mongodb.mongodb-vscode",
            ],
            TeamType.IDE_MINIMAL: [
                "ms-python.python",
                "ms-vscode.vscode-json",
            ],
        }

        return team_extensions.get(self.config.team_type, [])

    def _get_team_specific_tasks(self) -> List[Dict[str, Any]]:
        """Retorna tarefas específicas por tipo de equipe."""
        if self.config.team_type == TeamType.ALL:
            return [
                {
                    "label": "Run Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest"],
                    "group": "test",
                },
                {
                    "label": "Build Frontend",
                    "type": "shell",
                    "command": "npm",
                    "args": ["run", "build"],
                    "group": "build",
                },
            ]
        elif self.config.team_type == TeamType.FULLSTACK:
            return [
                {
                    "label": "Run Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest"],
                    "group": "test",
                },
                {
                    "label": "Start Dev Server",
                    "type": "shell",
                    "command": "npm",
                    "args": ["run", "dev"],
                    "group": "build",
                },
            ]
        elif self.config.team_type == TeamType.NO_UI:
            return [
                {
                    "label": "Run API Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest", "tests/api/"],
                    "group": "test",
                },
                {
                    "label": "Start API Server",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "uvicorn", "main:app", "--reload"],
                    "group": "build",
                },
            ]

        return []

    def validate_configuration(self) -> Dict[str, bool]:
        """
        Valida se as configurações foram aplicadas corretamente.

        Returns:
            Dict com status de validação de cada arquivo
        """
        validation_results = {}

        files_to_check = [
            ("settings.json", self.vscode_dir / "settings.json"),
            ("extensions.json", self.vscode_dir / "extensions.json"),
            ("tasks.json", self.vscode_dir / "tasks.json"),
            ("launch.json", self.vscode_dir / "launch.json"),
        ]

        for name, file_path in files_to_check:
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        json.load(f)  # Testa se é JSON válido
                    validation_results[name] = True
                except json.JSONDecodeError:
                    validation_results[name] = False
            else:
                validation_results[name] = False

        return validation_results
