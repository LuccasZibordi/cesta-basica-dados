> Registro histórico da etapa/branch original. Para a integração atual, consultar [validação final](validacao_final.md).

# Validação — integrante 1

Verificado em 20/11/2026, Python 3.12.15. Branch `feat/integrante-1-dados`; mudanças locais, sem commit/push.

## Testes

Comando: `.venv/bin/python -m pytest -q` — **30 passaram**. Dependências verificadas com `uv pip check --python .venv/bin/python`: 11 pacotes compatíveis.

Casos cobertos: repetições exatas versus marcas diferentes; opção de manter repetições; datas ausentes/inválidas; valores negativos/não finitos/quantidade zero; divergência PPK; aliases e nomes genéricos; leitura de esquema; marcas textuais `NA` e `001`; preço por litro; lacunas mensais; cobertura zero de produto em quarentena; média com peso igual entre mercados; estabilidade do preço histórico ao acrescentar futuro; exportação sem arredondar PPK original; execução fora da pasta do projeto; preservação do Excel; recusa de sobrescrita; reprodução de saídas e propagação de falhas dos módulos.

Os testes foram executados antes da implementação dos respectivos comportamentos e depois dela. Três regressões adicionais foram reproduzidas e corrigidas durante a revisão: inferência indevida de marcas na leitura, janela de cobertura encurtada por identificador inválido e arredondamento do CSV.

## Execução real e reprodução

O fluxo final foi executado duas vezes em diretórios temporários novos, com a planilha original e a mesma configuração. Os **11 artefatos de dados/diagnóstico tiveram hashes SHA-256 idênticos** entre as execuções. Manifestos possuem horários diferentes, como esperado.

Hash da origem antes/depois, sem alteração:

```text
d92c1a8b2e3273dc90a2f6c07c1620940ec83f114ab7548f9e8aaf45f96fa836
```

Os arquivos publicados em `dados/preparados` correspondem à primeira dessas duas execuções finais. O manifesto contém hashes do código final de preparação, regras e artefatos.

| Resultado | Quantidade |
| --- | ---: |
| Linhas da fonte | 46.264 |
| Válidas para séries sob as regras atuais | 44.370 |
| Repetições exatas excedentes | 1.743 |
| Quarentena | 151 |
| Pares mercado/produto normalizados | 1.004 |
| Pares completos nos 48 meses | 34 |

## Revisão e limites

Revisão independente final: código aprovado, sem achados pendentes; reexecução independente dos 30 testes aprovada. Foram conferidos pesos entre mercados, pares em quarentena, preservação de marcas e erros de integração.

Essa validação comprova comportamento do software e reprodução; **não confirma empiricamente unidades, aliases, suspeitas ou equivalência de cestas**. Essas hipóteses permanecem documentadas e revisáveis. Integração dos módulos reais dos colegas ainda não foi possível porque não existem no projeto; apenas o contrato foi testado com módulos controlados. Não foram calculadas respostas às questões nem gerados relatórios individuais de extensão.
