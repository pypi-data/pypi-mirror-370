#!/usr/bin/env python3
"""
Testes para AgentInstaller - História 2.2
Instalação de Agentes Especializados JTECH™ Core
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.agent_installer import (
    AgentInfo,
    AgentInstaller,
    AgentType,
)


class TestAgentInstaller:
    """Testes abrangentes para AgentInstaller."""

    @pytest.fixture
    def temp_project_dir(self):
        """Cria diretório temporário para testes."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def config(self, temp_project_dir):
        """Configuração básica para testes."""
        return InstallationConfig(
            project_path=temp_project_dir,
            install_type=InstallationType.GREENFIELD,
            team_type=TeamType.ALL,
            vs_code_integration=True,
            custom_config={},
        )

    @pytest.fixture
    def agent_installer(self, config):
        """Instância do AgentInstaller para testes."""
        return AgentInstaller(config)

    @pytest.fixture
    def sample_agents_dir(self, temp_project_dir):
        """Cria estrutura de agentes de exemplo."""
        agents_dir = temp_project_dir / "sample_agents"
        agents_dir.mkdir()

        # Criar ChatMode
        chatmode_dir = agents_dir / "chatmodes"
        chatmode_dir.mkdir()
        chatmode_file = chatmode_dir / "dev.chatmode.md"
        chatmode_content = """---
title: Developer Agent
description: Assists with development tasks
version: 1.0
---

# Developer Agent

This agent helps with development tasks.
"""
        chatmode_file.write_text(chatmode_content)

        # Criar Template
        templates_dir = agents_dir / "templates"
        templates_dir.mkdir()
        template_file = templates_dir / "story-template.md"
        template_content = """# Story Template

Template for user stories.
"""
        template_file.write_text(template_content)

        # Criar Workflow
        workflows_dir = agents_dir / "workflows"
        workflows_dir.mkdir()
        workflow_file = workflows_dir / "ci-pipeline.yml"
        workflow_content = """name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
"""
        workflow_file.write_text(workflow_content)

        # Criar Especialista
        specialist_file = agents_dir / "qa-specialist.md"
        specialist_content = """# QA Specialist

Quality assurance specialist agent.
"""
        specialist_file.write_text(specialist_content)

        return agents_dir

    def test_agent_installer_initialization(self, agent_installer, config):
        """Testa inicialização do AgentInstaller."""
        assert agent_installer.config == config
        assert agent_installer.project_path == Path(config.project_path)
        assert (
            agent_installer.jtech_core_path
            == Path(config.project_path) / ".jtech-core"
        )
        assert (
            agent_installer.agents_path
            == Path(config.project_path) / ".jtech-core" / "agents"
        )
        assert len(agent_installer.agent_directories) == 4
        assert agent_installer.discovered_agents == []
        assert agent_installer.installation_log == []

    def test_agent_type_enum(self):
        """Testa valores do enum AgentType."""
        assert AgentType.CHATMODE.value == "chatmode"
        assert AgentType.TEMPLATE.value == "template"
        assert AgentType.WORKFLOW.value == "workflow"
        assert AgentType.SPECIALIST.value == "specialist"

    def test_agent_info_dataclass(self):
        """Testa dataclass AgentInfo."""
        source_path = Path("/source/agent.md")
        target_path = Path("/target/agent.md")

        agent_info = AgentInfo(
            name="test-agent",
            type=AgentType.SPECIALIST,
            source_path=source_path,
            target_path=target_path,
            description="Test agent",
            metadata={"version": "1.0"},
            checksum="abc123",
            installed=True,
        )

        assert agent_info.name == "test-agent"
        assert agent_info.type == AgentType.SPECIALIST
        assert agent_info.source_path == source_path
        assert agent_info.target_path == target_path
        assert agent_info.description == "Test agent"
        assert agent_info.metadata == {"version": "1.0"}
        assert agent_info.checksum == "abc123"
        assert agent_info.installed is True

    def test_discover_agents_no_source_dir(self, agent_installer):
        """Testa descoberta quando diretório fonte não existe."""
        non_existent = Path("/non/existent/path")
        agents = agent_installer.discover_agents(non_existent)

        assert agents == []
        assert len(agent_installer.installation_log) == 1
        assert "não encontrado" in agent_installer.installation_log[0]

    def test_discover_agents_success(self, agent_installer, sample_agents_dir):
        """Testa descoberta bem-sucedida de agentes."""
        agents = agent_installer.discover_agents(sample_agents_dir)

        assert len(agents) == 4  # chatmode, template, workflow, specialist

        # Verificar tipos descobertos
        types_found = {agent.type for agent in agents}
        assert AgentType.CHATMODE in types_found
        assert AgentType.TEMPLATE in types_found
        assert AgentType.WORKFLOW in types_found
        assert AgentType.SPECIALIST in types_found

        # Verificar log
        assert "Descobertos 4 agentes" in agent_installer.installation_log[-1]

    def test_parse_agent_file_chatmode(
        self, agent_installer, sample_agents_dir
    ):
        """Testa parsing de arquivo ChatMode."""
        chatmode_file = sample_agents_dir / "chatmodes" / "dev.chatmode.md"
        agent_info = agent_installer._parse_agent_file(
            chatmode_file, AgentType.CHATMODE
        )

        assert agent_info is not None
        assert agent_info.name == "dev"
        assert agent_info.type == AgentType.CHATMODE
        assert agent_info.source_path == chatmode_file
        assert "chatmodes" in str(agent_info.target_path)
        assert agent_info.description == "Assists with development tasks"
        assert agent_info.metadata["title"] == "Developer Agent"
        assert agent_info.checksum != ""

    def test_parse_agent_file_template(
        self, agent_installer, sample_agents_dir
    ):
        """Testa parsing de arquivo Template."""
        template_file = sample_agents_dir / "templates" / "story-template.md"
        agent_info = agent_installer._parse_agent_file(
            template_file, AgentType.TEMPLATE
        )

        assert agent_info is not None
        assert agent_info.name == "story-template"
        assert agent_info.type == AgentType.TEMPLATE
        assert "templates" in str(agent_info.target_path)

    def test_extract_metadata_with_frontmatter(self, agent_installer):
        """Testa extração de metadados com frontmatter YAML."""
        content = """---
title: Test Agent
description: A test agent
version: 1.0.0
---

# Test Agent

Content here.
"""
        with patch("builtins.open", mock_open(read_data=content)):
            metadata = agent_installer._extract_metadata(Path("test.md"))

        assert metadata["title"] == "Test Agent"
        assert metadata["description"] == "A test agent"
        assert metadata["version"] == "1.0.0"

    def test_extract_metadata_without_frontmatter(self, agent_installer):
        """Testa extração de metadados sem frontmatter."""
        content = """# Test Agent

description: A simple test agent
version: 2.0

Some content here.
"""
        with patch("builtins.open", mock_open(read_data=content)):
            metadata = agent_installer._extract_metadata(Path("test.md"))

        assert metadata["title"] == "Test Agent"
        assert metadata["description"] == "A simple test agent"
        assert metadata["version"] == "2.0"

    def test_calculate_checksum(self, agent_installer, temp_project_dir):
        """Testa cálculo de checksum."""
        test_file = temp_project_dir / "test.txt"
        content = "Test content for checksum"
        test_file.write_text(content)

        checksum = agent_installer._calculate_checksum(test_file)

        # Verificar se é um hash SHA256 válido
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

        # Verificar consistência
        checksum2 = agent_installer._calculate_checksum(test_file)
        assert checksum == checksum2

        # Verificar que conteúdo diferente gera hash diferente
        test_file.write_text("Different content")
        checksum3 = agent_installer._calculate_checksum(test_file)
        assert checksum != checksum3

    def test_install_agents_no_agents(self, agent_installer):
        """Testa instalação sem agentes descobertos."""
        result = agent_installer.install_agents()

        assert result["success"] is False
        assert result["installed_count"] == 0
        assert result["failed_count"] == 0
        assert "Nenhum agente descoberto" in result["error"]

    def test_install_agents_success(
        self, agent_installer, sample_agents_dir, temp_project_dir
    ):
        """Testa instalação bem-sucedida de agentes."""
        # Descobrir agentes
        agents = agent_installer.discover_agents(sample_agents_dir)

        # Instalar agentes
        result = agent_installer.install_agents(agents)

        assert result["success"] is True
        assert result["installed_count"] == 4
        assert result["failed_count"] == 0
        assert len(result["installed_agents"]) == 4
        assert len(result["failed_agents"]) == 0

        # Verificar se arquivos foram copiados
        chatmodes_dir = (
            temp_project_dir / ".jtech-core" / "agents" / "chatmodes"
        )
        assert (chatmodes_dir / "dev.chatmode.md").exists()

        templates_dir = (
            temp_project_dir / ".jtech-core" / "agents" / "templates"
        )
        assert (templates_dir / "story-template.md").exists()

        # Verificar registro de agentes
        registry_file = (
            temp_project_dir / ".jtech-core" / "registry" / "agents.yml"
        )
        assert registry_file.exists()

        with open(registry_file, "r") as f:
            registry_data = yaml.safe_load(f)

        assert "agents" in registry_data
        assert len(registry_data["agents"]) == 4

    def test_install_agents_with_copy_failure(
        self, agent_installer, sample_agents_dir
    ):
        """Testa instalação com falha na cópia."""
        agents = agent_installer.discover_agents(sample_agents_dir)

        # Simular falha na cópia
        with patch(
            "shutil.copy2", side_effect=PermissionError("No permission")
        ):
            result = agent_installer.install_agents(agents)

        assert result["success"] is False
        assert result["installed_count"] == 0
        assert result["failed_count"] == 4

    def test_verify_agent_integrity_success(
        self, agent_installer, temp_project_dir
    ):
        """Testa verificação de integridade bem-sucedida."""
        # Criar arquivo e AgentInfo
        test_file = temp_project_dir / "test.md"
        content = "Test content"
        test_file.write_text(content)

        checksum = agent_installer._calculate_checksum(test_file)
        agent_info = AgentInfo(
            name="test",
            type=AgentType.SPECIALIST,
            source_path=test_file,
            target_path=test_file,
            checksum=checksum,
        )

        assert agent_installer._verify_agent_integrity(agent_info) is True

    def test_verify_agent_integrity_failure(
        self, agent_installer, temp_project_dir
    ):
        """Testa verificação de integridade com falha."""
        # Criar AgentInfo para arquivo inexistente
        non_existent = temp_project_dir / "non_existent.md"
        agent_info = AgentInfo(
            name="test",
            type=AgentType.SPECIALIST,
            source_path=non_existent,
            target_path=non_existent,
            checksum="wrong_checksum",
        )

        assert agent_installer._verify_agent_integrity(agent_info) is False

    def test_list_installed_agents_empty(self, agent_installer):
        """Testa listagem com registro vazio."""
        installed = agent_installer.list_installed_agents()
        assert installed == []

    def test_list_installed_agents_with_data(
        self, agent_installer, temp_project_dir
    ):
        """Testa listagem com agentes instalados."""
        # Criar registro de agentes
        registry_dir = temp_project_dir / ".jtech-core" / "registry"
        registry_dir.mkdir(parents=True)
        registry_file = registry_dir / "agents.yml"

        registry_data = {
            "agents": {
                "dev": {
                    "type": "chatmode",
                    "installed_path": ".jtech-core/agents/chatmodes/dev.chatmode.md",
                    "checksum": "abc123",
                    "metadata": {"version": "1.0"},
                },
                "qa": {
                    "type": "specialist",
                    "installed_path": ".jtech-core/agents/specialists/qa.md",
                    "checksum": "def456",
                    "metadata": {"version": "2.0"},
                },
            }
        }

        with open(registry_file, "w") as f:
            yaml.dump(registry_data, f)

        installed = agent_installer.list_installed_agents()

        assert len(installed) == 2
        assert installed[0]["name"] == "dev"
        assert installed[0]["type"] == "chatmode"
        assert installed[1]["name"] == "qa"
        assert installed[1]["type"] == "specialist"

    def test_get_installation_report(self, agent_installer, sample_agents_dir):
        """Testa geração de relatório de instalação."""
        # Descobrir agentes primeiro
        agents = agent_installer.discover_agents(sample_agents_dir)

        report = agent_installer.get_installation_report()

        assert report["discovered_agents_count"] == 4
        assert report["agents_by_type"]["chatmode"] == 1
        assert report["agents_by_type"]["template"] == 1
        assert report["agents_by_type"]["workflow"] == 1
        assert report["agents_by_type"]["specialist"] == 1
        assert "installation_log" in report
        assert "installed_agents" in report
        assert "target_directories" in report

    def test_ensure_agent_directories(self, agent_installer, temp_project_dir):
        """Testa criação de diretórios de agentes."""
        agent_installer._ensure_agent_directories()

        agents_path = temp_project_dir / ".jtech-core" / "agents"
        assert (agents_path / "chatmodes").exists()
        assert (agents_path / "templates").exists()
        assert (agents_path / "workflows").exists()
        assert (agents_path / "specialists").exists()

    def test_update_agents_registry_new_file(
        self, agent_installer, temp_project_dir, sample_agents_dir
    ):
        """Testa atualização de registro com arquivo novo."""
        agents = agent_installer.discover_agents(sample_agents_dir)
        installed_agents = agents[:2]  # Usar apenas 2 agentes

        agent_installer._update_agents_registry(installed_agents)

        registry_file = (
            temp_project_dir / ".jtech-core" / "registry" / "agents.yml"
        )
        assert registry_file.exists()

        with open(registry_file, "r") as f:
            registry_data = yaml.safe_load(f)

        assert "agents" in registry_data
        assert len(registry_data["agents"]) == 2

    def test_update_agents_registry_existing_file(
        self, agent_installer, temp_project_dir, sample_agents_dir
    ):
        """Testa atualização de registro com arquivo existente."""
        # Criar registro existente
        registry_dir = temp_project_dir / ".jtech-core" / "registry"
        registry_dir.mkdir(parents=True)
        registry_file = registry_dir / "agents.yml"

        existing_data = {
            "agents": {
                "existing-agent": {
                    "type": "specialist",
                    "installed_path": "path/to/existing.md",
                    "checksum": "existing123",
                }
            }
        }

        with open(registry_file, "w") as f:
            yaml.dump(existing_data, f)

        # Adicionar novos agentes
        agents = agent_installer.discover_agents(sample_agents_dir)
        installed_agents = agents[:1]  # Usar apenas 1 agente

        agent_installer._update_agents_registry(installed_agents)

        # Verificar que agente existente foi preservado
        with open(registry_file, "r") as f:
            registry_data = yaml.safe_load(f)

        assert len(registry_data["agents"]) == 2  # 1 existente + 1 novo
        assert "existing-agent" in registry_data["agents"]

    def test_install_agents_dry_run_concept(
        self, agent_installer, sample_agents_dir
    ):
        """Testa conceito de dry run (sem copiar arquivos)."""
        agents = agent_installer.discover_agents(sample_agents_dir)

        # Simular dry run não copiando arquivos
        with patch("shutil.copy2") as mock_copy:
            # Mock para não fazer nada (dry run)
            mock_copy.return_value = None

            result = agent_installer.install_agents(
                agents, verify_integrity=False
            )

            # Verificar que copy2 foi chamado para todos os agentes
            assert mock_copy.call_count == 4

            # Em dry run real, success seria determinado diferentemente
            assert result["installed_count"] == 4

    def test_agent_installer_integration_full_cycle(
        self, agent_installer, sample_agents_dir
    ):
        """Teste de integração do ciclo completo."""
        # 1. Descobrir agentes
        agents = agent_installer.discover_agents(sample_agents_dir)
        assert len(agents) == 4

        # 2. Instalar agentes
        result = agent_installer.install_agents(agents)
        assert result["success"] is True

        # 3. Listar agentes instalados
        installed = agent_installer.list_installed_agents()
        assert len(installed) == 4

        # 4. Gerar relatório
        report = agent_installer.get_installation_report()
        assert report["discovered_agents_count"] == 4

        # 5. Verificar estrutura criada
        assert agent_installer.agents_path.exists()
        assert (agent_installer.agents_path / "chatmodes").exists()
        assert (agent_installer.agents_path / "templates").exists()
        assert (agent_installer.agents_path / "workflows").exists()
        assert (agent_installer.agents_path / "specialists").exists()
