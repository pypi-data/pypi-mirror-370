#!/usr/bin/env python3
"""
🚀 JTECH™ Core Installer - CLI Principal
Instalador automatizado para configurar ambiente JTECH™ Core
"""

import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.engine import InstallationEngine
from ..core.models import InstallationConfig, InstallationType, TeamType
from ..validator.integrity import IntegrityValidator
from ..validator.post_installation import PostInstallationValidator

console = Console()


@click.group(invoke_without_command=True)
@click.option("--help", "-h", is_flag=True, help="Mostrar ajuda")
@click.option("--version", "-v", is_flag=True, help="Mostrar versão")
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
    help="Tipo de equipe/configuração",
)
@click.option("--force", "-f", is_flag=True, help="Forçar reinstalação")
@click.option(
    "--validate-only", is_flag=True, help="Apenas validar instalação existente"
)
@click.pass_context
def cli(ctx, help, version, team, force, validate_only):
    """
    🚀 JTECH™ Core Installer

    Instala e configura automaticamente o ambiente JTECH™ Core no projeto atual.

    Exemplos:
        jtech-installer                    # Instala com configuração fullstack
        jtech-installer --team ide-minimal # Instala configuração mínima
        jtech-installer --validate-only    # Apenas valida instalação
        jtech-installer --help             # Mostra esta ajuda
    """

    if version:
        console.print("🚀 JTECH™ Core Installer v0.1.0", style="bold blue")
        return

    if help or ctx.invoked_subcommand is not None:
        if help:
            console.print(ctx.get_help())
        return

    # Comando principal - instalar
    project_path = Path.cwd()

    console.print(
        Panel.fit(
            "[bold blue]🚀 JTECH™ Core Installer[/bold blue]\n"
            f"📁 Projeto: [cyan]{{project_path}}[/cyan]\n"
            f"⚙️ Tipo de equipe: [green]{{team}}[/green]",
            title="🔧 Configuração",
            border_style="blue",
        )
    )

    if validate_only:
        return validate_installation(project_path, team)

    return install_jtech_core(project_path, team, force)


def install_jtech_core(
    project_path: Path, team_type: str, force: bool = False
):
    """Executa a instalação completa do JTECH™ Core."""

    # Verificar se já existe instalação
    jtech_core = project_path / ".jtech-core"
    if jtech_core.exists() and not force:
        console.print("⚠️ Instalação JTECH™ Core já existe!", style="yellow")
        console.print("💡 Use --force para reinstalar", style="dim")

        if not click.confirm("Deseja continuar e atualizar a instalação?"):
            console.print("❌ Instalação cancelada", style="red")
            return False

    # Mapear tipo de equipe
    team_mapping = {
        "ide-minimal": TeamType.IDE_MINIMAL,
        "fullstack": TeamType.FULLSTACK,
        "no-ui": TeamType.NO_UI,
        "all": TeamType.ALL,
    }

    team_enum = team_mapping[team_type]

    # Determinar tipo de instalação
    install_type = (
        InstallationType.BROWNFIELD
        if any(
            p.exists()
            for p in [
                project_path / "package.json",
                project_path / "requirements.txt",
                project_path / "pom.xml",
                project_path / "Cargo.toml",
            ]
        )
        else InstallationType.GREENFIELD
    )

    # Criar configuração
    config = InstallationConfig(
        project_path=project_path,
        install_type=install_type,
        team_type=team_enum,
        vs_code_integration=True,
        custom_config={},
        framework_source_path=get_framework_source_path(),
    )

    # Executar instalação com progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Passo 1: Criar estrutura
        task = progress.add_task(
            "🏗️ Criando estrutura de diretórios...", total=None
        )
        engine = InstallationEngine()

        try:
            # Instalar
            result = engine.install(config)
            progress.update(task, description="✅ Estrutura criada")
            time.sleep(0.5)

            # Passo 2: Copiar chatmodes reais
            progress.update(task, description="💬 Configurando chatmodes...")
            copy_real_chatmodes(project_path)
            time.sleep(0.5)

            # Passo 3: Configurar VS Code real
            progress.update(task, description="🔧 Configurando VS Code...")
            copy_real_vscode_config(project_path)
            time.sleep(0.5)

            # Passo 4: Validar
            progress.update(task, description="🔍 Validando instalação...")
            validator = PostInstallationValidator(config)
            report = validator.validate_all()

            progress.remove_task(task)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Erro durante instalação: {e}", style="red")
            return False

    # Mostrar resultado
    show_installation_result(report, project_path)
    return True


