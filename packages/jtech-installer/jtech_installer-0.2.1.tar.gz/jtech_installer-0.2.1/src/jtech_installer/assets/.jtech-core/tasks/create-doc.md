<!-- Powered by JTECH™ Core -->

# Criar Documento a partir de Template (Orientado por YAML)

## ⚠️ AVISO CRÍTICO DE EXECUÇÃO ⚠️

**ESTE É UM WORKFLOW EXECUTÁVEL - NÃO MATERIAL DE REFERÊNCIA**

Quando esta tarefa é invocada:

1. **DESABILITE TODAS AS OTIMIZAÇÕES DE EFICIÊNCIA** - Este workflow requer interação completa do usuário
2. **EXECUÇÃO PASSO A PASSO MANDATÓRIA** - Cada seção deve ser processada sequencialmente com feedback do usuário
3. **ELICITAÇÃO É OBRIGATÓRIA** - Quando `elicit: true`, você DEVE usar o formato 1-9 e aguardar resposta do usuário
4. **NÃO SÃO PERMITIDOS ATALHOS** - Documentos completos não podem ser criados sem seguir este workflow

**INDICADOR DE VIOLAÇÃO:** Se você criar um documento completo sem interação do usuário, violou este workflow.

## Crítico: Descoberta de Template

Se um Template YAML não foi fornecido, liste todos os templates de .jtech-core/templates ou peça ao usuário para fornecer outro.

## CRÍTICO: Formato de Elicitação Mandatório

**Quando `elicit: true`, isto é uma PARADA OBRIGATÓRIA exigindo interação do usuário:**

**VOCÊ DEVE:**

1. Apresentar conteúdo da seção
2. Fornecer justificativa detalhada (explicar trade-offs, suposições, decisões tomadas)
3. **PARE e apresente opções numeradas 1-9:**
   - **Opção 1:** Sempre "Prosseguir para próxima seção"
   - **Opções 2-9:** Selecionar 8 métodos de data/elicitation-methods
   - Terminar com: "Selecione 1-9 ou apenas digite sua pergunta/feedback:"
4. **AGUARDE RESPOSTA DO USUÁRIO** - Não prossiga até usuário selecionar opção ou fornecer feedback

**VIOLAÇÃO DE WORKFLOW:** Criar conteúdo para seções elicit=true sem interação do usuário viola esta tarefa.

**NUNCA faça perguntas sim/não ou use qualquer outro formato.**

## Fluxo de Processamento

1. **Parse do template YAML** - Carregar metadados e seções do template
2. **Definir preferências** - Mostrar modo atual (Interativo), confirmar arquivo de saída
3. **Processar cada seção:**
   - Pular se condição não atendida
   - Verificar permissões do agente (owner/editors) - anotar se seção é restrita a agentes específicos
   - Rascunhar conteúdo usando instrução da seção
   - Apresentar conteúdo + justificativa detalhada
   - **SE elicit: true** → Formato MANDATÓRIO de opções 1-9
   - Salvar em arquivo se possível
