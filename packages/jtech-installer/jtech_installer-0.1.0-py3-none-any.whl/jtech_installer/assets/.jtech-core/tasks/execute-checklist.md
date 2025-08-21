<!-- Powered by JTECH™ Core -->

# Tarefa de Validação de Checklist

Esta tarefa fornece instruções para validar documentação contra checklists. O agente DEVE seguir estas instruções para garantir validação completa e sistemática de documentos.

## Checklists Disponíveis

Se o usuário perguntar ou não especificar uma checklist específica, liste as checklists disponíveis para a persona do agente. Se a tarefa estiver sendo executada sem um agente específico, diga ao usuário para verificar a pasta .jtech-core/checklists para selecionar a apropriada.

## Instruções

1. **Avaliação Inicial**
   - Se usuário ou tarefa executada fornecer nome de checklist:
     - Tente correspondência difusa (ex: "checklist arquitetura" -> "architect-checklist")
     - Se múltiplas correspondências encontradas, peça esclarecimento ao usuário
     - Carregue a checklist apropriada de .jtech-core/checklists/
   - Se nenhuma checklist especificada:
     - Pergunte ao usuário qual checklist deseja usar
     - Apresente as opções disponíveis dos arquivos na pasta checklists
