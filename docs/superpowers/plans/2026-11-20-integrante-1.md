# Integrante 1 — Implementation Plan

> **For agentic workers:** executar sequencialmente com superpowers:executing-plans; conferir testes e registrar evidências abaixo.

**Goal:** entregar preparação reproduzível dos dados e ponto de integração para os três módulos analíticos.

**Architecture:** preprocessing.py importa, valida e classifica as linhas; series_temporais.py agrega e mede cobertura; main.py exporta e orquestra módulos opcionais. Regras externas em config/tratamento.json, artefatos em dados/ e documentação em docs/.

**Tech Stack:** Python >=3.12, pandas, openpyxl; pytest para verificação.

**Spec:** ../specs/2026-11-20-integrante-1.md

## Global Constraints
- Preservar Excel e valores originais; manter trilha de cada exclusão.
- Não preencher ausências nem aprender filtros a partir do futuro.
- Unidades inferidas e nomes genéricos pendentes devem ficar explícitos.
- Não implementar questões 1–3 nem afirmar integração real de módulos ausentes.

## Review Focus
- Arquivo ou esquema inválido deve falhar sem gerar resultado aparentemente completo.
- Repetições não podem eliminar observações de marcas diferentes.
- Pares totalmente em quarentena devem aparecer com cobertura zero.
- Muitos registros em uma loja não podem dominá-la na média geral.
- Módulo solicitado ausente ou com erro deve retornar falha verificável.

### Task 1: Importação e tratamento
**Files:** preprocessing.py, config/tratamento.json, tests/test_preprocessing.py.
**Interfaces:** carregar_excel(caminho: Path, aba: str) -> DataFrame; tratar_dados(brutos: DataFrame, regras: dict) -> DataFrame. Saída mantém originais e adiciona linha_origem, mes, mercado, produto, marca, preco_embalagem, quantidade, preco_unitario, unidade, unidade_status, status, motivos, duplicata_de.
- [x] Escrever/rodar testes de repetição, quantidade zero, preço inválido, PPK incoerente, data ausente, nomes ambíguos e importação com coluna extra preenchida.
- [x] Implementar leitura/validação e configuração auditável.
- [x] Rodar .venv/bin/python -m pytest tests/test_preprocessing.py -q; esperado: todos passam.

### Task 2: Séries e cobertura
**Files:** series_temporais.py, tests/test_series.py.
**Interfaces:** construir_series(base: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame], respectivamente mercado, geral, cobertura; consome saída de tratar_dados.
- [x] Escrever/rodar testes de média de mercados com pesos iguais, mês ausente, produto só em quarentena e preservação de prefixo histórico.
- [x] Implementar agregação, grade e cobertura com lacunas explícitas.
- [x] Rodar .venv/bin/python -m pytest -q; esperado: todos passam.

### Task 3: Execução, integração e documentação
**Files:** main.py, tests/test_main.py, README.md, docs/metodologia.md, docs/contrato_dados.md, requirements*.txt, .gitignore.
**Interfaces:** executar_pipeline(entrada: Path, saida: Path, config: Path, modulos: tuple[str, ...] = ()) -> dict. Módulos opcionais exportam executar(dados_dir: Path, saida_dir: Path).
- [x] Escrever/rodar testes CLI/pipeline com Excel sintético, hash da origem preservado, exportação reprodutível e módulos ausentes/com falha.
- [x] Exportar CSVs, diagnóstico JSON/Markdown, cópia das regras e manifesto com hashes/versões.
- [x] Documentar reprodução, decisões, contrato e limites de integração.
- [x] Rodar suíte completa, pipeline real e comparar duas execuções independentes.
- [x] Solicitar revisão independente final, resolver achados relevantes e registrar evidências.

## Registro de execução
- Planejamento e especificação produzidos com base no PDF e na auditoria real. Luccas confirmou ser o integrante 1 e pediu planejar e executar depois; execução local na mesma sessão, sem nova confirmação.
- Decisão: branch feat/integrante-1-dados na pasta existente, preservando o Excel não rastreado e evitando duplicação da base em outro checkout. Sem commit/push.
- Interfaces: tarefa 2 consome a classificação da tarefa 1; tarefa 3 exporta as três tabelas da tarefa 2. Nenhuma dependência dos módulos analíticos para preparar os dados.

- Tarefa 1 concluída: 19 testes de preparação passaram após regressões de leitura; fonte preservada.
- Tarefa 2 concluída: 5 testes de séries passaram; janela global corrigida para incluir meses com identificadores inválidos.
- Tarefa 3 concluída: 6 testes de execução/integração passaram; suíte total 30/30, dependências compatíveis.
- Revisão independente final aprovada sem achados pendentes. Removido arredondamento CSV; preservados tokens textuais/zeros à esquerda; corrigida janela global.
- Duas execuções finais da base real produziram 11 artefatos idênticos por SHA-256. 44.370 válidas, 1.743 duplicatas, 151 quarentenas; Excel intacto. Evidências em docs/validacao.md.
- Integração real com módulos dos colegas e validação das hipóteses metodológicas permanecem dependências externas, não resultados alegados.
