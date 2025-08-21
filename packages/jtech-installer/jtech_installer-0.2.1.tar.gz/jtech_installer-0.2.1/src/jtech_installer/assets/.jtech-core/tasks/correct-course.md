<!-- Powered by JTECH™ Core -->

# Tarefa Corrigir Curso

## Propósito

- Guiar uma resposta estruturada a um gatilho de mudança usando o `.jtech-core/checklists/change-checklist`.
- Analisar os impactos da mudança em épicos, artefatos do projeto e o MVP, guiado pela estrutura da checklist.
- Explorar soluções potenciais (ex: ajustar escopo, reverter elementos, re-dimensionar funcionalidades) conforme solicitado pela checklist.
- Rascunhar atualizações específicas e acionáveis propostas para quaisquer artefatos de projeto afetados (ex: épicos, histórias de usuário, seções de PRD, seções de documento de arquitetura) baseadas na análise.
- Produzir um documento consolidado "Proposta de Mudança de Sprint" que contém a análise de impacto e as edições propostas claramente rascunhadas para revisão e aprovação do usuário.
- Garantir um caminho claro de handoff se a natureza das mudanças necessitar replanejamento fundamental por outros agentes centrais (como PM ou Arquiteto).

## Instruções

### 1. Configuração Inicial & Seleção de Modo

- **Confirmar Tarefa & Entradas:**
  - Confirme com o usuário que a "Tarefa Corrigir Curso" (Navegação e Integração de Mudança) está sendo iniciada.
  - Verifique o gatilho de mudança e garanta que tem a explicação inicial do usuário sobre o problema e seu impacto percebido.
  - Confirme acesso a todos os artefatos de projeto relevantes (ex: PRD, Épicos/Histórias, Documentos de Arquitetura, Especificações UI/UX) e, criticamente, o `.jtech-core/checklists/change-checklist`.
- **Estabelecer Modo de Interação:**
  - Pergunte ao usuário seu modo de interação preferido para esta tarefa:
    - **"Incrementalmente (Padrão & Recomendado):** Vamos trabalhar a change-checklist seção por seção, discutindo achados e rascunhando colaborativamente mudanças propostas para cada parte relevante antes de seguir para a próxima? Isso permite refinamento detalhado, passo a passo."
    - **"Modo YOLO (Processamento em Lote):** Ou, prefere que eu conduza uma análise mais em lote baseada na checklist e depois apresente um conjunto consolidado de achados e mudanças propostas para uma revisão mais ampla? Isso pode ser mais rápido para avaliação inicial mas pode exigir revisão mais extensa das propostas combinadas."
  - Assim que o usuário escolher, confirme o modo selecionado e então informe: "Agora usaremos a change-checklist para analisar a mudança e rascunhar atualizações propostas. Vou guiá-lo através dos itens da checklist baseado em nosso modo de interação escolhido."

### 2. Executar Análise da Checklist (Iterativamente ou em Lote, conforme Modo de Interação)

- Trabalhe sistematicamente através das Seções 1-4 da change-checklist (tipicamente cobrindo Contexto de Mudança, Análise de Impacto de Épico/História, Resolução de Conflito de Artefato e Avaliação/Recomendação de Caminho).
- Para cada item da checklist ou grupo lógico de itens (dependendo do modo de interação):
  - Apresente o(s) prompt(s) ou considerações relevantes da checklist ao usuário.
  - Solicite informações necessárias e analise ativamente os artefatos de projeto relevantes (PRD, épicos, documentos de arquitetura, histórico de histórias, etc.) para avaliar o impacto.
  - Discuta seus achados para cada item com o usuário.
  - Registre o status de cada item da checklist (ex: `[x] Resolvido`, `[N/A]`, `[!] Ação Adicional Necessária`) e quaisquer notas ou decisões pertinentes.
  - Concordem colaborativamente sobre o "Caminho Recomendado Adiante" conforme solicitado pela Seção 4 da checklist.

### 3. Rascunhar Mudanças Propostas (Iterativamente ou em Lote)

- Baseado na análise da checklist completa (Seções 1-4) e o "Caminho Recomendado Adiante" acordado (excluindo cenários que requerem replanos fundamentais que necessitariam handoff imediato para PM/Arquiteto):
  - Identifique os artefatos de projeto específicos que requerem atualizações (ex: épicos específicos, histórias de usuário, seções de PRD, componentes de documento de arquitetura, diagramas).
  - **Rascunhe as mudanças propostas direta e explicitamente para cada artefato identificado.** Exemplos incluem:
    - Revisar texto de história de usuário, critérios de aceitação ou prioridade.
    - Adicionar, remover, reordenar ou dividir histórias de usuário dentro de épicos.
    - Propor trechos modificados de diagrama de arquitetura (ex: fornecendo um bloco de diagrama Mermaid atualizado ou descrição textual clara da mudança para um diagrama existente).
    - Atualizar listas de tecnologia, detalhes de configuração ou seções específicas dentro dos documentos PRD ou arquitetura.
    - Rascunhar novos artefatos de apoio pequenos se necessário (ex: um breve adendo para uma decisão específica).
  - Se em "Modo Incremental," discuta e refine essas edições propostas para cada artefato ou pequeno grupo de artefatos relacionados com o usuário conforme são rascunhados.
  - Se em "Modo YOLO," compile todas as edições rascunhadas para apresentação no próximo passo.