def copy_real_chatmodes(project_path: Path):
    """Copia os chatmodes reais do ambiente do usuário."""
    source_chatmodes = Path(
        "/jtech/home/angelo.vicente/code/jtech-kpi/.github/chatmodes"
    )
    target_chatmodes = project_path / ".github" / "chatmodes"

    if not source_chatmodes.exists():
        console.print("⚠️ Chatmodes de origem não encontrados", style="yellow")
        return

    # Criar diretório target
    target_chatmodes.mkdir(parents=True, exist_ok=True)

    # Copiar todos os arquivos .chatmode.md
    import shutil

    copied_files = []

    for chatmode_file in source_chatmodes.glob("*.chatmode.md"):
        target_file = target_chatmodes / chatmode_file.name
        shutil.copy2(chatmode_file, target_file)
        copied_files.append(chatmode_file.name)

    console.print(f"✅ Copiados {len(copied_files)} chatmodes", style="green")


def copy_real_vscode_config(project_path: Path):
    """Copia a configuração real do VS Code do ambiente do usuário."""
    source_vscode = Path(
        "/jtech/home/angelo.vicente/code/jtech-kpi/.vscode/settings.json"
    )
    target_vscode_dir = project_path / ".vscode"
    target_vscode_file = target_vscode_dir / "settings.json"

    if not source_vscode.exists():
        console.print(
            "⚠️ Configuração VS Code de origem não encontrada", style="yellow"
        )
        return

    # Criar diretório target
    target_vscode_dir.mkdir(parents=True, exist_ok=True)

    # Copiar configuração
    import shutil

    shutil.copy2(source_vscode, target_vscode_file)

    console.print("✅ Configuração VS Code copiada", style="green")


def get_framework_source_path() -> Path:
    """Retorna o caminho para os arquivos fonte do framework."""
    # Por enquanto, usar o diretório do próprio installer
    installer_dir = Path(__file__).parent.parent.parent.parent
    framework_dir = installer_dir / "framework"

    if framework_dir.exists():
        return framework_dir

    # Fallback para diretório de templates
    return installer_dir / "templates"


def validate_installation(project_path: Path, team_type: str):
    """Valida uma instalação existente."""
    console.print("🔍 Validando instalação JTECH™ Core...", style="blue")

    # Verificar se existe instalação
    jtech_core = project_path / ".jtech-core"
    if not jtech_core.exists():
        console.print(
            "❌ Nenhuma instalação JTECH™ Core encontrada", style="red"
        )
        console.print(
            "💡 Execute 'jtech-installer' para instalar", style="dim"
        )
        return False

    # Mapear tipo de equipe
    team_mapping = {
        "ide-minimal": TeamType.IDE_MINIMAL,
        "fullstack": TeamType.FULLSTACK,
        "no-ui": TeamType.NO_UI,
        "all": TeamType.ALL,
    }

    # Criar configuração para validação
    config = InstallationConfig(
        project_path=project_path,
        install_type=InstallationType.BROWNFIELD,
        team_type=team_mapping[team_type],
        vs_code_integration=True,
        custom_config={},
        framework_source_path=get_framework_source_path(),
    )

    # Executar validação
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Executando validação...", total=None)

        try:
            # Validação pós-instalação
            validator = PostInstallationValidator(config)
            report = validator.validate_all()

            # Validação de integridade
            integrity_validator = IntegrityValidator(config)
            integrity_valid = integrity_validator.validate_all()

            progress.remove_task(task)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Erro durante validação: {e}", style="red")
            return False

    # Mostrar resultado da validação
    show_validation_result(report, integrity_valid, project_path)
    return report.is_valid


def show_installation_result(report, project_path: Path):
    """Mostra o resultado da instalação."""

    if report.is_valid:
        console.print(
            Panel.fit(
                "[bold green]🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO![/bold green]\n\n"
                f"📁 Projeto: [cyan]{{project_path}}[/cyan]\n"
                f"🔧 Estrutura: [green].jtech-core/[/green] criada\n"
                f"💬 ChatModes: [green].github/chatmodes/[/green] configurados\n"
                f"⚙️ VS Code: [green].vscode/settings.json[/green] configurado",
                title="✅ Sucesso",
                border_style="green",
            )
        )

        # Mostrar próximos passos
        next_steps = Table(title="📋 Próximos Passos")
        next_steps.add_column("Comando", style="cyan")
        next_steps.add_column("Descrição", style="white")

        next_steps.add_row("code .", "Abrir projeto no VS Code")
        next_steps.add_row(
            "jtech-installer --validate-only", "Validar instalação"
        )
        next_steps.add_row("ls .jtech-core/", "Explorar estrutura criada")

        console.print(next_steps)

    else:
        console.print(
            Panel.fit(
                "[bold yellow]⚠️ INSTALAÇÃO COM AVISOS[/bold yellow]\n\n"
                f"📁 Projeto: [cyan]{{project_path}}[/cyan]\n"
                f"🔍 Validações: [red]{{len([r for r in report.components if not r.is_valid])}}[/red] falharam",
                title="⚠️ Atenção",
                border_style="yellow",
            )
        )


