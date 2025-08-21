"""
Core engine for JTECH™ Installer
"""

import time
from pathlib import Path
from typing import Optional

from jtech_installer.analyzer.environment import AdvancedEnvironmentAnalyzer
from jtech_installer.core.models import (
    InstallationConfig,
    InstallationResult,
    InstallationType,
    SystemInfo,
    TeamType,
)
from jtech_installer.detector.prerequisites import PrerequisitesChecker
from jtech_installer.detector.system import SystemDetector
from jtech_installer.installer.asset_copier import AssetCopier
from jtech_installer.installer.config_generator import ConfigGenerator
from jtech_installer.installer.structure import StructureCreator
from jtech_installer.installer.vscode_configurator import VSCodeConfigurator
from jtech_installer.validator.integrity import IntegrityValidator
from jtech_installer.validator.post_installation import PostInstallationValidator


class InstallerEngine:
    """Engine principal de instalação do JTECH™ Core"""

    def __init__(
        self,
        target_path: Path,
        install_type: InstallationType,
        team_type: Optional[TeamType] = None,
        vscode_integration: bool = True,
        framework_source_path: Optional[Path] = None,
        dry_run: bool = False,
    ):
        self.config = InstallationConfig(
            project_path=target_path,
            install_type=install_type,
            team_type=team_type or TeamType.FULLSTACK,
            vs_code_integration=vscode_integration,
            custom_config={},
            framework_source_path=framework_source_path,
        )
        self.dry_run = dry_run
        self.start_time = time.time()

    def detect_system(self) -> SystemInfo:
        """Detecta informações do sistema"""
        detector = SystemDetector()
        return detector.detect()

    def check_prerequisites(self, system_info: SystemInfo) -> None:
        """Verifica pré-requisitos do sistema"""
        checker = PrerequisitesChecker()
        checker.check_all(system_info)

    def analyze_environment(self):
        """
        Executa análise avançada do ambiente.

        Returns:
            Resultado da análise de ambiente
        """
        analyzer = AdvancedEnvironmentAnalyzer(self.config)
        return analyzer.analyze_environment()

    def install(self) -> InstallationResult:
        """Executa a instalação completa"""
        try:
            installed_components = []
            errors = []
            warnings = []

            # Criar estrutura de diretórios
            structure_creator = StructureCreator(self.config, self.dry_run)
            if structure_creator.create_structure():
                installed_components.append("directory_structure")

            # Copiar assets do framework
            asset_copier = AssetCopier(self.config, self.dry_run)
            try:
                assets_result = asset_copier.copy_all()

                # Contar componentes instalados
                for asset_type, assets in assets_result.items():
                    if assets:
                        installed_components.append(
                            f"{asset_type}_{len(assets)}_files"
                        )

            except Exception as e:
                errors.append(f"Erro ao copiar assets: {e}")
                warnings.append(
                    "Alguns componentes podem não ter sido instalados"
                )

            # Gerar configuração personalizada
            config_generator = ConfigGenerator()
            try:
                core_config = config_generator.generate_config(
                    self.config, self.config.project_path
                )

                if not self.dry_run:
                    config_file = config_generator.write_config(
                        core_config, self.config.project_path
                    )

                    # Validar configuração gerada
                    if config_generator.validate_config(core_config):
                        installed_components.append("core_config")
                    else:
                        warnings.append(
                            "Configuração gerada pode ter problemas"
                        )

                else:
                    installed_components.append("core_config_simulated")

            except Exception as e:
                errors.append(f"Erro ao gerar configuração: {e}")
                warnings.append("Configuração core-config.yml não foi gerada")

            # Configurar VS Code se habilitado
            if self.config.vs_code_integration:
                vscode_configurator = VSCodeConfigurator(
                    self.config, self.dry_run
                )
                try:
                    vscode_results = vscode_configurator.configure_all()

                    # Contar configurações aplicadas
                    applied_configs = sum(
                        1 for result in vscode_results.values() if result
                    )
                    if applied_configs > 0:
                        installed_components.append(
                            f"vscode_{applied_configs}_configs"
                        )

                    # Validar configurações
                    validation_results = (
                        vscode_configurator.validate_configuration()
                    )
                    failed_validations = [
                        name
                        for name, valid in validation_results.items()
                        if not valid
                    ]

                    if failed_validations:
                        warnings.append(
                            f"Alguns arquivos VS Code podem ter problemas: {', '.join(failed_validations)}"
                        )

                except Exception as e:
                    errors.append(f"Erro ao configurar VS Code: {e}")
                    warnings.append("Configuração do VS Code não foi aplicada")

            # Validação pós-instalação
            validation_passed = False
            try:
                validator = PostInstallationValidator(self.config)
                validation_report = validator.validate_all()

                validation_passed = validation_report.overall_status

                if validation_passed:
                    installed_components.append("validation_passed")
                else:
                    failed_components = [
                        result.component
                        for result in validation_report.results
                        if not result.status
                    ]
                    warnings.append(
                        f"Validação falhou em: {', '.join(failed_components)}"
                    )

            except Exception as e:
                errors.append(f"Erro durante validação: {e}")
                warnings.append(
                    "Validação pós-instalação não pôde ser executada"
                )

            # TODO: Implementar outras fases da instalação

            duration = time.time() - self.start_time

            return InstallationResult(
                success=len(errors) == 0,
                installed_components=installed_components,
                errors=errors,
                warnings=warnings,
                duration=duration,
                config_generated=True,
                validation_passed=validation_passed,
            )

        except Exception as e:
            duration = time.time() - self.start_time
            return InstallationResult(
                success=False,
                installed_components=[],
                errors=[str(e)],
                warnings=[],
                duration=duration,
            )

    def validate_installation(self) -> bool:
        """Valida a instalação realizada"""
        validator = IntegrityValidator(self.config)
        return validator.validate_all()
