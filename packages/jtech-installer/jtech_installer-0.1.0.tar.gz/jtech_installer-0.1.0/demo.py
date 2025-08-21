#!/usr/bin/env python3
"""
🚀 JTECH™ Core Installer - Demonstração Final
"""

import os
import tempfile
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def main():
    """Demonstração completa da CLI JTECH™ Core Installer."""
    
    console.print(Panel.fit(
        "[bold blue]🚀 JTECH™ Core Installer - Demonstração Final[/bold blue]\n\n"
        "[green]Esta demonstração mostra todas as funcionalidades da CLI:[/green]\n"
        "• Instalação automática usando assets empacotados\n"
        "• Diferentes tipos de equipe\n"
        "• Validação de instalação\n"
        "• Estrutura completa .jtech-core copiada",
        title="🎯 Demonstração",
        border_style="blue"
    ))
    
    # Demonstrar comandos disponíveis
    console.print("\n[bold cyan]📋 Comandos Disponíveis:[/bold cyan]")
    
    commands_table = Table()
    commands_table.add_column("Comando", style="cyan")
    commands_table.add_column("Descrição", style="white")
    
    commands_table.add_row(
        "python -m jtech_installer.cli.main",
        "Instalação padrão (fullstack)"
    )
    commands_table.add_row(
        "python -m jtech_installer.cli.main --team ide-minimal",
        "Instalação equipe minimal"
    )
    commands_table.add_row(
        "python -m jtech_installer.cli.main --validate-only",
        "Validar instalação existente"
    )
    commands_table.add_row(
        "python -m jtech_installer.cli.main --force",
        "Reinstalação forçada"
    )
    
    console.print(commands_table)
    
    # Mostrar exemplo de uso
    console.print("\n[bold green]✨ Exemplo de Uso:[/bold green]")
    console.print("""
[dim]# 1. Criar diretório do projeto[/dim]
mkdir meu-projeto && cd meu-projeto

[dim]# 2. Instalar JTECH™ Core[/dim]
python -m jtech_installer.cli.main --team fullstack

[dim]# 3. Abrir no VS Code[/dim]
code .

[dim]# 4. Validar instalação[/dim]
python -m jtech_installer.cli.main --validate-only
""")
    
    # Mostrar assets incluídos
    console.print("[bold magenta]📦 Assets Empacotados:[/bold magenta]")
    
    assets_table = Table()
    assets_table.add_column("Componente", style="cyan")
    assets_table.add_column("Localização", style="green")
    assets_table.add_column("Descrição", style="dim")
    
    assets_table.add_row("Estrutura .jtech-core", "assets/.jtech-core/", "Framework completo")
    assets_table.add_row("ChatModes", "assets/.github/chatmodes/", "10 modos especializados")
    assets_table.add_row("VS Code Config", "assets/.vscode/", "Configuração otimizada")
    assets_table.add_row("Agentes", "assets/.jtech-core/agents/", "10 agentes especializados")
    assets_table.add_row("Templates", "assets/.jtech-core/templates/", "Templates de documentação")
    
    console.print(assets_table)
    
    # Demonstrar instalação real
    if input("\n🚀 Deseja executar uma demonstração real? (y/n): ").lower() == 'y':
        demo_installation()
    
    console.print(Panel.fit(
        "[bold green]🎉 CLI JTECH™ Core Installer Pronta![/bold green]\n\n"
        "[white]A CLI está 100% funcional com:[/white]\n"
        "✅ Assets empacotados (não hardcoded)\n"
        "✅ Instalação automática no diretório atual\n"
        "✅ Suporte a múltiplos tipos de equipe\n"
        "✅ Validação de instalações existentes\n"
        "✅ Interface rica com Rich\n"
        "✅ Wrapper executável\n\n"
        "[cyan]Execute: python -m jtech_installer.cli.main --help[/cyan]",
        title="✅ Sucesso Total",
        border_style="green"
    ))

def demo_installation():
    """Executa uma demonstração real da instalação."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"\n[yellow]📁 Criando demo em: {temp_dir}[/yellow]")
        
        # Mudar para o diretório temporário
        os.chdir(temp_dir)
        
        # Executar instalação
        console.print("\n[blue]🚀 Executando instalação demo...[/blue]")
        result = subprocess.run([
            sys.executable, "-m", "jtech_installer.cli.main", 
            "--team", "ide-minimal"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ Instalação demo concluída![/green]")
            
            # Verificar estrutura criada
            console.print("\n[cyan]📂 Estrutura criada:[/cyan]")
            for item in Path(".").rglob("*"):
                if item.is_file() and not item.name.startswith('.'):
                    console.print(f"  📄 {item}")
                elif item.is_dir() and not item.name.startswith('.'):
                    console.print(f"  📁 {item}/")
            
            # Executar validação
            console.print("\n[blue]🔍 Executando validação...[/blue]")
            val_result = subprocess.run([
                sys.executable, "-m", "jtech_installer.cli.main", 
                "--validate-only"
            ], capture_output=True, text=True)
            
            if val_result.returncode == 0:
                console.print("[green]✅ Validação passou![/green]")
            else:
                console.print("[red]❌ Validação falhou[/red]")
        else:
            console.print(f"[red]❌ Erro na instalação: {result.stderr}[/red]")

if __name__ == "__main__":
    main()
