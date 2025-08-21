#!/usr/bin/env python3
"""
Instalador de Agentes Especializados JTECH™ Core
Copia e configura todos os agentes especializados do framework.
"""

import hashlib
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..core.models import InstallationConfig


class AgentType(Enum):
    """Tipos de agentes suportados."""

    CHATMODE = "chatmode"
    TEMPLATE = "template"
    WORKFLOW = "workflow"
    SPECIALIST = "specialist"


@dataclass
class AgentInfo:
    """Informações sobre um agente."""

    name: str
    type: AgentType
    source_path: Path
    target_path: Path
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    installed: bool = False


class AgentInstaller:
    """
    Gerencia instalação de agentes especializados JTECH™.

    Responsável por:
    - Descobrir agentes disponíveis
    - Copiar arquivos mantendo estrutura
    - Verificar integridade pós-instalação
    - Gerenciar metadados de agentes
    """

    def __init__(self, config: InstallationConfig):
        """Inicializa o instalador de agentes."""
        self.config = config
        self.project_path = Path(config.project_path)
        self.jtech_core_path = self.project_path / ".jtech-core"
        self.agents_path = self.jtech_core_path / "agents"
        self.agents_registry = self.jtech_core_path / "registry" / "agents.yml"

        # Mapeamento de diretórios de agentes
        self.agent_directories = {
            AgentType.CHATMODE: "chatmodes",
            AgentType.TEMPLATE: "templates",
            AgentType.WORKFLOW: "workflows",
            AgentType.SPECIALIST: "specialists",
        }

        self.discovered_agents: List[AgentInfo] = []
        self.installation_log: List[str] = []

    def discover_agents(
        self, source_dir: Optional[Path] = None
    ) -> List[AgentInfo]:
        """
        Descobre agentes disponíveis para instalação.

        Args:
            source_dir: Diretório fonte dos agentes (opcional)

        Returns:
            Lista de agentes descobertos
        """
        if source_dir is None:
            # Procurar agentes no próprio projeto
            source_dir = self.project_path / "agents"

        if not source_dir.exists():
            msg = f"Diretório de agentes não encontrado: {source_dir}"
            self.installation_log.append(msg)
            return []

        agents = []

        # Buscar ChatModes (.chatmode.md)
        chatmode_pattern = "**/*.chatmode.md"
        for chatmode_file in source_dir.glob(chatmode_pattern):
            agent_info = self._parse_agent_file(
                chatmode_file, AgentType.CHATMODE
            )
            if agent_info:
                agents.append(agent_info)

        # Buscar Templates (.md)
        template_pattern = "**/templates/**/*.md"
        for template_file in source_dir.glob(template_pattern):
            agent_info = self._parse_agent_file(
                template_file, AgentType.TEMPLATE
            )
            if agent_info:
                agents.append(agent_info)

        # Buscar Workflows (.yml, .yaml)
        workflow_patterns = ["**/workflows/**/*.yml", "**/workflows/**/*.yaml"]
        for workflow_pattern in workflow_patterns:
            for workflow_file in source_dir.glob(workflow_pattern):
                agent_info = self._parse_agent_file(
                    workflow_file, AgentType.WORKFLOW
                )
                if agent_info:
                    agents.append(agent_info)

        # Buscar Especialistas (outros .md)
        specialist_pattern = "**/*.md"
        for specialist_file in source_dir.glob(specialist_pattern):
            # Excluir chatmodes e templates já processados
            if (
                ".chatmode." not in specialist_file.name
                and "/templates/" not in str(specialist_file)
            ):
                agent_info = self._parse_agent_file(
                    specialist_file, AgentType.SPECIALIST
                )
                if agent_info:
                    agents.append(agent_info)

        self.discovered_agents = agents
        msg = f"Descobertos {len(agents)} agentes para instalação"
        self.installation_log.append(msg)
        return agents

    def _parse_agent_file(
        self, file_path: Path, agent_type: AgentType
    ) -> Optional[AgentInfo]:
        """
        Parseia arquivo de agente e extrai metadados.

        Args:
            file_path: Caminho do arquivo
            agent_type: Tipo do agente

        Returns:
            AgentInfo ou None se erro
        """
        try:
            # Calcular checksum
            checksum = self._calculate_checksum(file_path)

            # Determinar nome e caminho alvo
            name = file_path.stem
            if agent_type == AgentType.CHATMODE:
                name = name.replace(".chatmode", "")
                target_subdir = "chatmodes"
            else:
                target_subdir = self.agent_directories[agent_type]

            target_path = self.agents_path / target_subdir / file_path.name

            # Extrair metadados do arquivo
            metadata = self._extract_metadata(file_path)
            description = metadata.get(
                "description", f"{agent_type.value} - {name}"
            )

            return AgentInfo(
                name=name,
                type=agent_type,
                source_path=file_path,
                target_path=target_path,
                description=description,
                metadata=metadata,
                checksum=checksum,
            )

        except Exception as e:
            self.installation_log.append(f"Erro ao parsear {file_path}: {e}")
            return None

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrai metadados do arquivo de agente.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com metadados
        """
        metadata = {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Buscar por frontmatter YAML
            if content.startswith("---"):
                end_pos = content.find("---", 3)
                if end_pos > 0:
                    frontmatter = content[3:end_pos].strip()
                    try:
                        metadata = yaml.safe_load(frontmatter) or {}
                    except yaml.YAMLError:
                        pass

            # Extrair informações básicas do conteúdo
            lines = content.split("\n")
            for line in lines[:10]:  # Primeiras 10 linhas
                line = line.strip()
                if line.startswith("# "):
                    metadata.setdefault("title", line[2:].strip())
                elif "description:" in line.lower():
                    desc = line.split(":", 1)[1].strip()
                    metadata.setdefault("description", desc)
                elif "version:" in line.lower():
                    ver = line.split(":", 1)[1].strip()
                    metadata.setdefault("version", ver)

            return metadata

        except Exception as e:
            msg = f"Erro ao extrair metadados de {file_path}: {e}"
            self.installation_log.append(msg)
            return {}

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calcula checksum SHA256 do arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Checksum hexadecimal
        """
        sha256_hash = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

    def install_agents(
        self,
        agents: Optional[List[AgentInfo]] = None,
        verify_integrity: bool = True,
    ) -> Dict[str, Any]:
        """
        Instala agentes especializados.

        Args:
            agents: Lista específica de agentes (opcional)
            verify_integrity: Verificar integridade após instalação

        Returns:
            Resultado da instalação
        """
        if agents is None:
            agents = self.discovered_agents

        if not agents:
            return {
                "success": False,
                "error": "Nenhum agente descoberto para instalação",
                "installed_count": 0,
                "failed_count": 0,
            }

        # Criar diretórios necessários
        self._ensure_agent_directories()

        installed_agents = []
        failed_agents = []

        for agent in agents:
            try:
                # Copiar arquivo
                target_dir = agent.target_path.parent
                target_dir.mkdir(parents=True, exist_ok=True)

                shutil.copy2(agent.source_path, agent.target_path)

                # Verificar integridade se solicitado
                if verify_integrity:
                    if not self._verify_agent_integrity(agent):
                        failed_agents.append(agent)
                        continue

                agent.installed = True
                installed_agents.append(agent)
                msg = f"Instalado: {agent.name} ({agent.type.value})"
                self.installation_log.append(msg)

            except Exception as e:
                failed_agents.append(agent)
                msg = f"Falha na instalação de {agent.name}: {e}"
                self.installation_log.append(msg)

        # Atualizar registro de agentes
        if installed_agents:
            self._update_agents_registry(installed_agents)

        return {
            "success": len(failed_agents) == 0,
            "installed_count": len(installed_agents),
            "failed_count": len(failed_agents),
            "installed_agents": [a.name for a in installed_agents],
            "failed_agents": [a.name for a in failed_agents],
            "log": self.installation_log.copy(),
        }

    def _ensure_agent_directories(self):
        """Garante que diretórios de agentes existem."""
        for agent_type, subdir in self.agent_directories.items():
            dir_path = self.agents_path / subdir
            dir_path.mkdir(parents=True, exist_ok=True)

    def _verify_agent_integrity(self, agent: AgentInfo) -> bool:
        """
        Verifica integridade do agente instalado.

        Args:
            agent: Informações do agente

        Returns:
            True se íntegro
        """
        if not agent.target_path.exists():
            return False

        # Verificar checksum
        installed_checksum = self._calculate_checksum(agent.target_path)
        return installed_checksum == agent.checksum

    def _update_agents_registry(self, installed_agents: List[AgentInfo]):
        """
        Atualiza registro de agentes instalados.

        Args:
            installed_agents: Lista de agentes instalados
        """
        try:
            # Criar diretório do registro
            registry_dir = self.agents_registry.parent
            registry_dir.mkdir(parents=True, exist_ok=True)

            # Ler registro existente ou criar novo
            registry_data = {}
            if self.agents_registry.exists():
                with open(self.agents_registry, "r", encoding="utf-8") as f:
                    registry_data = yaml.safe_load(f) or {}

            # Adicionar agentes instalados
            if "agents" not in registry_data:
                registry_data["agents"] = {}

            for agent in installed_agents:
                relative_path = agent.target_path.relative_to(
                    self.project_path
                )
                registry_data["agents"][agent.name] = {
                    "type": agent.type.value,
                    "installed_path": str(relative_path),
                    "checksum": agent.checksum,
                    "metadata": agent.metadata,
                    # Será preenchido por outro sistema se necessário
                    "installed_at": None,
                }

            # Salvar registro atualizado
            with open(self.agents_registry, "w", encoding="utf-8") as f:
                yaml.dump(
                    registry_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )

            msg = (
                f"Registro de agentes atualizado: {len(installed_agents)} "
                "entradas"
            )
            self.installation_log.append(msg)

        except Exception as e:
            msg = f"Erro ao atualizar registro de agentes: {e}"
            self.installation_log.append(msg)

    def list_installed_agents(self) -> List[Dict[str, Any]]:
        """
        Lista agentes instalados.

        Returns:
            Lista de agentes instalados
        """
        installed = []

        if not self.agents_registry.exists():
            return installed

        try:
            with open(self.agents_registry, "r", encoding="utf-8") as f:
                registry_data = yaml.safe_load(f) or {}

            agents_data = registry_data.get("agents", {})
            for name, info in agents_data.items():
                installed.append(
                    {
                        "name": name,
                        "type": info.get("type"),
                        "path": info.get("installed_path"),
                        "checksum": info.get("checksum"),
                        "metadata": info.get("metadata", {}),
                    }
                )

            return installed

        except Exception as e:
            msg = f"Erro ao listar agentes instalados: {e}"
            self.installation_log.append(msg)
            return []

    def get_installation_report(self) -> Dict[str, Any]:
        """
        Gera relatório detalhado da instalação.

        Returns:
            Relatório de instalação
        """
        return {
            "discovered_agents_count": len(self.discovered_agents),
            "agents_by_type": {
                agent_type.value: len(
                    [a for a in self.discovered_agents if a.type == agent_type]
                )
                for agent_type in AgentType
            },
            "installation_log": self.installation_log,
            "installed_agents": self.list_installed_agents(),
            "target_directories": {
                agent_type.value: str(self.agents_path / subdir)
                for agent_type, subdir in self.agent_directories.items()
            },
        }
