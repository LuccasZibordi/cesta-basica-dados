# Roteiro de arguição

1. **Qual problema e aplicação?** Comparar alternativas de compra, investigar sazonalidade e avaliar previsão mensal. Aplicação potencial ao planejamento de compras; não afirmar benefício social medido.
2. **De onde vêm os dados?** Planilha fornecida ao grupo, 48 meses e códigos de mercado. A documentação detalhada da coleta e unidades precisa de confirmação.
3. **Como trataram duplicatas e suspeitas?** Critérios explícitos, original preservado, linha de origem, quarentena e sensibilidade mantendo duplicatas. Igualdade de registros não prova erro de coleta.
4. **Qual é a unidade de preço?** kg, litro ou unidade inferidos conforme produto. PPK não é sempre R$/kg. Multiplicar pelo consumo exige quantidades fundamentadas.
5. **Por que não comparar médias de todas as lojas?** Meses diferentes introduzem efeito de período. O painel principal tem as mesmas lojas em todos os meses; demais comparações são pareadas nos meses comuns.
6. **A cesta representa uma família?** Não. É uma cesta comparativa reduzida e unitária. Mostrar `cesta_utilizada.csv` e explicar escolha e sensibilidade dos pesos.
7. **O que significa economia distribuída?** Diferença para mínimos mensais por item no mesmo painel, comparada também ao melhor mercado único. Não inclui transporte nem garante ofertas simultâneas.
8. **Como reconhecer sazonalidade?** STL em log, força sazonal, ACF da variação mensal e consistência entre anos. Cortes exploratórios e quatro ciclos limitam inferência. Mostrar gráfico com tendência, sazonal e resíduos.
9. **Há vazamento temporal?** Features só até t−1; RF ajustada na validação; teste final separado. Seleção de séries completas e regras de limpeza são retrospectivas e devem ser assumidas como limitação.
10. **Por que essas variáveis/modelos?** Persistência recente, lag anual, suavização por médias móveis e calendário. Naive controla se complexidade traz ganho; RF pode perder com pouco histórico.
11. **Como interpretar MAE/RMSE/MAPE?** MAE na unidade do produto; RMSE penaliza grandes desvios; MAPE relativo com preços positivos. Não somar médias de erros com unidades distintas como se fossem orçamento familiar.
12. **Por que reajustar depois do teste?** A avaliação fica congelada. Para o próximo mês da base, usar todo o histórico disponível mantendo hiperparâmetros previamente escolhidos.
13. **Se Naive ganhar, o projeto falhou?** Não. Responde que os modelos propostos não ofereceram ganho médio naquele teste. Não trocar recorte para conseguir resultado favorável.
14. **Como reproduzir?** Mostrar requirements, comando completo, manifesto, testes e fonte preservada.
15. **O que falta fora do código?** Cada integrante envia seu relatório individual em tarefa separada. Restam a submissão, a preparação para a arguição e, para ampliar a aplicação dos resultados, a confirmação documental das hipóteses da coleta.

Cada integrante deve consultar o relatório coletivo final, suas tabelas e a seção que implementou. A assistente não atesta domínio oral dos alunos.
