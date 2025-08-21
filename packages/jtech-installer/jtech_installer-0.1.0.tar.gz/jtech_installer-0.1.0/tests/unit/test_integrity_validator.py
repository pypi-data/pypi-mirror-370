"""Testes para IntegrityValidator."""

import tempfile
from pathlib import Path

import pytest

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.validator.integrity import IntegrityCheckResult, IntegrityValidator


class TestIntegrityValidator:
    """Testes para IntegrityValidator."""

    @pytest.fixture
    def temp_config(self):
        """Fixture para configuração temporária."""
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

    def test_integrity_validator_initialization(self, temp_config):
        """Testa inicialização do IntegrityValidator."""
        validator = IntegrityValidator(temp_config)

        assert validator.config == temp_config
        assert validator.project_path == temp_config.project_path
        expected_jtech_path = temp_config.project_path / ".jtech-core"
        assert validator.jtech_core_path == expected_jtech_path

    def test_integrity_check_result_creation(self):
        """Testa criação de IntegrityCheckResult."""
        result = IntegrityCheckResult(
            component="test",
            is_valid=True,
            expected_checksum="abc123",
            actual_checksum="abc123",
        )

        assert result.component == "test"
        assert result.is_valid is True
        assert result.expected_checksum == "abc123"
        assert result.actual_checksum == "abc123"
        assert result.error_message is None

    def test_validate_directory_structure_missing_dirs(self, temp_config):
        """Testa validação quando diretórios estão faltando."""
        validator = IntegrityValidator(temp_config)
        results = validator._validate_directory_structure()

        # Todos devem falhar pois não criamos nenhum diretório
        assert len(results) > 0
        assert all(not result.is_valid for result in results)
        assert all("não existe" in result.error_message for result in results)

    def test_validate_directory_structure_with_dirs(self, temp_config):
        """Testa validação quando diretórios existem."""
        # Criar estrutura básica
        jtech_core = temp_config.project_path / ".jtech-core"
        jtech_core.mkdir()
        (jtech_core / "agents").mkdir()
        (jtech_core / "chatmodes").mkdir()
        (jtech_core / "templates").mkdir()

        validator = IntegrityValidator(temp_config)
        results = validator._validate_directory_structure()

        # Alguns devem passar
        passed_results = [r for r in results if r.is_valid]
        assert len(passed_results) >= 3  # Pelo menos os 3 que criamos

    def test_validate_config_files_missing(self, temp_config):
        """Testa validação quando arquivos de config estão faltando."""
        validator = IntegrityValidator(temp_config)
        results = validator._validate_config_files()

        # core-config.yml deve falhar
        core_config_result = next(
            (r for r in results if "core-config.yml" in r.component), None
        )
        assert core_config_result is not None
        assert not core_config_result.is_valid

        # .vscode/settings.json deve falhar (VS Code habilitado)
        vscode_result = next(
            (r for r in results if "settings.json" in r.component), None
        )
        assert vscode_result is not None
        assert not vscode_result.is_valid

    def test_validate_config_files_existing(self, temp_config):
        """Testa validação quando arquivos de config existem."""
        # Criar arquivos necessários
        jtech_core = temp_config.project_path / ".jtech-core"
        jtech_core.mkdir()

        core_config = jtech_core / "core-config.yml"
        core_config.write_text("# Config file")

        vscode_dir = temp_config.project_path / ".vscode"
        vscode_dir.mkdir()
        settings = vscode_dir / "settings.json"
        settings.write_text("{}")

        validator = IntegrityValidator(temp_config)
        results = validator._validate_config_files()

        # Ambos devem passar
        assert all(result.is_valid for result in results)

    def test_validate_config_files_no_vscode(self, temp_config):
        """Testa validação quando VS Code está desabilitado."""
        temp_config.vs_code_integration = False

        validator = IntegrityValidator(temp_config)
        results = validator._validate_config_files()

        # Deve apenas validar core-config.yml
        assert len(results) == 1
        assert "core-config.yml" in results[0].component

    def test_validate_agents_missing_directory(self, temp_config):
        """Testa validação quando diretório de agentes não existe."""
        validator = IntegrityValidator(temp_config)
        results = validator._validate_agents()

        assert len(results) == 1
        assert not results[0].is_valid
        assert "não existe" in results[0].error_message

    def test_validate_agents_with_agents(self, temp_config):
        """Testa validação quando agentes existem."""
        # Criar diretório e alguns agentes
        agents_dir = temp_config.project_path / ".jtech-core" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "pm.md").write_text("# PM Agent")
        (agents_dir / "dev.md").write_text("# Dev Agent")

        validator = IntegrityValidator(temp_config)
        results = validator._validate_agents()

        # Pelo menos 2 devem passar (pm.md e dev.md)
        passed_results = [r for r in results if r.is_valid]
        assert len(passed_results) >= 2

    def test_validate_chatmodes_missing_directory(self, temp_config):
        """Testa validação quando diretório chatmodes não existe."""
        validator = IntegrityValidator(temp_config)
        results = validator._validate_chatmodes()

        assert len(results) == 1
        assert not results[0].is_valid
        assert "não existe" in results[0].error_message

    def test_validate_chatmodes_with_chatmodes(self, temp_config):
        """Testa validação quando chatmodes existem."""
        # Criar diretório e chatmodes
        chatmodes_dir = temp_config.project_path / ".github" / "chatmodes"
        chatmodes_dir.mkdir(parents=True)

        (chatmodes_dir / "dev.chatmode.md").write_text("# Dev Chatmode")
        (chatmodes_dir / "pm.chatmode.md").write_text("# PM Chatmode")

        validator = IntegrityValidator(temp_config)
        results = validator._validate_chatmodes()

        assert len(results) == 1
        assert results[0].is_valid
        assert "2 arquivos" in results[0].component

    def test_calculate_file_checksum(self, temp_config):
        """Testa cálculo de checksum de arquivo."""
        # Criar arquivo temporário
        test_file = temp_config.project_path / "test.txt"
        test_file.write_text("Hello, World!")

        validator = IntegrityValidator(temp_config)
        checksum = validator.calculate_file_checksum(test_file)

        # Deve retornar uma string hexadecimal de 64 caracteres (SHA256)
        assert isinstance(checksum, str)
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_calculate_file_checksum_missing_file(self, temp_config):
        """Testa cálculo de checksum de arquivo inexistente."""
        missing_file = temp_config.project_path / "missing.txt"

        validator = IntegrityValidator(temp_config)

        with pytest.raises(Exception):
            validator.calculate_file_checksum(missing_file)

    def test_verify_checksums_valid(self, temp_config):
        """Testa verificação de checksums válidos."""
        # Criar arquivo e calcular checksum
        test_file = temp_config.project_path / "test.txt"
        test_file.write_text("Hello, World!")

        validator = IntegrityValidator(temp_config)
        expected_checksum = validator.calculate_file_checksum(test_file)

        # Verificar checksum
        results = validator.verify_checksums({"test.txt": expected_checksum})

        assert len(results) == 1
        assert results[0].is_valid
        assert results[0].expected_checksum == expected_checksum
        assert results[0].actual_checksum == expected_checksum

    def test_verify_checksums_invalid(self, temp_config):
        """Testa verificação de checksums inválidos."""
        # Criar arquivo
        test_file = temp_config.project_path / "test.txt"
        test_file.write_text("Hello, World!")

        validator = IntegrityValidator(temp_config)

        # Usar checksum incorreto
        wrong_checksum = "0" * 64
        results = validator.verify_checksums({"test.txt": wrong_checksum})

        assert len(results) == 1
        assert not results[0].is_valid
        assert results[0].expected_checksum == wrong_checksum
        assert results[0].actual_checksum != wrong_checksum
        assert "não confere" in results[0].error_message

    def test_validate_all_empty_project(self, temp_config):
        """Testa validação completa em projeto vazio."""
        validator = IntegrityValidator(temp_config)
        result = validator.validate_all()

        # Deve falhar pois não há nada instalado
        assert result is False

    def test_validate_all_complete_project(self, temp_config):
        """Testa validação completa em projeto completo."""
        # Criar estrutura completa
        jtech_core = temp_config.project_path / ".jtech-core"
        jtech_core.mkdir()

        # Diretórios necessários
        required_dirs = [
            "agents",
            "chatmodes",
            "templates",
            "workflows",
            "tasks",
            "checklists",
            "data",
            "utils",
        ]
        for dir_name in required_dirs:
            (jtech_core / dir_name).mkdir()

        # Arquivos de configuração
        (jtech_core / "core-config.yml").write_text("# Config")

        vscode_dir = temp_config.project_path / ".vscode"
        vscode_dir.mkdir()
        (vscode_dir / "settings.json").write_text("{}")

        # Agentes básicos
        agents_dir = jtech_core / "agents"
        (agents_dir / "pm.md").write_text("# PM")
        (agents_dir / "architect.md").write_text("# Architect")
        (agents_dir / "dev.md").write_text("# Dev")

        # Chatmodes
        chatmodes_dir = temp_config.project_path / ".github" / "chatmodes"
        chatmodes_dir.mkdir(parents=True)
        (chatmodes_dir / "dev.chatmode.md").write_text("# Dev")

        validator = IntegrityValidator(temp_config)
        result = validator.validate_all()

        # Deve passar
        assert result is True
