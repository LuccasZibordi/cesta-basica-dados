# Análise comparativa e preditiva de preços da cesta básica

Relatório coletivo de PI e extensão — 2º semestre de 2026.

**Instituição:** PUC-Campinas · Escola Politécnica  
**Curso:** Engenharia de Computação  
**Turma:** 218040  
**Disciplina:** Sistemas Inteligentes e Aprendizado de Máquina  
**Professor:** Fernando Soares de Aguiar Neto

| Integrante | RA |
| --- | --- |
| Luccas Gomes Zibordi | 24007138 |
| Bruno Vinicius Selingardi | 24004238 |
| João Vitor Bombo Guimarães | 24018551 |
| Vinícius de Moraes Chaves | 24007303 |

## Introdução e aplicação esperada

O estudo explora onde comprar, quando comprar e como interpretar previsões para o mês seguinte. O público potencial são consumidores e famílias interessados em organizar compras. O produto é uma análise acessível com gráficos e tabelas; não se afirma que houve atendimento comunitário ou economia efetivamente obtida.

O professor solicita ao menos uma questão com objetivo/motivação, método/avaliação e conclusão. O grupo desenvolve as três questões previstas no planejamento. Os relatórios individuais seguem exigência institucional separada.

## Fonte, preparação e decisões

Base fornecida ao grupo: ICB_DADOS_2026.xlsx, aba ACUMUL_DESAGREG; 46264 registros, 51 códigos de mercado, 48 meses (2022-09-01 a 2026-08-01). Não há documentação institucional detalhada da coleta disponível nesta entrega.

Tratamento: 44370 linhas válidas, 1743 duplicatas e 151 quarentenas. A planilha original é preservada; base_auditada.csv mantém a linha de origem e motivos.

Mês de referência é a chave temporal; ausência de data exata não elimina preço mensal. Marcas ausentes são admitidas. Duplicatas exatas são removidas por hipótese operacional e preservadas separadamente. Nomes genéricos e valores suspeitos ficam em quarentena, sem correções presumidas.

Preço normalizado é Preco/Quantidade quando coerente com PPK (tolerância absoluta 0,011). Limites inclusivos ≤0,10 ou ≥999 e combinações suspeitas de produto/quantidade são regras fixas motivadas pela auditoria. Não são prova de erro. Aliases de carnes são propostas semânticas explícitas.

Unidades kg/L/unidade foram inferidas; nenhuma foi confirmada documentalmente. Isso limita interpretações monetárias por quantidade. Os cenários e resultados são condicionais a essas hipóteses, não validação da coleta.

Agregação: média das ofertas por produto/mercado/mês; série geral é média dessas médias com pesos iguais por loja. Sem imputação e sem preço zero para ausências. Preços são nominais, sem deflação, pesos de vendas ou consumo familiar. Detalhes das regras estão em regras_aplicadas.json e docs/metodologia.md do código entregue.

A base foi inspecionada retrospectivamente; selecionar cobertura de 48 meses pode excluir produtos que não sobreviveram até o fim. A avaliação não é uma experiência prospectiva cega.

# Questão 1 — Comparação econômica

## Questão
Quais mercados têm menor custo de uma cesta equivalente e qual economia potencial de distribuir as compras?

## Objetivo e motivação
Apoiar a comparação de alternativas de compra. A aplicação direta depende de identificar as lojas, conhecer os itens consumidos e descontar transporte.