def show_validation_result(report, integrity_valid: bool, project_path: Path):
    """Mostra o resultado da validação."""

    # Tabela de resultados
    table = Table(title="🔍 Resultado da Validação")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Detalhes", style="dim")

    # Adicionar resultados individuais
    for result in report.components:
        status = "✅ OK" if result.is_valid else "❌ FALHA"
        table.add_row(result.component, status, result.message or "")

    # Adicionar integridade
    integrity_status = "✅ OK" if integrity_valid else "❌ FALHA"
    table.add_row("Integridade", integrity_status, "Verificação de checksums")

    console.print(table)

    # Resultado geral
    if report.is_valid and integrity_valid:
        console.print(
            "\n🎉 [bold green]Instalação válida e íntegra![/bold green]"
        )
    else:
        console.print(
            "\n⚠️ [bold yellow]Instalação com problemas detectados[/bold yellow]"
        )


@cli.command()
def validate():
    """Valida a instalação JTECH™ Core no diretório atual."""
    project_path = Path.cwd()
    return validate_installation(project_path, "fullstack")


@cli.command()
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
)
def install(team):
    """Instala JTECH™ Core no diretório atual."""
    project_path = Path.cwd()
    return install_jtech_core(project_path, team, force=False)


@cli.command()
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
)
def reinstall(team):
    """Reinstala JTECH™ Core (força reinstalação)."""
    project_path = Path.cwd()
    return install_jtech_core(project_path, team, force=True)


