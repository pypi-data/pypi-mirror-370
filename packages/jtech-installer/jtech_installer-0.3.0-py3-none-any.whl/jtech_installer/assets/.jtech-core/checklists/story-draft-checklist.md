<!-- Powered by JTECH™ Core -->

# Checklist de Rascunho de História

O Scrum Master deve usar esta checklist para validar se cada história contém contexto suficiente para que um agente desenvolvedor possa implementá-la com sucesso, assumindo que o agente tem capacidade razoável para descobrir detalhes.

[[LLM: INSTRUÇÕES DE INICIALIZAÇÃO - VALIDAÇÃO DE RASCUNHO DE HISTÓRIA

Antes de prosseguir com esta checklist, certifique-se de ter acesso a:

1. O documento da história a ser validada (geralmente em docs/stories/ ou fornecido diretamente)
2. Contexto do épico pai
3. Quaisquer documentos de arquitetura ou design referenciados
4. Histórias anteriores relacionadas, se for uma continuação

IMPORTANTE: Esta checklist valida histórias individuais ANTES do início da implementação.

PRINCÍPIOS DE VALIDAÇÃO:

1. Clareza - O desenvolvedor deve entender O QUE construir
2. Contexto - POR QUE está sendo construído e como se encaixa
3. Orientação - Decisões técnicas e padrões a seguir
4. Testabilidade - Como verificar se a implementação funciona
5. Autossuficiência - A maioria das informações necessárias está na própria história

LEMBRE-SE: Assumimos agentes desenvolvedores competentes que podem:

- Pesquisar documentação e bases de código
- Tomar decisões técnicas razoáveis
- Seguir padrões estabelecidos
- Pedir esclarecimentos quando realmente necessário

Estamos verificando orientação SUFICIENTE, não detalhes exaustivos.]]

## 1. CLAREZA DE OBJETIVO & CONTEXTO

[[LLM: Sem objetivos claros, desenvolvedores constroem a coisa errada. Verifique:

1. A história declara QUE funcionalidade implementar
2. O valor de negócio ou benefício ao usuário está claro
3. Como isso se encaixa no épico/produto maior está explicado
4. Dependências estão explícitas ("requer História X concluída")
5. Sucesso é algo específico, não vago]]

- [ ] Objetivo/propósito da história está claramente declarado
- [ ] Relação com objetivos do épico é evidente
- [ ] Como a história se encaixa no fluxo geral do sistema está explicado
- [ ] Dependências de histórias anteriores estão identificadas (se aplicável)
- [ ] Contexto de negócio e valor estão claros
