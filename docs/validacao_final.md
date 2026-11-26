# Validação final para entrega — 26/11/2026

## Escopo e requisitos

O pacote coletivo contém as três questões do planejamento, cada uma com objetivo/motivação, método/avaliação e conclusão, além de gráficos e tabelas, código-fonte, base original e bases utilizadas. O coletivo identifica Engenharia de Computação, turma 218040, e os quatro integrantes com seus RAs.

O relatório individual de cada integrante é entregue em tarefa separada, conforme orientação do grupo. Nenhum relatório individual, modelo em branco ou backup faz parte do novo ZIP. A revisão não comprova submissão, domínio oral, aprovação de horas ou impacto social já ocorrido.

## Verificações executadas

- Suíte completa: **56 testes passaram em 13,18 s**, após a correção de formatação encontrada nesta revisão.
- Versões das dependências instaladas conferem com `requirements.txt`; ambiente Python 3.12.
- Duas execuções completas com os três módulos, sensibilidades e geração do relatório. Comparação dos 113 artefatos por SHA-256, excluindo o manifesto por conter horários e caminhos diferentes.
- Leitura dos CSVs e JSONs, verificação dos PNGs e SVGs, conferência de links locais nos relatórios e dos hashes de código, configurações e planilha original.
- Dados numéricos, imagens e configurações resultantes continuam iguais aos resultados de 25/11; as mudanças são de apresentação e identificação.
- PDF coletivo exportado com WeasyPrint: **40 páginas**, nove tabelas HTML, sem páginas vazias. Conferência visual do documento e das tabelas corrigidas; nomes e RAs conferidos.
- ZIP final extraído e validado por hashes; contém apenas arquivos selecionados para a entrega e nenhum relatório individual.

Os detalhes computacionais estão em `verificacao_entrega_2026-11-26.json`. O arquivo `MANIFESTO_ARQUIVOS_SHA256.txt`, na raiz do ZIP, registra os hashes dos arquivos incluídos, exceto ele próprio.

## Correções desta revisão

Duas tabelas eram interpretadas como texto corrido porque faltava uma linha em branco antes do cabeçalho Markdown. A correção foi aplicada nos geradores de sazonalidade e sensibilidade, seguida de novos testes e execuções completas. Não houve alteração de algoritmo, parâmetros ou resultados numéricos.

A documentação da entrega foi atualizada para retirar instruções antigas sobre o adiamento dos individuais e direcionar a reprodução para `dados/entrega_2026-11-26`. O README termina com instalação, execução completa/parcial, testes e exportação do relatório.

## Rigor metodológico e limites

- Comparação principal em três mercados nos mesmos 48 meses, com comparações pareadas adicionais em períodos comuns. A cesta reduzida é uma referência de preços, não o consumo mensal de uma família.
- Sazonalidade exploratória com sensibilidade à composição dos mercados; mudanças de classificação discutidas no relatório.
- Previsão com separação cronológica, ajuste de hiperparâmetros na validação e teste separado. Reajuste posterior para o mês seguinte ao fim da base. Naive apresentou o menor erro médio no teste.
- Unidades, equivalências de produtos e critérios de quarentena continuam hipóteses documentadas. Não há confirmação documental integral da coleta, identificação pública das lojas nem medição de economia das famílias.

Os arquivos atendem aos entregáveis técnicos do enunciado fornecido. Cada integrante ainda precisa realizar a submissão correspondente e preparar-se para a arguição.
