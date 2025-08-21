# ====================================================================
# JTECH™ Core Installer - Makefile
# Build, Test & Publish Automation
# ====================================================================

.PHONY: help clean install install-dev test test-fast test-cov lint format \
        check build build-clean publish publish-test version bump-patch \
        bump-minor bump-major dev-setup pre-commit docs serve-docs \
        validate-build demo install-from-build

# ====================================================================
# Configuration
# ====================================================================

PYTHON := python3.12
PIP := pip
UV := uv
PACKAGE_NAME := jtech-installer
SRC_DIR := src/jtech_installer
TESTS_DIR := tests
DIST_DIR := dist
BUILD_DIR := build
DOCS_DIR := docs

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# ====================================================================
# Help
# ====================================================================

help: ## 📋 Mostrar comandos disponíveis
	@echo "$(BLUE)🚀 JTECH™ Core Installer - Makefile$(RESET)"
	@echo ""
	@echo "$(GREEN)📦 Build & Publish:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E '(build|publish|version|bump)' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)🧪 Development & Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E '(dev|test|lint|format|check|install)' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)📚 Documentation & Utils:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		grep -E '(docs|demo|clean|validate)' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'

# ====================================================================
# Development Setup
# ====================================================================

dev-setup: ## 🔧 Configurar ambiente de desenvolvimento completo
	@echo "$(BLUE)🔧 Configurando ambiente de desenvolvimento...$(RESET)"
	$(UV) sync --dev
	$(UV) run pre-commit install
	@echo "$(GREEN)✅ Ambiente configurado!$(RESET)"

install: ## 📦 Instalar pacote em modo editable
	@echo "$(BLUE)📦 Instalando pacote...$(RESET)"
	$(PIP) install -e .
	@echo "$(GREEN)✅ Pacote instalado!$(RESET)"

install-dev: ## 🔧 Instalar com dependências de desenvolvimento
	@echo "$(BLUE)🔧 Instalando com dependências dev...$(RESET)"
	$(UV) sync --dev
	@echo "$(GREEN)✅ Dependências dev instaladas!$(RESET)"

# ====================================================================
# Code Quality & Testing
# ====================================================================

lint: ## 🔍 Executar linting (flake8, mypy)
	@echo "$(BLUE)🔍 Executando linting...$(RESET)"
	$(UV) run flake8 $(SRC_DIR) $(TESTS_DIR)
	$(UV) run mypy $(SRC_DIR)
	@echo "$(GREEN)✅ Linting passou!$(RESET)"

format: ## 🎨 Formatar código (black, isort)
	@echo "$(BLUE)🎨 Formatando código...$(RESET)"
	$(UV) run black $(SRC_DIR) $(TESTS_DIR)
	$(UV) run isort $(SRC_DIR) $(TESTS_DIR)
	@echo "$(GREEN)✅ Código formatado!$(RESET)"

format-fix: ## 🔧 Corrigir problemas de formatação automaticamente
	@echo "$(BLUE)🔧 Corrigindo problemas de formatação...$(RESET)"
	$(UV) run black $(SRC_DIR) $(TESTS_DIR) --line-length 79
	$(UV) run isort $(SRC_DIR) $(TESTS_DIR)
	@echo "$(BLUE)🧹 Removendo espaços em branco...$(RESET)"
	find $(SRC_DIR) $(TESTS_DIR) -name "*.py" -exec sed -i 's/[[:space:]]*$$//' {} \;
	@echo "$(BLUE)🔍 Corrigindo imports não utilizados...$(RESET)"
	-$(UV) run autoflake --in-place --remove-all-unused-imports --recursive $(SRC_DIR) $(TESTS_DIR)
	@echo "$(GREEN)✅ Formatação corrigida automaticamente!$(RESET)"

lint-relax: ## 🔍 Linting com linha mais longa (110 chars)
	@echo "$(BLUE)🔍 Executando linting relaxed...$(RESET)"
	$(UV) run flake8 $(SRC_DIR) $(TESTS_DIR) --max-line-length=110 --ignore=E203,W503,F401,F841,E402,F811,F541 --exclude=$(SRC_DIR)/cli/main_backup.py
	@echo "$(GREEN)✅ Linting relaxed passou!$(RESET)"

lint-full: lint ## 🔍 Linting completo com mypy
	@echo "$(BLUE)🔍 Executando mypy...$(RESET)"
	$(UV) run mypy $(SRC_DIR)
	@echo "$(GREEN)✅ Linting completo passou!$(RESET)"

check: lint format ## ✅ Verificação completa de qualidade
	@echo "$(GREEN)✅ Verificação de qualidade completa!$(RESET)"

test: ## 🧪 Executar todos os testes
	@echo "$(BLUE)🧪 Executando testes...$(RESET)"
	$(UV) run pytest -v
	@echo "$(GREEN)✅ Testes concluídos!$(RESET)"

