# JTECH™ Core Framework Installer

Instalador de ambiente automatizado para o JTECH™ Core Framework.

## 🚀 Instalação

```bash
pip install jtech-installer
```

## 🎯 Uso Básico

### Instalação Rápida (Greenfield)

```bash
jtech-install
```

### Instalação com Opções

```bash
# Projeto greenfield com team full-stack
jtech-install --type greenfield --team fullstack

# Projeto brownfield sem VS Code
jtech-install --type brownfield --no-vscode

# Instalação em diretório específico
jtech-install --path /meu/projeto --team all
```

## 📋 Comandos Disponíveis

- `jtech-install` - Instalar o framework JTECH™ Core
- `jtech-install validate` - Validar instalação existente
- `jtech-install version` - Mostrar versão do instalador

## 🎯 Tipos de Equipe

### Team All
Equipe completa com todos os agentes disponíveis:
- Analyst, PM, PO, Architect, Dev, QA, UX Expert, SM
- Ideal para projetos complexos e de grande escala

### Team Full-Stack  
Equipe otimizada para desenvolvimento full-stack:
- Analyst, PM, UX Expert, Architect, PO, Dev
- Foco em desenvolvimento web completo

### Team No UI
Equipe para APIs e serviços backend:
- Analyst, PM, Architect, Dev, QA
- Sem componentes de frontend/UX

### Team IDE Minimal
Equipe mínima para desenvolvimento rápido:
- PM, Architect, Dev
- Ideal para prototipagem e desenvolvimento ágil

## 🏗️ O que é Instalado

O instalador configura automaticamente:

### Estrutura de Diretórios
```
projeto/
├── .jtech-core/           # Framework core
│   ├── agents/           # Agentes especializados
│   ├── templates/        # Templates de documentação
│   ├── workflows/        # Workflows de desenvolvimento
│   ├── tasks/           # Tarefas executáveis
│   ├── checklists/      # Checklists de qualidade
│   └── core-config.yml  # Configuração principal
├── .github/
│   └── chatmodes/       # Integração GitHub Copilot
├── .vscode/
│   └── settings.json    # Configurações VS Code
└── docs/                # Documentação inicial
```

### Agentes Disponíveis
- **Analyst** - Análise de negócio e requisitos
- **PM** - Product Manager
- **PO** - Product Owner  
- **Architect** - Arquitetura de sistema
- **Dev** - Desenvolvimento
- **QA** - Quality Assurance
- **UX Expert** - User Experience
- **SM** - Scrum Master

## 🔧 Desenvolvimento

### Setup do Ambiente de Desenvolvimento

```bash
git clone <repo>
cd jtech-installer
uv sync --dev
```

### Executar Testes

```bash
uv run pytest
```

### Lint e Formatação

```bash
uv run black .
uv run isort .
uv run flake8 .
```

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

*Desenvolvido pela equipe JTECH™ Core*