## Método e avaliação
Cesta comparativa de referência: uma unidade-base de cada produto (1 kg ou 1 L). É um índice de comparação de preços, não uma estimativa de consumo mensal familiar.
Os cinco itens básicos não perecíveis ou de compra frequente permitem uma comparação reduzida com cobertura longitudinal; não representam a composição nutricional oficial de uma cesta básica. Quantidades unitárias isolam a comparação de preços sem inventar consumo familiar.
Preço representativo: média mensal das ofertas válidas em cada mercado. O custo é a soma de preço por unidade × quantidade da cesta. Item ausente torna a cesta incompleta, nunca custo zero.
O ranking principal usa somente mercados com cesta completa em TODOS os meses da janela global, selecionados pela cobertura, sem olhar os menores preços. Todas as médias comparam os mesmos meses. É um painel restrito, não uma classificação de todas as lojas.
A análise complementar compara pares com pelo menos 24 meses comuns. A diferença A−B usa somente a interseção exportada em comparacoes_pareadas.csv. Pares com períodos distintos não formam um ranking global. O corte reduz comparações com pouco histórico; a sensibilidade ao corte consta no relatório coletivo.
Empates recebem a mesma posição mínima; cada empatado conta como vencedor do mês. A frequência divide vitórias pelos meses do painel. Top-3 é complementar e pouco informativo se o painel tem apenas três lojas.
Rankings anuais usam o mesmo painel e os mesmos meses dentro de cada ano. A correlação de Spearman entre anos usa apenas anos com 12 meses, evitando comparar estações distintas. Não há inferência causal.
Compra distribuída escolhe o mínimo por item apenas entre lojas do mesmo painel, no mesmo mês. Apresentamos a economia frente a cada loja e frente ao melhor mercado único. São mínimos de médias mensais, não ofertas garantidas disponíveis simultaneamente. Deslocamento não entra no cálculo.

## Resultados
Painel: 3 mercados, 48 meses, 09/2022–08/2026. Menor custo médio neste painel: SUP_01, R$ 28.68.
Economia média da distribuição frente ao melhor mercado único: R$ 0.11 (0.36%, média dos percentuais mensais).

| Mercado | Meses | Custo médio (R$) | Meses com menor custo |
| --- | ---: | ---: | ---: |
| SUP_01 | 48 | 28.68 | 48 |
| SUP_32 | 48 | 33.28 | 0 |
| SUP_50 | 48 | 34.32 | 0 |

![Custos no painel](../analises/comparacao_mercados/ranking_custo_medio.svg)
![Trajetória](../analises/comparacao_mercados/trajetoria_custos.svg)

## Conclusão e discussão
SUP_01 tem o menor custo médio entre as lojas do painel, não necessariamente entre todas as lojas da cidade. A redução do painel é o preço da comparação temporal rigorosa; os demais mercados são examinados apenas em pares.
A economia calculada é bruta: só compensa distribuir compras se superar transporte e outros custos. Não equivale a economia mensal de uma família sem informar sua cesta e frequência de compra.
Comparações pareadas elegíveis: 372; veja meses e diferenças no CSV.
Unidades são inferidas, códigos SUP_* não identificam endereços e preços são nominais. Marcas, cobertura e quantidades afetam as conclusões. Não há custo de transporte, ponderação por vendas ou garantia de disponibilidade.
Cobertura/exclusões: cobertura_cesta.csv; cestas completas e incompletas: custos_disponiveis.csv; parâmetros: config_utilizada.json; estabilidade: ranking_anual.csv e estabilidade_anual.csv.


# Questão 2 — Sazonalidade dos preços

## Questão
Há padrões recorrentes que indiquem épocas potencialmente mais econômicas para adquirir os produtos?

## Objetivo e motivação
Apoiar o planejamento de compras, distinguindo tendência de longo prazo e oscilações recorrentes. Um mês historicamente favorável não garante desconto futuro.

## Método e avaliação
Selecionamos séries mensais gerais completas com preços positivos e unidade única conhecida (ainda inferida). A média geral atribui peso igual aos mercados disponíveis; a composição pode mudar. Elegibilidade e exclusões estão no CSV.
STL robusta no log do preço, período 12, janela sazonal padrão 7. O log expressa variações proporcionais. Médias móveis 3 meses retrospectiva e 12 centrada são apenas descritivas e não entram em previsão. Volatilidade: desvio-padrão das diferenças mensais do log.
Força sazonal: máximo entre zero e 1 − Var(resíduo)/Var(sazonal+resíduo). ACF sobre diferenças do log reduz tendência; linhas ±1,96/raiz(n) são referências aproximadas de ruído branco, sem correção para múltiplas comparações, não um teste confirmatório.
Comparamos perfis anuais sem tendência por correlação, exigindo ao menos seis meses comuns por par de anos. Anos parciais são identificados nas tabelas. Indício exploratório: força sazonal e correlação média ≥0,30. Esses cortes buscam sinais não triviais, são escolhas operacionais e não níveis de significância; a sensibilidade é apresentada abaixo.

