<!-- Powered by JTECH™ Core -->

# Tarefa Criar Próxima História

## Propósito

Identificar a próxima história lógica baseada no progresso do projeto e definições de épico, e então preparar um arquivo de história abrangente, autocontido e acionável usando o `Template de História`. Esta tarefa garante que a história seja enriquecida com todo contexto técnico necessário, requisitos e critérios de aceitação, tornando-a pronta para implementação eficiente por um Agente Desenvolvedor com necessidade mínima de pesquisa adicional ou busca de contexto próprio.

## Execução de Tarefa SEQUENCIAL (não prossiga até tarefa atual estar completa)

### 0. Carregar Configuração Central e Verificar Workflow

- Carregar `.jtech-core/core-config.yml` da raiz do projeto
- Se o arquivo não existir, PARE e informe o usuário: "core-config.yml não encontrado. Este arquivo é necessário para criação de histórias. Você pode: 1) Copiá-lo do GITHUB jtech-core/core-config.yml e configurá-lo para seu projeto OU 2) Executar o instalador JTech contra seu projeto para atualizar e adicionar o arquivo automaticamente. Por favor adicione e configure core-config.yml antes de prosseguir."
- Extrair configurações-chave: `devStoryLocation`, `prd.*`, `architecture.*`, `workflow.*`

### 1. Identificar Próxima História para Preparação

#### 1.1 Localizar Arquivos de Épico e Revisar Histórias Existentes

- Baseado em `prdSharded` da config, localizar arquivos de épico (localização/padrão fragmentado ou seções PRD monolítico)
- Se `devStoryLocation` tem arquivos de história, carregar o arquivo `{epicNum}.{storyNum}.story.md` mais alto
- **Se história mais alta existe:**
  - Verificar se status é 'Done'. Se não, alertar usuário: "ALERTA: História incompleta encontrada! Arquivo: {lastEpicNum}.{lastStoryNum}.story.md Status: [status atual] Você deve corrigir esta história primeiro, mas gostaria de aceitar risco & sobrescrever para criar próxima história em rascunho?"
  - Se prosseguindo, selecionar próxima história sequencial no épico atual
  - Se épico está completo, perguntar ao usuário: "Épico {epicNum} Completo: Todas as histórias no Épico {epicNum} foram completadas. Gostaria de: 1) Começar Épico {epicNum + 1} com história 1 2) Selecionar uma história específica para trabalhar 3) Cancelar criação de história"
  - **CRÍTICO**: NUNCA pule automaticamente para outro épico. Usuário DEVE instruir explicitamente qual história criar.
- **Se nenhum arquivo de história existe:** A próxima história é SEMPRE 1.1 (primeira história do primeiro épico)
- Anunciar a história identificada ao usuário: "Próxima história identificada para preparação: {epicNum}.{storyNum} - {Título da História}"

### 2. Coletar Requisitos da História e Contexto de História Anterior

- Extrair requisitos da história do arquivo de épico identificado
- Se história anterior existe, revisar seções do Registro do Agente Dev para:
  - Notas de Completude e Referências de Log de Debug
  - Desvios de implementação e decisões técnicas
  - Desafios encontrados e lições aprendidas
- Extrair insights relevantes que informam a preparação da história atual

### 3. Coletar Contexto de Arquitetura

#### 3.1 Determinar Estratégia de Leitura de Arquitetura

- **Se `architectureVersion: >= v4` e `architectureSharded: true`**: Ler `{architectureShardedLocation}/index.md` então seguir ordem de leitura estruturada abaixo
- **Senão**: Usar `architectureFile` monolítico para seções similares

#### 3.2 Ler Documentos de Arquitetura Baseado no Tipo de História

**Para TODAS as Histórias:** tech-stack.md, unified-project-structure.md, coding-standards.md, testing-strategy.md
