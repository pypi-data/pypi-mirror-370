<!-- Powered by JTECH™ Core -->

# Matriz de Prioridades de Teste

Guia para priorizar cenários de teste com base em risco, criticidade e impacto de negócio.

## Níveis de Prioridade

### P0 - Crítico (Deve Testar)

**Critérios:**

- Funcionalidade que impacta receita
- Caminhos críticos de segurança
- Operações de integridade de dados
- Requisitos de conformidade regulatória
- Funcionalidade previamente quebrada (prevenção de regressão)

**Exemplos:**

- Processamento de pagamento
- Autenticação/autorização
- Criação/remoção de dados de usuário
- Cálculos financeiros
- Conformidade GDPR/privacidade
- Conformidade LGPD/privacidade

**Requisitos de Teste:**

- Cobertura abrangente em todos os níveis
- Caminhos de sucesso e falha
- Casos extremos e cenários de erro
- Performance sob carga

### P1 - Alto (Deve Testar)

**Critérios:**

- Jornadas principais do usuário
- Funcionalidades frequentemente usadas
- Funcionalidades com lógica complexa
- Pontos de integração entre sistemas
- Funcionalidades que afetam experiência do usuário

**Exemplos:**

- Fluxo de cadastro de usuário
- Funcionalidade de busca
- Importação/exportação de dados
- Sistemas de notificação
- Exibição de dashboards
