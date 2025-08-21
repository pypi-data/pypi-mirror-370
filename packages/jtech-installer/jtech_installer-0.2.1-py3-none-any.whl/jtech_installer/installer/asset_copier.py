"""
Asset copier for JTECH™ Installer - handles copying framework files
"""

import hashlib
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

from jtech_installer.core.exceptions import FileOperationError
from jtech_installer.core.models import (
    AssetInfo,
    InstallationConfig,
    InstallationProgress,
    TeamType,
)


class AssetCopier:
    """Gerencia cópia de assets do framework JTECH™ Core"""

    # Mapeamento de arquivos por tipo de equipe
    TEAM_AGENT_MAPPING = {
        TeamType.ALL: [
            "jtech-master.md",
            "jtech-orchestrator.md",
            "analyst.md",
            "pm.md",
            "po.md",
            "architect.md",
            "dev.md",
            "qa.md",
            "ux-expert.md",
            "sm.md",
        ],
        TeamType.FULLSTACK: [
            "jtech-orchestrator.md",
            "analyst.md",
            "pm.md",
            "ux-expert.md",
            "architect.md",
            "po.md",
            "dev.md",
        ],
        TeamType.NO_UI: [
            "jtech-orchestrator.md",
            "analyst.md",
            "pm.md",
            "architect.md",
            "dev.md",
            "qa.md",
        ],
        TeamType.IDE_MINIMAL: ["pm.md", "architect.md", "dev.md"],
    }

    def __init__(
        self,
        config: InstallationConfig,
        dry_run: bool = False,
        progress_callback: Optional[
            Callable[[InstallationProgress], None]
        ] = None,
    ):
        self.config = config
        self.dry_run = dry_run
        self.progress_callback = progress_callback
        self._determine_source_path()

    def _determine_source_path(self) -> None:
        """Determina o caminho fonte do framework"""
        if self.config.framework_source_path:
            self.framework_source = self.config.framework_source_path
        else:
            # Usar o framework do projeto atual como fonte
            current_project = Path(__file__).parent.parent.parent.parent.parent
            self.framework_source = current_project / ".jtech-core"

        if not self.framework_source.exists():
            raise FileOperationError(
                f"Framework source não encontrado: {self.framework_source}"
            )

    def copy_agents(self) -> List[AssetInfo]:
        """Copia agentes especializados baseado no tipo de equipe"""
        agent_files = self.TEAM_AGENT_MAPPING.get(
            self.config.team_type, self.TEAM_AGENT_MAPPING[TeamType.FULLSTACK]
        )

        assets_copied = []
        source_agents_dir = self.framework_source / "agents"
        target_agents_dir = self.config.project_path / ".jtech-core" / "agents"

        if not source_agents_dir.exists():
            raise FileOperationError(
                f"Diretório de agentes não encontrado: {source_agents_dir}"
            )

        # Criar diretório de destino se não existir
        if not self.dry_run:
            target_agents_dir.mkdir(parents=True, exist_ok=True)

        total_files = len(agent_files)

        for i, agent_file in enumerate(agent_files):
            source_file = source_agents_dir / agent_file
            target_file = target_agents_dir / agent_file

            if source_file.exists():
                # Calcular progresso
                if self.progress_callback:
                    progress = InstallationProgress(
                        current_phase="Copiando agentes",
                        total_phases=5,
                        current_phase_number=2,
                        files_processed=i,
                        total_files=total_files,
                        current_file=agent_file,
                    )
                    self.progress_callback(progress)

                # Copiar arquivo
                asset_info = self._copy_file(source_file, target_file)
                assets_copied.append(asset_info)
            else:
                # Log warning mas continue
                print(f"⚠️  Agente não encontrado: {source_file}")

        return assets_copied

    def copy_chatmodes(self) -> List[AssetInfo]:
        """Copia arquivos chatmode para .github/chatmodes/"""
        assets_copied = []
        source_chatmodes_dir = self.framework_source / "chatmodes"
        target_chatmodes_dir = (
            self.config.project_path / ".github" / "chatmodes"
        )

        if not source_chatmodes_dir.exists():
            # Tentar localização alternativa
            source_chatmodes_dir = (
                self.framework_source.parent / ".github" / "chatmodes"
            )

        if not source_chatmodes_dir.exists():
            print(f"⚠️  Diretório chatmodes não encontrado, pulando...")
            return assets_copied

        # Criar diretório de destino
        if not self.dry_run:
            target_chatmodes_dir.mkdir(parents=True, exist_ok=True)

        # Copiar todos os arquivos .chatmode.md
        chatmode_files = list(source_chatmodes_dir.glob("*.chatmode.md"))

        for i, source_file in enumerate(chatmode_files):
            target_file = target_chatmodes_dir / source_file.name

            if self.progress_callback:
                progress = InstallationProgress(
                    current_phase="Copiando chatmodes",
                    total_phases=5,
                    current_phase_number=3,
                    files_processed=i,
                    total_files=len(chatmode_files),
                    current_file=source_file.name,
                )
                self.progress_callback(progress)

            asset_info = self._copy_file(source_file, target_file)
            assets_copied.append(asset_info)

        return assets_copied

    def copy_templates_and_workflows(self) -> List[AssetInfo]:
        """Copia templates e workflows"""
        assets_copied = []

        # Diretórios a copiar
        directories_to_copy = [
            ("templates", "templates"),
            ("workflows", "workflows"),
            ("tasks", "tasks"),
            ("checklists", "checklists"),
            ("utils", "utils"),
            ("data", "data"),
        ]

        for source_dir, target_dir in directories_to_copy:
            source_path = self.framework_source / source_dir
            target_path = self.config.project_path / ".jtech-core" / target_dir

            if source_path.exists():
                assets = self._copy_directory(source_path, target_path)
                assets_copied.extend(assets)

        return assets_copied

    def copy_core_config(self) -> Optional[AssetInfo]:
        """Copia e adapta core-config.yml"""
        source_config = self.framework_source / "core-config.yml"
        target_config = (
            self.config.project_path / ".jtech-core" / "core-config.yml"
        )

        if source_config.exists():
            return self._copy_file(source_config, target_config)
        return None

    def _copy_file(self, source: Path, target: Path) -> AssetInfo:
        """Copia um arquivo individual com verificação"""
        try:
            # Calcular checksum do arquivo fonte
            checksum = (
                self._calculate_checksum(source) if source.exists() else None
            )

            if not self.dry_run:
                # Criar diretório pai se necessário
                target.parent.mkdir(parents=True, exist_ok=True)

                # Copiar arquivo
                shutil.copy2(source, target)

                # Verificar se foi copiado corretamente
                if not target.exists():
                    raise FileOperationError(
                        f"Falha ao copiar {source} -> {target}"
                    )

            return AssetInfo(
                source_path=source,
                target_path=target,
                file_type=source.suffix,
                checksum=checksum,
            )

        except Exception as e:
            raise FileOperationError(f"Erro ao copiar {source}: {e}")

    def _copy_directory(self, source: Path, target: Path) -> List[AssetInfo]:
        """Copia um diretório completo"""
        assets_copied = []

        if not self.dry_run:
            target.mkdir(parents=True, exist_ok=True)

        # Copiar todos os arquivos do diretório
        for source_file in source.rglob("*"):
            if source_file.is_file():
                relative_path = source_file.relative_to(source)
                target_file = target / relative_path

                asset_info = self._copy_file(source_file, target_file)
                assets_copied.append(asset_info)

        return assets_copied

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum SHA256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def copy_all(self) -> Dict[str, List[AssetInfo]]:
        """Copia todos os assets necessários"""
        all_assets = {
            "agents": self.copy_agents(),
            "chatmodes": self.copy_chatmodes(),
            "templates_workflows": self.copy_templates_and_workflows(),
        }

        # Copiar core-config separadamente
        core_config = self.copy_core_config()
        if core_config:
            all_assets["core_config"] = [core_config]

        return all_assets