def main():
    """Ponto de entrada principal."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n❌ Operação cancelada pelo usuário", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()

import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.engine import InstallationEngine
from ..core.models import InstallationConfig, InstallationType, TeamType
from ..validator.integrity import IntegrityValidator
from ..validator.post_installation import PostInstallationValidator

console = Console()


@click.group(invoke_without_command=True)
@click.option("--help", "-h", is_flag=True, help="Mostrar ajuda")
@click.option("--version", "-v", is_flag=True, help="Mostrar versão")
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
    help="Tipo de equipe/configuração",
)
@click.option("--force", "-f", is_flag=True, help="Forçar reinstalação")
@click.option(
    "--validate-only", is_flag=True, help="Apenas validar instalação existente"
)
@click.pass_context
def cli(ctx, help, version, team, force, validate_only):
    """
    🚀 JTECH™ Core Installer

    Instala e configura automaticamente o ambiente JTECH™ Core no projeto atual.

    Exemplos:
        jtech-installer                    # Instala com configuração fullstack
        jtech-installer --team ide-minimal # Instala configuração mínima
        jtech-installer --validate-only    # Apenas valida instalação
        jtech-installer --help             # Mostra esta ajuda
    """

    if version:
        console.print("🚀 JTECH™ Core Installer v0.1.0", style="bold blue")
        return

    if help or ctx.invoked_subcommand is not None:
        if help:
            console.print(ctx.get_help())
        return

    # Comando principal - instalar
    project_path = Path.cwd()

    console.print(
        Panel.fit(
            "[bold blue]🚀 JTECH™ Core Installer[/bold blue]\n"
            f"📁 Projeto: [cyan]{project_path}[/cyan]\n"
            f"⚙️ Tipo de equipe: [green]{team}[/green]",
            title="🔧 Configuração",
            border_style="blue",
        )
    )

    if validate_only:
        return validate_installation(project_path, team)

    return install_jtech_core(project_path, team, force)


def install_jtech_core(
    project_path: Path, team_type: str, force: bool = False
):
    """Executa a instalação completa do JTECH™ Core."""

    # Verificar se já existe instalação
    jtech_core = project_path / ".jtech-core"
    if jtech_core.exists() and not force:
        console.print("⚠️ Instalação JTECH™ Core já existe!", style="yellow")
        console.print("💡 Use --force para reinstalar", style="dim")

        if not click.confirm("Deseja continuar e atualizar a instalação?"):
            console.print("❌ Instalação cancelada", style="red")
            return False

    # Mapear tipo de equipe
    team_mapping = {
        "ide-minimal": TeamType.IDE_MINIMAL,
        "fullstack": TeamType.FULLSTACK,
        "no-ui": TeamType.NO_UI,
        "all": TeamType.ALL,
    }

    team_enum = team_mapping[team_type]

    # Determinar tipo de instalação
    install_type = (
        InstallationType.BROWNFIELD
        if any(
            p.exists()
            for p in [
                project_path / "package.json",
                project_path / "requirements.txt",
                project_path / "pom.xml",
                project_path / "Cargo.toml",
            ]
        )
        else InstallationType.GREENFIELD
    )

    # Criar configuração
    config = InstallationConfig(
        project_path=project_path,
        install_type=install_type,
        team_type=team_enum,
        vs_code_integration=True,
        custom_config={},
        framework_source_path=get_framework_source_path(),
    )

    # Executar instalação com progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Passo 1: Criar estrutura
        task = progress.add_task(
            "🏗️ Criando estrutura de diretórios...", total=None
        )
        engine = InstallationEngine()

        try:
            # Instalar
            result = engine.install(config)
            progress.update(task, description="✅ Estrutura criada")
            time.sleep(0.5)

            # Passo 2: Copiar chatmodes reais
            progress.update(task, description="💬 Configurando chatmodes...")
            copy_real_chatmodes(project_path)
            time.sleep(0.5)

            # Passo 3: Configurar VS Code real
            progress.update(task, description="🔧 Configurando VS Code...")
            copy_real_vscode_config(project_path)
            time.sleep(0.5)

            # Passo 4: Validar
            progress.update(task, description="🔍 Validando instalação...")
            validator = PostInstallationValidator(config)
            report = validator.validate_all()

            progress.remove_task(task)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Erro durante instalação: {e}", style="red")
            return False

    # Mostrar resultado
    show_installation_result(report, project_path)
    return True


def copy_real_chatmodes(project_path: Path):
    """Copia os chatmodes reais do ambiente do usuário."""
    source_chatmodes = Path(
        "/jtech/home/angelo.vicente/code/jtech-kpi/.github/chatmodes"
    )
    target_chatmodes = project_path / ".github" / "chatmodes"

    if not source_chatmodes.exists():
        console.print("⚠️ Chatmodes de origem não encontrados", style="yellow")
        return

    # Criar diretório target
    target_chatmodes.mkdir(parents=True, exist_ok=True)

    # Copiar todos os arquivos .chatmode.md
    import shutil

    copied_files = []

    for chatmode_file in source_chatmodes.glob("*.chatmode.md"):
        target_file = target_chatmodes / chatmode_file.name
        shutil.copy2(chatmode_file, target_file)
        copied_files.append(chatmode_file.name)

    console.print(f"✅ Copiados {len(copied_files)} chatmodes", style="green")


def copy_real_vscode_config(project_path: Path):
    """Copia a configuração real do VS Code do ambiente do usuário."""
    source_vscode = Path(
        "/jtech/home/angelo.vicente/code/jtech-kpi/.vscode/settings.json"
    )
    target_vscode_dir = project_path / ".vscode"
    target_vscode_file = target_vscode_dir / "settings.json"

    if not source_vscode.exists():
        console.print(
            "⚠️ Configuração VS Code de origem não encontrada", style="yellow"
        )
        return

    # Criar diretório target
    target_vscode_dir.mkdir(parents=True, exist_ok=True)

    # Copiar configuração
    import shutil

    shutil.copy2(source_vscode, target_vscode_file)

    console.print("✅ Configuração VS Code copiada", style="green")


def get_framework_source_path() -> Path:
    """Retorna o caminho para os arquivos fonte do framework."""
    # Por enquanto, usar o diretório do próprio installer
    installer_dir = Path(__file__).parent.parent.parent.parent
    framework_dir = installer_dir / "framework"

    if framework_dir.exists():
        return framework_dir

    # Fallback para diretório de templates
    return installer_dir / "templates"


def validate_installation(project_path: Path, team_type: str):
    """Valida uma instalação existente."""
    console.print("🔍 Validando instalação JTECH™ Core...", style="blue")

    # Verificar se existe instalação
    jtech_core = project_path / ".jtech-core"
    if not jtech_core.exists():
        console.print(
            "❌ Nenhuma instalação JTECH™ Core encontrada", style="red"
        )
        console.print(
            "💡 Execute 'jtech-installer' para instalar", style="dim"
        )
        return False

    # Mapear tipo de equipe
    team_mapping = {
        "ide-minimal": TeamType.IDE_MINIMAL,
        "fullstack": TeamType.FULLSTACK,
        "no-ui": TeamType.NO_UI,
        "all": TeamType.ALL,
    }

    # Criar configuração para validação
    config = InstallationConfig(
        project_path=project_path,
        install_type=InstallationType.BROWNFIELD,
        team_type=team_mapping[team_type],
        vs_code_integration=True,
        custom_config={},
        framework_source_path=get_framework_source_path(),
    )

    # Executar validação
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Executando validação...", total=None)

        try:
            # Validação pós-instalação
            validator = PostInstallationValidator(config)
            report = validator.validate_all()

            # Validação de integridade
            integrity_validator = IntegrityValidator(config)
            integrity_valid = integrity_validator.validate_all()

            progress.remove_task(task)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Erro durante validação: {e}", style="red")
            return False

    # Mostrar resultado da validação
    show_validation_result(report, integrity_valid, project_path)
    return report.is_valid


def show_installation_result(report, project_path: Path):
    """Mostra o resultado da instalação."""

    if report.is_valid:
        console.print(
            Panel.fit(
                "[bold green]🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO![/bold green]\n\n"
                f"📁 Projeto: [cyan]{project_path}[/cyan]\n"
                f"🔧 Estrutura: [green].jtech-core/[/green] criada\n"
                f"💬 ChatModes: [green].github/chatmodes/[/green] configurados\n"
                f"⚙️ VS Code: [green].vscode/settings.json[/green] configurado",
                title="✅ Sucesso",
                border_style="green",
            )
        )

        # Mostrar próximos passos
        next_steps = Table(title="📋 Próximos Passos")
        next_steps.add_column("Comando", style="cyan")
        next_steps.add_column("Descrição", style="white")

        next_steps.add_row("code .", "Abrir projeto no VS Code")
        next_steps.add_row(
            "jtech-installer --validate-only", "Validar instalação"
        )
        next_steps.add_row("ls .jtech-core/", "Explorar estrutura criada")

        console.print(next_steps)

    else:
        console.print(
            Panel.fit(
                "[bold yellow]⚠️ INSTALAÇÃO COM AVISOS[/bold yellow]\n\n"
                f"📁 Projeto: [cyan]{project_path}[/cyan]\n"
                f"🔍 Validações: [red]{len([r for r in report.components if not r.is_valid])}[/red] falharam",
                title="⚠️ Atenção",
                border_style="yellow",
            )
        )


def show_validation_result(report, integrity_valid: bool, project_path: Path):
    """Mostra o resultado da validação."""

    # Tabela de resultados
    table = Table(title="🔍 Resultado da Validação")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Detalhes", style="dim")

    # Adicionar resultados individuais
    for result in report.components:
        status = "✅ OK" if result.is_valid else "❌ FALHA"
        table.add_row(result.component, status, result.message or "")

    # Adicionar integridade
    integrity_status = "✅ OK" if integrity_valid else "❌ FALHA"
    table.add_row("Integridade", integrity_status, "Verificação de checksums")

    console.print(table)

    # Resultado geral
    if report.is_valid and integrity_valid:
        console.print(
            "\n🎉 [bold green]Instalação válida e íntegra![/bold green]"
        )
    else:
        console.print(
            "\n⚠️ [bold yellow]Instalação com problemas detectados[/bold yellow]"
        )


@cli.command()
def validate():
    """Valida a instalação JTECH™ Core no diretório atual."""
    project_path = Path.cwd()
    return validate_installation(project_path, "fullstack")


@cli.command()
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
)
def install(team):
    """Instala JTECH™ Core no diretório atual."""
    project_path = Path.cwd()
    return install_jtech_core(project_path, team, force=False)


@cli.command()
@click.option(
    "--team",
    "-t",
    type=click.Choice(["ide-minimal", "fullstack", "no-ui", "all"]),
    default="fullstack",
)
def reinstall(team):
    """Reinstala JTECH™ Core (força reinstalação)."""
    project_path = Path.cwd()
    return install_jtech_core(project_path, team, force=True)


def main():
    """Ponto de entrada principal."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n❌ Operação cancelada pelo usuário", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
