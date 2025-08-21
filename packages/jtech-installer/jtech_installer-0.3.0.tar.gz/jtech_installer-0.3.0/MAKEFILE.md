# 🚀 JTECH™ Core Installer - Makefile

Este Makefile fornece automação completa para desenvolvimento, build e publicação do JTECH™ Core Installer.

## 📋 Comandos Principais

### 🔧 Setup Inicial
```bash
make dev-setup    # Configura ambiente completo de desenvolvimento
make install-dev  # Instala dependências de desenvolvimento
make install      # Instala pacote em modo editable
```

### 🧪 Desenvolvimento e Testes
```bash
make test         # Executa todos os testes
make test-fast    # Testes rápidos (sem coverage)
make test-cov     # Testes com coverage
make lint         # Linting com flake8 e mypy
make format       # Formatação com black e isort
make check        # Verificação completa de qualidade
```

### 🏗️ Build e Validação
```bash
make build        # Constrói pacote para distribuição
make validate-build # Valida build com twine
make clean        # Limpa arquivos de build
make build-clean  # Limpa e reconstrói
```

### 📊 Gerenciamento de Versão
```bash
make version      # Mostra versão atual
make bump-patch   # 0.1.0 -> 0.1.1
make bump-minor   # 0.1.0 -> 0.2.0  
make bump-major   # 0.1.0 -> 1.0.0
```

### 🚀 Publicação
```bash
make publish-test # Publica no Test PyPI
make publish      # Publica no PyPI oficial
```

### 🎯 Workflows Completos
```bash
make prepare-release # Preparação completa para release
make full-check      # Verificação completa
make quick-test      # Teste rápido com formatação
```

### 📚 Utilitários
```bash
make demo         # Executa demonstração da CLI
make status       # Mostra status do projeto
make help         # Lista todos os comandos
```

## 🔄 Workflow de Release Recomendado

### 1. Desenvolvimento
```bash
# Setup inicial
make dev-setup

# Durante desenvolvimento
make quick-test    # Testes rápidos
make format        # Formatação
```

### 2. Preparação para Release
```bash
# Verificação completa
make full-check

# Preparar release
make prepare-release

# Incrementar versão
make bump-patch    # ou bump-minor/bump-major
```

### 3. Publicação
```bash
# Testar no Test PyPI primeiro
make publish-test

# Instalar e testar
pip install --index-url https://test.pypi.org/simple/ jtech-installer

# Publicar em produção
make publish
```

## 📦 Estrutura de Build

O Makefile cria os seguintes artefatos:

- `dist/jtech_installer-X.Y.Z-py3-none-any.whl` - Wheel package
- `dist/jtech_installer-X.Y.Z.tar.gz` - Source distribution
- `htmlcov/` - Coverage HTML report

## 🔧 Requisitos

- Python 3.12+
- uv (gerenciador de pacotes)
- make

## 📝 Configuração PyPI

Para publicar no PyPI, configure suas credenciais:

```bash
# Para Test PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-token

# Para PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-production-token
```

Ou use um arquivo `~/.pypirc`:

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-production-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token
```

## 🎨 Customização

O Makefile suporta várias variáveis de ambiente:

- `PYTHON` - Executável Python (padrão: python3.12)
- `UV` - Executável UV (padrão: uv)
- `PACKAGE_NAME` - Nome do pacote (padrão: jtech-installer)

Exemplo:
```bash
PYTHON=python3.11 make test
```

## 🔍 Troubleshooting

### Erro "twine not found"
```bash
uv add --dev twine
```

### Erro de permissão no PyPI
Verifique suas credenciais e tokens de acesso.

### Erro de build
```bash
make clean
make build
```
