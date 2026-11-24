# Questão 3 — previsão de preços da cesta básica

## Questão e objetivo

É possível prever o preço médio dos produtos da cesta básica no mês seguinte usando dados históricos? O objetivo é avaliar se a previsão ajuda a reservar recursos para a compra do próximo mês.

## Método

- Entrada: `series_geral.csv` (12 produtos com 48/48 meses válidos e unidade conhecida). Produtos com lacunas, poucos meses ou unidade desconhecida foram excluídos sem imputação.
- Variáveis: lags 1, 2, 3, 12, médias móveis 3, 6 calculadas com deslocamento de um mês, seno/cosseno do mês. Toda feature usa apenas preços até t-1.
- Divisão cronológica: 36 meses marcados como treino, dos quais 24 entram no modelo após o aquecimento do lag 12; 6 de validação e 6 de teste (2026-03 a 2026-08). O grid do Random Forest foi escolhido pelo MAPE na validação; os modelos finais foram reajustados em treino+validação e avaliados uma única vez no teste.
- Modelos: Naive (último preço observado), regressão linear padronizada e Random Forest. Métricas: MAE, RMSE e MAPE, comparadas com o Naive.

## Avaliação

| Modelo | MAE médio (R$/unidade) | RMSE médio | MAPE médio (%) | Diferença de MAPE vs Naive (p.p.) |
| --- | ---: | ---: | ---: | ---: |
| naive | 0.9944 | 1.2329 | 7.93 | +0.00 |
| linear | 1.2671 | 1.4582 | 8.06 | +0.13 |
| rf | 1.5425 | 1.7280 | 9.53 | +1.61 |

Modelo de menor MAPE médio: **naive**. Vitórias por produto (menor MAPE): naive=6, linear=3, rf=3.
MAE e RMSE são agregados apenas para referência: as unidades são kg, L e unidade, então o MAPE é a medida comparável entre produtos.

## Conclusão

No período de teste, o modelo **naive** apresentou o menor erro relativo médio. Nenhum modelo superou a referência Naive em média, o que indica pouco ganho previsível com as variáveis utilizadas.
A previsão do próximo mês é um ponto estimado; o erro histórico do modelo é a medida de incerteza disponível, não um intervalo de confiança.

## Previsão para o mês seguinte

| Produto | Unidade | Mês | Modelo | Preço previsto |
| --- | --- | --- | --- | ---: |
| Arroz | kg | 2026-09 | linear | 5.0600 |
| Arroz | kg | 2026-09 | naive | 4.9981 |
| Arroz | kg | 2026-09 | rf | 5.3589 |
| Açúcar | kg | 2026-09 | linear | 4.4555 |
| Açúcar | kg | 2026-09 | naive | 4.0152 |
| Açúcar | kg | 2026-09 | rf | 4.5898 |
| Banana Nanica | kg | 2026-09 | linear | 7.0978 |
| Banana Nanica | kg | 2026-09 | naive | 7.0492 |
| Banana Nanica | kg | 2026-09 | rf | 7.3314 |
| Banana Prata | kg | 2026-09 | linear | 11.3414 |
| Banana Prata | kg | 2026-09 | naive | 11.5965 |
| Banana Prata | kg | 2026-09 | rf | 11.3068 |
| Batata | kg | 2026-09 | linear | 6.3657 |
| Batata | kg | 2026-09 | naive | 6.0419 |
| Batata | kg | 2026-09 | rf | 5.3896 |
| Café | kg | 2026-09 | linear | 54.9312 |
| Café | kg | 2026-09 | naive | 59.2394 |
| Café | kg | 2026-09 | rf | 67.0780 |
| Carne Bovina Coxão Mole | kg | 2026-09 | linear | 52.3141 |
| Carne Bovina Coxão Mole | kg | 2026-09 | naive | 54.3104 |
| Carne Bovina Coxão Mole | kg | 2026-09 | rf | 50.3152 |
| Feijão | kg | 2026-09 | linear | 9.0659 |
| Feijão | kg | 2026-09 | naive | 10.0530 |
| Feijão | kg | 2026-09 | rf | 8.2595 |
| Leite | L | 2026-09 | linear | 6.1534 |
| Leite | L | 2026-09 | naive | 6.5801 |
| Leite | L | 2026-09 | rf | 5.7602 |
| Manteiga | kg | 2026-09 | linear | 74.8553 |
| Manteiga | kg | 2026-09 | naive | 72.1504 |
| Manteiga | kg | 2026-09 | rf | 72.6650 |
| Tomate | kg | 2026-09 | linear | 7.6287 |
| Tomate | kg | 2026-09 | naive | 7.7942 |
| Tomate | kg | 2026-09 | rf | 7.6174 |
| Óleo | L | 2026-09 | linear | 8.5668 |
| Óleo | L | 2026-09 | naive | 8.7689 |
| Óleo | L | 2026-09 | rf | 9.2639 |

## Limitações

- A janela tem apenas 48 meses (cerca de quatro ciclos anuais) e 12 meses de aquecimento para o lag 12.
- Unidades são inferidas e não confirmadas pela fonte; preços são nominais.
- Selecionar séries completas é viés de sobrevivência: produtos com histórico curto ficam de fora.
- A série geral pondera mercados igualmente; mudanças na composição de lojas afetam o preço médio.
- Hiperparâmetros foram escolhidos retrospectivamente na validação; não houve avaliação prospectiva cega.
- Sem pesos de consumo, inflação ou promoções: a previsão não substitui o orçamento familiar.
