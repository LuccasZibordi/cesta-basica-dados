# Metodologia da preparação — integrante 1

## Objetivo

Produzir dados mensais comparáveis e auditáveis para as três questões do projeto. O tratamento não responde às questões nem garante, sozinho, comparabilidade de cestas ou validade de previsões.

## Fonte e rastreabilidade

Fonte fornecida pelo grupo: `ICB_DADOS_2026.xlsx`, aba `ACUMUL_DESAGREG`. Sua proveniência institucional detalhada e o dicionário de coleta precisam ser acrescentados pelo grupo. A leitura encontrou 46.264 registros, 48 meses (09/2022–08/2026), 51 códigos de mercado e 30 rótulos brutos de produto.

O Excel permanece intacto. As oito colunas originais são mantidas em `base_auditada.csv`, junto à linha física da planilha (`linha_origem`, começando em 2). CSV é representação tabular e não preserva estilos/fórmulas/tipos de célula; para consulta exata da fonte, use o Excel e seu hash no manifesto.

Cada linha recebe `status` e `motivos`. Os estados formam uma partição: `valido`, `duplicata` ou `quarentena`. Uma repetição que também tem problemas fica em `duplicata`, mas mantém todos os motivos. Somente `valido` entra nas séries. A presença de avisos, como marca ou data de coleta ausente, não significa exclusão.

## Decisões de tratamento

1. **Esquema:** exigir as oito colunas. Colunas adicionais vazias são ignoradas; adicionais preenchidas causam erro para evitar perda silenciosa. Linhas inteiramente vazias são ignoradas, mantendo a numeração física da origem.
2. **Datas:** mês de referência é a chave temporal, normalizado para seu primeiro dia. Data de coleta ausente é permitida porque o mês está disponível. Data inválida ou fora do mês vai para quarentena. Nenhuma data de coleta é inventada.
3. **Nomes:** retirar espaços excessivos; padronizar identificador de mercado e reconhecer grafias configuradas. Quatro aliases de carne são propostas explícitas de equivalência. `Farinha`, `Pão` e `Macarrão` permanecem em quarentena por não especificarem o subtipo. Revisar equivalências com a origem antes das conclusões.
4. **Unidades:** atribuir kg, L ou unidade pelo produto conforme configuração. Todas são inicialmente `inferida`, não confirmadas. Ovos são expressos por unidade; leite/óleo por litro. Quantidade é tamanho da embalagem, não consumo mensal da família.
5. **Valores:** exigir preço, quantidade e PPK numéricos, finitos e positivos. Verificar `abs(Preco / Quantidade - PPK) <= 0.011` (tolerância absoluta para arredondamento da fonte). Quando coerentes, o preço unitário é recalculado da razão, sem arredondamento antes da média. Divergência vai para revisão, sem escolher arbitrariamente qual campo estaria correto.
6. **Repetições:** comparar exatamente os oito campos originais. Manter a primeira ocorrência e ligar as demais a `duplicata_de`. Não deduplicar apenas mês/mercado/produto: marcas/coletas distintas são observações diferentes. A exclusão é uma hipótese, não prova de erro de coleta. A configuração permite mantê-las em análise de sensibilidade.
7. **Suspeitas:** limites fixos inclusivos de preço unitário `<= 0.10` e `>= 999`, além das combinações de produto/quantidade listadas na configuração, encaminham registros à quarentena. Foram motivados pela auditoria, não estimados por distribuição futura. São hipóteses conservadoras: não provam erro nem detectam todos os possíveis problemas. Não aplicar winsorização/correção automática.
8. **Marca:** ausência é permitida (especialmente granel); valores numéricos viram texto no campo normalizado e recebem aviso, sem presumir que sejam inválidos.

Resultado da execução inicial: **44.370 linhas válidas, 1.743 repetições excedentes e 151 em quarentena**. A quarentena inclui 137 nomes genéricos, seis suspeitas de preço e oito de quantidade. Existem 184 ocorrências de nomes normalizados. Consulte a saída gerada, pois esses números mudam com regras ou fonte.

## Agregação

Por produto/mercado/mês, calcular média aritmética das observações válidas de preço unitário. Exportar também mediana, mínimo, máximo, número de observações e marcas distintas não ausentes. A média representa a oferta amostrada, não pondera vendas, marcas, preferência do consumidor ou dias do mês. Se houver coletas repetidas de uma marca, ela terá maior peso; o grupo deve avaliar se outra regra atende melhor à questão.