test-fast: ## ⚡ Executar testes rápidos (sem coverage)
	@echo "$(BLUE)⚡ Executando testes rápidos...$(RESET)"
	$(UV) run pytest -v --no-cov -x
	@echo "$(GREEN)✅ Testes rápidos concluídos!$(RESET)"

test-cov: ## 📊 Executar testes com coverage
	@echo "$(BLUE)📊 Executando testes com coverage...$(RESET)"
	$(UV) run pytest --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage gerado em htmlcov/$(RESET)"

pre-commit: ## 🎯 Executar pre-commit hooks
	@echo "$(BLUE)🎯 Executando pre-commit...$(RESET)"
	$(UV) run pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit concluído!$(RESET)"

# ====================================================================
# Build & Package
# ====================================================================

clean: ## 🧹 Limpar arquivos de build
	@echo "$(BLUE)🧹 Limpando arquivos de build...$(RESET)"
	rm -rf $(DIST_DIR) $(BUILD_DIR) *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Limpeza concluída!$(RESET)"

build-clean: clean build ## 🔄 Limpar e construir

build-internal: format-fix lint-relax test ## � Build para distribuição interna Veolia
	@echo "$(BLUE)🏢 Construindo pacote para distribuição interna...$(RESET)"
	@echo "$(GREEN)✅ Testes e qualidade verificados$(RESET)"
	$(UV) build --out-dir $(DIST_DIR)
	@echo "$(GREEN)✅ Pacote construído em $(DIST_DIR)/$(RESET)"
	@echo "$(BLUE)📋 Arquivos gerados:$(RESET)"
	@ls -la $(DIST_DIR)/
	@echo "$(YELLOW)💡 Para instalar localmente: pip install dist/*.whl$(RESET)"

build: clean ## 🔨 Construir o pacote
	@echo "$(BLUE)🏗️ Construindo pacote...$(RESET)"
	$(UV) build
	@echo "$(GREEN)✅ Pacote construído em $(DIST_DIR)/$(RESET)"
	@ls -la $(DIST_DIR)/

