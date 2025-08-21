#!/usr/bin/env python3
"""
Testes para ChatModeConfigurator - História 2.3
Configuração de ChatModes para GitHub Copilot
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from jtech_installer.core.models import InstallationConfig, InstallationType, TeamType
from jtech_installer.installer.chatmodes import (
    ChatModeCompatibility,
    ChatModeConfigurator,
    ChatModeInfo,
)


class TestChatModeConfigurator:
    """Testes abrangentes para ChatModeConfigurator."""

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
            team_type=TeamType.FULLSTACK,
            vs_code_integration=True,
            custom_config={},
        )

    @pytest.fixture
    def chatmode_configurator(self, config):
        """Instância do ChatModeConfigurator para testes."""
        return ChatModeConfigurator(config)

    @pytest.fixture
    def sample_chatmodes_dir(self, temp_project_dir):
        """Cria diretório com chatmodes de exemplo."""
        chatmodes_dir = temp_project_dir / "sample_chatmodes"
        chatmodes_dir.mkdir()

        # ChatMode totalmente compatível
        compatible_chatmode = chatmodes_dir / "dev.chatmode.md"
        compatible_content = """---
title: Developer Assistant
description: Assists with development tasks
version: 1.0
tags: development, coding, assistance
---

# Developer Assistant

## Role
You are a helpful development assistant.

## Context
This agent helps with coding tasks and development workflow.

## Instructions
- Provide clear and concise code suggestions
- Follow best practices
- Explain your reasoning

## Capabilities
- Code generation
- Bug fixing
- Code review
- Documentation

## Examples
### Example 1: Code Generation
User: "Create a Python function to calculate factorial"
Assistant: Here's a clean factorial function...
"""
        compatible_chatmode.write_text(compatible_content)

        # ChatMode com problemas menores
        mostly_compatible_chatmode = chatmodes_dir / "qa.chatmode.md"
        mostly_content = """# QA Specialist

description: Quality assurance specialist for testing

This agent helps with testing and quality assurance tasks.

## Instructions
- Create comprehensive test cases
- Review code for quality issues
"""
        mostly_compatible_chatmode.write_text(mostly_content)

        # ChatMode incompatível
        incompatible_chatmode = chatmodes_dir / "legacy.chatmode.md"
        incompatible_content = """Some legacy content without proper structure.

