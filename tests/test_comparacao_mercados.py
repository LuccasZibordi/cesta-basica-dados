import numpy as np
import pandas as pd
import pytest
import comparacao_mercados as cm


def fixture():
    config = {'itens': [{'produto': 'Arroz', 'unidade': 'kg', 'quantidade': 2}],
              'meses_minimos_por_mercado': 2}
    rows = []
    for mercado, valores in {'A': [2, 3, 4], 'B': [2, 5, 6], 'C': [1, 1, np.nan]}.items():
        for mes, preco in zip(pd.date_range('2024-01-01', periods=3, freq='MS'), valores):
            rows.append(dict(mes=mes, mercado=mercado, produto='Arroz', unidade='kg',
                             preco_medio=preco, observado=pd.notna(preco)))
    return pd.DataFrame(rows), config


def test_painel_nao_mistura_periodos_e_pares_usam_intersecao():
    series, config = fixture()
    result = cm.calcular_comparacao(series, config)
    ranking = result['ranking_mercados'].set_index('mercado')
    assert set(ranking.index) == {'A', 'B'}
    assert ranking.loc['A', 'custo_medio'] == 6
    assert ranking.loc['B', 'custo_medio'] == pytest.approx(26/3)
    assert ranking.loc['A', 'vezes_menor_custo'] == 3
    assert ranking.loc['B', 'vezes_menor_custo'] == 1  # empate conta para ambos
    pares = result['comparacoes_pareadas'].set_index(['mercado_a','mercado_b'])
    assert pares.loc[('A','C'), 'meses_comuns'] == 2
    assert pares.loc[('A','C'), 'diferenca_media_a_menos_b'] == 3
    distribuida = result['compra_distribuida_mensal']
    assert distribuida.custo_distribuido.tolist() == [4,6,8]  # C não pertence ao painel
    assert distribuida.economia_melhor_unico.tolist() == [0,0,0]


def test_sem_painel_nao_inventa_ranking_global():
    series, config = fixture()
    series.loc[series.mercado.eq('B') & series.mes.eq('2024-03-01'), ['preco_medio','observado']] = [np.nan,False]
    result = cm.calcular_comparacao(series, config)
    assert result['ranking_mercados'].empty
    assert not result['comparacoes_pareadas'].empty


def test_cesta_incompleta_nao_vira_custo_parcial():
    series, config = fixture()
    config['itens'].append({'produto':'Feijão','unidade':'kg','quantidade':1})
    feijao = series.assign(produto='Feijão',preco_medio=10.,observado=True)
    feijao.loc[feijao.mercado.eq('B') & feijao.mes.eq('2024-02-01'), ['preco_medio','observado']] = [np.nan,False]
    result = cm.calcular_comparacao(pd.concat([series,feijao]), config)
    custos = result['custos_disponiveis'].set_index(['mercado','mes'])
    assert pd.isna(custos.loc[('B',pd.Timestamp('2024-02-01')), 'custo_cesta'])
    assert custos.loc[('A',pd.Timestamp('2024-01-01')), 'custo_cesta'] == 14


def test_rejeita_chaves_duplicadas_e_unidades_misturadas():
    series, config = fixture()
    with pytest.raises(ValueError):
        cm.calcular_comparacao(pd.concat([series,series.iloc[:1]]), config)
    series.loc[0,'unidade'] = 'L'
    with pytest.raises(ValueError):
        cm.calcular_comparacao(series,config)
