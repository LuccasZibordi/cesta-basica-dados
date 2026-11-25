import importlib.util
import pandas as pd
import pytest


def test_diferencas_de_composicao_sao_pareadas_no_mes():
    assert importlib.util.find_spec('sensibilidade') is not None
    from sensibilidade import comparar_series
    a=pd.DataFrame({'mes':['2024-01','2024-02'],'produto':['Arroz']*2,'unidade':['kg']*2,'preco_medio':[10.,20.]})
    b=pd.DataFrame({'mes':['2024-02','2024-03'],'produto':['Arroz']*2,'unidade':['kg']*2,'preco_medio':[25.,100.]})
    r=comparar_series(a,b)
    assert r.iloc[0].meses_comuns==1
    assert r.iloc[0].diferenca_media==5
    assert r.iloc[0].diferenca_absoluta_media_pct==25


def test_sensibilidade_revela_mudanca_de_conclusao_sazonal():
    import numpy as np
    import sensibilidade as modulo
    assert hasattr(modulo,'comparar_sazonalidade')
    base=pd.DataFrame({'mes':pd.date_range('2022-01-01',periods=48,freq='MS'),
                       'produto':'Arroz','unidade':'kg','preco_medio':5.})
    alternativa=base.assign(preco_medio=np.exp(1+.2*np.sin(2*np.pi*np.arange(48)/12)))
    r=modulo.comparar_sazonalidade(base,alternativa)
    assert not r.iloc[0].indicio_base
    assert r.iloc[0].indicio_painel_fixo
    assert r.iloc[0].mudou_indicio
