# Contrato de dados e integração — versão 1

## Formato comum

CSV UTF-8, separador vírgula, decimal ponto, datas `YYYY-MM-DD`, ausência como campo vazio. Booleanos são `True`/`False`. Nomes de produtos preservam acentos. Não usar o índice da linha como identidade: use `linha_origem` para a fonte e as chaves explícitas para séries.

```python
from pathlib import Path
import pandas as pd

dados_dir = Path('dados/preparados')
serie = pd.read_csv(dados_dir / 'series_mercado.csv', parse_dates=['mes'])
```

## Observações

`base_auditada.csv` contém todas as linhas não vazias da fonte. `base_tratada.csv`, `base_quarentena.csv` e `base_duplicatas.csv` são partições pelos respectivos status.

| Campos | Semântica |
| --- | --- |
| `Mes_Ano_Data`, `Data_Coleta`, `Estab`, `Produto`, `Marca`, `Preco`, `Quantidade`, `PPK` | Valores da fonte representados em CSV; Excel preservado para fidelidade de célula |
| `linha_origem` | Número físico da linha na aba de origem |
| `mes`, `data_coleta` | Datas normalizadas; coleta pode faltar |
| `mercado`, `produto`, `marca` | Identificação normalizada |
| `preco_embalagem`, `quantidade`, `ppk_informado` | Valores numéricos convertidos |
| `preco_unitario` | Preço da embalagem dividido pela quantidade; só utilizar linhas válidas |
| `unidade`, `unidade_status` | kg/L/unidade/desconhecida; inferida/confirmada/pendente |
| `status` | valido, quarentena ou duplicata |
| `motivos` | Códigos de aviso/revisão separados por ponto e vírgula |
| `duplicata_de` | Linha da primeira ocorrência idêntica; vazio caso contrário |

## Séries

**series_mercado.csv**: chave única `mes + mercado + produto + unidade + unidade_status`.

- `preco_medio`, `preco_mediano`, `preco_minimo`, `preco_maximo`: estatísticas dos preços unitários válidos naquele mês/mercado/produto.
- `n_observacoes`: quantidade de linhas utilizadas; `n_marcas`: marcas conhecidas distintas (não inclui ausentes).
- `observado`: há ao menos uma observação elegível. Quando falso, preços são ausentes, contagens zero.

**series_geral.csv**: chave `mes + produto + unidade + unidade_status`.

- `preco_medio`: média com peso igual das médias dos mercados disponíveis.
- `preco_mediano_mercados`, `preco_minimo_mercados`, `preco_maximo_mercados`: estatísticas dessas médias; não são estatísticas diretas de todas as ofertas individuais.
- `n_mercados`, `n_observacoes`, `observado`: suporte amostral do mês.

Preços estão em reais por unidade indicada. Não misturar kg, L e unidade. Unidades inferidas são pendência metodológica, mesmo em linhas com status válido.

## Cobertura e proveniência

- `cobertura.csv`: por mercado/produto/unidade, meses observados, meses da janela global, fração `cobertura`, `serie_completa`, primeira/última observação elegível e contagem total.
- `cobertura_mensal.csv`: contagem de linhas por mês/status, antes da agregação dos preços; permite ver o efeito do tratamento.
- `diagnostico.json`/`.md`: resumo e limitações.
- `regras_aplicadas.json`: cópia integral da configuração usada.
- `manifesto.json`: estado, horários, hashes e dependências. Tempos e caminhos podem variar entre execuções; hashes dos artefatos devem coincidir no mesmo ambiente/regras.

## Interface dos módulos futuros

Criar `comparacao_mercados.py`, `sazonalidade.py` e `previsao.py` na raiz do projeto. Cada módulo implementa:

```python
from pathlib import Path

def executar(dados_dir: Path, saida_dir: Path) -> None:
    # Ler CSVs documentados de dados_dir.
    # Gerar resultados próprios dentro de saida_dir.
    # Levantar exceção se não puder concluir.
    ...
```

`main.py` cria a pasta de resultados de cada módulo, executa na ordem informada em `--modulos` e registra status. O diretório recebido já existe e está vazio para aquele módulo. Usar somente seus arquivos de saída; não modificar bases/configuração/origem. Não depender de diretório corrente nem executar treinamento no import. Dependências analíticas adicionais devem ser acordadas e acrescentadas a requirements.txt.

Para executar só um módulo após nova preparação: `python main.py --saida dados/analise_1 --modulos comparacao_mercados`. Para trabalhar repetidamente sobre uma versão já preparada, o colega pode importar sua própria função e passar as pastas explicitamente.

Sem `--modulos`, executa apenas preparação. Se um módulo solicitado não existir ou falhar, a execução retorna erro e registra `status: falhou`; os arquivos produzidos antes da falha permanecem para diagnóstico, não representam integração concluída. Não existem placeholders fingindo respostas às três questões.

## Acordos ainda coletivos

Regra de seleção da cesta/consumo, preço representativo para a questão 1, cobertura mínima e painel de mercados, recortes temporais, critérios de avaliação e confirmação dos nomes/unidades. Este contrato é a proposta técnica implementada por Luccas para os colegas revisarem; não representa aprovação que ainda não ocorreu.
