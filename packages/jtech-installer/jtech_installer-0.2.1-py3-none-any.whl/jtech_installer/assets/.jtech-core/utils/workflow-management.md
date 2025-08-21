<!-- Powered by JTECH™ Core -->

# Gerenciamento de Workflow

Permite ao orquestrador JTech gerenciar e executar workflows de equipe.

## Carregamento Dinâmico de Workflow

Leia workflows disponíveis do campo `workflows` da configuração atual da equipe. Cada bundle de equipe define seus próprios workflows suportados.

**Comandos-Chave**:

- `/workflows` - Lista workflows no bundle atual ou pasta workflows
- `/agent-list` - Mostra agentes no bundle atual

## Comandos de Workflow

### /workflows

Lista workflows disponíveis com títulos e descrições.

### /workflow-start {workflow-id}

Inicia workflow e transiciona para o primeiro agente.

### /workflow-status

Mostra progresso atual, artefatos completados e próximos passos.

### /workflow-resume

Resume workflow da última posição. Usuário pode fornecer artefatos completados.

### /workflow-next

Mostra próximo agente e ação recomendados.

## Fluxo de Execução

1. **Iniciando**: Carrega definição → Identifica primeira etapa → Transiciona para agente → Orienta criação de artefato

2. **Transições de Etapa**: Marca completo → Verifica condições → Carrega próximo agente → Passa artefatos

3. **Rastreamento de Artefatos**: Rastreia status, criador, timestamps no workflow_state

4. **Tratamento de Interrupção**: Analisa artefatos fornecidos → Determina posição → Sugere próximo passo

## Passagem de Contexto

Ao transicionar, passe:

- Artefatos criados na etapa atual
- Estado do workflow (progresso, metadados)
- Contexto relevante para próxima etapa
- Instruções específicas para o próximo agente

## Estados de Workflow

- **not_started**: Workflow definido mas não iniciado
- **in_progress**: Ativamente sendo executado
- **paused**: Pausado aguardando entrada/decisão
- **completed**: Todos os artefatos criados e objetivos atingidos
- **failed**: Erro ou condição de falha encontrada

## Estrutura de Dados

```yaml
workflow_state:
  id: greenfield-fullstack
  status: in_progress
  current_stage: 2
  artifacts:
    - name: project-brief
      status: completed
      creator: Product Owner
      timestamp: 2024-02-15T10:30:00Z
    - name: prd
      status: in_progress
      creator: Product Owner
      timestamp: 2024-02-15T11:00:00Z
  metadata:
    started_at: 2024-02-15T10:00:00Z
    team_bundle: fullstack-team
```