A série geral é a média das médias de cada mercado disponível naquele mês: cada mercado recebe o mesmo peso. Assim, uma loja com dez marcas não pesa dez vezes mais que outra com uma. Ainda pode haver efeito de composição quando mercados entram/saem: isso deve ser discutido e, se necessário, estudado com painel fixo.

Usar mediana/min/máx e contagens para inspeção e sensibilidade. O mínimo entre médias de mercados não equivale ao menor preço individual ofertado. A comparação utiliza mínimos entre médias mensais de mercados, com painel e períodos equivalentes.

## Cobertura e lacunas

Expandir cada par mercado/produto presente na origem válida para identificação (mesmo que suas observações estejam em quarentena) para a janela mensal global. Ausência de preço gera campo vazio, `observado=False` e contagem zero; **o preço nunca vira zero**. Produtos genéricos sem preço elegível também ficam visíveis com cobertura zero.

`cobertura` é meses com ao menos um preço elegível / total de meses da janela global. Não afirma que a loja estivesse ativa em todos os meses. Na execução inicial, 34 de 1.004 pares normalizados possuem os 48 meses completos. A série geral de um produto pode ser completa mesmo sem nenhum mercado individual completo.

Não foi fixado um corte arbitrário de cobertura: a preparação fornece todas as séries; cada análise documenta seus critérios de seleção. Farinha de Trigo e Pão Francês têm lacuna em março/2026 enquanto seus rótulos genéricos aguardam revisão. Não é correto preencher essa lacuna por associação não documentada.

## Prevenção de vazamento temporal

Não há imputação, média móvel, escala aprendida, detecção estatística de outliers ou decomposição nesta etapa. Cada preço mensal usa apenas observações desse mês. Para previsão de t+1, a previsão usa dados disponíveis até t; ajusta os modelos no treino e seleciona hiperparâmetros na validação, mantendo o teste separado.

A matriz de cobertura usa a janela completa e serve ao diagnóstico. Selecionar séries com base em cobertura futura pode introduzir viés de sobrevivência: para avaliar previsão como teria sido feita no passado, decidir elegibilidade apenas com o histórico disponível em cada corte. As próprias regras motivadas pela inspeção integral da base devem ser descritas como limpeza retrospectiva; não alegar avaliação prospectiva completamente cega.

## Como revisar uma decisão

Copiar `config/tratamento.json`, alterar a regra com justificativa e executar com `--config` em uma nova pasta. Para confirmar unidade, adicionar o produto em `unidades_confirmadas` somente após obter evidência. Para resolver nome genérico, acrescentar alias e unidade de destino depois de confirmar subtipo. Para revisar suspeitas, alterar limites/listas explicitamente e comparar o impacto nos resultados.

O código não corrige uma célula pontualmente por suposição. Quando a fonte trouxer correção oficial, preservar o original, salvar uma nova versão e registrar sua proveniência. Quarentena e repetição sempre podem ser reavaliadas a partir da auditoria.

## Limitações para a extensão

Os mercados aparecem como SUP_*, sem endereços ou identificação pública. Não é possível indicar lojas reais sem documentação/autorização apropriada. Não há pesos de consumo, transporte, inflação, promoções identificadas ou volume de vendas. A aplicação social é potencial: onde/quando comprar e quanto reservar dependem das análises e da comunicação das incertezas. Não inventar interação comunitária, horas ou resultados no relatório individual.

## Análises integradas e sensibilidade (25/11/2026)

A comparação foi corrigida para um painel completo em todos os meses; o corte de 24 meses serve apenas às comparações pareadas adicionais. Os cortes 12/24/36 e peso duplo do arroz são cenários de sensibilidade, não parâmetros escolhidos para favorecer resultados.

O módulo sensibilidade.py reaplica o tratamento mantendo duplicatas e exporta séries alternativas/configuração. Também compara séries de mercados disponíveis com painéis completos específicos de cada produto. Os resultados constam em analises/sensibilidade e no relatório coletivo. Isso documenta impacto sem presumir confirmação dos dados.

Não foram recebidos dicionário da coleta, correção oficial dos nomes genéricos ou confirmação de unidades. Permanecem inferidas; as conclusões são condicionais. Não preencher lacunas por associação nominal não demonstrada.