## Resultados e avaliação
12 produtos completos analisados. A classificação e meses extremos descrevem esta amostra, não recomendações universais.
| Produto | Força sazonal | Correlação entre anos | Indício | Mês de menor componente |
| --- | ---: | ---: | --- | --- |
| Arroz | 0.254 | -0.076 | não | Mar |
| Açúcar | 0.000 | -0.047 | não | Jul |
| Banana Nanica | 0.598 | 0.306 | sim | Abr |
| Banana Prata | 0.295 | 0.151 | não | Jul |
| Batata | 0.448 | 0.349 | sim | Set |
| Café | 0.000 | -0.290 | não | Ago |
| Carne Bovina Coxão Mole | 0.138 | -0.073 | não | Jul |
| Feijão | 0.471 | 0.149 | não | Out |
| Leite | 0.449 | 0.441 | sim | Fev |
| Manteiga | 0.000 | 0.142 | não | Dez |
| Tomate | 0.642 | 0.435 | sim | Set |
| Óleo | 0.175 | 0.321 | não | Jul |

Corte exploratório 0.2 em ambas as medidas: 4 produtos com indício.
Corte exploratório 0.3 em ambas as medidas: 4 produtos com indício.
Corte exploratório 0.5 em ambas as medidas: 0 produtos com indício.

![Calendário sazonal](../analises/sazonalidade/graficos/calendario_precos.png)

## Conclusão e discussão
Indícios pelos critérios principais: Banana Nanica, Batata, Leite, Tomate.
O objetivo de explorar épocas favoráveis foi atendido de forma descritiva. Produtos sem consistência suficiente não sustentam indicação de um mês de compra. ACF, força e comparação entre anos são evidências complementares, não prova causal.
Há apenas quatro ciclos na base original; o ajuste e a avaliação descritiva usam a mesma amostra. Clima, inflação e entrada/saída de lojas podem alterar os perfis. Não extrapolar para anos futuros sem novas observações.
Mesmo com indício, antecipar compras depende de conservação, espaço, necessidade e capital disponível; especialmente perecíveis não devem ser estocados só pelo calendário.

Os CSVs de médias móveis, perfil por ano e resumo sustentam a análise. Figuras stl_* e acf_* mostram cada produto; as unidades de preço constam em elegibilidade.csv.


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
| Arroz | kg | 2026-09 | linear | 5.0529 |
| Arroz | kg | 2026-09 | naive | 4.9981 |
| Arroz | kg | 2026-09 | rf | 5.0614 |
| Açúcar | kg | 2026-09 | linear | 4.0639 |
| Açúcar | kg | 2026-09 | naive | 4.0152 |
| Açúcar | kg | 2026-09 | rf | 4.1739 |
| Banana Nanica | kg | 2026-09 | linear | 7.2187 |
| Banana Nanica | kg | 2026-09 | naive | 7.0492 |
| Banana Nanica | kg | 2026-09 | rf | 7.2992 |
| Banana Prata | kg | 2026-09 | linear | 11.5981 |
| Banana Prata | kg | 2026-09 | naive | 11.5965 |
| Banana Prata | kg | 2026-09 | rf | 11.2007 |
| Batata | kg | 2026-09 | linear | 6.5152 |
| Batata | kg | 2026-09 | naive | 6.0419 |
| Batata | kg | 2026-09 | rf | 5.5192 |
| Café | kg | 2026-09 | linear | 58.2222 |
| Café | kg | 2026-09 | naive | 59.2394 |
| Café | kg | 2026-09 | rf | 60.7627 |
| Carne Bovina Coxão Mole | kg | 2026-09 | linear | 54.9584 |
| Carne Bovina Coxão Mole | kg | 2026-09 | naive | 54.3104 |
| Carne Bovina Coxão Mole | kg | 2026-09 | rf | 53.0738 |
| Feijão | kg | 2026-09 | linear | 9.4212 |
| Feijão | kg | 2026-09 | naive | 10.0530 |
| Feijão | kg | 2026-09 | rf | 9.7149 |
| Leite | L | 2026-09 | linear | 6.2579 |
| Leite | L | 2026-09 | naive | 6.5801 |
| Leite | L | 2026-09 | rf | 6.0922 |
| Manteiga | kg | 2026-09 | linear | 74.1780 |
| Manteiga | kg | 2026-09 | naive | 72.1504 |
| Manteiga | kg | 2026-09 | rf | 72.6370 |
| Tomate | kg | 2026-09 | linear | 7.2459 |
| Tomate | kg | 2026-09 | naive | 7.7942 |
| Tomate | kg | 2026-09 | rf | 7.7079 |
| Óleo | L | 2026-09 | linear | 8.7765 |
| Óleo | L | 2026-09 | naive | 8.7689 |
| Óleo | L | 2026-09 | rf | 9.0668 |

