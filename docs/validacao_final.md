# Verificação da adequação — 25/11/2026

Base Git: `610d43f`, branch `feat/integrante-1-dados`. Alterações locais, sem commit/push. Auditoria anterior em `auditoria-2026-11-25.txt`; os resultados históricos foram preservados e identificados como históricos.

## Requisitos e estado

| Requisito | Evidência atual | Estado |
| --- | --- | --- |
| Questão, objetivo/motivação, método/avaliação e conclusão | Três seções completas no relatório coletivo | Atendido tecnicamente |
| Comparação com cestas/períodos equivalentes | Painel de três lojas nos 48 meses; comparações pareadas adicionais com meses exportados | Corrigido |
| Frequência de menor custo, estabilidade e economia | Frequência com empates, anos completos para Spearman, economia frente a cada loja e melhor mercado único | Implementado |
| Sazonalidade, gráficos e discussão | STL, ACF, médias móveis, volatilidade, calendário, consistência anual e seção escrita | Implementado, exploratório |
| Previsão e avaliação cronológica | Naive, linear, RF, grade na validação, teste congelado, MAE/RMSE/MAPE por produto | Implementado |
| Previsão posterior ao teste | Reajuste separado em todo o histórico; coluna treinado_ate | Corrigido |
| Sensibilidade das decisões | Duplicatas, cortes de cobertura, peso do arroz e composição; confronto de conclusões sazonais | Implementado |
| Código, base original e bases usadas | Fonte preservada, scripts, requirements, saídas e manifesto | Disponíveis |
| Relatório coletivo com figuras/tabelas | Markdown e HTML independente gerados pelo pipeline | Disponível, identificação acadêmica a conferir pelo grupo |
| Relatórios individuais no modelo | Modelo recebido e salvo; usuário pediu para não elaborar agora | Adiado explicitamente |
| Horas, atividades e submissões individuais | Dependem de informações verdadeiras e ação dos integrantes | Não confirmados |
| Defesa metodológica na arguição | Roteiro em arguicao.md | Material preparado; domínio oral não verificável pelo código |

O professor exige ao menos uma questão; as três do planejamento foram mantidas. Não há exigência conhecida de dashboard ou base externa.

## Testes e execução

- 56 testes aprovados, incluindo regressões novas que falharam antes das correções: painel temporal, custos incompletos, ausência de painel, unidade misturada, série constante, histórico insuficiente, reajuste sem mudar teste, sensibilidade sazonal, manifesto e HTML com imagens incorporadas.
- Falha antiga de módulo ausente foi corrigida simulando explicitamente a importação ausente, sem supor que um arquivo real não exista.
- Ambiente novo Python 3.12.15 instalado exclusivamente de requirements-dev.txt (que inclui requirements.txt), com verificação de dependências compatíveis. statsmodels e Markdown agora são declarados.
- Comando completo: `python main.py --saida <pasta_nova> --modulos comparacao_mercados sazonalidade previsao`.
- Fonte e hipóteses de tratamento preservadas. Os modelos de teste não foram retreinados em dados futuros; o reajuste para o próximo mês ocorre depois da avaliação congelada.
- Naive perfeito não provoca divisão por zero na melhora relativa; resultado não definido dos outros modelos fica ausente, sem infinito.

## Revisão independente e decisões

A revisão final confirmou o painel e a separação teste/refit; apontou dois problemas materiais, corrigidos com regressões RED→GREEN:

1. O diagnóstico de composição precisava mostrar mudanças nas conclusões sazonais. Foi acrescentado o confronto base/painel fixo, sem selecionar a série mais favorável. Batata e feijão mudam de classificação; leite muda seu mês de mínimo componente entre os cenários.
2. A previsão poderia misturar unidades diferentes antes da elegibilidade. Agora rejeita esse caso antes de agregar produto/mês.

Decisões explícitas: painel integral reduz a amostra a três lojas (custo de comparabilidade); demais lojas permanecem na análise pareada. As unidades e aliases continuam hipóteses sem confirmação documental. Relatórios individuais foram adiados a pedido de Luccas, após fornecer o modelo. Não houve defeito material da revisão deixado sem tratamento.

## Limites da verificação

Testes e reprodução comprovam o comportamento computacional, não a veracidade da coleta, a validade nutricional da cesta, uma economia efetiva familiar ou aprovação acadêmica. O desempenho preditivo continua condicionado à média de mercados disponíveis; não foi reavaliado em todos os painéis alternativos. A sazonalidade foi confrontada com o painel fixo e os resultados não são universalmente estáveis.

Consultar `pendencias_entrega.md`. A versão HTML foi renderizada para inspeção de texto, tabelas e figuras. A cópia do modelo institucional foi conferida por hash; não foi preenchida nem revisada detalhadamente, conforme pedido.

## Evidências finais desta execução

- Suíte no ambiente novo: **56 passed em 21,24 s (execução final, com reprodução em paralelo)**; ambiente local: **56 passed em 13,18 s**.
- Duas execuções completas independentes concluídas: `dados/entrega_2026-11-25` e `/tmp/cesta-reproducao-final-v2-2026-11-25`. **113/113 artefatos com hashes idênticos**, excluindo o próprio manifesto (horários/caminhos variam); 65 CSVs também conferidos à tolerância 1e-10. Evidência em `reproducao_final.json`.
- Leitura de todos os 65 CSVs, verificação de 28 PNGs e 3 SVGs, parsing de JSON, leitura dos documentos e conferência de links locais: sem erro. Hashes de código, configurações e Excel conferem com o manifesto. Evidência em `verificacao_artefatos.json`.
- Relatório PDF: **38 páginas**, gerado do HTML final com WeasyPrint 70.0, sem páginas vazias; texto, tabelas, calendário e seção de sensibilidade inspecionados visualmente. Exportação opcional documentada no README.
- Modelo institucional: cópia idêntica à origem, hash registrado em `modelos/LEIA-ME.md`. Nenhum relatório individual elaborado, por solicitação explícita do usuário.
- A reprodução em `/tmp` é evidência temporária; o pacote conserva os resultados finais e manifestos necessários, não depende dessa pasta.

## Atualização posterior — individual de Luccas (25/11/2026)

Luccas autorizou posteriormente somente seu relatório individual. Documento preenchido em `entrega/relatorio_individual_Luccas_Gomes_Zibordi.docx` e no caminho original de Downloads. A cópia institucional em `docs/modelos` permanece virgem. Total de 40 h adotado conforme orientação do estudante, com rateio e intervalos de datas identificados como estimativas. Faltam conferir datas, quantitativos institucionais e paginação no Word. Não há comprovação de impacto social ou devolutiva já realizada. Os demais individuais continuam pendentes. O ZIP técnico produzido anteriormente não foi regenerado; o individual deve acompanhar o pacote como arquivo separado.
