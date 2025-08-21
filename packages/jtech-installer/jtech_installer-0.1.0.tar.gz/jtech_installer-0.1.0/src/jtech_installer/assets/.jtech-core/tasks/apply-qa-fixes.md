<!-- Powered by JTECH™ Core -->

# apply-qa-fixes

Implementar correções baseadas em resultados de QA (gate e avaliações) para uma história específica. Esta tarefa é para o agente Dev consumir sistematicamente saídas de QA e aplicar mudanças de código/teste enquanto atualiza apenas seções permitidas no arquivo de história.

## Propósito

- Ler saídas de QA para uma história (gate YAML + markdowns de avaliação)
- Criar um plano de correção priorizado e determinístico
- Aplicar mudanças de código e teste para fechar lacunas e resolver problemas
- Atualizar apenas as seções de história permitidas para o agente Dev

## Entradas

```yaml
required:
  - story_id: '{epic}.{story}' # ex: "2.2"
  - qa_root: de `.jtech-core/core-config.yml` chave `qa.qaLocation` (ex: `docs/project/qa`)
  - story_root: de `.jtech-core/core-config.yml` chave `devStoryLocation` (ex: `docs/project/stories`)

optional:
  - story_title: '{title}' # derive do H1 da história se faltando
  - story_slug: '{slug}' # derive do título (minúsculo, hifenizado) se faltando
```

## Fontes de QA para Ler

- Gate (YAML): `{qa_root}/gates/{epic}.{story}-*.yml`
  - Se múltiplos, use o mais recente por tempo de modificação
- Avaliações (Markdown):
  - Design de Teste: `{qa_root}/assessments/{epic}.{story}-test-design-*.md`
  - Rastreabilidade: `{qa_root}/assessments/{epic}.{story}-trace-*.md`
  - Perfil de Risco: `{qa_root}/assessments/{epic}.{story}-risk-*.md`
  - Avaliação NFR: `{qa_root}/assessments/{epic}.{story}-nfr-*.md`

## Pré-requisitos

- Repositório compila e testes executam localmente (Deno 2)
- Comandos de lint e teste disponíveis:
  - `deno lint`
  - `deno test -A`

## Processo (Não pule etapas)

### 0) Carregar Config Central & Localizar História

- Ler `.jtech-core/core-config.yml` e resolver `qa_root` e `story_root`
- Localizar arquivo de história em `{story_root}/{epic}.{story}.*.md`
  - PARE se faltando e peça id/caminho correto da história