## Interpretação por produto

| Produto | Menor MAPE no teste | MAPE (%) | MAE (R$/unidade) |
| --- | --- | ---: | ---: |
| Arroz | linear | 2.99 | 0.1436 |
| Açúcar | naive | 4.73 | 0.1996 |
| Banana Nanica | linear | 5.15 | 0.3533 |
| Banana Prata | rf | 7.57 | 0.7684 |
| Batata | rf | 18.78 | 1.5345 |
| Café | naive | 2.38 | 1.4877 |
| Carne Bovina Coxão Mole | naive | 2.39 | 1.2776 |
| Feijão | naive | 5.98 | 0.5687 |
| Leite | naive | 7.52 | 0.4469 |
| Manteiga | rf | 2.44 | 1.7445 |
| Tomate | linear | 17.48 | 1.7144 |
| Óleo | naive | 1.78 | 0.1584 |

O vencedor por produto é uma descrição posterior do teste, não uma seleção validada para implantação. Não selecionar hiperparâmetros por essas vitórias.
Os lags 1–3 capturam persistência recente; lag 12 representa o mesmo mês do ano anterior. Médias 3/6 suavizam ruído; seno/cosseno preservam continuidade do calendário. São escolhas parcimoniosas para apenas 48 meses.
Grid RF: 100/300 árvores, profundidade livre/5, mínimo 1/3 observações por folha. A validação temporal escolhe MAPE; profundidade e tamanho de folha controlam complexidade. Há poucos exemplos para modelos flexíveis.
Teste: previsões sequenciais a um passo com preços reais conhecidos até o mês anterior, sem reajustar pesos dentro do bloco. Não é previsão simultânea de seis meses.
Depois de congelar métricas, modelos operacionais são reajustados em todo o histórico com os mesmos hiperparâmetros. A coluna treinado_ate documenta o corte. O mês seguinte é relativo ao fim da base, não à data em que este relatório é lido.
Aplicação: para uma quantidade explicitada q de um único produto, q × MAE ilustra a magnitude média histórica do erro monetário. Isso não é margem garantida nem intervalo de confiança; combinar erros de produtos exige avaliar a cesta conjunta. Sem consumo familiar informado não estimamos orçamento mensal.
![Comparação dos modelos](../analises/previsao/comparacao_modelos.png)
![Preços reais e previstos](../analises/previsao/precos_reais_vs_previstos.png)
![Erros no tempo](../analises/previsao/erros_no_tempo.png)

## Limitações

- A janela tem apenas 48 meses (cerca de quatro ciclos anuais) e 12 meses de aquecimento para o lag 12.
- Unidades são inferidas e não confirmadas pela fonte; preços são nominais.
- Selecionar séries completas é viés de sobrevivência: produtos com histórico curto ficam de fora.
- A série geral pondera mercados igualmente; mudanças na composição de lojas afetam o preço médio.
- Hiperparâmetros foram escolhidos retrospectivamente na validação; não houve avaliação prospectiva cega.
- Sem pesos de consumo, inflação ou promoções: a previsão não substitui o orçamento familiar.