validate-build: build ## ✅ Validar build construído
	@echo "$(BLUE)✅ Validando build...$(RESET)"
	$(UV) run twine check $(DIST_DIR)/*
	@echo "$(GREEN)✅ Build validado!$(RESET)"

install-from-build: build ## 📦 Instalar a partir do build
	@echo "$(BLUE)📦 Instalando a partir do build...$(RESET)"
	$(PIP) install $(DIST_DIR)/*.whl --force-reinstall
	@echo "$(GREEN)✅ Instalado a partir do build!$(RESET)"

# ====================================================================
# Version Management
# ====================================================================

version: ## 📋 Mostrar versão atual
	@echo "$(BLUE)📋 Versão atual:$(RESET)"
	@grep '^version = ' pyproject.toml | cut -d'"' -f2

bump-patch: ## 🔢 Incrementar versão patch (0.1.0 -> 0.1.1)
	@echo "$(BLUE)🔢 Incrementando versão patch...$(RESET)"
	@current=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{$$3++; print $$1"."$$2"."$$3}'); \
	sed -i 's/^version = ".*"/version = "'$$new'"/' pyproject.toml; \
	echo "$(GREEN)✅ Versão atualizada: $$current -> $$new$(RESET)"

bump-minor: ## 🔢 Incrementar versão minor (0.1.0 -> 0.2.0)
	@echo "$(BLUE)🔢 Incrementando versão minor...$(RESET)"
	@current=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{$$2++; $$3=0; print $$1"."$$2"."$$3}'); \
	sed -i 's/^version = ".*"/version = "'$$new'"/' pyproject.toml; \
	echo "$(GREEN)✅ Versão atualizada: $$current -> $$new$(RESET)"

bump-major: ## 🔢 Incrementar versão major (0.1.0 -> 1.0.0)
	@echo "$(BLUE)🔢 Incrementando versão major...$(RESET)"
	@current=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	new=$$(echo $$current | awk -F. '{$$1++; $$2=0; $$3=0; print $$1"."$$2"."$$3}'); \
	sed -i 's/^version = ".*"/version = "'$$new'"/' pyproject.toml; \
	echo "$(GREEN)✅ Versão atualizada: $$current -> $$new$(RESET)"

# ====================================================================
# Publishing
# ====================================================================

publish-test: validate-build ## 🧪 Publicar no Test PyPI
	@echo "$(BLUE)🧪 Publicando no Test PyPI...$(RESET)"
	@echo "$(YELLOW)⚠️  Certifique-se de ter configurado suas credenciais do Test PyPI$(RESET)"
	$(UV) run twine upload --repository testpypi $(DIST_DIR)/*
	@echo "$(GREEN)✅ Publicado no Test PyPI!$(RESET)"
	@echo "$(BLUE)📋 Teste a instalação com:$(RESET)"
	@echo "pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"

publish: validate-build ## 🚀 Publicar no PyPI oficial
	@echo "$(RED)⚠️  ATENÇÃO: Este é um pacote PROPRIETÁRIO da Veolia$(RESET)"
	@echo "$(RED)⚠️  NÃO deve ser publicado em repositórios públicos!$(RESET)"
	@echo "$(YELLOW)💡 Use 'make publish-private' para repositório interno$(RESET)"
	@read -p "Tem certeza que deseja publicar no PyPI PÚBLICO? (y/N): " confirm && [ "$$confirm" = "y" ]
	$(UV) run twine upload $(DIST_DIR)/*
	@echo "$(GREEN)✅ Publicado no PyPI!$(RESET)"
	@echo "$(BLUE)📋 Instale com:$(RESET)"
	@echo "pip install $(PACKAGE_NAME)"

publish-private: validate-build ## 🏢 Publicar em repositório privado Veolia
	@echo "$(BLUE)🏢 Publicando em repositório privado Veolia...$(RESET)"
	@echo "$(YELLOW)⚠️  Configure o repositório privado da Veolia primeiro$(RESET)"
	@echo "$(BLUE)💡 Exemplo de configuração:$(RESET)"
	@echo "  twine upload --repository-url https://pypi.veolia.com/simple/ dist/*"
	@read -p "Tem certeza que deseja publicar no repositório privado? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(RED)❌ Repositório privado não configurado ainda$(RESET)"
	@echo "$(BLUE)📋 Configure primeiro:$(RESET)"
	@echo "  1. Adicione o repositório no ~/.pypirc"
	@echo "  2. Configure as credenciais"
	@echo "  3. Execute: twine upload --repository veolia-private dist/*"

# ====================================================================
# Documentation
# ====================================================================

docs: ## 📚 Gerar documentação
	@echo "$(BLUE)📚 Gerando documentação...$(RESET)"
	@if [ -d "$(DOCS_DIR)" ]; then \
		cd $(DOCS_DIR) && make html; \
		echo "$(GREEN)✅ Documentação gerada!$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  Diretório docs não encontrado$(RESET)"; \
	fi

serve-docs: docs ## 🌐 Servir documentação localmente
	@echo "$(BLUE)🌐 Servindo documentação...$(RESET)"
	@if [ -d "$(DOCS_DIR)/_build/html" ]; then \
		cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000; \
	else \
		echo "$(RED)❌ Documentação não encontrada. Execute 'make docs' primeiro$(RESET)"; \
	fi

# ====================================================================
# Demo & Utilities
# ====================================================================

demo: ## 🎬 Executar demonstração da CLI
	@echo "$(BLUE)🎬 Executando demonstração...$(RESET)"
	$(PYTHON) demo.py
	@echo "$(GREEN)✅ Demonstração concluída!$(RESET)"

# ====================================================================
# Workflows Completos
# ====================================================================

prepare-release: clean format-fix lint-relax test build validate-build ## 🎯 Preparar para release
	@echo "$(GREEN)🎯 Preparação para release concluída!$(RESET)"
	@echo "$(BLUE)📋 Próximos passos:$(RESET)"
	@echo "1. make bump-patch|minor|major"
	@echo "2. make publish-test (para testar)"
	@echo "3. make publish (para produção)"

quick-test: format test-fast ## ⚡ Teste rápido com formatação

full-check: clean format lint test-cov build validate-build ## 🔍 Verificação completa

# ====================================================================
# Development Shortcuts
# ====================================================================

dev: install-dev ## 🔧 Alias para install-dev
test-w: ## 🔄 Executar testes em modo watch (requer pytest-watch)
	@echo "$(BLUE)🔄 Executando testes em modo watch...$(RESET)"
	$(UV) run ptw -- --no-cov

# ====================================================================
# Status & Info
# ====================================================================

status: ## 📊 Mostrar status do projeto
	@echo "$(BLUE)📊 Status do Projeto JTECH™ Core Installer$(RESET)"
	@echo ""
	@echo "$(GREEN)📦 Pacote:$(RESET) $(PACKAGE_NAME)"
	@echo "$(GREEN)📋 Versão:$(RESET) $$(grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "$(GREEN)🐍 Python:$(RESET) $$($(PYTHON) --version)"
	@echo "$(GREEN)📁 Diretório:$(RESET) $$(pwd)"
	@echo ""
	@echo "$(GREEN)📊 Estatísticas:$(RESET)"
	@find $(SRC_DIR) -name "*.py" | wc -l | awk '{print "  Arquivos Python:", $$1}'
	@find $(TESTS_DIR) -name "*.py" | wc -l | awk '{print "  Arquivos de Teste:", $$1}'
	@find $(SRC_DIR) -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  Linhas de Código:", $$1}'
