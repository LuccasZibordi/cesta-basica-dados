# Cesta básica — análise de preços e previsão

Projeto acadêmico de PI e extensão desenvolvido na disciplina de Sistemas Inteligentes e Aprendizado de Máquina. O grupo utiliza Python para estudar preços de alimentos em varejistas de Campinas, comparar mercados, investigar variações ao longo do ano e avaliar previsões para o mês seguinte.

O objetivo é transformar a planilha de preços em informações que ajudem a compreender o custo dos alimentos e possam apoiar a divulgação pelo Observatório PUC-Campinas. O trabalho reúne preparação dos dados, análise exploratória, séries temporais e aprendizado supervisionado. Não houve avaliação do uso dos resultados pela comunidade nem medição de economia efetiva das famílias.

## Questões do projeto

| Questão | Objetivo | Método |
| --- | --- | --- |
| Quais mercados apresentam menor custo? | Comparar uma cesta de referência e avaliar a economia de comprar em lojas diferentes. | Comparação nos mesmos meses, rankings, frequência de menor custo e economia frente à melhor compra em um único mercado. |
| Os preços apresentam padrões ao longo do ano? | Investigar se determinados meses costumam apresentar preços maiores ou menores. | Decomposição STL, médias móveis, autocorrelação, volatilidade e comparação dos padrões entre anos. |
| É possível prever o preço do próximo mês? | Verificar se modelos de aprendizado supervisionado superam uma previsão simples. | Naive, regressão linear e Random Forest, com treino, validação e teste em ordem cronológica. |

O relatório coletivo apresenta questão, objetivo e motivação, método, avaliação e conclusão para cada uma das três análises.

## Dados utilizados

A fonte é a planilha [`ICB_DADOS_2026.xlsx`](ICB_DADOS_2026.xlsx), aba `ACUMUL_DESAGREG`, fornecida para o trabalho. Ela contém **46.264 registros**, **51 códigos de mercado** e **48 meses**, de setembro de 2022 a agosto de 2026.

A preparação confere datas e valores, padroniza nomes de produtos por regras explícitas, identifica duplicatas e separa registros duvidosos para revisão. A planilha original é preservada, e as saídas registram os motivos dos tratamentos.

| Resultado da preparação | Quantidade |
| --- | ---: |
| Registros válidos | 44.370 |
| Duplicatas exatas removidas | 1.743 |
| Registros separados em quarentena | 151 |

As séries mensais usam a média por produto e mercado. A série geral calcula a média entre mercados com o mesmo peso para cada loja. Preços ausentes não são substituídos por zero nem preenchidos artificialmente.

## Resultados e limitações

- **Comparação de mercados:** o painel principal usa `SUP_01`, `SUP_32` e `SUP_50` nos mesmos 48 meses. Há também 372 comparações entre pares com pelo menos 24 meses em comum. Isso evita comparar médias de períodos diferentes.
- **Sazonalidade:** alguns padrões mudam quando fixamos a composição dos mercados. Batata e feijão, por exemplo, mudam de classificação entre os cenários. Os resultados são exploratórios e não sustentam uma regra universal de compra por mês.
- **Previsão:** no teste, o erro percentual absoluto médio foi de **7,93% para Naive**, **8,06% para regressão linear** e **9,53% para Random Forest**. Os modelos mais complexos não superaram a referência simples em média.
- **Validação técnica:** a revisão de 26/11/2026 executou os testes e reproduziu as análises. As contagens e comparações estão nos registros de validação. Consulte a [validação final](docs/validacao_final.md) e a [verificação de reprodução](docs/verificacao_entrega_2026-11-26.json).

A cesta comparativa contém arroz, açúcar, feijão, leite e óleo, com uma unidade-base de cada produto: 1 kg ou 1 L. Ela é uma referência de preços, **não uma estimativa do consumo mensal de uma família**. Os códigos `SUP_*` não permitem identificar lojas reais, e a economia calculada não inclui transporte.

Unidades e equivalências entre nomes de produtos dependem de confirmação documental da coleta. As análises explicitam essas hipóteses e examinam a sensibilidade dos resultados. A previsão posterior ao fim da base é para setembro de 2026, não para o mês seguinte à execução do programa. A avaliação no teste ocorre antes do reajuste dos modelos com todo o histórico disponível.

## Onde consultar os resultados

- [Relatório coletivo em PDF](entrega/relatorio_coletivo.pdf), com 40 páginas.
- [Relatório coletivo em HTML](dados/entrega_2026-11-26/relatorios/relatorio_coletivo.html), com imagens incorporadas, para abrir no navegador.
- [Relatório coletivo em Markdown](dados/entrega_2026-11-26/relatorios/relatorio_coletivo.md).
- Pacote final: `cesta-basica-entrega-final-2026-11-26.zip`, distribuído separadamente; não há outro ZIP dentro dele.
- Os relatórios individuais são enviados em tarefa separada e não fazem parte deste pacote.
- [Metodologia](docs/metodologia.md), [contrato dos dados](docs/contrato_dados.md) e [roteiro para a arguição](docs/arguicao.md).

