<!-- Powered by JTECH™ Core -->

# Tarefa Criar História Brownfield

## Propósito

Criar histórias detalhadas e prontas para implementação para projetos brownfield onde documentos tradicionais de PRD/arquitetura fragmentados podem não existir. Esta tarefa conecta a lacuna entre vários formatos de documentação (saída document-project, PRDs brownfield, épicos ou documentação de usuário) e histórias executáveis para o agente Dev.

## Quando Usar Esta Tarefa

**Use esta tarefa quando:**

- Trabalhando em projetos brownfield com documentação não padrão
- Histórias precisam ser criadas a partir da saída document-project
- Trabalhando com épicos brownfield sem PRD/arquitetura completos
- Documentação de projeto existente não segue estrutura JTech v4+
- Precisa coletar contexto adicional do usuário durante criação da história

**Use create-next-story quando:**

- Trabalhando com documentos PRD e arquitetura v4 fragmentados adequadamente
- Seguindo workflow greenfield padrão ou brownfield bem documentado
- Todo contexto técnico está disponível em formato estruturado

## Instruções de Execução da Tarefa

### 0. Contexto de Documentação

Verifique documentação disponível nesta ordem:

1. **PRD/Arquitetura Fragmentados** (docs/prd/, docs/architecture/)
   - Se encontrado, recomende usar tarefa create-next-story

2. **Documento de Arquitetura Brownfield** (docs/brownfield-architecture.md ou similar)
   - Criado pela tarefa document-project
   - Contém estado real do sistema, dívida técnica, workarounds

3. **PRD Brownfield** (docs/prd.md)
   - Pode conter detalhes técnicos embutidos

4. **Arquivos de Épico** (docs/epics/ ou similar)
   - Criados pela tarefa brownfield-create-epic

5. **Documentação Fornecida pelo Usuário**
   - Peça ao usuário para especificar localização e formato

### 1. Identificação de História e Coleta de Contexto

#### 1.1 Identificar Fonte da História
