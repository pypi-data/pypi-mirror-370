<!-- Powered by JTECH™ Core -->

# Checklist Mestre de Validação do Product Owner (PO)

Esta checklist serve como um framework abrangente para o Product Owner validar planos de projeto antes da execução do desenvolvimento. Adapta-se inteligentemente conforme o tipo de projeto (greenfield vs brownfield) e inclui considerações de UI/UX quando aplicável.

[[LLM: INSTRUÇÕES DE INICIALIZAÇÃO - CHECKLIST MESTRE PO

DETECÇÃO DO TIPO DE PROJETO:
Primeiro, determine o tipo de projeto verificando:

1. É um projeto GREENFIELD (novo do zero)?
   - Procure: Inicialização de novo projeto, sem referências a código existente
   - Verifique: prd.md, architecture.md, histórias de setup de novo projeto

2. É um projeto BROWNFIELD (aprimorando sistema existente)?
   - Procure: Referências a código existente, linguagem de aprimoramento/modificação
   - Verifique: brownfield-prd.md, brownfield-architecture.md, análise de sistema existente

3. O projeto inclui componentes UI/UX?
   - Verifique: frontend-architecture.md, especificações UI/UX, arquivos de design
   - Procure: Histórias de frontend, especificações de componentes, menções a interface de usuário

REQUISITOS DE DOCUMENTAÇÃO:
Conforme o tipo de projeto, certifique-se de ter acesso a:

Para projetos GREENFIELD:

- prd.md - Documento de Requisitos do Produto
- architecture.md - Arquitetura do sistema
- frontend-architecture.md - Se houver UI/UX
- Todas as definições de épico e história

Para projetos BROWNFIELD:

- brownfield-prd.md - Requisitos de aprimoramento brownfield
- brownfield-architecture.md - Arquitetura de aprimoramento
- Acesso ao código do projeto existente (CRÍTICO - não prossiga sem isso)
- Detalhes de configuração de implantação e infraestrutura atuais
- Esquemas de banco de dados, documentação de API, configuração de monitoramento

INSTRUÇÕES DE PULAR:

- Pule seções marcadas [[BROWNFIELD ONLY]] para projetos greenfield
- Pule seções marcadas [[GREENFIELD ONLY]] para projetos brownfield
- Pule seções marcadas [[UI/UX ONLY]] para projetos apenas backend
- Informe todas as seções puladas em seu relatório final

ABORDAGEM DE VALIDAÇÃO:
