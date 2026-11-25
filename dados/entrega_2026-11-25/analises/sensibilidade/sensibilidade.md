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
