<!-- Powered by JTECH™ Core -->

# Documentar um Projeto Existente

## Propósito

Gerar documentação abrangente para projetos existentes otimizada para agentes de desenvolvimento AI. Esta tarefa cria materiais de referência estruturados que permitem agentes AI entender contexto, convenções e padrões do projeto para contribuição efetiva a qualquer base de código.

## Instruções da Tarefa

### 1. Análise Inicial do Projeto

**CRÍTICO:** Primeiro, verifique se um PRD ou documento de requisitos existe no contexto. Se sim, use-o para focar seus esforços de documentação apenas em áreas relevantes.

**SE PRD EXISTE**:

- Revise o PRD para entender que melhoria/funcionalidade está planejada
- Identifique quais módulos, serviços ou áreas serão afetados
- Foque documentação APENAS nestas áreas relevantes
- Pule partes não relacionadas da base de código para manter docs enxutos

**SE NÃO HÁ PRD**:
Pergunte ao usuário:

"Notei que você não forneceu um PRD ou documento de requisitos. Para criar documentação mais focada e útil, recomendo uma destas opções:

1. **Criar um PRD primeiro** - Gostaria que eu ajudasse a criar um PRD brownfield antes de documentar? Isso ajuda a focar documentação em áreas relevantes.

2. **Fornecer requisitos existentes** - Você tem um documento de requisitos, épico ou descrição de funcionalidade que pode compartilhar?

3. **Descrever o foco** - Pode descrever brevemente que melhoria ou funcionalidade está planejando? Por exemplo:
   - 'Adicionando processamento de pagamento ao serviço de usuário'
   - 'Refatorando o módulo de autenticação'
   - 'Integrando com uma nova API de terceiros'

4. **Documentar tudo** - Ou devo prosseguir com documentação abrangente de toda a base de código? (Nota: Isso pode criar documentação excessiva para projetos grandes)

Por favor me informe sua preferência, ou posso prosseguir com documentação completa se preferir."

Baseado na resposta:

- Se escolherem opção 1-3: Use esse contexto para focar documentação
- Se escolherem opção 4 ou recusarem: Prossiga com análise abrangente abaixo

Comece conduzindo análise do projeto existente. Use ferramentas disponíveis para:

1. **Descoberta de Estrutura do Projeto**: Examinar estrutura do diretório raiz, identificar pastas principais e entender organização geral
2. **Identificação de Stack Tecnológica**: Procurar package.json, requirements.txt, Cargo.toml, pom.xml, etc. para identificar linguagens, frameworks e dependências
3. **Análise de Sistema de Build**: Encontrar scripts de build, configurações CI/CD e comandos de desenvolvimento
4. **Revisão de Documentação Existente**: Verificar arquivos README, pastas docs e qualquer documentação existente
