# 🚀 JTECH™ Core Installer - Guia de Uso

## Instalação

O instalador JTECH™ Core está pronto para uso. Você pode executá-lo de duas formas:

### Opção 1: Via Módulo Python (Recomendado)
```bash
python -m jtech_installer.cli.main --help
```

### Opção 2: Via Script Wrapper
```bash
./jtech-installer --help
```

## Comandos Disponíveis

### 1. Instalação Padrão (Fullstack)
```bash
python -m jtech_installer.cli.main
```
Instala o ambiente JTECH™ Core completo com configuração fullstack no diretório atual.

### 2. Instalação com Tipo de Equipe Específico
```bash
# Equipe IDE Minimal (desenvolvimento rápido)
python -m jtech_installer.cli.main --team ide-minimal

# Equipe Full-Stack (desenvolvimento web completo)
python -m jtech_installer.cli.main --team fullstack

# Equipe No UI (apenas backend/APIs)
python -m jtech_installer.cli.main --team no-ui

# Equipe All (configuração completa)
python -m jtech_installer.cli.main --team all
```

### 3. Reinstalação Forçada
```bash
python -m jtech_installer.cli.main --force
```
Força a reinstalação mesmo se já existir uma instalação.

### 4. Validação de Instalação Existente
```bash
python -m jtech_installer.cli.main --validate-only
```
Apenas valida se a instalação existente está correta, sem instalar nada.

### 5. Comandos Específicos
```bash
# Instalar
python -m jtech_installer.cli.main install --team fullstack

# Reinstalar
python -m jtech_installer.cli.main reinstall --team ide-minimal

# Validar
python -m jtech_installer.cli.main validate
```

## O que é Instalado

### Estrutura .jtech-core/
- **agents/**: Agentes especializados (Architect, Dev, PM, QA, etc.)
- **agents-teams/**: Configurações de equipes
- **chatmodes/**: Modos de chat para GitHub Copilot
- **checklists/**: Listas de verificação para diferentes processos
- **data/**: Base de conhecimento e dados de referência
- **tasks/**: Tarefas automatizadas
- **templates/**: Templates para documentos e arquitetura
- **utils/**: Utilitários diversos
- **workflows/**: Fluxos de trabalho predefinidos

### Configuração GitHub (.github/)
- **chatmodes/**: 10 chatmodes especializados para GitHub Copilot

### Configuração VS Code (.vscode/)
- **settings.json**: Configurações otimizadas para o GitHub Copilot

## Exemplos de Uso

### 1. Projeto Novo (Greenfield)
```bash
mkdir meu-projeto
cd meu-projeto
python -m jtech_installer.cli.main --team fullstack
```

### 2. Projeto Existente (Brownfield)
```bash
cd projeto-existente
python -m jtech_installer.cli.main --team no-ui
```

### 3. Validar Instalação
```bash
cd projeto-com-jtech
python -m jtech_installer.cli.main --validate-only
```

## Próximos Passos Após Instalação

1. **Abrir no VS Code**: `code .`
2. **Explorar estrutura**: `ls -la .jtech-core/`
3. **Testar ChatModes**: Abrir GitHub Copilot Chat no VS Code
4. **Ler documentação**: `cat .jtech-core/README.md`

## Troubleshooting

### Erro: "command not found"
Use o módulo Python:
```bash
python -m jtech_installer.cli.main --help
```

### Erro: "Module not found"
Reinstale o instalador:
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
pip install -e . --force-reinstall
```

### Reinstalar Tudo
```bash
python -m jtech_installer.cli.main --force
```

## Assets Incluídos

Os seguintes assets estão empacotados no instalador:
- ✅ Estrutura completa .jtech-core
- ✅ 10 ChatModes especializados  
- ✅ Configuração VS Code otimizada
- ✅ Agentes especializados (Architect, Dev, PM, QA, UX, etc.)
- ✅ Templates de documentação
- ✅ Fluxos de trabalho automatizados
- ✅ Base de conhecimento JTECH™

## Sucesso!

Você agora tem uma CLI completamente funcional que:
- 🚀 Instala automaticamente no diretório atual
- 📦 Usa assets empacotados (não caminhos hardcoded)
- 🔧 Copia configurações reais do VS Code
- 💬 Configura ChatModes do GitHub Copilot
- ✅ Valida instalações existentes
- 🎯 Suporta diferentes tipos de equipe

Execute `python -m jtech_installer.cli.main --help` para começar!
