<!-- Powered by JTECH™ Core -->

# Framework de Níveis de Teste

Guia abrangente para determinar níveis de teste apropriados (unitário, integração, E2E) para diferentes cenários.

## Matriz de Decisão de Nível de Teste

### Testes Unitários

**Quando usar:**

- Teste de funções puras e lógica de negócio
- Correção de algoritmos
- Validação de entrada e transformação de dados
- Tratamento de erros em componentes isolados
- Cálculos complexos ou máquinas de estado

**Características:**

- Execução rápida (feedback imediato)
- Sem dependências externas (BD, API, sistema de arquivos)
- Altamente estável e fácil de manter
- Fácil de depurar falhas

**Exemplo de cenário:**

```yaml
unit_test:
  component: 'PriceCalculator'
  scenario: 'Calcular desconto com múltiplas regras'
  justification: 'Lógica de negócio complexa com múltiplos ramos'
  mock_requirements: 'Nenhum - função pura'
```

### Testes de Integração

**Quando usar:**

- Verificação de interação entre componentes
- Operações e transações de banco de dados
- Contratos de endpoints de API
- Comunicação entre serviços
- Comportamento de middlewares e interceptadores

**Características:**

- Tempo de execução moderado
- Testa limites de componentes
- Pode usar bancos de dados ou containers de teste
