# Cesta básica — PI e extensão

Análise comparativa e preditiva de preços para planejamento financeiro familiar. Esta entrega implementa a parte do **integrante 1 (Luccas)**: diagnóstico, tratamento rastreável, séries mensais e execução centralizada.

## Estado da entrega

- Preparação implementada e executada sobre `ICB_DADOS_2026.xlsx`.
- Dados preparados em [`dados/preparados`](dados/preparados); leia primeiro o [diagnóstico](dados/preparados/diagnostico.md).
- A previsão (integrante 4) está implementada em `previsao.py`/`avaliacao.py`, executada e documentada em `dados/analise_previsao/questao3.md`.
- Comparação de mercados e sazonalidade são responsabilidades dos integrantes 2–3. Esses módulos ainda não foram entregues.
- Unidades são inferidas; nomes genéricos e observações suspeitas aguardam revisão da fonte. Os CSVs são uma versão preliminar documentada para desenvolvimento, não resultados finais da pesquisa.

## Executar

Python 3.12 ou superior. No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --saida dados/nova_execucao
```

No Windows, ative com `.venv\Scripts\activate` no lugar do comando `source`. Com `uv`, a instalação equivalente é `uv venv .venv` e `uv pip install --python .venv/bin/python -r requirements.txt`.

A execução sem argumentos usa o Excel da raiz e a saída `dados/preparados`. Como esta entrega já inclui essa saída, escolha um **diretório novo/vazio** para reproduzir; arquivos existentes nunca são sobrescritos pelo programa. A execução demora alguns segundos nesta base.

```bash
python main.py --entrada ICB_DADOS_2026.xlsx --config config/tratamento.json --saida dados/reproducao
```

O programa informa sucesso ou retorna código 1 em caso de falha. O `manifesto.json` registra versões, hashes da origem/configuração/código, artefatos e estado da execução. Confirme `status: concluido` antes de consumir resultados.

## O que cada arquivo faz

| Arquivo | Responsabilidade |
| --- | --- |
| `preprocessing.py` | Leitura, validação, normalização, classificação e rastreabilidade |
| `series_temporais.py` | Agregação por mês/mercado/produto, série geral e cobertura |
| `main.py` | Execução, exportação, diagnóstico e integração opcional |
| `previsao.py` | Previsão a um mês: features, modelos cronológicos e saídas (integrante 4) |
| `avaliacao.py` | MAE, RMSE, MAPE e comparação com o Naive (integrante 4) |
| `config/tratamento.json` | Regras explícitas, aliases, unidades e justificativas |
| `tests/` | Casos controlados de qualidade de dados, médias, lacunas, previsão e integração |

## Entregar aos colegas

Compartilhe a pasta de dados inteira, junto de [contrato de dados](docs/contrato_dados.md) e [metodologia](docs/metodologia.md). A interpretação dos campos e das ausências faz parte da entrega.

| Integrante | Arquivos iniciais |
| --- | --- |
| 2 — comparação | `series_mercado.csv`, `cobertura.csv`, `base_tratada.csv` |
| 3 — sazonalidade | `series_geral.csv` ou `series_mercado.csv`, `cobertura.csv` |
| 4 — previsão | `series_geral.csv`; módulo entregue, saídas em `dados/analise_previsao` |

Não somar preços unitários para calcular uma cesta sem definir quantidades consumidas. Não comparar cestas incompletas. Não preencher lacunas com zero. Todos os preços são nominais.

Quando os módulos reais existirem na raiz e seguirem o contrato:

```bash
python main.py --saida dados/integrada --modulos comparacao_mercados sazonalidade previsao
```

## Verificar

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes usam planilhas pequenas com resultados calculados à mão e não dependem de serviços externos. A reprodução da base real é feita com `main.py`; comparar `artefatos_sha256` de duas execuções com mesmas regras e dependências. Datas de execução do manifesto mudam; os CSVs e diagnósticos devem coincidir.

## Documentação e pendências

- [Plano de implementação](docs/superpowers/plans/2026-11-20-integrante-1.md)
- [Métodos, decisões e limites](docs/metodologia.md)
- [Contrato de dados e integração](docs/contrato_dados.md)
- [Validação da entrega](docs/validacao.md)
- [Validação da previsão](docs/validacao_previsao.md)

Para fechar o trabalho completo ainda faltam: revisão das unidades/nomes/quarentena com a fonte; definição coletiva da cesta, cobertura e períodos; módulos 2–3 e integração conjunta; relatório coletivo, relatórios individuais de extensão e preparação da arguição. O modelo institucional e o prazo não foram fornecidos. Não há dashboard nem base externa nesta etapa.
