<!-- Powered by JTECH™ Core -->

# Especificação de Template de Documento JTech

## Visão Geral

Os templates de documento JTech são definidos em formato YAML para facilitar a geração interativa de documentos e a interação com agentes. Os templates separam a definição de estrutura da geração de conteúdo, tornando-os amigáveis tanto para humanos quanto para agentes LLM.

## Estrutura do Template

```yaml
template:
  id: identificador-template
  name: Nome Legível do Template
  version: 1.0
  output:
    format: markdown
    filename: caminho-padrao/para/{{filename}}.md
    title: '{{variable}} Título do Documento'

workflow:
  mode: interactive
  elicitation: advanced-elicitation

sections:
  - id: id-secao
    title: Título da Seção
    instruction: |
      Instruções detalhadas para o LLM sobre como tratar esta seção
    # ... propriedades adicionais da seção
```

## Campos Principais

### Metadados do Template

- **id**: Identificador único do template
- **name**: Nome legível exibido na interface
- **version**: Versão do template para controle de alterações
- **output.format**: Padrão "markdown" para templates de documento
- **output.filename**: Caminho padrão do arquivo de saída (pode incluir variáveis)
- **output.title**: Título do documento (vira H1 no markdown)

### Configuração de Workflow

- **workflow.mode**: Modo de interação padrão ("interactive" ou "yolo")
- **workflow.elicitation**: Tarefa de elicitação a ser usada ("advanced-elicitation")

## Propriedades da Seção
