import pandas as pd
import pytest

from test_preprocessing import amostra, tratar


def test_media_geral_da_peso_igual_a_mercados_e_nao_a_marcas():
    from series_temporais import construir_series
    b = tratar([amostra(Preco=10, PPK=2), amostra(Preco=20, PPK=4, Marca='B'),
                amostra(Preco=30, PPK=6, Estab='SUP_02')])
    mercados, geral, cobertura = construir_series(b)
    assert mercados.preco_medio.tolist() == [3., 6.]
    assert geral.loc[0, 'preco_medio'] == 4.5
    assert geral.loc[0, 'n_mercados'] == 2
    assert geral.loc[0, 'n_observacoes'] == 3
    assert cobertura.cobertura.tolist() == [1., 1.]


def test_mes_ausente_e_serie_so_em_quarentena_nao_viram_zero():
    from series_temporais import construir_series
    b = tratar([amostra(), amostra(Mes_Ano_Data=pd.Timestamp('2024-03-01')),
                amostra(Produto='Banana Nanica', Preco=999, Quantidade=1, PPK=999)])
    mercados, geral, cobertura = construir_series(b)
    arroz = mercados.query("produto == 'Arroz'")
    assert arroz.mes.dt.month.tolist() == [1, 2, 3]
    assert arroz.preco_medio.iloc[1] != arroz.preco_medio.iloc[1]  # NaN, não zero
    assert arroz.n_observacoes.tolist() == [1, 0, 1]
    assert cobertura.query("produto == 'Arroz'").cobertura.iloc[0] == pytest.approx(2 / 3)
    assert cobertura.query("produto == 'Banana Nanica'").meses_observados.iloc[0] == 0
    assert geral.query("produto == 'Banana Nanica'").preco_medio.isna().all()


def test_novas_observacoes_nao_alteram_preco_historico():
    from series_temporais import construir_series
    base = tratar([amostra(), amostra(Estab='SUP_02', Preco=30, PPK=6)])
    extra = tratar([amostra(Mes_Ano_Data=pd.Timestamp('2025-01-01'), Preco=100, PPK=20)])
    antes = construir_series(base)[1]
    depois = construir_series(pd.concat([base, extra], ignore_index=True))[1]
    assert antes.loc[0, 'preco_medio'] == depois.loc[0, 'preco_medio'] == 5.5


def test_base_sem_mes_util_falha_explicitamente():
    from series_temporais import construir_series
    with pytest.raises(ValueError):
        construir_series(tratar([amostra(Mes_Ano_Data=None)]))


def test_janela_inclui_mes_com_identificador_invalido_na_origem():
    from series_temporais import construir_series
    base = tratar([amostra(), amostra(Mes_Ano_Data=pd.Timestamp('2024-03-01'), Estab=None)])
    mercado, _, cobertura = construir_series(base)
    assert mercado.mes.dt.month.tolist() == [1, 2, 3]
    assert cobertura.loc[0, 'cobertura'] == pytest.approx(1 / 3)
