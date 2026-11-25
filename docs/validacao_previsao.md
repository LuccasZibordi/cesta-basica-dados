# Validação — integrante 4 (previsão)

Verificado em 24/11/2026, branch `integrante-4-precos`, Python 3.14.4. Ambiente criado com `python -m venv .venv` e `pip install -r requirements.txt -r requirements-dev.txt`.

## Testes e integração

- `.venv/bin/python -m pytest -q` — **39 passaram** (30 do integrante 1 + 9 do módulo de previsão).
- `.venv/bin/python -m pip check` — sem conflitos de dependências.
- `python main.py --saida <pasta nova> --modulos previsao` — `status: concluido` e módulo `concluido` no manifesto, com 20 artefatos registrados.
- Casos novos: seleção de séries completas, dois `unidade_status` no mesmo mês, divisão cronológica, features imunes ao futuro, métricas calculadas à mão, comparação com o Naive, saídas sem alterar entradas, determinismo do modelo e validação do esquema de entrada.

## Reprodução

Três execuções independentes, em processos separados, sobre `dados/preparados` produziram **9 arquivos idênticos por SHA-256**. O Random Forest usa `random_state=0` e `n_jobs=1`: com paralelismo, empates de MAPE no grid eram resolvidos de forma diferente entre execuções.

| Artefato | SHA-256 |
| --- | --- |
| `metricas.csv` | `83c2d94d7476edd3fbbfa4a4bb0b5e916f73398c3f78a2a5cee5da3f0a1bd2ad` |
| `questao3.md` | `c7e9cf2cd9b57ff9a5fb6591ab1532b82480bd43dc1c534156616061942635ba` |

Saídas publicadas: `dados/analise_previsao`. Relatório da questão: `dados/analise_previsao/questao3.md`.

## Resultados e limites verificados

12 produtos com 48/48 meses entraram na previsão; os demais foram excluídos sem imputação. No teste (2026-03 a 2026-08), o MAPE médio foi 7,93% (Naive), 8,06% (linear) e 9,53% (Random Forest); o Naive venceu em 6 de 12 produtos.

A validação comprova comportamento do código e reprodução, **não a validade econômica das previsões**. Unidades são inferidas, a seleção por série completa é viés de sobrevivência e não houve avaliação prospectiva cega. Nenhum resultado de sazonalidade ou comparação de mercados foi produzido aqui.
