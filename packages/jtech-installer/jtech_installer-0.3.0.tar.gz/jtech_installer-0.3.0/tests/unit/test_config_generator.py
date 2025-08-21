"""Testes para o gerador de configuração."""

import tempfile
from pathlib import Path

import pytest
import yaml

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.config_generator import ConfigGenerator


class TestConfigGenerator:
    """Testes para ConfigGenerator."""

    @pytest.fixture
    def generator(self):
        """Fixture para ConfigGenerator."""
        return ConfigGenerator()

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
        """Fixture para configuração full-stack."""
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

    def test_generate_config_ide_minimal(self, generator, minimal_config):
        """Testa geração de configuração para equipe IDE minimal."""
        config_dict = generator.generate_config(
            minimal_config, minimal_config.project_path
        )

        # Verifica estrutura base
        assert "markdownExploder" in config_dict
        assert "slashPrefix" in config_dict
        assert "prd" in config_dict
        assert "architecture" in config_dict
        assert "qa" in config_dict

        # Verifica configuração específica IDE minimal
        assert config_dict["customTechnicalDocuments"] is None
        assert len(config_dict["devLoadAlwaysFiles"]) == 2
        assert (
            "docs/architecture/coding-standards.md"
            in config_dict["devLoadAlwaysFiles"]
        )
        assert (
            "docs/architecture/tech-stack.md"
            in config_dict["devLoadAlwaysFiles"]
        )

    def test_generate_config_fullstack(self, generator, fullstack_config):
        """Testa geração de configuração para equipe full-stack."""
        config_dict = generator.generate_config(
            fullstack_config, fullstack_config.project_path
        )

        # Verifica configuração específica full-stack
        assert config_dict["customTechnicalDocuments"] is not None
        assert len(config_dict["customTechnicalDocuments"]) == 4
        assert (
            "docs/architecture/deployment.md"
            in config_dict["customTechnicalDocuments"]
        )

        assert len(config_dict["devLoadAlwaysFiles"]) == 3

    def test_brownfield_detection(self, generator):
        """Testa detecção de projeto brownfield."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Projeto greenfield (vazio)
            assert not generator._is_brownfield_project(project_path)

            # Projeto brownfield (com src/)
            (project_path / "src").mkdir()
            assert generator._is_brownfield_project(project_path)

    def test_write_config(self, generator, minimal_config):
        """Testa escrita do arquivo de configuração."""
        config_dict = generator.generate_config(
            minimal_config, minimal_config.project_path
        )

        config_file = generator.write_config(
            config_dict, minimal_config.project_path
        )

        # Verifica se arquivo foi criado
        assert config_file.exists()
        assert config_file.name == "core-config.yml"

        # Verifica conteúdo do arquivo
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_config = yaml.safe_load(f)

        assert loaded_config["slashPrefix"] == "jtech"
        assert loaded_config["markdownExploder"] is True

    def test_validate_config_valid(self, generator, minimal_config):
        """Testa validação de configuração válida."""
        config_dict = generator.generate_config(
            minimal_config, minimal_config.project_path
        )

        assert generator.validate_config(config_dict) is True

    def test_validate_config_invalid(self, generator):
        """Testa validação de configuração inválida."""
        invalid_config = {
            "markdownExploder": True
            # Faltando campos obrigatórios
        }

        assert generator.validate_config(invalid_config) is False

    def test_team_all_config(self, generator):
        """Testa configuração para equipe completa."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = InstallationConfig(
                project_path=Path(temp_dir),
                install_type=InstallationType.GREENFIELD,
                team_type=TeamType.ALL,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )

            config_dict = generator.generate_config(
                config, config.project_path
            )

            # Verifica configuração completa
            assert len(config_dict["customTechnicalDocuments"]) == 5
            assert len(config_dict["devLoadAlwaysFiles"]) == 4
            assert (
                "docs/architecture/security.md"
                in config_dict["customTechnicalDocuments"]
            )

    def test_no_ui_team_config(self, generator):
        """Testa configuração para equipe sem UI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = InstallationConfig(
                project_path=Path(temp_dir),
                install_type=InstallationType.GREENFIELD,
                team_type=TeamType.NO_UI,
                vs_code_integration=True,
                custom_config={},
                framework_source_path=None,
            )

            config_dict = generator.generate_config(
                config, config.project_path
            )

            # Verifica configuração específica no-ui
            assert (
                "docs/architecture/api-design.md"
                in config_dict["customTechnicalDocuments"]
            )
            assert (
                "docs/architecture/api-design.md"
                in config_dict["devLoadAlwaysFiles"]
            )
            assert len(config_dict["customTechnicalDocuments"]) == 3

    def test_project_type_detection(self, generator):
        """Testa detecção do tipo de projeto."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Greenfield
            greenfield_config = generator._get_project_specific_config(
                project_path
            )
            assert greenfield_config["projectType"] == "greenfield"

            # Brownfield
            (project_path / "package.json").touch()
            brownfield_config = generator._get_project_specific_config(
                project_path
            )
            assert brownfield_config["projectType"] == "brownfield"
