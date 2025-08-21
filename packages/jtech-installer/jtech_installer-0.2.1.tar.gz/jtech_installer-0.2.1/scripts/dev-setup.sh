#!/bin/bash
# Script de desenvolvimento para JTECH™ Installer

set -e

echo "🚀 JTECH™ Installer - Setup de Desenvolvimento"

# Instalar dependências de desenvolvimento
echo "📦 Instalando dependências..."
uv sync --dev

# Executar testes
echo "🧪 Executando testes..."
uv run pytest tests/ -v --cov=jtech_installer

# Lint e formatação
echo "🔍 Executando lint..."
uv run black src/ tests/
uv run isort src/ tests/

# Verificar se CLI funciona
echo "✅ Testando CLI..."
uv run jtech-install --version

echo "🎉 Setup concluído com sucesso!"
echo "💡 Use 'uv run jtech-install install --help' para começar"
