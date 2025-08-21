#!/usr/bin/env python3
"""
Configurador de ChatModes para GitHub Copilot
Copia e configura chatmodes para integração com VS Code e GitHub Copilot.
"""

import re
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.models import InstallationConfig


class ChatModeCompatibility(Enum):
    """Níveis de compatibilidade com GitHub Copilot."""

    FULLY_COMPATIBLE = "fully_compatible"
    MOSTLY_COMPATIBLE = "mostly_compatible"
    NEEDS_ADJUSTMENT = "needs_adjustment"
    INCOMPATIBLE = "incompatible"


@dataclass
class ChatModeInfo:
    """Informações sobre um ChatMode."""

    name: str
    source_path: Path
    target_path: Path
    description: str = ""
    version: str = "1.0"
    compatibility: ChatModeCompatibility = (
        ChatModeCompatibility.FULLY_COMPATIBLE
    )
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_issues: List[str] = field(default_factory=list)
    installed: bool = False


class ChatModeConfigurator:
    """
    Configura ChatModes para GitHub Copilot.

    Responsável por:
    - Descobrir arquivos *.chatmode.md
    - Validar compatibilidade com GitHub Copilot
    - Copiar para .github/chatmodes/
    - Configurar permissões apropriadas
    - Verificar integração com VS Code
    """

    def __init__(self, config: InstallationConfig):
        """Inicializa o configurador de ChatModes."""
        self.config = config
        self.project_path = Path(config.project_path)
        self.github_dir = self.project_path / ".github"
        self.chatmodes_dir = self.github_dir / "chatmodes"

        self.discovered_chatmodes: List[ChatModeInfo] = []
        self.installation_log: List[str] = []

        # Padrões para validação de compatibilidade
        self.copilot_patterns = {
            "required_headers": [
                r"^#\s+.+",  # Título principal
                r"description:",  # Descrição
            ],
            "recommended_sections": [
                r"##\s+(role|context|instructions)",
                r"##\s+(capabilities|limitations)",
                r"##\s+(examples|usage)",
            ],
            "compatibility_issues": [
                r"@[a-zA-Z]+\s*\(",  # Funções não suportadas
                r"\${[^}]+}",  # Variáveis não suportadas
                r"<script",  # Scripts não permitidos
            ],
        }

    def discover_chatmodes(
        self, source_dir: Optional[Path] = None
    ) -> List[ChatModeInfo]:
        """
        Descobre ChatModes disponíveis para configuração.

        Args:
            source_dir: Diretório fonte dos chatmodes (opcional)

        Returns:
            Lista de chatmodes descobertos
        """
        if source_dir is None:
            # Procurar chatmodes no próprio projeto
            search_paths = [
                self.project_path / "chatmodes",
                self.project_path / ".github" / "chatmodes",
                self.project_path / "agents" / "chatmodes",
            ]
        else:
            search_paths = [source_dir]

        chatmodes = []

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # Buscar arquivos *.chatmode.md
            chatmode_pattern = "**/*.chatmode.md"
            for chatmode_file in search_path.glob(chatmode_pattern):
                chatmode_info = self._parse_chatmode_file(chatmode_file)
                if chatmode_info:
                    chatmodes.append(chatmode_info)

        self.discovered_chatmodes = chatmodes
        msg = f"Descobertos {len(chatmodes)} chatmodes para configuração"
        self.installation_log.append(msg)
        return chatmodes

    def _parse_chatmode_file(self, file_path: Path) -> Optional[ChatModeInfo]:
        """
        Parseia arquivo de ChatMode e extrai informações.

        Args:
            file_path: Caminho do arquivo

        Returns:
            ChatModeInfo ou None se erro
        """
        try:
            # Extrair nome do arquivo
            name = file_path.stem.replace(".chatmode", "")

            # Determinar caminho alvo
            target_path = self.chatmodes_dir / file_path.name

            # Ler e analisar conteúdo
            content = file_path.read_text(encoding="utf-8")

            # Extrair metadados
            metadata = self._extract_chatmode_metadata(content)
            description = metadata.get("description", f"ChatMode - {name}")
            version = metadata.get("version", "1.0")

            # Validar compatibilidade
            compatibility, issues = self._validate_copilot_compatibility(
                content
            )

            return ChatModeInfo(
                name=name,
                source_path=file_path,
                target_path=target_path,
                description=description,
                version=str(version),
                compatibility=compatibility,
                metadata=metadata,
                validation_issues=issues,
            )

        except Exception as e:
            msg = f"Erro ao parsear ChatMode {file_path}: {e}"
            self.installation_log.append(msg)
            return None

    def _extract_chatmode_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extrai metadados do ChatMode.

        Args:
            content: Conteúdo do arquivo

        Returns:
            Dicionário com metadados
        """
        metadata = {}

        # Extrair título
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        # Extrair descrição (várias formas possíveis)
        desc_patterns = [
            r"^description:\s*(.+)$",
            r"^##\s*description\s*\n(.+?)(?=\n##|\n#|\Z)",
            r"^\*\*description:\*\*\s*(.+)$",
        ]

        for pattern in desc_patterns:
            desc_match = re.search(
                pattern, content, re.MULTILINE | re.IGNORECASE
            )
            if desc_match:
                metadata["description"] = desc_match.group(1).strip()
                break

        # Extrair versão
        version_match = re.search(
            r"^version:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE
        )
        if version_match:
            metadata["version"] = version_match.group(1).strip()

        # Extrair tags/categorias
        tags_match = re.search(
            r"^tags:\s*(.+)$", content, re.MULTILINE | re.IGNORECASE
        )
        if tags_match:
            tags_str = tags_match.group(1).strip()
            metadata["tags"] = [tag.strip() for tag in tags_str.split(",")]

        return metadata

    def _validate_copilot_compatibility(
        self, content: str
    ) -> tuple[ChatModeCompatibility, List[str]]:
        """
        Valida compatibilidade com GitHub Copilot.

        Args:
            content: Conteúdo do ChatMode

        Returns:
            Tupla com nível de compatibilidade e lista de issues
        """
        issues = []

        # Verificar cabeçalhos obrigatórios
        missing_headers = []
        for pattern in self.copilot_patterns["required_headers"]:
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing_headers.append(pattern)

        if missing_headers:
            msg = f"Cabeçalhos obrigatórios faltando: {missing_headers}"
            issues.append(msg)

        # Verificar seções recomendadas
        missing_sections = 0
        for pattern in self.copilot_patterns["recommended_sections"]:
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing_sections += 1

        if missing_sections > 1:
            issues.append(f"Faltam {missing_sections} seções recomendadas")

        # Verificar problemas de compatibilidade
        compatibility_problems = []
        for pattern in self.copilot_patterns["compatibility_issues"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                compatibility_problems.extend(matches)

        if compatibility_problems:
            issues.append(f"Elementos incompatíveis: {compatibility_problems}")

        # Determinar nível de compatibilidade
        if not issues:
            compatibility = ChatModeCompatibility.FULLY_COMPATIBLE
        elif len(issues) == 1 and "seções recomendadas" in issues[0]:
            compatibility = ChatModeCompatibility.MOSTLY_COMPATIBLE
        elif missing_headers or compatibility_problems:
            compatibility = ChatModeCompatibility.INCOMPATIBLE
        else:
            compatibility = ChatModeCompatibility.NEEDS_ADJUSTMENT

        return compatibility, issues

    def configure_chatmodes(
        self,
        chatmodes: Optional[List[ChatModeInfo]] = None,
        force_install: bool = False,
    ) -> Dict[str, Any]:
        """
        Configura ChatModes para GitHub Copilot.

        Args:
            chatmodes: Lista específica de chatmodes (opcional)
            force_install: Instalar mesmo com problemas de compatibilidade

        Returns:
            Resultado da configuração
        """
        if chatmodes is None:
            chatmodes = self.discovered_chatmodes

        if not chatmodes:
            return {
                "success": False,
                "error": "Nenhum ChatMode descoberto para configuração",
                "configured_count": 0,
                "skipped_count": 0,
                "failed_count": 0,
            }

        # Criar diretório de destino
        self._ensure_chatmodes_directory()

        configured_chatmodes = []
        skipped_chatmodes = []
        failed_chatmodes = []

        for chatmode in chatmodes:
            try:
                # Verificar compatibilidade
                incompatible = (
                    chatmode.compatibility
                    == ChatModeCompatibility.INCOMPATIBLE
                )
                if not force_install and incompatible:
                    skipped_chatmodes.append(chatmode)
                    msg = f"Pulado (incompatível): {chatmode.name}"
                    self.installation_log.append(msg)
                    continue

                # Copiar arquivo
                shutil.copy2(chatmode.source_path, chatmode.target_path)

                # Configurar permissões
                self._set_chatmode_permissions(chatmode.target_path)

                chatmode.installed = True
                configured_chatmodes.append(chatmode)
                msg = (
                    f"Configurado: {chatmode.name} "
                    f"({chatmode.compatibility.value})"
                )
                self.installation_log.append(msg)

            except Exception as e:
                failed_chatmodes.append(chatmode)
                msg = f"Falha na configuração de {chatmode.name}: {e}"
                self.installation_log.append(msg)

        # Criar arquivo de configuração do GitHub Copilot se necessário
        if configured_chatmodes:
            self._create_copilot_config(configured_chatmodes)

        return {
            "success": len(failed_chatmodes) == 0,
            "configured_count": len(configured_chatmodes),
            "skipped_count": len(skipped_chatmodes),
            "failed_count": len(failed_chatmodes),
            "configured_chatmodes": [cm.name for cm in configured_chatmodes],
            "skipped_chatmodes": [cm.name for cm in skipped_chatmodes],
            "failed_chatmodes": [cm.name for cm in failed_chatmodes],
            "compatibility_summary": self._get_compatibility_summary(
                chatmodes
            ),
            "log": self.installation_log.copy(),
        }

    def _ensure_chatmodes_directory(self):
        """Garante que diretório de chatmodes existe com permissões."""
        # Criar .github se não existir
        self.github_dir.mkdir(exist_ok=True)

        # Criar chatmodes com permissões apropriadas
        self.chatmodes_dir.mkdir(exist_ok=True)

        # Configurar permissões (755 para compatibilidade GitHub)
        if hasattr(self.chatmodes_dir, "chmod"):
            self.chatmodes_dir.chmod(0o755)

    def _set_chatmode_permissions(self, file_path: Path):
        """
        Configura permissões apropriadas para arquivo ChatMode.

        Args:
            file_path: Caminho do arquivo
        """
        if hasattr(file_path, "chmod"):
            # Permissão 644 (leitura para todos, escrita para dono)
            file_path.chmod(0o644)

    def _create_copilot_config(self, configured_chatmodes: List[ChatModeInfo]):
        """
        Cria arquivo de configuração para GitHub Copilot.

        Args:
            configured_chatmodes: Lista de chatmodes configurados
        """
        try:
            config_file = self.chatmodes_dir / ".copilot-config.json"

            config_data = {
                "version": "1.0",
                "chatmodes": [
                    {
                        "name": cm.name,
                        "file": cm.target_path.name,
                        "description": cm.description,
                        "compatibility": cm.compatibility.value,
                        "version": cm.version,
                    }
                    for cm in configured_chatmodes
                ],
                "configured_at": None,  # Seria preenchido com timestamp
                "total_chatmodes": len(configured_chatmodes),
            }

            import json

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            msg = (
                f"Configuração do Copilot criada: "
                f"{len(configured_chatmodes)} chatmodes"
            )
            self.installation_log.append(msg)

        except Exception as e:
            msg = f"Erro ao criar configuração do Copilot: {e}"
            self.installation_log.append(msg)

    def _get_compatibility_summary(
        self, chatmodes: List[ChatModeInfo]
    ) -> Dict[str, int]:
        """
        Gera resumo de compatibilidade dos chatmodes.

        Args:
            chatmodes: Lista de chatmodes

        Returns:
            Resumo por nível de compatibilidade
        """
        summary = {}
        for compatibility in ChatModeCompatibility:
            count = len(
                [cm for cm in chatmodes if cm.compatibility == compatibility]
            )
            summary[compatibility.value] = count

        return summary

    def validate_vscode_integration(self) -> Dict[str, Any]:
        """
        Valida integração com VS Code.

        Returns:
            Resultado da validação
        """
        validation = {
            "vscode_detected": False,
            "copilot_extension_available": False,
            "chatmodes_accessible": False,
            "configuration_valid": True,
            "issues": [],
        }

        try:
            # Verificar se VS Code está configurado no projeto
            vscode_dir = self.project_path / ".vscode"
            if vscode_dir.exists():
                validation["vscode_detected"] = True

                # Verificar configurações específicas
                settings_file = vscode_dir / "settings.json"
                if settings_file.exists():
                    # Aqui poderia verificar configurações específicas
                    pass

            # Verificar se diretório de chatmodes está acessível
            if self.chatmodes_dir.exists() and self.chatmodes_dir.is_dir():
                validation["chatmodes_accessible"] = True

                # Verificar se há chatmodes configurados
                chatmode_files = list(self.chatmodes_dir.glob("*.chatmode.md"))
                if not chatmode_files:
                    validation["issues"].append(
                        "Nenhum ChatMode encontrado em .github/chatmodes/"
                    )
            else:
                validation["issues"].append(
                    "Diretório .github/chatmodes/ não encontrado"
                )

            # Nota: Verificação real da extensão Copilot exigiria
            # acesso ao VS Code, que não é possível em ambiente de teste
            validation["copilot_extension_available"] = None  # Indeterminado

        except Exception as e:
            validation["configuration_valid"] = False
            validation["issues"].append(f"Erro na validação: {e}")

        return validation

    def list_configured_chatmodes(self) -> List[Dict[str, Any]]:
        """
        Lista chatmodes configurados.

        Returns:
            Lista de chatmodes configurados
        """
        configured = []

        if not self.chatmodes_dir.exists():
            return configured

        for chatmode_file in self.chatmodes_dir.glob("*.chatmode.md"):
            try:
                content = chatmode_file.read_text(encoding="utf-8")
                metadata = self._extract_chatmode_metadata(content)
                compatibility, issues = self._validate_copilot_compatibility(
                    content
                )

                configured.append(
                    {
                        "name": chatmode_file.stem.replace(".chatmode", ""),
                        "file": chatmode_file.name,
                        "description": metadata.get("description", ""),
                        "version": metadata.get("version", "1.0"),
                        "compatibility": compatibility.value,
                        "issues": issues,
                        "size": chatmode_file.stat().st_size,
                        "path": str(
                            chatmode_file.relative_to(self.project_path)
                        ),
                    }
                )

            except Exception as e:
                msg = f"Erro ao processar {chatmode_file}: {e}"
                self.installation_log.append(msg)

        return configured

    def get_configuration_report(self) -> Dict[str, Any]:
        """
        Gera relatório detalhado da configuração.

        Returns:
            Relatório de configuração
        """
        return {
            "discovered_chatmodes_count": len(self.discovered_chatmodes),
            "configured_chatmodes_count": len(
                self.list_configured_chatmodes()
            ),
            "chatmodes_directory": str(self.chatmodes_dir),
            "vscode_integration": self.validate_vscode_integration(),
            "compatibility_summary": self._get_compatibility_summary(
                self.discovered_chatmodes
            ),
            "configuration_log": self.installation_log,
            "chatmodes_details": self.list_configured_chatmodes(),
        }
