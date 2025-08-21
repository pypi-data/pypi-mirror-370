<!-- Powered by JTECH™ Core -->

# Checklist de Validação de Solução de Arquitetura

Esta checklist serve como um framework abrangente para o Arquiteto validar o design técnico e a arquitetura antes da execução do desenvolvimento. O Arquiteto deve trabalhar sistematicamente cada item, garantindo que a arquitetura seja robusta, escalável, segura e alinhada aos requisitos do produto.

[[LLM: INSTRUÇÕES DE INICIALIZAÇÃO - ARTEFATOS NECESSÁRIOS

Antes de prosseguir com esta checklist, certifique-se de ter acesso a:

1. architecture.md - Documento principal de arquitetura (ver docs/architecture.md)
2. prd.md - Documento de Requisitos do Produto para alinhamento de requisitos (ver docs/prd.md)
3. frontend-architecture.md ou fe-architecture.md - Se for um projeto de UI (ver docs/frontend-architecture.md)
4. Quaisquer diagramas de sistema referenciados na arquitetura
5. Documentação de API, se disponível
6. Detalhes da stack tecnológica e especificações de versão

IMPORTANTE: Se algum documento necessário estiver faltando ou inacessível, peça imediatamente ao usuário sua localização ou conteúdo antes de prosseguir.

DETECÇÃO DO TIPO DE PROJETO:
Primeiro, determine o tipo de projeto verificando:

- A arquitetura inclui componente frontend/UI?
- Existe documento frontend-architecture.md?
- O PRD menciona interfaces de usuário ou requisitos de frontend?

Se for um projeto apenas backend ou serviço:

- Pule seções marcadas com [[FRONTEND ONLY]]
- Foque atenção extra em design de API, arquitetura de serviços e padrões de integração
- Informe em seu relatório final que seções de frontend foram puladas devido ao tipo de projeto

ABORDAGEM DE VALIDAÇÃO:
Para cada seção, você deve:

1. Análise Profunda - Não apenas marque caixas, analise minuciosamente cada item com base na documentação fornecida
2. Baseado em Evidências - Cite seções ou trechos específicos dos documentos ao validar
3. Pensamento Crítico - Questione suposições e identifique lacunas, não apenas confirme o que está presente
4. Avaliação de Riscos - Considere o que pode dar errado em cada decisão arquitetural

MODO DE EXECUÇÃO:
Pergunte ao usuário se deseja trabalhar a checklist:

- Seção por seção (modo interativo) - Revise cada seção, apresente achados, obtenha confirmação antes de prosseguir
- Tudo de uma vez (modo abrangente) - Faça análise completa e apresente relatório ao final]]

## 1. ALINHAMENTO DE REQUISITOS

[[LLM: Antes de avaliar esta seção, entenda completamente o propósito e os objetivos do produto a partir do PRD. Qual é o problema central a ser resolvido? Quem são os usuários? Quais são os fatores críticos de sucesso? Tenha isso em mente ao validar o alinhamento. Para cada item, não apenas verifique se está mencionado - certifique-se de que a arquitetura fornece uma solução técnica concreta.]]
