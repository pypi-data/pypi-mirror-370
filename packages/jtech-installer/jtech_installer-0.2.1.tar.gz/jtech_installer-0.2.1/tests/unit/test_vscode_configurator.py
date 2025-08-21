"""Testes para o configurador do VS Code."""

import json
import tempfile
from pathlib import Path

import pytest

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.vscode_configurator import VSCodeConfigurator


class TestVSCodeConfigurator:
    """Testes para VSCodeConfigurator."""

    @pytest.fixture
    def minimal_config(self):
        """Fixture para configuração minimal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = InstallationConfig(
                project_path=Path(temp_dir),
                install_type=InstallationType.GREENFIELD,
                team_type=TeamType.IDE_MINIMAL,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )
            yield config

    @pytest.fixture
    def fullstack_config(self):
        """Fixture para configuração fullstack."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = InstallationConfig(
                project_path=Path(temp_dir),
                install_type=InstallationType.GREENFIELD,
                team_type=TeamType.FULLSTACK,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )
            yield config

    def test_init(self, minimal_config):
        """Testa inicialização do configurador."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=True)

        assert configurator.config == minimal_config
        assert configurator.dry_run is True
        assert (
            configurator.vscode_dir == minimal_config.project_path / ".vscode"
        )

    def test_configure_settings_ide_minimal(self, minimal_config):
        """Testa configuração de settings para IDE minimal."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        result = configurator._configure_settings()
        assert result is True

        # Verificar se arquivo foi criado
        settings_file = (
            minimal_config.project_path / ".vscode" / "settings.json"
        )
        assert settings_file.exists()

        # Verificar conteúdo
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Configurações base devem estar presentes
        assert "github.copilot.enable" in settings
        assert "markdown.preview.scrollEditorWithPreview" in settings
        assert "jtech.framework.autoload" in settings

        # Configurações específicas IDE minimal
        assert settings.get("editor.minimap.enabled") is False
        assert settings.get("editor.wordWrap") == "on"

    def test_configure_settings_fullstack(self, fullstack_config):
        """Testa configuração de settings para fullstack."""
        configurator = VSCodeConfigurator(fullstack_config, dry_run=False)

        result = configurator._configure_settings()
        assert result is True

        settings_file = (
            fullstack_config.project_path / ".vscode" / "settings.json"
        )
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Configurações específicas fullstack
        assert "python.defaultInterpreterPath" in settings
        assert "emmet.includeLanguages" in settings
        assert (
            "javascript.preferences.includePackageJsonAutoImports" in settings
        )

    def test_configure_extensions_ide_minimal(self, minimal_config):
        """Testa configuração de extensões para IDE minimal."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        result = configurator._configure_extensions()
        assert result is True

        extensions_file = (
            minimal_config.project_path / ".vscode" / "extensions.json"
        )
        assert extensions_file.exists()

        with open(extensions_file, "r", encoding="utf-8") as f:
            extensions = json.load(f)

        recommendations = extensions["recommendations"]

        # Extensões base devem estar presentes
        assert "github.copilot" in recommendations
        assert "github.copilot-chat" in recommendations
        assert "yzhang.markdown-all-in-one" in recommendations

        # Extensões específicas IDE minimal
        assert "ms-python.python" in recommendations
        assert "ms-vscode.vscode-json" in recommendations

        # Não deve ter extensões complexas
        assert "ms-vscode.vscode-react-native" not in recommendations

    def test_configure_extensions_fullstack(self, fullstack_config):
        """Testa configuração de extensões para fullstack."""
        configurator = VSCodeConfigurator(fullstack_config, dry_run=False)

        result = configurator._configure_extensions()
        assert result is True

        extensions_file = (
            fullstack_config.project_path / ".vscode" / "extensions.json"
        )
        with open(extensions_file, "r", encoding="utf-8") as f:
            extensions = json.load(f)

        recommendations = extensions["recommendations"]

        # Extensões fullstack específicas
        assert "ms-vscode.vscode-react-native" in recommendations
        assert "formulahendry.auto-rename-tag" in recommendations
        assert "bradlc.vscode-tailwindcss" in recommendations

    def test_configure_tasks(self, minimal_config):
        """Testa configuração de tarefas."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        result = configurator._configure_tasks()
        assert result is True

        tasks_file = minimal_config.project_path / ".vscode" / "tasks.json"
        assert tasks_file.exists()

        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        assert "version" in tasks
        assert "tasks" in tasks
        assert len(tasks["tasks"]) >= 2  # Pelo menos as tarefas base

        # Verificar tarefas base
        task_labels = [task["label"] for task in tasks["tasks"]]
        assert "JTECH: Validate Framework" in task_labels
        assert "JTECH: Generate Documentation" in task_labels

    def test_configure_launch(self, minimal_config):
        """Testa configuração de launch."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        result = configurator._configure_launch()
        assert result is True

        launch_file = minimal_config.project_path / ".vscode" / "launch.json"
        assert launch_file.exists()

        with open(launch_file, "r", encoding="utf-8") as f:
            launch = json.load(f)

        assert "version" in launch
        assert "configurations" in launch
        assert len(launch["configurations"]) >= 1

    def test_configure_all_dry_run(self, minimal_config):
        """Testa configuração completa em modo dry-run."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=True)

        results = configurator.configure_all()

        # Deve retornar status de todas as configurações
        expected_keys = ["settings", "extensions", "tasks", "launch"]
        assert all(key in results for key in expected_keys)

        # Arquivos não devem ter sido criados em dry-run
        vscode_dir = minimal_config.project_path / ".vscode"
        assert not vscode_dir.exists()

    def test_configure_all_real(self, minimal_config):
        """Testa configuração completa real."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        results = configurator.configure_all()

        # Todas as configurações devem ter sucesso
        assert all(results.values())

        # Diretório e arquivos devem existir
        vscode_dir = minimal_config.project_path / ".vscode"
        assert vscode_dir.exists()
        assert (vscode_dir / "settings.json").exists()
        assert (vscode_dir / "extensions.json").exists()
        assert (vscode_dir / "tasks.json").exists()
        assert (vscode_dir / "launch.json").exists()

    def test_merge_existing_settings(self, minimal_config):
        """Testa merge com configurações existentes."""
        vscode_dir = minimal_config.project_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        settings_file = vscode_dir / "settings.json"

        # Criar configurações existentes
        existing_settings = {
            "editor.fontSize": 14,
            "workbench.colorTheme": "Dark+ (default dark)",
            "github.copilot.enable": {"*": False},  # Será sobrescrito
        }

        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(existing_settings, f, indent=2)

        configurator = VSCodeConfigurator(minimal_config, dry_run=False)
        result = configurator._configure_settings()
        assert result is True

        # Verificar merge
        with open(settings_file, "r", encoding="utf-8") as f:
            merged_settings = json.load(f)

        # Configurações existentes preservadas
        assert merged_settings["editor.fontSize"] == 14
        assert (
            merged_settings["workbench.colorTheme"] == "Dark+ (default dark)"
        )

        # Nossas configurações aplicadas (sobrescrevendo conflitos)
        assert merged_settings["github.copilot.enable"]["*"] is True
        assert "jtech.framework.autoload" in merged_settings

    def test_validate_configuration(self, minimal_config):
        """Testa validação de configurações."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Configurar primeiro
        configurator.configure_all()

        # Validar
        validation_results = configurator.validate_configuration()

        # Todos os arquivos devem ser válidos
        assert validation_results["settings.json"] is True
        assert validation_results["extensions.json"] is True
        assert validation_results["tasks.json"] is True
        assert validation_results["launch.json"] is True

    def test_team_specific_configurations(self):
        """Testa configurações específicas por tipo de equipe."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Teste NO_UI
            no_ui_path = Path(temp_dir) / "no_ui"
            no_ui_path.mkdir(
                parents=True, exist_ok=True
            )  # Criar diretório pai

            no_ui_config = InstallationConfig(
                project_path=no_ui_path,
                install_type=InstallationType.GREENFIELD,
                team_type=TeamType.NO_UI,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )

            configurator = VSCodeConfigurator(no_ui_config, dry_run=False)
            configurator.configure_all()

            # Verificar extensões específicas NO_UI
            extensions_file = (
                no_ui_config.project_path / ".vscode" / "extensions.json"
            )
            with open(extensions_file, "r", encoding="utf-8") as f:
                extensions = json.load(f)

            recommendations = extensions["recommendations"]
            assert "humao.rest-client" in recommendations
            assert "mongodb.mongodb-vscode" in recommendations

    def test_error_handling_corrupted_settings(self, minimal_config):
        """Testa tratamento de settings.json corrompido."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Criar diretório .vscode
        vscode_dir = minimal_config.project_path / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)

        # Criar arquivo settings.json corrompido
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text("{ invalid json")

        # Configurar deve funcionar (ignorando arquivo corrompido)
        result = configurator._configure_settings()
        assert result is True

        # Verificar que arquivo foi reescrito corretamente
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
        assert "github.copilot.chat.enable" in settings

    def test_error_handling_permission_denied(self, minimal_config):
        """Testa tratamento de erro de permissão."""
        from unittest.mock import mock_open, patch

        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Simular erro de permissão
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")

            result = configurator._configure_settings()
            assert result is False

    def test_get_team_specific_settings_all_teams(self):
        """Testa configurações específicas para todos os tipos de equipe."""
        teams_to_test = [
            TeamType.IDE_MINIMAL,
            TeamType.FULLSTACK,
            TeamType.NO_UI,
            TeamType.ALL,
        ]

        for team_type in teams_to_test:
            with tempfile.TemporaryDirectory() as temp_dir:
                config = InstallationConfig(
                    project_path=Path(temp_dir),
                    install_type=InstallationType.GREENFIELD,
                    team_type=team_type,
                    vs_code_integration=True,
                    custom_config={},
                    framework_source_path=None,
                )

                configurator = VSCodeConfigurator(config, dry_run=True)
                team_settings = configurator._get_team_specific_settings()

                # Cada tipo de equipe deve ter configurações específicas
                assert isinstance(team_settings, dict)
                assert len(team_settings) > 0

    def test_get_team_specific_extensions_all_teams(self):
        """Testa extensões específicas para todos os tipos de equipe."""
        teams_to_test = [
            TeamType.IDE_MINIMAL,
            TeamType.FULLSTACK,
            TeamType.NO_UI,
            TeamType.ALL,
        ]

        for team_type in teams_to_test:
            with tempfile.TemporaryDirectory() as temp_dir:
                config = InstallationConfig(
                    project_path=Path(temp_dir),
                    install_type=InstallationType.GREENFIELD,
                    team_type=team_type,
                    vs_code_integration=True,
                    custom_config={},
                    framework_source_path=None,
                )

                configurator = VSCodeConfigurator(config, dry_run=True)
                team_extensions = configurator._get_team_specific_extensions()

                # Cada tipo de equipe deve ter extensões específicas
                assert isinstance(team_extensions, list)
                assert len(team_extensions) > 0

    def test_configure_extensions_error_handling(self, minimal_config):
        """Testa tratamento de erro ao configurar extensões."""
        from unittest.mock import mock_open, patch

        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Simular erro de I/O
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Disk full")

            result = configurator._configure_extensions()
            assert result is False

    def test_configure_tasks_error_handling(self, minimal_config):
        """Testa tratamento de erro ao configurar tasks."""
        from unittest.mock import mock_open, patch

        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Simular erro de I/O
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Write error")

            result = configurator._configure_tasks()
            assert result is False

    def test_configure_launch_error_handling(self, minimal_config):
        """Testa tratamento de erro ao configurar launch."""
        from unittest.mock import mock_open, patch

        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Simular erro de I/O
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Write error")

            result = configurator._configure_launch()
            assert result is False

    def test_validate_configuration_missing_files(self, minimal_config):
        """Testa validação com arquivos faltando."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Criar apenas diretório .vscode sem arquivos
        vscode_dir = minimal_config.project_path / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)

        validation = configurator.validate_configuration()

        # Todos devem falhar pois não existem arquivos
        assert validation["settings.json"] is False
        assert validation["extensions.json"] is False
        assert validation["tasks.json"] is False
        assert validation["launch.json"] is False

    def test_validate_configuration_invalid_json(self, minimal_config):
        """Testa validação com JSON inválido."""
        configurator = VSCodeConfigurator(minimal_config, dry_run=False)

        # Criar diretório .vscode
        vscode_dir = minimal_config.project_path / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)

        # Criar arquivo com JSON inválido
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text("{ invalid json")

        validation = configurator.validate_configuration()

        # settings.json deve falhar por JSON inválido
        assert validation["settings.json"] is False

    def test_integration_brownfield_mode(self):
        """Testa integração em modo brownfield."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Criar estrutura existente
            (project_path / "src").mkdir()
            (project_path / "package.json").write_text('{"name": "existing"}')

            config = InstallationConfig(
                project_path=project_path,
                install_type=InstallationType.BROWNFIELD,
                team_type=TeamType.FULLSTACK,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )

            configurator = VSCodeConfigurator(config, dry_run=False)
            results = configurator.configure_all()

            # Todas as configurações devem ter sucesso
            assert all(results.values())

            # Verificar se arquivos foram criados
            vscode_dir = project_path / ".vscode"
            assert (vscode_dir / "settings.json").exists()
            assert (vscode_dir / "extensions.json").exists()
            assert (vscode_dir / "tasks.json").exists()
            assert (vscode_dir / "launch.json").exists()