A execução completa de referência está em `dados/entrega_2026-11-26/`. O pacote final inclui somente essa execução. As pastas de execuções anteriores permanecem no repositório de trabalho como histórico e não devem substituir os resultados finais.

O pacote contém o relatório coletivo, o código, a planilha original, as bases utilizadas, os testes e a documentação necessária para reprodução. Relatórios individuais, modelos em branco, backups, ambientes virtuais e arquivos de controle do Git ficam fora do ZIP.

## Organização do projeto

| Arquivo ou pasta | Responsabilidade |
| --- | --- |
| `main.py` | Executa as etapas solicitadas e registra o manifesto da execução. |
| `preprocessing.py` | Importa, confere, padroniza e audita os dados. |
| `series_temporais.py` | Monta séries mensais e indicadores de disponibilidade dos dados. |
| `comparacao_mercados.py` | Compara mercados, rankings e alternativas de compra. |
| `sazonalidade.py` | Investiga padrões temporais e produz gráficos e calendário sazonal. |
| `previsao.py` e `avaliacao.py` | Treinam e avaliam previsões com separação cronológica. |
| `sensibilidade.py` | Examina o efeito de duplicatas, cobertura, pesos da cesta e composição das lojas. |
| `relatorio.py` | Reúne os resultados no relatório coletivo em Markdown e HTML. |
| `config/` | Guarda as regras de tratamento e a definição da cesta comparativa. |
| `tests/` | Contém testes automatizados das etapas e das correções metodológicas. |
| `docs/` | Reúne metodologia, validações e o modelo institucional preservado. |
| `dados/` | Guarda bases processadas e saídas das análises. |
| `entrega/` | Reúne documentos e o pacote de suporte para entrega. |

## Entrega acadêmica

Cada integrante deve enviar seu próprio relatório de extensão e os arquivos de suporte na atividade de **EXTENSÃO**. O relatório individual de Luccas está preenchido; os demais integrantes elaborarão os seus. O modelo institucional é tratado separadamente, fora deste pacote técnico.

O grupo ainda deve verificar prazo e formatos aceitos, reunir os relatórios individuais e se preparar para justificar as escolhas na arguição. A existência dos arquivos não significa que a submissão ou a validação das horas já ocorreu.

## Como rodar o projeto

### 1. Preparar o ambiente

Use **Python 3.12**, versão utilizada na validação. Execute os comandos na raiz do projeto, onde estão `main.py`, `requirements.txt` e a planilha original.

No Linux ou macOS:

```bash
cd /caminho/para/cesta-basica-dados
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows, pelo PowerShell:

```powershell
cd C:\caminho\para\cesta-basica-dados
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nos próximos comandos, usuários do Windows podem substituir `python` por `.\.venv\Scripts\python.exe`, sem precisar ativar o ambiente.

### 2. Executar a análise completa

```bash
python main.py --saida dados/nova_execucao --modulos comparacao_mercados sazonalidade previsao
```

O comando prepara os dados, executa as três análises, calcula as sensibilidades e gera o relatório coletivo. O ajuste dos modelos pode levar alguns minutos.

**Escolha uma pasta de saída nova ou vazia.** O programa interrompe a execução se ela já contiver arquivos. Para repetir, use outro nome, como `dados/nova_execucao_2`.

Ao terminar, consulte:

- `dados/nova_execucao/manifesto.json`: deve conter `"status": "concluido"`; registra versões, configurações e hashes dos arquivos.
- `dados/nova_execucao/diagnostico.md`: resumo da preparação dos dados.
- `dados/nova_execucao/analises/`: tabelas, gráficos e resultados dos módulos.
- `dados/nova_execucao/relatorios/relatorio_coletivo.html`: relatório para abrir no navegador.

### 3. Executar somente parte do trabalho

Somente preparação, sem os módulos de análise:

```bash
python main.py --entrada ICB_DADOS_2026.xlsx --config config/tratamento.json --saida dados/nova_preparacao
```

Preparação seguida apenas da comparação entre mercados:

```bash
python main.py --saida dados/nova_comparacao --modulos comparacao_mercados
```

O relatório coletivo e as análises complementares de sensibilidade são gerados quando os três módulos são solicitados juntos. Para consultar os argumentos disponíveis:

```bash
python main.py --help
```

### 4. Rodar os testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

### 5. Exportar o relatório coletivo para PDF, se necessário

A execução gera HTML e Markdown. Abra o HTML no navegador e use a opção de imprimir como PDF. Como alternativa, em um ambiente com suporte ao WeasyPrint e com `uv` instalado:

```bash
uv run --no-project --with-requirements requirements-exportacao.txt weasyprint dados/nova_execucao/relatorios/relatorio_coletivo.html dados/nova_execucao/relatorios/relatorio_coletivo.pdf
```

Confira a paginação do PDF antes de utilizá-lo na entrega.