# Sensibilidade das decisões

Análises retrospectivas, sem selecionar o cenário que favorece um modelo. Alteramos uma decisão por vez.
Duplicatas: mantemos todas as repetições e reaplicamos as demais regras. As séries alternativas e a configuração estão nesta pasta. A quarentena continua ativa.
Composição: para cada produto, comparamos a média dos mercados disponíveis com a média de lojas observadas em todos os meses. São painéis específicos por produto; itens sem loja completa não têm comparação. Isso mede sensibilidade, não estima o efeito causal de entrada/saída de lojas.
| Produto | Meses pareados | Diferença absoluta média (%) — composição |
| --- | ---: | ---: |
| Arroz | 48 | 2.354 |
| Açúcar | 48 | 3.741 |
| Batata | 48 | 8.220 |
| Café | 48 | 2.899 |
| Carne Bovina Coxão Mole | 48 | 5.379 |
| Feijão | 48 | 2.648 |
| Leite | 48 | 2.683 |
| Manteiga | 48 | 3.323 |
| Tomate | 48 | 6.434 |
| Óleo | 48 | 1.906 |

Duplicatas: maior diferença absoluta média percentual por produto = 0.119%. Veja impacto_duplicatas.csv.

| Cenário | Lojas no painel | Pares elegíveis | Menor custo no painel | Economia vs melhor único (R$) |
| --- | ---: | ---: | --- | ---: |
| base | 3 | 372 | SUP_01 | 0.107 |
| cobertura_12 | 3 | 424 | SUP_01 | 0.107 |
| cobertura_36 | 3 | 298 | SUP_01 | 0.107 |
| arroz_peso_2 | 3 | 372 | SUP_01 | 0.128 |
| com_duplicatas | 3 | 372 | SUP_01 | 0.107 |

## A composição altera as conclusões sazonais?
| Produto | Indício na base | Indício no painel fixo | Mínimo na base | Mínimo no painel fixo |
| --- | --- | --- | --- | --- |
| Arroz | False | False | Mar | Ago |
| Açúcar | False | False | Jul | Ago |
| Batata | True | False | Set | Set |
| Café | False | False | Ago | Jul |
| Carne Bovina Coxão Mole | False | False | Jul | Mar |
| Feijão | False | True | Out | Out |
| Leite | True | True | Fev | Jan |
| Manteiga | False | False | Dez | Nov |
| Tomate | True | True | Set | Set |
| Óleo | False | False | Jul | Jul |

Mudança de classificação: Batata, Feijão.
Meses mínimos só sugerem época favorável quando há indício e consistência. Divergências entre as duas séries mostram que a conclusão depende da composição; não escolhemos a versão com sazonalidade mais forte. Produtos sem painel fixo completo não puderam ser confrontados.
A questão 2 deve ser lida junto deste confronto: os padrões não são robustos universalmente ao conjunto de lojas. Não reavaliamos modelos preditivos sobre esses painéis; sua avaliação continua condicionada à série geral original.

Os cortes 12/24/36 mudam o suporte das comparações pareadas; o painel principal continua exigindo a janela inteira. Peso 2 para arroz é cenário ilustrativo de preferência, não consumo familiar observado.
Estabilidade nesses cenários não valida unidades inferidas, aliases ou observações em quarentena. Não foi feita busca exaustiva de cestas nem reavaliação prospectiva dos modelos. Mudanças de composição podem afetar sazonalidade e previsão; seus resultados permanecem condicionados à série de mercados disponíveis.


# Apêndice — decomposição e autocorrelação por produto

As figuras abaixo usam a janela da base. Preço observado está em R$ por unidade inferida do produto; componentes STL estão em log. A tabela de elegibilidade identifica a unidade.

![stl_acucar](../analises/sazonalidade/graficos/stl_acucar.png)

![ACF stl_acucar](../analises/sazonalidade/graficos/acf_acucar.png)

