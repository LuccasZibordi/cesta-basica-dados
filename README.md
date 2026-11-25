# Cesta básica — PI e extensão

Análise comparativa e preditiva de preços para planejamento financeiro familiar. O projeto reúne a preparação de dados do integrante 1 e a comparação de mercados do integrante 2.

## Estado da entrega

- Preparação implementada e executada sobre `ICB_DADOS_2026.xlsx`.
- Dados preparados em [`dados/preparados`](dados/preparados); leia primeiro o [diagnóstico](dados/preparados/diagnostico.md).
- Comparação de mercados implementada em `comparacao_mercados.py`; a cesta e os resultados estão em `config/cesta_comparacao.json` e `dados/comparacao_integrada/analises/comparacao_mercados/`. A cesta unitária e o corte de cobertura são escolhas metodológicas explícitas desta comparação e podem ser alterados para análise de sensibilidade.
- Sazonalidade e previsão continuam pendentes (integrantes 3 e 4). O contrato de integração foi testado com módulos de teste; a integração real da comparação é executável.
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
| `comparacao_mercados.py` | Custos de cesta, rankings, compra distribuída, gráficos e texto da questão 1 |
| `config/cesta_comparacao.json` | Produtos, quantidades da cesta de referência e mínimo de meses completos |
| `main.py` | Execução, exportação, diagnóstico e integração opcional |
| `config/tratamento.json` | Regras explícitas, aliases, unidades e justificativas |
| `tests/` | Casos controlados de qualidade de dados, médias, lacunas e integração |

## Entregar aos colegas

Compartilhe a pasta de dados inteira, junto de [contrato de dados](docs/contrato_dados.md) e [metodologia](docs/metodologia.md). A interpretação dos campos e das ausências faz parte da entrega.

| Integrante | Arquivos iniciais |
| --- | --- |
| 2 — comparação | `series_mercado.csv`, `cobertura.csv`, `base_tratada.csv`; análise implementada em `comparacao_mercados.py` |
| 3 — sazonalidade | `series_geral.csv` ou `series_mercado.csv`, `cobertura.csv` |
| 4 — previsão | `series_geral.csv`, `cobertura.csv`; divisão cronológica e features ficam no seu módulo |

Não somar preços unitários para calcular uma cesta sem definir quantidades consumidas. Não comparar cestas incompletas. Não preencher lacunas com zero. Todos os preços são nominais.

Para executar a comparação de mercados integrada ao fluxo principal:

```bash
python main.py --saida dados/comparacao_integrada --modulos comparacao_mercados
```

Os módulos de sazonalidade e previsão serão integrados quando forem entregues pelos respectivos integrantes.

Para reproduzir somente a comparação usando a base já preparada, escolha uma pasta de saída nova:

```bash
python comparacao_mercados.py --dados dados/preparados --saida dados/analise_comparacao_nova
```

O relatório da questão 1 fica em `dados/comparacao_integrada/analises/comparacao_mercados/questao_1_comparacao.md`. Os resultados refletem uma cesta comparativa unitária, mercados identificados apenas por códigos e unidades ainda inferidas; descreva esses limites ao apresentar as conclusões.

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

Para fechar o trabalho completo ainda faltam: revisão das unidades/nomes/quarentena com a fonte; módulos de sazonalidade e previsão e sua integração; relatório coletivo, relatórios individuais de extensão e preparação da arguição. O modelo institucional e o prazo não foram fornecidos. Não há dashboard nem base externa nesta etapa.
