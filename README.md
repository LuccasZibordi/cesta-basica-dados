# Cesta básica — PI e extensão

Exploração de preços para comparação de compras, sazonalidade e previsão mensal. As três questões estão implementadas. A entrega técnica atual usa um painel temporal comparável, explicita incertezas da base e inclui relatório coletivo gerado pelo código.

## Ler os resultados

- [Relatório coletivo em PDF](entrega/relatorio_coletivo.pdf).
- [Relatório coletivo em HTML](dados/entrega_2026-11-25/relatorios/relatorio_coletivo.html): independente, com imagens incorporadas, pode ser aberto no navegador e impresso.
- [Relatório coletivo em Markdown](dados/entrega_2026-11-25/relatorios/relatorio_coletivo.md).
- [Pendências de entrega](docs/pendencias_entrega.md): os relatórios individuais ainda dependem do modelo institucional e de informações verdadeiras dos integrantes.
- [Verificação final](docs/validacao_final.md) e [roteiro de arguição](docs/arguicao.md).

A presença do relatório técnico não significa submissão ou validação de horas. Unidades e aliases permanecem hipóteses documentadas; não foram inventadas confirmações da coleta.

## Instalar e reproduzir

Python 3.12 ou superior. Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --saida dados/nova_entrega --modulos comparacao_mercados sazonalidade previsao
```

Windows: ativar `.venv\Scripts\activate`. A execução completa leva alguns minutos, principalmente pelo ajuste dos modelos. Sempre escolher diretório novo/vazio; arquivos anteriores são preservados.

Com os três módulos solicitados, o comando também executa as sensibilidades e monta o relatório coletivo em `relatorios/`. Sem `--modulos`, faz apenas preparação. Um subconjunto executa apenas as análises pedidas. Conferir `status: concluido` no manifesto antes de usar a saída.

```bash
python main.py --entrada ICB_DADOS_2026.xlsx --config config/tratamento.json --saida dados/preparacao_nova
python comparacao_mercados.py --dados dados/preparados --saida dados/comparacao_nova
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

O manifesto registra versões, hashes da origem, código, configurações e artefatos. O teste cronológico de previsão fica preservado; modelos para o mês seguinte ao fim da base são depois reajustados com todo o histórico. Setembro/2026 não é uma previsão futura em relação à data de leitura deste trabalho.

## Arquivos e métodos

| Arquivo | Função |
| --- | --- |
| `preprocessing.py` | Importação, normalização, auditoria e quarentena |
| `series_temporais.py` | Médias mensais e cobertura, sem imputação |
| `comparacao_mercados.py` | Painel integral, pares em meses comuns, rankings, economias e questão 1 |
| `sazonalidade.py` | STL, ACF, calendário, consistência anual e questão 2 |
| `previsao.py`, `avaliacao.py` | Naive, regressão linear, Random Forest, avaliação temporal e questão 3 |
| `sensibilidade.py` | Duplicatas, pesos da cesta, cobertura e composição de lojas |
| `relatorio.py` | Relatório coletivo com figuras e exportação HTML |
| `main.py` | Orquestração, manifesto e preservação dos dados |
| `config/` | Hipóteses de tratamento e cesta comparativa |
| `tests/` | Casos controlados com resultados verificáveis e regressões |

Leia [metodologia](docs/metodologia.md) e [contrato](docs/contrato_dados.md). O relatório contém justificativas, resultados e limites de cada questão.

A cesta de cinco itens com quantidades unitárias é um índice comparativo, não uma estimativa do gasto mensal familiar. Códigos SUP_* não identificam lojas reais; a economia exclui deslocamento. A seleção de séries completas é retrospectiva. Resultados não demonstram causalidade nem garantem preços futuros.

## Dados e histórico

`ICB_DADOS_2026.xlsx` é a fonte preservada. `dados/entrega_2026-11-25` é a execução atual completa. `dados/preparados`, `dados/comparacao_integrada` e `dados/analise_previsao` são execuções anteriores preservadas para rastreabilidade; **não são a entrega final atual**. A comparação antiga misturava períodos e foi substituída pela análise atual.

Documentos de auditoria e planos de 20/11 descrevem estados históricos. Consulte `docs/validacao_final.md` para o estado vigente. Não interpretar contagens antigas de testes como validação do checkout atual.

## Entrega acadêmica

O enunciado pede ao menos uma questão completa; o grupo mantém as três planejadas. São necessários relatório coletivo, relatórios individuais conforme modelo e código/bases. Cada aluno deve submeter seu relatório individual e os arquivos de suporte na atividade de EXTENSÃO.

O modelo institucional fornecido está preservado em `docs/modelos/`. A pedido de Luccas, os relatórios individuais não foram elaborados nesta execução. Não há registro inventado de horas, participação comunitária ou submissão. Não é necessário criar dashboard ou fonte externa para cumprir o enunciado fornecido.

## Exportação opcional em PDF

O pipeline gera HTML independente e Markdown. A cópia PDF em `entrega/` foi exportada desse HTML com WeasyPrint 70.0. Para repetir a exportação no ambiente com suporte ao WeasyPrint:

```bash
uv run --no-project --with-requirements requirements-exportacao.txt weasyprint dados/entrega_2026-11-25/relatorios/relatorio_coletivo.html entrega/relatorio_coletivo.pdf
```

Alternativamente, abrir o HTML e imprimir como PDF pelo navegador. A conferência do formato aceito na atividade continua a cargo do grupo.