@function_call(param1, param2)
${VARIABLE_NOT_SUPPORTED}
<script>alert('not allowed')</script>
"""
        incompatible_chatmode.write_text(incompatible_content)

        return chatmodes_dir

    def test_chatmode_configurator_initialization(
        self, chatmode_configurator, config
    ):
        """Testa inicialização do ChatModeConfigurator."""
        assert chatmode_configurator.config == config
        assert chatmode_configurator.project_path == Path(config.project_path)
        assert (
            chatmode_configurator.github_dir
            == Path(config.project_path) / ".github"
        )
        assert (
            chatmode_configurator.chatmodes_dir
            == Path(config.project_path) / ".github" / "chatmodes"
        )
        assert chatmode_configurator.discovered_chatmodes == []
        assert chatmode_configurator.installation_log == []
        assert "required_headers" in chatmode_configurator.copilot_patterns

    def test_chatmode_compatibility_enum(self):
        """Testa valores do enum ChatModeCompatibility."""
        assert (
            ChatModeCompatibility.FULLY_COMPATIBLE.value == "fully_compatible"
        )
        assert (
            ChatModeCompatibility.MOSTLY_COMPATIBLE.value
            == "mostly_compatible"
        )
        assert (
            ChatModeCompatibility.NEEDS_ADJUSTMENT.value == "needs_adjustment"
        )
        assert ChatModeCompatibility.INCOMPATIBLE.value == "incompatible"

    def test_chatmode_info_dataclass(self):
        """Testa dataclass ChatModeInfo."""
        source_path = Path("/source/test.chatmode.md")
        target_path = Path("/target/test.chatmode.md")

        chatmode_info = ChatModeInfo(
            name="test-chatmode",
            source_path=source_path,
            target_path=target_path,
            description="Test ChatMode",
            version="2.0",
            compatibility=ChatModeCompatibility.MOSTLY_COMPATIBLE,
            metadata={"tags": ["test"]},
            validation_issues=["Minor issue"],
            installed=True,
        )

        assert chatmode_info.name == "test-chatmode"
        assert chatmode_info.source_path == source_path
        assert chatmode_info.target_path == target_path
        assert chatmode_info.description == "Test ChatMode"
        assert chatmode_info.version == "2.0"
        assert (
            chatmode_info.compatibility
            == ChatModeCompatibility.MOSTLY_COMPATIBLE
        )
        assert chatmode_info.metadata == {"tags": ["test"]}
        assert chatmode_info.validation_issues == ["Minor issue"]
        assert chatmode_info.installed is True

    def test_discover_chatmodes_no_source_dir(self, chatmode_configurator):
        """Testa descoberta quando diretório fonte não existe."""
        non_existent = Path("/non/existent/path")
        chatmodes = chatmode_configurator.discover_chatmodes(non_existent)

        assert chatmodes == []
        assert len(chatmode_configurator.installation_log) == 1
        assert "0 chatmodes" in chatmode_configurator.installation_log[0]

    def test_discover_chatmodes_success(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa descoberta bem-sucedida de chatmodes."""
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )

        assert len(chatmodes) == 3

        # Verificar nomes descobertos
        names = {cm.name for cm in chatmodes}
        assert "dev" in names
        assert "qa" in names
        assert "legacy" in names

        # Verificar log
        assert (
            "Descobertos 3 chatmodes"
            in chatmode_configurator.installation_log[-1]
        )

    def test_parse_chatmode_file_fully_compatible(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa parsing de ChatMode totalmente compatível."""
        chatmode_file = sample_chatmodes_dir / "dev.chatmode.md"
        chatmode_info = chatmode_configurator._parse_chatmode_file(
            chatmode_file
        )

        assert chatmode_info is not None
        assert chatmode_info.name == "dev"
        assert chatmode_info.source_path == chatmode_file
        assert "chatmodes" in str(chatmode_info.target_path)
        assert chatmode_info.description == "Assists with development tasks"
        assert chatmode_info.version == "1.0"
        assert (
            chatmode_info.compatibility
            == ChatModeCompatibility.FULLY_COMPATIBLE
        )
        assert chatmode_info.metadata["title"] == "Developer Assistant"
        assert "development" in chatmode_info.metadata["tags"]
        assert len(chatmode_info.validation_issues) == 0

    def test_parse_chatmode_file_mostly_compatible(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa parsing de ChatMode com compatibilidade parcial."""
        chatmode_file = sample_chatmodes_dir / "qa.chatmode.md"
        chatmode_info = chatmode_configurator._parse_chatmode_file(
            chatmode_file
        )

        assert chatmode_info is not None
        assert chatmode_info.name == "qa"
        assert chatmode_info.compatibility in [
            ChatModeCompatibility.MOSTLY_COMPATIBLE,
            ChatModeCompatibility.NEEDS_ADJUSTMENT,
        ]
        assert len(chatmode_info.validation_issues) > 0

    def test_parse_chatmode_file_incompatible(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa parsing de ChatMode incompatível."""
        chatmode_file = sample_chatmodes_dir / "legacy.chatmode.md"
        chatmode_info = chatmode_configurator._parse_chatmode_file(
            chatmode_file
        )

        assert chatmode_info is not None
        assert chatmode_info.name == "legacy"
        assert (
            chatmode_info.compatibility == ChatModeCompatibility.INCOMPATIBLE
        )
        assert len(chatmode_info.validation_issues) > 0

        # Verificar que problemas específicos foram detectados
        issues_text = " ".join(chatmode_info.validation_issues)
        assert "incompatíveis" in issues_text or "faltando" in issues_text

    def test_extract_chatmode_metadata_with_frontmatter(
        self, chatmode_configurator
    ):
        """Testa extração de metadados com frontmatter."""
        content = """---
title: Test ChatMode
description: A test chatmode
version: 2.5
tags: test, example
---

# Test ChatMode

Content here.
"""
        metadata = chatmode_configurator._extract_chatmode_metadata(content)

        assert metadata["title"] == "Test ChatMode"
        assert metadata["description"] == "A test chatmode"
        assert metadata["version"] == "2.5"
        assert metadata["tags"] == ["test", "example"]

    def test_extract_chatmode_metadata_without_frontmatter(
        self, chatmode_configurator
    ):
        """Testa extração de metadados sem frontmatter."""
        content = """# Test ChatMode

description: A simple test chatmode
version: 1.5

Some content here.
"""
        metadata = chatmode_configurator._extract_chatmode_metadata(content)

        assert metadata["title"] == "Test ChatMode"
        assert metadata["description"] == "A simple test chatmode"
        assert metadata["version"] == "1.5"

    def test_validate_copilot_compatibility_fully_compatible(
        self, chatmode_configurator
    ):
        """Testa validação de compatibilidade total."""
        content = """# Test Agent

description: Test description

## Role
Test role

## Context
Test context

## Instructions
Test instructions

## Capabilities
Can do amazing things

## Examples
Here are some examples
"""
        compatibility, issues = (
            chatmode_configurator._validate_copilot_compatibility(content)
        )

        assert compatibility == ChatModeCompatibility.FULLY_COMPATIBLE
        assert len(issues) == 0

    def test_validate_copilot_compatibility_with_issues(
        self, chatmode_configurator
    ):
        """Testa validação com problemas de compatibilidade."""
        content = """Some content without proper headers.

@unsupported_function(param)
${VARIABLE}
<script>alert('test')</script>
"""
        compatibility, issues = (
            chatmode_configurator._validate_copilot_compatibility(content)
        )

        assert compatibility == ChatModeCompatibility.INCOMPATIBLE
        assert len(issues) > 0

        # Verificar que problemas foram detectados
        issues_text = " ".join(issues)
        assert "incompatíveis" in issues_text or "faltando" in issues_text

    def test_configure_chatmodes_no_chatmodes(self, chatmode_configurator):
        """Testa configuração sem chatmodes descobertos."""
        result = chatmode_configurator.configure_chatmodes()

        assert result["success"] is False
        assert result["configured_count"] == 0
        assert result["skipped_count"] == 0
        assert result["failed_count"] == 0
        assert "Nenhum ChatMode descoberto" in result["error"]

    def test_configure_chatmodes_success(
        self, chatmode_configurator, sample_chatmodes_dir, temp_project_dir
    ):
        """Testa configuração bem-sucedida de chatmodes."""
        # Descobrir chatmodes
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )

        # Configurar chatmodes
        result = chatmode_configurator.configure_chatmodes(chatmodes)

        # Verificar resultado
        assert result["success"] is True  # Sucesso (sem falhas)
        assert result["configured_count"] >= 1  # Pelo menos um compatível
        assert result["skipped_count"] >= 1  # Pelo menos um incompatível
        assert result["failed_count"] == 0

        # Verificar arquivos copiados
        chatmodes_dir = temp_project_dir / ".github" / "chatmodes"
        assert chatmodes_dir.exists()

        # Deve haver pelo menos um arquivo copiado
        copied_files = list(chatmodes_dir.glob("*.chatmode.md"))
        assert len(copied_files) >= 1

        # Verificar configuração do Copilot
        config_file = chatmodes_dir / ".copilot-config.json"
        assert config_file.exists()

        with open(config_file, "r") as f:
            config_data = json.load(f)

        assert "chatmodes" in config_data
        assert config_data["total_chatmodes"] == result["configured_count"]

    def test_configure_chatmodes_force_install(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa configuração forçada incluindo incompatíveis."""
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )

        result = chatmode_configurator.configure_chatmodes(
            chatmodes, force_install=True
        )

        # Com force_install=True, deve tentar instalar todos
        total_attempted = result["configured_count"] + result["failed_count"]
        assert total_attempted == len(chatmodes)
        assert result["skipped_count"] == 0

    def test_configure_chatmodes_with_copy_failure(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa configuração com falha na cópia."""
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )

        # Simular falha na cópia
        with patch(
            "shutil.copy2", side_effect=PermissionError("No permission")
        ):
            result = chatmode_configurator.configure_chatmodes(chatmodes)

        assert result["success"] is False
        assert result["configured_count"] == 0
        # Todos devem falhar ou ser pulados
        assert (result["failed_count"] + result["skipped_count"]) == len(
            chatmodes
        )

    def test_ensure_chatmodes_directory(
        self, chatmode_configurator, temp_project_dir
    ):
        """Testa criação de diretório de chatmodes."""
        chatmode_configurator._ensure_chatmodes_directory()

        github_dir = temp_project_dir / ".github"
        chatmodes_dir = temp_project_dir / ".github" / "chatmodes"

        assert github_dir.exists()
        assert chatmodes_dir.exists()
        assert chatmodes_dir.is_dir()

    def test_set_chatmode_permissions(
        self, chatmode_configurator, temp_project_dir
    ):
        """Testa configuração de permissões."""
        # Criar arquivo de teste
        test_file = temp_project_dir / "test.chatmode.md"
        test_file.write_text("test content")

        # Configurar permissões
        chatmode_configurator._set_chatmode_permissions(test_file)

        # Verificar que método executou sem erro
        assert test_file.exists()

    def test_create_copilot_config(
        self, chatmode_configurator, temp_project_dir
    ):
        """Testa criação de configuração do Copilot."""
        # Criar diretório de chatmodes
        chatmode_configurator._ensure_chatmodes_directory()

        # Criar ChatModeInfo de exemplo
        chatmode_info = ChatModeInfo(
            name="test",
            source_path=Path("/test.chatmode.md"),
            target_path=Path("/target/test.chatmode.md"),
            description="Test ChatMode",
            version="1.0",
            compatibility=ChatModeCompatibility.FULLY_COMPATIBLE,
        )

        # Criar configuração
        chatmode_configurator._create_copilot_config([chatmode_info])

        # Verificar arquivo criado
        config_file = (
            temp_project_dir / ".github" / "chatmodes" / ".copilot-config.json"
        )
        assert config_file.exists()

        # Verificar conteúdo
        with open(config_file, "r") as f:
            config_data = json.load(f)

        assert config_data["version"] == "1.0"
        assert len(config_data["chatmodes"]) == 1
        assert config_data["chatmodes"][0]["name"] == "test"
        assert config_data["total_chatmodes"] == 1

    def test_get_compatibility_summary(self, chatmode_configurator):
        """Testa geração de resumo de compatibilidade."""
        chatmodes = [
            ChatModeInfo(
                name="test1",
                source_path=Path("/test1"),
                target_path=Path("/target1"),
                compatibility=ChatModeCompatibility.FULLY_COMPATIBLE,
            ),
            ChatModeInfo(
                name="test2",
                source_path=Path("/test2"),
                target_path=Path("/target2"),
                compatibility=ChatModeCompatibility.MOSTLY_COMPATIBLE,
            ),
            ChatModeInfo(
                name="test3",
                source_path=Path("/test3"),
                target_path=Path("/target3"),
                compatibility=ChatModeCompatibility.INCOMPATIBLE,
            ),
        ]

        summary = chatmode_configurator._get_compatibility_summary(chatmodes)

        assert summary["fully_compatible"] == 1
        assert summary["mostly_compatible"] == 1
        assert summary["needs_adjustment"] == 0
        assert summary["incompatible"] == 1

    def test_validate_vscode_integration_no_vscode(
        self, chatmode_configurator
    ):
        """Testa validação sem VS Code configurado."""
        validation = chatmode_configurator.validate_vscode_integration()

        assert validation["vscode_detected"] is False
        assert validation["chatmodes_accessible"] is False
        assert validation["copilot_extension_available"] is None
        assert len(validation["issues"]) > 0
        assert "não encontrado" in validation["issues"][0]

    def test_validate_vscode_integration_with_vscode(
        self, chatmode_configurator, temp_project_dir
    ):
        """Testa validação com VS Code configurado."""
        # Criar estrutura VS Code
        vscode_dir = temp_project_dir / ".vscode"
        vscode_dir.mkdir()

        settings_file = vscode_dir / "settings.json"
        settings_file.write_text('{"editor.fontSize": 14}')

        # Criar diretório de chatmodes
        chatmode_configurator._ensure_chatmodes_directory()

        validation = chatmode_configurator.validate_vscode_integration()

        assert validation["vscode_detected"] is True
        assert validation["chatmodes_accessible"] is True
        assert validation["configuration_valid"] is True

        # Deve ter issue sobre falta de chatmodes
        assert len(validation["issues"]) >= 1
        assert "Nenhum ChatMode encontrado" in validation["issues"][0]

    def test_list_configured_chatmodes_empty(self, chatmode_configurator):
        """Testa listagem com diretório vazio."""
        configured = chatmode_configurator.list_configured_chatmodes()
        assert configured == []

    def test_list_configured_chatmodes_with_data(
        self, chatmode_configurator, temp_project_dir
    ):
        """Testa listagem com chatmodes configurados."""
        # Criar diretório e arquivo de chatmode
        chatmode_configurator._ensure_chatmodes_directory()

        chatmode_file = (
            temp_project_dir / ".github" / "chatmodes" / "test.chatmode.md"
        )
        chatmode_content = """# Test ChatMode

description: Test description

## Role
Test role
"""
        chatmode_file.write_text(chatmode_content)

        configured = chatmode_configurator.list_configured_chatmodes()

        assert len(configured) == 1
        assert configured[0]["name"] == "test"
        assert configured[0]["file"] == "test.chatmode.md"
        assert configured[0]["description"] == "Test description"
        assert configured[0]["compatibility"] in [
            "fully_compatible",
            "mostly_compatible",
            "needs_adjustment",
        ]
        assert configured[0]["size"] > 0

    def test_get_configuration_report(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Testa geração de relatório de configuração."""
        # Descobrir chatmodes
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )

        report = chatmode_configurator.get_configuration_report()

        assert report["discovered_chatmodes_count"] == 3
        assert (
            report["configured_chatmodes_count"] == 0
        )  # Ainda não configurados
        assert "chatmodes" in report["chatmodes_directory"]
        assert "vscode_integration" in report
        assert "compatibility_summary" in report
        assert "configuration_log" in report
        assert "chatmodes_details" in report

        # Verificar resumo de compatibilidade
        summary = report["compatibility_summary"]
        assert summary["fully_compatible"] >= 1
        assert summary["incompatible"] >= 1

    def test_chatmode_configurator_integration_full_cycle(
        self, chatmode_configurator, sample_chatmodes_dir
    ):
        """Teste de integração do ciclo completo."""
        # 1. Descobrir chatmodes
        chatmodes = chatmode_configurator.discover_chatmodes(
            sample_chatmodes_dir
        )
        assert len(chatmodes) == 3

        # 2. Configurar chatmodes
        result = chatmode_configurator.configure_chatmodes(chatmodes)
        assert result["configured_count"] >= 1

        # 3. Listar configurados
        configured = chatmode_configurator.list_configured_chatmodes()
        assert len(configured) == result["configured_count"]

        # 4. Validar integração VS Code
        validation = chatmode_configurator.validate_vscode_integration()
        assert validation["chatmodes_accessible"] is True

        # 5. Gerar relatório
        report = chatmode_configurator.get_configuration_report()
        assert (
            report["configured_chatmodes_count"] == result["configured_count"]
        )

        # 6. Verificar estrutura criada
        assert chatmode_configurator.chatmodes_dir.exists()
        config_file = (
            chatmode_configurator.chatmodes_dir / ".copilot-config.json"
        )
        assert config_file.exists()
