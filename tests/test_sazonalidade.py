import numpy as np
import pandas as pd
import pytest
from sazonalidade import analisar_produto, selecionar_series


def test_constante_nao_produz_indicio_ou_infinito():
    s = pd.Series(5., index=pd.date_range('2022-01-01',periods=48,freq='MS'))
    a = analisar_produto(s)
    assert a['resumo']['forca_sazonal'] == 0
    assert not a['resumo']['indicio_sazonal']
    assert np.isfinite(a['perfil_pct']).all()


def test_padrao_sazonal_sintetico_e_tendencia():
    idx = pd.date_range('2022-01-01',periods=48,freq='MS')
    t = np.arange(48)
    a = analisar_produto(pd.Series(np.exp(1 + .01*t + .2*np.sin(2*np.pi*t/12)),index=idx))
    assert a['resumo']['indicio_sazonal']
    assert a['resumo']['mes_mais_barato'] == 'Out'
    trend = analisar_produto(pd.Series(np.exp(1+.01*t),index=idx))
    assert not trend['resumo']['indicio_sazonal']


@pytest.mark.parametrize('n,valor',[(12,5),(48,0),(48,-1)])
def test_rejeita_historico_insuficiente_e_precos_invalidos(n,valor):
    with pytest.raises(ValueError):
        analisar_produto(pd.Series(valor,index=pd.date_range('2022-01-01',periods=n,freq='MS')))


def test_selecao_exclui_lacunas_unidade_desconhecida_e_status_textual():
    d = pd.DataFrame({'mes':pd.date_range('2022-01-01',periods=24,freq='MS'),
                      'produto':'Arroz','unidade':'kg','unidade_status':'inferida',
                      'preco_medio':5.,'observado':'True'})
    d.loc[0,'observado']='False'
    series, _ = selecionar_series(d)
    assert not series
    d['observado']='True'; d['unidade']='desconhecida'
    series, _ = selecionar_series(d)
    assert not series
