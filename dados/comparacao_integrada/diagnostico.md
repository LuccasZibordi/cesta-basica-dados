# Diagnóstico da preparação

Origem: 46264 registros; 51 mercados; 48 meses observados.
Período: 2022-09-01 a 2026-08-01.

## Destino das linhas

| Status | Linhas |
| --- | ---: |
| valido | 44370 |
| duplicata | 1743 |
| quarentena | 151 |

## Ocorrências de motivos

Uma linha pode ter vários motivos; avisos não implicam exclusão.

| Motivo | Linhas |
| --- | ---: |
| coleta_ausente | 9818 |
| marca_ausente | 9346 |
| marca_numerica | 324 |
| nome_ambiguo | 137 |
| nome_normalizado | 184 |
| preco_suspeito | 6 |
| quantidade_suspeita | 8 |
| repeticao_exata | 1743 |
| unidade_desconhecida | 137 |

## Cobertura e decisões pendentes

34 de 1004 pares possuem preço válido em todos os meses da janela.

- Unidades inferidas exigem confirmação no dicionário da coleta.
- Quarentena indica revisão pendente, não erro comprovado. Regras não detectam todos os erros.
- Repetições exatas são excluídas por hipótese configurável; todas preservadas na auditoria.
- Média geral usa mercados disponíveis; mudanças de composição podem afetar a série.
- Cobertura usa a janela global e não comprova que a loja esteve ativa durante todo o período.
- Não houve imputação, treinamento de modelos, cálculo de cesta ou conclusão das questões.

Consultar base_quarentena.csv, base_duplicatas.csv, cobertura.csv e regras_aplicadas.json para revisar as decisões.
