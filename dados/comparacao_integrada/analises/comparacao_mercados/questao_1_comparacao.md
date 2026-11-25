# Questão 1 — Comparação de mercados

## Questão
Quais mercados apresentam o menor custo para uma cesta padronizada ao longo do tempo, e qual seria a economia potencial ao distribuir as compras?

## Objetivo
Comparar o custo mensal da cesta de referência nos mercados com cobertura suficiente e estimar o limite superior de economia de uma compra distribuída.

## Cesta e critérios
Cesta comparativa de referência: uma unidade-base de cada produto (1 kg ou 1 L). É um índice de comparação de preços, não uma estimativa de consumo mensal familiar.
Critério adotado nesta análise: exigir ao menos 24 meses com a cesta completa, metade da janela observada de 48 meses. Isso reduz a influência de mercados com poucos registros e mantém uma amostra temporal ampla. Produtos, quantidades e corte podem ser alterados em `config/cesta_comparacao.json` para análise de sensibilidade.
Quantidades usadas e unidades estão em `cesta_utilizada.csv`. As unidades da base são inferidas e ainda precisam ser confirmadas na fonte. Não se somam kg e L como quantidades físicas: cada preço unitário é multiplicado pela quantidade de referência do respectivo produto, e os custos monetários são somados.

## Método e avaliação
O preço representativo é a média mensal já agregada por produto e mercado em `series_mercado.csv`. O custo da cesta de um mercado é calculado apenas nos meses em que todos os itens têm preço observado. Mercados entram no ranking se tiverem o mínimo configurado de meses com cesta completa. O ranking geral ordena o custo médio mensal; a estabilidade é descrita pela posição mensal média, desvio das posições, frequência entre os três menores custos e correlação de Spearman entre rankings anuais, para pares de anos com ao menos seis meses por mercado.
A compra distribuída escolhe, em cada mês, o menor preço observado de cada item, mesmo que isso exija visitar vários mercados. A economia é a diferença entre a cesta completa de um único mercado e essa referência distribuída nos mesmos meses. Ela é um limite superior antes de deslocamento e outros custos. A avaliação pode ser reproduzida nos CSVs de custos mensais e rankings.

## Resultados desta execução
Foram avaliados 28 mercados elegíveis no período 09/2022–08/2026. O menor custo médio observado foi de SUP_01, com R$ 28.68 por cesta e 48 meses completos. A referência de compra distribuída economizou em média R$ 6.08 (17.9%) frente aos custos de mercados individuais, nos pares de mercado-mês comparáveis. A correlação média de Spearman entre rankings anuais foi 0.93; veja os coeficientes e tamanhos amostrais em `estabilidade_anual.csv`.

## Conclusão e limitações
Nesta cesta e nos critérios adotados, SUP_01 apresentou o menor custo médio entre os mercados elegíveis. A economia da compra distribuída representa um teto teórico: a decisão real depende de a economia superar o custo adicional total de deslocamento. Os códigos dos mercados não identificam lojas ou endereços, então não é possível estimar distâncias. A cesta unitária é uma referência de comparação, não uma recomendação de consumo familiar; resultados dependem das quantidades escolhidas, da seleção de produtos, da cobertura e das unidades ainda inferidas.
Os preços são nominais e representam a amostra mensal, sem ponderação por vendas ou tamanho da loja. Meses incompletos ficam fora do custo de uma cesta individual; diferenças de período entre mercados podem influenciar médias e posições. O menor preço por item pode vir de mercados e marcas diferentes e a coleta não inclui transporte, disponibilidade no momento da compra ou promoções. Os resultados não identificam causalidade nem representam necessariamente todos os supermercados.

## Arquivos gerados
- `ranking_mercados.csv`: custo médio, posição e comparação com compra distribuída.
- `custos_mensais_cesta.csv` e `compra_distribuida_mensal.csv`: resultados mensais e economias pareadas.
- `ranking_anual.csv` e `estabilidade_anual.csv`: comparação de posições entre anos.
- `ranking_custo_medio.svg`, `estabilidade_top3.svg` e `trajetoria_custos.svg`: gráficos vetoriais.
- `cesta_utilizada.csv` e `precos_itens_cesta.csv`: parâmetros e preços usados.
