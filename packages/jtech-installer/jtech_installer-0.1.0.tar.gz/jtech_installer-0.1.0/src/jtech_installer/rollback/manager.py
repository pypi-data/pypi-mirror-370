"""Sistema de rollback para JTECH™ Core Installer."""

import json
import shutil
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.exceptions import JTechInstallerException
from ..core.models import InstallationConfig


class RollbackType(Enum):
    """Tipos de rollback disponíveis."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"


class BackupType(Enum):
    """Tipos de backup."""

    FULL = "full"
    INCREMENTAL = "incremental"
    CONFIG_ONLY = "config_only"


@dataclass
class BackupEntry:
    """Entrada de backup individual."""

    source_path: str
    backup_path: str
    file_type: str
    timestamp: str
    checksum: Optional[str] = None


@dataclass
class RollbackPoint:
    """Ponto de rollback com informações completas."""

    id: str
    timestamp: str
    config: Dict[str, Any]
    backup_type: BackupType
    backup_entries: List[BackupEntry]
    installation_state: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class RollbackResult:
    """Resultado de operação de rollback."""

    success: bool
    rollback_point_id: str
    restored_files: List[str]
    failed_files: List[str]
    errors: List[str]
    warnings: List[str]
    duration: float


class RollbackManager:
    """Gerenciador de rollback para instalações JTECH™ Core."""

    def __init__(
        self, config: InstallationConfig, backup_dir: Optional[Path] = None
    ):
        """
        Inicializa o gerenciador de rollback.

        Args:
            config: Configuração de instalação
            backup_dir: Diretório para backups (opcional)
        """
        self.config = config
        self.project_path = config.project_path
        self.backup_dir = backup_dir or (
            self.project_path / ".jtech-core" / "backups"
        )
        self.rollback_log_file = self.backup_dir / "rollback.log"
        self.rollback_points_file = self.backup_dir / "rollback_points.json"

        # Garantir que diretório de backup existe
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_rollback_point(
        self,
        backup_type: BackupType = BackupType.FULL,
        description: Optional[str] = None,
    ) -> str:
        """
        Cria um ponto de rollback.

        Args:
            backup_type: Tipo de backup a ser criado
            description: Descrição opcional do ponto de rollback

        Returns:
            ID do ponto de rollback criado
        """
        rollback_id = self._generate_rollback_id()
        timestamp = datetime.now().isoformat()

        self._log_operation(
            f"Criando ponto de rollback {rollback_id} ({backup_type.value})"
        )

        try:
            # Criar backup baseado no tipo
            backup_entries = self._create_backup(rollback_id, backup_type)

            # Capturar estado atual da instalação
            installation_state = self._capture_installation_state()

            # Criar ponto de rollback
            rollback_point = RollbackPoint(
                id=rollback_id,
                timestamp=timestamp,
                config=self._serialize_config(self.config),
                backup_type=backup_type,
                backup_entries=backup_entries,
                installation_state=installation_state,
                metadata={
                    "description": description
                    or f"Rollback point {rollback_id}",
                    "created_by": "JTECH™ Installer",
                    "backup_size": self._calculate_backup_size(backup_entries),
                    "file_count": len(backup_entries),
                },
            )

            # Salvar ponto de rollback
            self._save_rollback_point(rollback_point)

            self._log_operation(
                f"Ponto de rollback {rollback_id} criado com sucesso "
                f"({len(backup_entries)} arquivos)"
            )

            return rollback_id

        except Exception as e:
            self._log_operation(
                f"Erro ao criar ponto de rollback {rollback_id}: {e}",
                level="ERROR",
            )
            raise JTechInstallerException(
                f"Falha ao criar ponto de rollback: {e}"
            )

    def rollback_to_point(
        self,
        rollback_id: str,
        rollback_type: RollbackType = RollbackType.MANUAL,
    ) -> RollbackResult:
        """
        Executa rollback para um ponto específico.

        Args:
            rollback_id: ID do ponto de rollback
            rollback_type: Tipo de rollback

        Returns:
            Resultado do rollback
        """
        start_time = time.time()
        restored_files = []
        failed_files = []
        errors = []
        warnings = []

        self._log_operation(
            f"Iniciando rollback para ponto {rollback_id} ({rollback_type.value})"
        )

        try:
            # Carregar ponto de rollback
            rollback_point = self._load_rollback_point(rollback_id)
            if not rollback_point:
                raise JTechInstallerException(
                    f"Ponto de rollback {rollback_id} não encontrado"
                )

            # Criar ponto de segurança antes do rollback
            if rollback_type != RollbackType.EMERGENCY:
                safety_point = self.create_rollback_point(
                    BackupType.CONFIG_ONLY,
                    f"Safety point before rollback to {rollback_id}",
                )
                self._log_operation(
                    f"Ponto de segurança criado: {safety_point}"
                )

            # Executar rollback
            for entry in rollback_point.backup_entries:
                try:
                    self._restore_file(entry)
                    restored_files.append(entry.source_path)
                except Exception as e:
                    failed_files.append(entry.source_path)
                    errors.append(
                        f"Falha ao restaurar {entry.source_path}: {e}"
                    )

            # Restaurar estado da instalação
            try:
                self._restore_installation_state(
                    rollback_point.installation_state
                )
            except Exception as e:
                warnings.append(
                    f"Falha ao restaurar estado completo da instalação: {e}"
                )

            # Verificar integridade pós-rollback
            integrity_issues = self._verify_rollback_integrity(rollback_point)
            if integrity_issues:
                warnings.extend(integrity_issues)

            duration = time.time() - start_time
            success = len(failed_files) == 0

            result = RollbackResult(
                success=success,
                rollback_point_id=rollback_id,
                restored_files=restored_files,
                failed_files=failed_files,
                errors=errors,
                warnings=warnings,
                duration=duration,
            )

            status = "sucesso" if success else "parcial"
            self._log_operation(
                f"Rollback para {rollback_id} concluído com {status} "
                f"({len(restored_files)} restaurados, {len(failed_files)} falharam)"
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Erro durante rollback: {e}"
            self._log_operation(error_msg, level="ERROR")

            return RollbackResult(
                success=False,
                rollback_point_id=rollback_id,
                restored_files=restored_files,
                failed_files=failed_files,
                errors=[error_msg],
                warnings=warnings,
                duration=duration,
            )

    def list_rollback_points(self) -> List[RollbackPoint]:
        """
        Lista todos os pontos de rollback disponíveis.

        Returns:
            Lista de pontos de rollback
        """
        try:
            if not self.rollback_points_file.exists():
                return []

            with open(self.rollback_points_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            rollback_points = []
            for point_data in data.get("rollback_points", []):
                # Converter backup_entries
                backup_entries = [
                    BackupEntry(**entry)
                    for entry in point_data["backup_entries"]
                ]

                point = RollbackPoint(
                    id=point_data["id"],
                    timestamp=point_data["timestamp"],
                    config=point_data["config"],
                    backup_type=BackupType(point_data["backup_type"]),
                    backup_entries=backup_entries,
                    installation_state=point_data["installation_state"],
                    metadata=point_data["metadata"],
                )
                rollback_points.append(point)

            # Ordenar por timestamp (mais recente primeiro)
            rollback_points.sort(key=lambda x: x.timestamp, reverse=True)

            return rollback_points

        except Exception as e:
            self._log_operation(
                f"Erro ao listar pontos de rollback: {e}", level="ERROR"
            )
            return []

    def delete_rollback_point(self, rollback_id: str) -> bool:
        """
        Remove um ponto de rollback.

        Args:
            rollback_id: ID do ponto de rollback

        Returns:
            True se removido com sucesso
        """
        try:
            rollback_points = self.list_rollback_points()
            point_to_delete = None

            for point in rollback_points:
                if point.id == rollback_id:
                    point_to_delete = point
                    break

            if not point_to_delete:
                return False

            # Remover arquivos de backup
            for entry in point_to_delete.backup_entries:
                backup_path = Path(entry.backup_path)
                if backup_path.exists():
                    backup_path.unlink()

            # Remover ponto da lista
            rollback_points = [
                p for p in rollback_points if p.id != rollback_id
            ]

            # Salvar lista atualizada
            self._save_rollback_points(rollback_points)

            self._log_operation(f"Ponto de rollback {rollback_id} removido")
            return True

        except Exception as e:
            self._log_operation(
                f"Erro ao remover ponto de rollback {rollback_id}: {e}",
                level="ERROR",
            )
            return False

    def cleanup_old_rollback_points(self, keep_count: int = 5) -> int:
        """
        Remove pontos de rollback antigos, mantendo apenas os mais recentes.

        Args:
            keep_count: Número de pontos para manter

        Returns:
            Número de pontos removidos
        """
        rollback_points = self.list_rollback_points()

        if len(rollback_points) <= keep_count:
            return 0

        points_to_remove = rollback_points[keep_count:]
        removed_count = 0

        for point in points_to_remove:
            if self.delete_rollback_point(point.id):
                removed_count += 1

        self._log_operation(
            f"Limpeza concluída: {removed_count} pontos removidos"
        )
        return removed_count

    def get_rollback_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos pontos de rollback.

        Returns:
            Dicionário com estatísticas
        """
        rollback_points = self.list_rollback_points()

        if not rollback_points:
            return {
                "total_points": 0,
                "total_size": 0,
                "oldest_point": None,
                "newest_point": None,
                "backup_types": {},
            }

        total_size = sum(
            point.metadata.get("backup_size", 0) for point in rollback_points
        )

        backup_types = {}
        for point in rollback_points:
            backup_type = point.backup_type.value
            backup_types[backup_type] = backup_types.get(backup_type, 0) + 1

        return {
            "total_points": len(rollback_points),
            "total_size": total_size,
            "oldest_point": (
                rollback_points[-1].timestamp if rollback_points else None
            ),
            "newest_point": (
                rollback_points[0].timestamp if rollback_points else None
            ),
            "backup_types": backup_types,
        }

    # Métodos privados
    def _generate_rollback_id(self) -> str:
        """Gera ID único para ponto de rollback."""
        import time

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        microseconds = int(time.time() * 1000000) % 1000000
        return f"rollback_{timestamp}_{microseconds:06d}"

    def _create_backup(
        self, rollback_id: str, backup_type: BackupType
    ) -> List[BackupEntry]:
        """Cria backup baseado no tipo."""
        backup_entries = []
        backup_root = self.backup_dir / rollback_id
        backup_root.mkdir(exist_ok=True)

        if backup_type == BackupType.FULL:
            # Backup completo do projeto
            files_to_backup = self._get_project_files()
        elif backup_type == BackupType.CONFIG_ONLY:
            # Apenas arquivos de configuração
            files_to_backup = self._get_config_files()
        else:  # INCREMENTAL
            # Arquivos modificados desde último backup
            files_to_backup = self._get_modified_files()

        for source_file in files_to_backup:
            try:
                backup_entry = self._backup_file(source_file, backup_root)
                backup_entries.append(backup_entry)
            except Exception as e:
                self._log_operation(
                    f"Erro ao fazer backup de {source_file}: {e}",
                    level="WARNING",
                )

        return backup_entries

    def _backup_file(
        self, source_path: Path, backup_root: Path
    ) -> BackupEntry:
        """Faz backup de um arquivo individual."""
        relative_path = source_path.relative_to(self.project_path)
        backup_path = backup_root / relative_path

        # Criar diretórios necessários
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copiar arquivo
        if source_path.is_file():
            shutil.copy2(source_path, backup_path)
            file_type = "file"
        elif source_path.is_dir():
            shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
            file_type = "directory"
        else:
            raise JTechInstallerException(
                f"Tipo de arquivo não suportado: {source_path}"
            )

        # Calcular checksum para arquivos
        checksum = None
        if source_path.is_file():
            checksum = self._calculate_checksum(source_path)

        return BackupEntry(
            source_path=str(relative_path),
            backup_path=str(backup_path),
            file_type=file_type,
            timestamp=datetime.now().isoformat(),
            checksum=checksum,
        )

    def _restore_file(self, entry: BackupEntry) -> None:
        """Restaura um arquivo do backup."""
        source_path = self.project_path / entry.source_path
        backup_path = Path(entry.backup_path)

        if not backup_path.exists():
            raise JTechInstallerException(
                f"Arquivo de backup não encontrado: {backup_path}"
            )

        # Criar diretórios necessários
        source_path.parent.mkdir(parents=True, exist_ok=True)

        # Restaurar arquivo
        if entry.file_type == "file":
            shutil.copy2(backup_path, source_path)
        elif entry.file_type == "directory":
            if source_path.exists():
                shutil.rmtree(source_path)
            shutil.copytree(backup_path, source_path)

        # Verificar checksum se disponível
        if entry.checksum and entry.file_type == "file":
            restored_checksum = self._calculate_checksum(source_path)
            if restored_checksum != entry.checksum:
                self._log_operation(
                    f"Aviso: Checksum não confere para {source_path}",
                    level="WARNING",
                )

    def _get_project_files(self) -> List[Path]:
        """Obtém lista de arquivos do projeto para backup."""
        files = []
        ignore_patterns = [
            "*/node_modules/*",
            "*/.git/*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/.env/*",
            "*/dist/*",
            "*/build/*",
            "*/.jtech-core/backups/*",  # Não fazer backup dos próprios backups
        ]

        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                # Verificar se deve ser ignorado
                should_ignore = any(
                    file_path.match(pattern) for pattern in ignore_patterns
                )
                if not should_ignore:
                    files.append(file_path)

        return files

    def _get_config_files(self) -> List[Path]:
        """Obtém lista de arquivos de configuração."""
        config_patterns = [
            "*.json",
            "*.yml",
            "*.yaml",
            "*.toml",
            "*.ini",
            "*.cfg",
            ".gitignore",
            ".env*",
            "requirements.txt",
            "package.json",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile",
        ]

        files = []
        # Busca apenas na raiz do projeto e primeiros 2 níveis para evitar travamento
        for pattern in config_patterns:
            files.extend(self.project_path.glob(pattern))
            # Limitar busca recursiva para evitar travamento em CI/CD
            try:
                # Apenas 2 níveis de profundidade para performance
                for level1 in self.project_path.glob("*/"):
                    if level1.is_dir() and not level1.name.startswith("."):
                        files.extend(level1.glob(pattern))
                        for level2 in level1.glob("*/"):
                            if level2.is_dir():
                                files.extend(level2.glob(pattern))
            except (OSError, PermissionError):
                # Ignorar erros de permissão/acesso
                pass

        # Adicionar diretórios de configuração
        config_dirs = [".jtech-core", ".vscode", ".github"]
        for dir_name in config_dirs:
            config_dir = self.project_path / dir_name
            if config_dir.exists():
                files.append(config_dir)

        return list(set(files))  # Remover duplicatas

    def _get_modified_files(self) -> List[Path]:
        """Obtém arquivos modificados desde último backup."""
        # Por simplicidade, retorna arquivos de configuração
        # Em implementação completa, usaria timestamps de modificação
        return self._get_config_files()

    def _capture_installation_state(self) -> Dict[str, Any]:
        """Captura estado atual da instalação."""
        state = {
            "jtech_core_exists": (self.project_path / ".jtech-core").exists(),
            "vscode_config_exists": (self.project_path / ".vscode").exists(),
            "core_config_exists": (
                self.project_path / ".jtech-core" / "core-config.yml"
            ).exists(),
        }

        # Capturar informações de configuração se existir
        core_config_file = (
            self.project_path / ".jtech-core" / "core-config.yml"
        )
        if core_config_file.exists():
            try:
                state["core_config_content"] = core_config_file.read_text(
                    encoding="utf-8"
                )
            except Exception:
                pass

        return state

    def _restore_installation_state(self, state: Dict[str, Any]) -> None:
        """Restaura estado da instalação."""
        # Restaurar core-config.yml se tiver no estado
        if "core_config_content" in state:
            core_config_file = (
                self.project_path / ".jtech-core" / "core-config.yml"
            )
            core_config_file.parent.mkdir(parents=True, exist_ok=True)
            core_config_file.write_text(
                state["core_config_content"], encoding="utf-8"
            )

    def _verify_rollback_integrity(
        self, rollback_point: RollbackPoint
    ) -> List[str]:
        """Verifica integridade após rollback."""
        issues = []

        for entry in rollback_point.backup_entries:
            source_path = self.project_path / entry.source_path

            if not source_path.exists():
                issues.append(
                    f"Arquivo não foi restaurado: {entry.source_path}"
                )
                continue

            # Verificar checksum se disponível
            if entry.checksum and entry.file_type == "file":
                current_checksum = self._calculate_checksum(source_path)
                if current_checksum != entry.checksum:
                    issues.append(f"Checksum não confere: {entry.source_path}")

        return issues

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de um arquivo."""
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _calculate_backup_size(self, backup_entries: List[BackupEntry]) -> int:
        """Calcula tamanho total do backup."""
        total_size = 0
        for entry in backup_entries:
            backup_path = Path(entry.backup_path)
            if backup_path.exists():
                if backup_path.is_file():
                    total_size += backup_path.stat().st_size
                elif backup_path.is_dir():
                    for file_path in backup_path.rglob("*"):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
        return total_size

    def _save_rollback_point(self, rollback_point: RollbackPoint) -> None:
        """Salva ponto de rollback no arquivo."""
        rollback_points = self.list_rollback_points()
        rollback_points.append(rollback_point)
        self._save_rollback_points(rollback_points)

    def _save_rollback_points(
        self, rollback_points: List[RollbackPoint]
    ) -> None:
        """Salva lista de pontos de rollback."""
        data = {
            "version": "1.0",
            "rollback_points": [
                {
                    "id": point.id,
                    "timestamp": point.timestamp,
                    "config": point.config,
                    "backup_type": point.backup_type.value,
                    "backup_entries": [
                        asdict(entry) for entry in point.backup_entries
                    ],
                    "installation_state": point.installation_state,
                    "metadata": point.metadata,
                }
                for point in rollback_points
            ],
        }

        # Converter recursivamente todos os objetos Path para string
        data = self._deep_convert_paths(data)

        with open(self.rollback_points_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _deep_convert_paths(self, obj):
        """Converte recursivamente objetos Path para string."""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {
                key: self._deep_convert_paths(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._deep_convert_paths(item) for item in obj]
        elif hasattr(obj, "value"):  # Enum
            return obj.value
        else:
            return obj

    def _load_rollback_point(
        self, rollback_id: str
    ) -> Optional[RollbackPoint]:
        """Carrega ponto de rollback específico."""
        rollback_points = self.list_rollback_points()
        for point in rollback_points:
            if point.id == rollback_id:
                return point
        return None

    def _log_operation(self, message: str, level: str = "INFO") -> None:
        """Registra operação no log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}\n"

        with open(self.rollback_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def _serialize_config(self, config: InstallationConfig) -> Dict[str, Any]:
        """Serializa configuração para JSON."""
        config_dict = asdict(config)

        # Converter Path para string
        if "project_path" in config_dict:
            config_dict["project_path"] = str(config_dict["project_path"])
        if (
            "framework_source_path" in config_dict
            and config_dict["framework_source_path"]
        ):
            config_dict["framework_source_path"] = str(
                config_dict["framework_source_path"]
            )

        # Converter enum para string
        if "install_type" in config_dict:
            config_dict["install_type"] = config_dict["install_type"].value
        if "team_type" in config_dict:
            config_dict["team_type"] = config_dict["team_type"].value

        return config_dict
