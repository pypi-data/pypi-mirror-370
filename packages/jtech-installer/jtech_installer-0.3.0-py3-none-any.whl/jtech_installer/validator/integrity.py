"""Integrity validator for JTECH™ Installer"""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ..core.exceptions import JTechInstallerException
from ..core.models import InstallationConfig


@dataclass
class IntegrityCheckResult:
    """Resultado de verificação de integridade"""

    component: str
    is_valid: bool
    expected_checksum: Optional[str] = None
    actual_checksum: Optional[str] = None
    error_message: Optional[str] = None


class IntegrityValidator:
    """Valida a integridade da instalação"""

    def __init__(self, config: InstallationConfig):
        self.config = config
        self.project_path = config.project_path
        self.jtech_core_path = self.project_path / ".jtech-core"

    def validate_all(self) -> bool:
        """Executa todas as validações de integridade"""
        results = []

        # Validar estrutura de diretórios
        results.extend(self._validate_directory_structure())

        # Validar arquivos de configuração
        results.extend(self._validate_config_files())

        # Validar agentes instalados
        results.extend(self._validate_agents())

        # Validar chatmodes
        results.extend(self._validate_chatmodes())

        # Verificar se há falhas
        failed_checks = [r for r in results if not r.is_valid]

        if failed_checks:
            for failure in failed_checks:
                print(f"❌ {failure.component}: {failure.error_message}")
            return False

        print(f"✅ Todos os {len(results)} checks de integridade passaram")
        return True

    def _validate_directory_structure(self) -> List[IntegrityCheckResult]:
        """Valida se a estrutura de diretórios está correta"""
        results = []

        required_dirs = [
            ".jtech-core",
            ".jtech-core/agents",
            ".jtech-core/chatmodes",
            ".jtech-core/templates",
            ".jtech-core/workflows",
            ".jtech-core/tasks",
            ".jtech-core/checklists",
            ".jtech-core/data",
            ".jtech-core/utils",
        ]

        for dir_path in required_dirs:
            full_path = self.project_path / dir_path
            if full_path.exists() and full_path.is_dir():
                results.append(
                    IntegrityCheckResult(
                        component=f"Directory {dir_path}", is_valid=True
                    )
                )
            else:
                results.append(
                    IntegrityCheckResult(
                        component=f"Directory {dir_path}",
                        is_valid=False,
                        error_message=f"Diretório {dir_path} não existe",
                    )
                )

        return results

    def _validate_config_files(self) -> List[IntegrityCheckResult]:
        """Valida arquivos de configuração críticos"""
        results = []

        # Verificar core-config.yml
        core_config = self.jtech_core_path / "core-config.yml"
        if core_config.exists():
            results.append(
                IntegrityCheckResult(
                    component="core-config.yml", is_valid=True
                )
            )
        else:
            results.append(
                IntegrityCheckResult(
                    component="core-config.yml",
                    is_valid=False,
                    error_message="Arquivo core-config.yml não encontrado",
                )
            )

        # Verificar .vscode/settings.json se VS Code habilitado
        if self.config.vs_code_integration:
            vscode_settings = self.project_path / ".vscode" / "settings.json"
            if vscode_settings.exists():
                results.append(
                    IntegrityCheckResult(
                        component=".vscode/settings.json", is_valid=True
                    )
                )
            else:
                results.append(
                    IntegrityCheckResult(
                        component=".vscode/settings.json",
                        is_valid=False,
                        error_message="Arquivo settings.json não encontrado",
                    )
                )

        return results

    def _validate_agents(self) -> List[IntegrityCheckResult]:
        """Valida integridade dos agentes instalados"""
        results = []
        agents_dir = self.jtech_core_path / "agents"

        if not agents_dir.exists():
            results.append(
                IntegrityCheckResult(
                    component="Agents directory",
                    is_valid=False,
                    error_message="Diretório de agentes não existe",
                )
            )
            return results

        # Verificar se há pelo menos alguns agentes básicos
        basic_agents = ["pm.md", "architect.md", "dev.md"]
        found_agents = 0

        for agent_file in basic_agents:
            agent_path = agents_dir / agent_file
            if agent_path.exists():
                found_agents += 1
                results.append(
                    IntegrityCheckResult(
                        component=f"Agent {agent_file}", is_valid=True
                    )
                )
            else:
                results.append(
                    IntegrityCheckResult(
                        component=f"Agent {agent_file}",
                        is_valid=False,
                        error_message=f"Agente {agent_file} não encontrado",
                    )
                )

        return results

    def _validate_chatmodes(self) -> List[IntegrityCheckResult]:
        """Valida chatmodes instalados"""
        results = []
        chatmodes_dir = self.project_path / ".github" / "chatmodes"

        if not chatmodes_dir.exists():
            results.append(
                IntegrityCheckResult(
                    component="Chatmodes directory",
                    is_valid=False,
                    error_message="Diretório .github/chatmodes não existe",
                )
            )
            return results

        # Contar arquivos .chatmode.md
        chatmode_files = list(chatmodes_dir.glob("*.chatmode.md"))

        if len(chatmode_files) > 0:
            results.append(
                IntegrityCheckResult(
                    component=f"Chatmodes ({len(chatmode_files)} arquivos)",
                    is_valid=True,
                )
            )
        else:
            results.append(
                IntegrityCheckResult(
                    component="Chatmodes",
                    is_valid=False,
                    error_message="Nenhum arquivo .chatmode.md encontrado",
                )
            )

        return results

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum SHA256 de um arquivo"""
        if not file_path.exists():
            raise JTechInstallerException(
                f"Arquivo não encontrado: {file_path}"
            )

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def verify_checksums(
        self, expected_checksums: Dict[str, str]
    ) -> List[IntegrityCheckResult]:
        """Verifica checksums de arquivos específicos"""
        results = []

        for relative_path, expected_checksum in expected_checksums.items():
            file_path = self.project_path / relative_path

            try:
                actual_checksum = self.calculate_file_checksum(file_path)
                is_valid = actual_checksum == expected_checksum

                results.append(
                    IntegrityCheckResult(
                        component=f"Checksum {relative_path}",
                        is_valid=is_valid,
                        expected_checksum=expected_checksum,
                        actual_checksum=actual_checksum,
                        error_message=(
                            None if is_valid else "Checksum não confere"
                        ),
                    )
                )
            except Exception as e:
                results.append(
                    IntegrityCheckResult(
                        component=f"Checksum {relative_path}",
                        is_valid=False,
                        error_message=str(e),
                    )
                )

        return results
