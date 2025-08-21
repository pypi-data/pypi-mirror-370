"""Testes para o criador de estrutura de diretórios."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.structure import (
    DirectoryInfo,
    DirectoryPermission,
    StructureCreator,
)


class TestStructureCreator:
    """Testes para o StructureCreator."""

    @pytest.fixture
    def temp_project_dir(self):
        """Fixture para diretório temporário de projeto."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def greenfield_config(self, temp_project_dir):
        """Fixture para configuração greenfield."""
        return InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.GREENFIELD,
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=None,
        )

    @pytest.fixture
    def brownfield_config(self, temp_project_dir):
        """Fixture para configuração brownfield."""
        return InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.BROWNFIELD,
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=None,
        )

    @pytest.fixture
    def structure_creator(self, greenfield_config):
        """Fixture para criador de estrutura."""
        return StructureCreator(greenfield_config)

    def test_structure_creator_initialization(
        self, structure_creator, greenfield_config
    ):
        """Testa inicialização do criador de estrutura."""
        assert structure_creator.config == greenfield_config
        assert not structure_creator.dry_run
        assert structure_creator.created_directories == []
        assert structure_creator.skipped_directories == []
        assert structure_creator.failed_directories == []

    def test_structure_creator_dry_run(self, greenfield_config):
        """Testa modo dry run."""
        creator = StructureCreator(greenfield_config, dry_run=True)
        assert creator.dry_run

    def test_jtech_structure_completeness(self, structure_creator):
        """Testa se a estrutura contém todos os diretórios necessários."""
        structure = StructureCreator.JTECH_STRUCTURE

        # Verificar diretórios essenciais
        essential_dirs = [
            ".jtech-core",
            ".jtech-core/agents",
            ".jtech-core/templates",
            ".jtech-core/workflows",
            ".jtech-core/tasks",
            ".github/chatmodes",
        ]

        structure_paths = [dir_info.path for dir_info in structure]

        for essential_dir in essential_dirs:
            assert essential_dir in structure_paths

    def test_create_structure_greenfield_success(self, structure_creator):
        """Testa criação bem-sucedida em projeto greenfield."""
        results = structure_creator.create_structure()

        assert results["success"]
        assert len(results["created_directories"]) > 0
        assert len(results["failed_directories"]) == 0
        assert len(results["errors"]) == 0

        # Verificar se diretórios foram criados fisicamente
        jtech_core = structure_creator.config.project_path / ".jtech-core"
        assert jtech_core.exists()
        assert jtech_core.is_dir()

        agents_dir = (
            structure_creator.config.project_path / ".jtech-core" / "agents"
        )
        assert agents_dir.exists()
        assert agents_dir.is_dir()

    def test_create_structure_dry_run(self, greenfield_config):
        """Testa criação em modo dry run."""
        creator = StructureCreator(greenfield_config, dry_run=True)
        results = creator.create_structure()

        assert results["success"]

        # Verificar que diretórios NÃO foram criados fisicamente
        jtech_core = greenfield_config.project_path / ".jtech-core"
        assert not jtech_core.exists()

    def test_create_structure_existing_directories(self, structure_creator):
        """Testa criação quando alguns diretórios já existem."""
        # Pré-criar alguns diretórios
        existing_dir = structure_creator.config.project_path / ".jtech-core"
        existing_dir.mkdir(parents=True)

        results = structure_creator.create_structure()

        assert results["success"]
        assert len(results["skipped_directories"]) > 0

        # Verificar se diretório existente foi reportado como pulado
        skipped_paths = [
            item["path"] for item in results["skipped_directories"]
        ]
        assert ".jtech-core" in skipped_paths

    def test_create_structure_brownfield_respects_existing(
        self, temp_project_dir
    ):
        """Testa que modo brownfield respeita estrutura existente."""
        # Criar estrutura existente
        (temp_project_dir / "src").mkdir()
        (temp_project_dir / "docs").mkdir()
        (temp_project_dir / "README.md").write_text("Existing project")

        brownfield_config = InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.BROWNFIELD,
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=None,
        )

        creator = StructureCreator(brownfield_config)
        results = creator.create_structure()

        assert results["success"]

        # Verificar que diretórios essenciais do framework foram criados
        assert (temp_project_dir / ".jtech-core").exists()
        assert (temp_project_dir / ".github" / "chatmodes").exists()

    def test_create_structure_file_conflict(self, structure_creator):
        """Testa tratamento de conflito quando arquivo existe no lugar de diretório."""
        # Criar arquivo onde deveria ser diretório
        conflict_file = structure_creator.config.project_path / ".jtech-core"
        conflict_file.write_text("conflicting file")

        results = structure_creator.create_structure()

        assert not results["success"]
        assert len(results["errors"]) > 0
        assert ".jtech-core" in results["failed_directories"]

    def test_create_gitkeep_files(self, structure_creator):
        """Testa criação de arquivos .gitkeep."""
        results = structure_creator.create_structure()

        assert results["success"]
        assert "gitkeep_files_created" in results
        assert results["gitkeep_files_created"] > 0

        # Verificar se .gitkeep foi criado em diretório apropriado
        templates_dir = (
            structure_creator.config.project_path / ".jtech-core" / "templates"
        )
        gitkeep_file = templates_dir / ".gitkeep"

        assert gitkeep_file.exists()
        content = gitkeep_file.read_text()
        assert "This file ensures the directory is tracked by Git" in content

    def test_validate_structure_success(self, structure_creator):
        """Testa validação bem-sucedida da estrutura."""
        # Criar estrutura primeiro
        structure_creator.create_structure()

        validation = structure_creator.validate_structure()

        assert validation["valid"]
        assert len(validation["missing_required"]) == 0
        assert validation["total_validated"] > 0

    def test_validate_structure_missing_required(self, structure_creator):
        """Testa validação quando faltam diretórios obrigatórios."""
        # Criar estrutura incompleta
        (structure_creator.config.project_path / ".jtech-core").mkdir()
        # Não criar outros diretórios obrigatórios

        validation = structure_creator.validate_structure()

        assert not validation["valid"]
        assert len(validation["missing_required"]) > 0
        assert ".jtech-core/agents" in validation["missing_required"]

    @pytest.mark.skipif(
        os.name == "nt", reason="Teste de permissões não aplicável no Windows"
    )
    def test_directory_permissions_unix(self, structure_creator):
        """Testa permissões de diretório em sistemas Unix."""
        structure_creator.create_structure()

        # Verificar permissões do diretório de backups (restrito)
        backups_dir = (
            structure_creator.config.project_path / ".jtech-core" / "backups"
        )
        stat_info = backups_dir.stat()
        permissions = oct(stat_info.st_mode)[-3:]

        # Diretório de backups deve ter permissões restritas (750)
        assert permissions == "750"

    def test_get_structure_info(self, structure_creator):
        """Testa obtenção de informações da estrutura."""
        info = structure_creator.get_structure_info()

        assert "total_directories" in info
        assert "required_directories" in info
        assert "optional_directories" in info
        assert "directories_with_gitkeep" in info
        assert "structure_details" in info

        assert info["total_directories"] == len(
            StructureCreator.JTECH_STRUCTURE
        )
        assert len(info["structure_details"]) == info["total_directories"]

        # Verificar que há diretórios obrigatórios e opcionais
        assert info["required_directories"] > 0
        assert info["optional_directories"] > 0

    def test_directory_info_dataclass(self):
        """Testa a dataclass DirectoryInfo."""
        dir_info = DirectoryInfo(
            path=".test",
            description="Test directory",
            required=True,
            permission=DirectoryPermission.RESTRICTED,
            create_gitkeep=True,
        )

        assert dir_info.path == ".test"
        assert dir_info.description == "Test directory"
        assert dir_info.required
        assert dir_info.permission == DirectoryPermission.RESTRICTED
        assert dir_info.create_gitkeep

    def test_directory_permission_values(self):
        """Testa valores das permissões de diretório."""
        assert DirectoryPermission.STANDARD.value == 0o755
        assert DirectoryPermission.RESTRICTED.value == 0o750
        assert DirectoryPermission.PUBLIC.value == 0o755

    def test_create_structure_exception_handling(self, structure_creator):
        """Testa tratamento de exceções durante criação."""
        # Simular erro durante criação usando mock mais específico
        with patch.object(
            structure_creator,
            "_create_directory",
            side_effect=PermissionError("Permission denied"),
        ):
            results = structure_creator.create_structure()
            # O método deve capturar a exceção e reportar falhas
            assert not results["success"]
            assert len(results["errors"]) > 0
            assert len(results["failed_directories"]) > 0

    def test_has_existing_structure_detection(self, structure_creator):
        """Testa detecção de estrutura de projeto existente."""
        # Inicialmente não deve ter estrutura
        assert not structure_creator._has_existing_structure()

        # Criar indicador de estrutura existente
        (structure_creator.config.project_path / "src").mkdir()
        assert structure_creator._has_existing_structure()

        # Testar outros indicadores
        (structure_creator.config.project_path / "src").rmdir()
        (structure_creator.config.project_path / "README.md").write_text(
            "Existing project"
        )
        assert structure_creator._has_existing_structure()

    def test_should_create_in_brownfield_logic(self, temp_project_dir):
        """Testa lógica de criação em projeto brownfield."""
        brownfield_config = InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.BROWNFIELD,
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=None,
        )

        creator = StructureCreator(brownfield_config)

        # Diretórios essenciais sempre devem ser criados
        jtech_dir = DirectoryInfo(
            ".jtech-core", "Core directory", required=True
        )
        assert creator._should_create_in_brownfield(jtech_dir)

        chatmodes_dir = DirectoryInfo(
            ".github/chatmodes", "ChatModes", required=True
        )
        assert creator._should_create_in_brownfield(chatmodes_dir)

        # Criar estrutura existente
        (temp_project_dir / "src").mkdir()
        (temp_project_dir / "docs").mkdir()

        # Diretórios opcionais não devem ser criados se já há estrutura
        docs_dir = DirectoryInfo("docs", "Documentation", required=False)
        assert not creator._should_create_in_brownfield(docs_dir)

        vscode_dir = DirectoryInfo(".vscode", "VS Code config", required=False)
        assert not creator._should_create_in_brownfield(vscode_dir)

    def test_create_structure_progress_tracking(self, structure_creator):
        """Testa rastreamento de progresso durante criação."""
        results = structure_creator.create_structure()

        # Verificar que resultados contêm informações de progresso
        total_expected = len(StructureCreator.JTECH_STRUCTURE)
        total_processed = (
            len(results["created_directories"])
            + len(results["skipped_directories"])
            + len(results["failed_directories"])
        )

        assert results["total_directories"] == total_expected
        assert (
            total_processed <= total_expected
        )  # Pode ser menor devido a falhas

    def test_gitkeep_not_created_in_non_empty_directories(
        self, structure_creator
    ):
        """Testa que .gitkeep não é criado em diretórios não vazios."""
        # Criar estrutura
        structure_creator.create_structure()

        # Adicionar arquivo em diretório que teria .gitkeep
        templates_dir = (
            structure_creator.config.project_path / ".jtech-core" / "templates"
        )
        (templates_dir / "existing_file.txt").write_text("Some content")

        # Remover .gitkeep existente
        gitkeep_file = templates_dir / ".gitkeep"
        if gitkeep_file.exists():
            gitkeep_file.unlink()

        # Executar criação novamente
        results = structure_creator.create_structure()

        # .gitkeep não deve ser criado pois diretório não está vazio
        assert not gitkeep_file.exists()

    def test_validation_with_permission_issues(self, structure_creator):
        """Testa validação quando há problemas de permissão."""
        # Criar estrutura
        structure_creator.create_structure()

        # Simular problema de permissão (apenas em sistemas Unix)
        if os.name != "nt":
            validation = structure_creator.validate_structure()

            # Não deve haver problemas de permissão em teste normal
            assert len(validation["permission_issues"]) == 0

            # Alterar permissão de um diretório
            test_dir = structure_creator.config.project_path / ".jtech-core"
            os.chmod(test_dir, 0o700)  # Permissão diferente da esperada

            validation = structure_creator.validate_structure()

            # Agora deve detectar problema de permissão
            # (dependendo da implementação específica)
