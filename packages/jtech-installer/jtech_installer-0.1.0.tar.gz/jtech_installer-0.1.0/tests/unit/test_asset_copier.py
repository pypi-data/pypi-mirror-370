"""
Testes para AssetCopier
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from jtech_installer.core.exceptions import FileOperationError
from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.asset_copier import AssetCopier


class TestAssetCopier:
    """Testes para AssetCopier"""

    @pytest.fixture
    def temp_dirs(self):
        """Cria diretórios temporários para teste"""
        source_dir = Path(tempfile.mkdtemp())
        target_dir = Path(tempfile.mkdtemp())

        # Criar estrutura de fonte simulada
        agents_dir = source_dir / "agents"
        agents_dir.mkdir()

        # Criar alguns arquivos de agente
        (agents_dir / "pm.md").write_text("# PM Agent")
        (agents_dir / "architect.md").write_text("# Architect Agent")
        (agents_dir / "dev.md").write_text("# Dev Agent")

        yield source_dir, target_dir

        # Cleanup
        shutil.rmtree(source_dir)
        shutil.rmtree(target_dir)

    @pytest.fixture
    def config(self, temp_dirs):
        """Configuração de teste"""
        source_dir, target_dir = temp_dirs
        return InstallationConfig(
            project_path=target_dir,
            install_type=InstallationType.GREENFIELD,
            team_type=TeamType.IDE_MINIMAL,
            vs_code_integration=True,
            custom_config={},
            framework_source_path=source_dir,
        )

    def test_init_with_explicit_source(self, config):
        """Testa inicialização com source explícito"""
        copier = AssetCopier(config)
        assert copier.framework_source == config.framework_source_path

    def test_copy_agents_ide_minimal(self, config, temp_dirs):
        """Testa cópia de agentes para team IDE minimal"""
        source_dir, target_dir = temp_dirs
        copier = AssetCopier(config, dry_run=False)

        assets = copier.copy_agents()

        # Verificar se os agentes corretos foram copiados
        assert len(assets) == 3  # pm.md, architect.md, dev.md

        # Verificar se os arquivos existem no destino
        target_agents = target_dir / ".jtech-core" / "agents"
        assert (target_agents / "pm.md").exists()
        assert (target_agents / "architect.md").exists()
        assert (target_agents / "dev.md").exists()

    def test_copy_agents_dry_run(self, config, temp_dirs):
        """Testa cópia em modo dry-run"""
        source_dir, target_dir = temp_dirs
        copier = AssetCopier(config, dry_run=True)

        assets = copier.copy_agents()

        # Assets devem ser reportados mas arquivos não devem existir
        assert len(assets) == 3

        target_agents = target_dir / ".jtech-core" / "agents"
        assert not target_agents.exists()

    def test_copy_agents_missing_source(self, config):
        """Testa erro quando diretório fonte não existe"""
        config.framework_source_path = Path("/path/que/nao/existe")

        with pytest.raises(
            FileOperationError, match="Framework source não encontrado"
        ):
            AssetCopier(config)

    def test_team_agent_mapping(self):
        """Testa mapeamento de agentes por tipo de equipe"""
        # Team All deve ter mais agentes
        all_agents = AssetCopier.TEAM_AGENT_MAPPING[TeamType.ALL]
        minimal_agents = AssetCopier.TEAM_AGENT_MAPPING[TeamType.IDE_MINIMAL]

        assert len(all_agents) > len(minimal_agents)
        assert "pm.md" in all_agents
        assert "pm.md" in minimal_agents
        assert "analyst.md" in all_agents
        assert "analyst.md" not in minimal_agents

    def test_calculate_checksum(self, config, temp_dirs):
        """Testa cálculo de checksum"""
        source_dir, target_dir = temp_dirs
        copier = AssetCopier(config)

        test_file = source_dir / "test.txt"
        test_file.write_text("Hello World")

        checksum = copier._calculate_checksum(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex

    def test_copy_chatmodes_not_found(self, config, temp_dirs):
        """Testa quando chatmodes não é encontrado"""
        source_dir, target_dir = temp_dirs
        copier = AssetCopier(config, dry_run=False)

        # Não criar diretório chatmodes
        assets = copier.copy_chatmodes()

        # Deve retornar lista vazia sem erro
        assert assets == []