![stl_arroz](../analises/sazonalidade/graficos/stl_arroz.png)

![ACF stl_arroz](../analises/sazonalidade/graficos/acf_arroz.png)

![stl_banana_nanica](../analises/sazonalidade/graficos/stl_banana_nanica.png)

![ACF stl_banana_nanica](../analises/sazonalidade/graficos/acf_banana_nanica.png)

![stl_banana_prata](../analises/sazonalidade/graficos/stl_banana_prata.png)

![ACF stl_banana_prata](../analises/sazonalidade/graficos/acf_banana_prata.png)

![stl_batata](../analises/sazonalidade/graficos/stl_batata.png)

![ACF stl_batata](../analises/sazonalidade/graficos/acf_batata.png)

![stl_cafe](../analises/sazonalidade/graficos/stl_cafe.png)

![ACF stl_cafe](../analises/sazonalidade/graficos/acf_cafe.png)

![stl_carne_bovina_coxao_mole](../analises/sazonalidade/graficos/stl_carne_bovina_coxao_mole.png)

![ACF stl_carne_bovina_coxao_mole](../analises/sazonalidade/graficos/acf_carne_bovina_coxao_mole.png)

![stl_feijao](../analises/sazonalidade/graficos/stl_feijao.png)

![ACF stl_feijao](../analises/sazonalidade/graficos/acf_feijao.png)

![stl_leite](../analises/sazonalidade/graficos/stl_leite.png)

![ACF stl_leite](../analises/sazonalidade/graficos/acf_leite.png)

![stl_manteiga](../analises/sazonalidade/graficos/stl_manteiga.png)

![ACF stl_manteiga](../analises/sazonalidade/graficos/acf_manteiga.png)

![stl_oleo](../analises/sazonalidade/graficos/stl_oleo.png)

![ACF stl_oleo](../analises/sazonalidade/graficos/acf_oleo.png)

![stl_tomate](../analises/sazonalidade/graficos/stl_tomate.png)

![ACF stl_tomate](../analises/sazonalidade/graficos/acf_tomate.png)

# Síntese e limites de uso

A comparação responde à questão dentro de um painel pequeno com períodos equivalentes; pares ampliam a exploração sem permitir ranking global. Sazonalidade oferece indícios exploratórios, não garantia de meses baratos. A previsão é julgada contra o último preço observado: resultados negativos continuam informativos para evitar complexidade sem ganho.

Não é possível recomendar lojas reais pelos códigos SUP_* nem estimar economia líquida sem transporte. A cesta de cinco itens é comparativa, não orçamento nutricional ou familiar. Para uso social direto, comunicar essas restrições e conferir preços atuais com os consumidores.

## Reproduzir

Na raiz do código, instalar requirements.txt e executar em pasta vazia:

```bash
python main.py --saida dados/reproducao --modulos comparacao_mercados sazonalidade previsao
```

O manifesto registra versões, hashes do código/configurações/origem e artefatos. O relatório deriva da mesma execução das tabelas e gráficos. A validação computacional não substitui validação dos dados ou aprovação acadêmica.

## Referências e fontes

- Enunciado do professor fornecido por Luccas e Planejamento_PI_Cesta_Basica.pdf (quatro páginas), consultados em 25/11/2026. Modelo institucional dos relatórios individuais recebido em 25/11/2026 e preservado em docs/modelos. Cada integrante elabora e submete seu próprio relatório de extensão, acompanhado dos arquivos de suporte.

- ICB_DADOS_2026.xlsx, base fornecida ao grupo, identificação detalhada da instituição/coleta pendente.

- [STL — documentação oficial statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html). Decomposição sazonal por LOESS; opções utilizadas documentadas na questão 2.

- [RandomForestRegressor — documentação oficial scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html). Parâmetros utilizados documentados na questão 3.

- [Validação temporal — documentação oficial scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split). Aqui usamos blocos cronológicos fixos, sem afirmar uso de TimeSeriesSplit.

Documentações consultadas em 25/11/2026.
