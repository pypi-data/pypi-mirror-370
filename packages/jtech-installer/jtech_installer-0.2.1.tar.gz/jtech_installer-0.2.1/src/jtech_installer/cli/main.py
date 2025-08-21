#!/usr/bin/env python3
"""
🚀 JTECH™ Core Installer - CLI Principal
Instalador automatizado para configurar ambiente JTECH™ Core
"""

import shutil
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

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

    Instala e configura automaticamente o ambiente JTECH™ Core
    no projeto atual.

    Exemplos:
        jtech-installer                    # Instala com configuração fullstack
        jtech-installer --team ide-minimal # Instala configuração mínima
        jtech-installer --validate-only    # Apenas valida instalação
        jtech-installer --help             # Mostra esta ajuda
    """

    if version:
        console.print("🚀 JTECH™ Core Installer v0.2.1", style="bold blue")
        return

    if help or ctx.invoked_subcommand is not None:
        if help:
            console.print(ctx.get_help())
        return

    # Comando principal - instalar
    project_path = Path.cwd()

    console.print(
        Panel.fit(
            f"[bold blue]🚀 JTECH™ Core Installer[/bold blue]\n"
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

    # Executar instalação com progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("🏗️ Iniciando instalação...", total=None)

        try:
            # Passo 1: Copiar estrutura .jtech-core completa
            progress.update(task, description="📦 Copiando framework...")
            copy_jtech_core_structure(project_path, force)
            time.sleep(0.5)

            # Passo 2: Copiar chatmodes
            progress.update(task, description="💬 Configurando chatmodes...")
            copy_chatmodes(project_path)
            time.sleep(0.5)

            # Passo 3: Configurar VS Code
            progress.update(task, description="🔧 Configurando VS Code...")
            copy_vscode_config(project_path)
            time.sleep(0.5)

            # Passo 4: Finalizar
            progress.update(task, description="🔍 Finalizando...")
            time.sleep(0.5)

            progress.remove_task(task)

        except Exception as e:
            progress.remove_task(task)
            console.print(f"❌ Erro durante instalação: {e}", style="red")
            return False

    # Mostrar resultado
    show_installation_result(True, project_path)
    return True


def copy_jtech_core_structure(project_path: Path, force: bool = False):
    """Copia toda a estrutura .jtech-core dos assets empacotados."""
    assets_dir = Path(__file__).parent.parent / "assets"
    source_jtech = assets_dir / ".jtech-core"
    target_jtech = project_path / ".jtech-core"

    if not source_jtech.exists():
        console.print(
            "⚠️ Estrutura .jtech-core não encontrada nos assets", style="yellow"
        )
        return

    # Copiar toda a estrutura
    if target_jtech.exists() and force:
        shutil.rmtree(target_jtech)

    if not target_jtech.exists():
        shutil.copytree(source_jtech, target_jtech)
        console.print(
            "✅ Estrutura .jtech-core copiada dos assets", style="green"
        )
    else:
        console.print("✅ Estrutura .jtech-core já existe", style="green")


def copy_chatmodes(project_path: Path):
    """Copia os chatmodes dos assets empacotados."""
    assets_dir = Path(__file__).parent.parent / "assets"
    source_chatmodes = assets_dir / ".github" / "chatmodes"
    target_chatmodes = project_path / ".github" / "chatmodes"

    if not source_chatmodes.exists():
        console.print("⚠️ Chatmodes não encontrados nos assets", style="yellow")
        return

    # Criar diretório target
    target_chatmodes.mkdir(parents=True, exist_ok=True)

    # Copiar todos os arquivos .chatmode.md
    copied_files = []

    for chatmode_file in source_chatmodes.glob("*.chatmode.md"):
        target_file = target_chatmodes / chatmode_file.name
        shutil.copy2(chatmode_file, target_file)
        copied_files.append(chatmode_file.name)

    console.print(
        f"✅ Copiados {len(copied_files)} chatmodes dos assets", style="green"
    )


def copy_vscode_config(project_path: Path):
    """Copia a configuração do VS Code dos assets empacotados."""
    assets_dir = Path(__file__).parent.parent / "assets"
    source_vscode = assets_dir / ".vscode" / "settings.json"
    target_vscode_dir = project_path / ".vscode"
    target_vscode_file = target_vscode_dir / "settings.json"

    if not source_vscode.exists():
        console.print(
            "⚠️ Configuração VS Code não encontrada nos assets", style="yellow"
        )
        return

    # Criar diretório target
    target_vscode_dir.mkdir(parents=True, exist_ok=True)

    # Copiar configuração
    shutil.copy2(source_vscode, target_vscode_file)

    console.print("✅ Configuração VS Code copiada dos assets", style="green")


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

    # Verificar componentes principais
    components = [
        (".jtech-core", "Estrutura principal"),
        (".jtech-core/agents", "Agentes"),
        (".jtech-core/tasks", "Tarefas"),
        (".jtech-core/templates", "Templates"),
        (".github/chatmodes", "ChatModes"),
        (".vscode/settings.json", "Configuração VS Code"),
    ]

    # Tabela de resultados
    table = Table(title="🔍 Resultado da Validação")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="white")

    all_valid = True

    for component_path, component_name in components:
        full_path = project_path / component_path
        if full_path.exists():
            status = "✅ OK"
        else:
            status = "❌ FALTA"
            all_valid = False

        table.add_row(component_name, status)

    console.print(table)

    # Resultado geral
    if all_valid:
        console.print("\n🎉 [bold green]Instalação válida![/bold green]")
    else:
        console.print(
            "\n⚠️ [bold yellow]Alguns componentes estão faltando[/bold yellow]"
        )

    return all_valid


def show_installation_result(success: bool, project_path: Path):
    """Mostra o resultado da instalação."""

    if success:
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
                "[bold yellow]⚠️ INSTALAÇÃO COM PROBLEMAS[/bold yellow]\n\n"
                f"📁 Projeto: [cyan]{project_path}[/cyan]\n"
                f"🔍 Verifique os logs acima",
                title="⚠️ Atenção",
                border_style="yellow",
            )
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
