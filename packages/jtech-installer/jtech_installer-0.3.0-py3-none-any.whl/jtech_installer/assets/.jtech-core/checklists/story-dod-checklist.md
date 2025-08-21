<!-- Powered by JTECH™ Core -->

# Checklist de Definição de Pronto (DoD) de História

## Instruções para o Agente Desenvolvedor

Antes de marcar uma história como 'Revisão', percorra cada item desta checklist. Relate o status de cada item (ex: [x] Pronto, [ ] Não Pronto, [N/A] Não Aplicável) e forneça comentários breves se necessário.

[[LLM: INSTRUÇÕES DE INICIALIZAÇÃO - VALIDAÇÃO DOD DE HISTÓRIA

Esta checklist é para AGENTES DESENVOLVEDORES se auto-validarem antes de marcar uma história como concluída.

IMPORTANTE: É uma autoavaliação. Seja honesto sobre o que realmente está pronto versus o que deveria estar. É melhor identificar problemas agora do que encontrá-los na revisão.

ABORDAGEM DE EXECUÇÃO:

1. Percorra cada seção sistematicamente
2. Marque itens como [x] Pronto, [ ] Não Pronto ou [N/A] Não Aplicável
3. Adicione comentários breves explicando itens [ ] ou [N/A]
4. Seja específico sobre o que foi realmente implementado
5. Aponte preocupações ou dívidas técnicas criadas

O objetivo é entrega de qualidade, não apenas marcar caixas.]]

## Itens da Checklist

1. **Requisitos Atendidos:**

   [[LLM: Seja específico - liste cada requisito e se está completo]]
   - [ ] Todos os requisitos funcionais especificados na história estão implementados.
   - [ ] Todos os critérios de aceitação definidos na história estão atendidos.

2. **Padrões de Código & Estrutura do Projeto:**

   [[LLM: Qualidade de código importa para manutenção. Verifique cada item cuidadosamente]]
   - [ ] Todo código novo/modificado segue estritamente as `Diretrizes Operacionais`.
   - [ ] Todo código novo/modificado está alinhado à `Estrutura do Projeto` (localização de arquivos, nomenclatura, etc.).
   - [ ] Aderência à `Stack Tecnológica` para tecnologias/versões usadas (se a história introduz ou modifica uso de tecnologia).
   - [ ] Aderência à `Referência de API` e `Modelos de Dados` (se a história envolve mudanças de API ou modelo de dados).
   - [ ] Práticas básicas de segurança aplicadas para código novo/modificado (validação de entrada, tratamento de erros, sem segredos hardcoded).
   - [ ] Nenhum novo erro ou aviso de linter introduzido.
   - [ ] Código bem comentado onde necessário (lógica complexa, não comentários óbvios).

3. **Testes:**

   [[LLM: Testes provam que seu código funciona. Seja honesto sobre cobertura de testes]]
   - [ ] Todos os testes unitários exigidos conforme a história e a Estratégia de Testes das `Diretrizes Operacionais` estão implementados.
   - [ ] Todos os testes de integração (se aplicável) conforme a história e a Estratégia de Testes das `Diretrizes Operacionais` estão implementados.
   - [ ] Todos os testes (unitários, integração, E2E se aplicável) passam com sucesso.
   - [ ] Cobertura de testes atende aos padrões do projeto (se definido).
