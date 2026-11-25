import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from avaliacao import comparar_com_naive, metricas
from previsao import (
    LAGS,
    N_TESTE,
    N_TREINO,
    N_VALIDACAO,
    ajustar_e_prever,
    carregar_series,
    construir_features,
    dividir_serie,
    executar,
    selecionar_produtos,
)


ROOT = Path(__file__).resolve().parents[1]


def serie_sintetica(produto='Arroz', n=48, mes_inicial='2022-09-01', base=5.0, lacunas=()):
    meses = pd.date_range(mes_inicial, periods=n, freq='MS')
    t = np.arange(n)
    preco = base + 0.01 * t + 0.2 * np.sin(t)
    serie = pd.DataFrame({
        'mes': meses, 'produto': produto, 'unidade': 'kg',
        'unidade_status': 'inferida', 'preco_medio': preco, 'observado': True,
    })
    serie.loc[list(lacunas), ['preco_medio', 'observado']] = [np.nan, False]
    return serie


def test_seleciona_apenas_series_completas_e_com_unidade_conhecida():
    geral = pd.concat([
        serie_sintetica(),
        serie_sintetica('Farinha de Trigo', lacunas=[20]),
        serie_sintetica('Farinha').assign(unidade='desconhecida'),
        serie_sintetica('Carne Bovina Acem', n=18, mes_inicial='2025-03-01'),
    ], ignore_index=True)
    selecionadas = selecionar_produtos(geral)
    assert selecionadas.produto.unique().tolist() == ['Arroz']


def test_divisao_cronologica_respeita_treino_validacao_teste():
    serie = dividir_serie(serie_sintetica())
    assert serie.conjunto.iloc[:N_TREINO].eq('treino').all()
    assert serie.conjunto.iloc[N_TREINO:N_TREINO + N_VALIDACAO].eq('validacao').all()
    assert serie.conjunto.iloc[N_TREINO + N_VALIDACAO:].eq('teste').all()
    assert serie.loc[serie.conjunto.eq('treino'), 'mes'].max() == pd.Timestamp('2025-08-01')
    assert serie.loc[serie.conjunto.eq('validacao'), 'mes'].min() == pd.Timestamp('2025-09-01')
    assert serie.loc[serie.conjunto.eq('teste'), 'mes'].min() == pd.Timestamp('2026-03-01')
    assert len(serie.loc[serie.conjunto.eq('teste')]) == N_TESTE


def test_features_nao_mudam_quando_o_futuro_muda():
    serie = dividir_serie(serie_sintetica())
    antes = construir_features(serie)
    alterada = serie.copy()
    alterada.loc[alterada.mes.gt('2024-01-01'), 'preco_medio'] += 100
    depois = construir_features(alterada)
    colunas = [f'lag_{k}' for k in LAGS] + ['mm_3', 'mm_6', 'seno_mes', 'cosseno_mes']
    linha = antes.mes.eq('2024-01-01')
    assert antes.loc[linha, colunas].round(10).equals(depois.loc[linha, colunas].round(10))
    assert antes[colunas].notna().all().all()


def test_metricas_calculadas_a_mao():
    m = metricas([2.0, 4.0], [1.0, 8.0])
    assert m['mae'] == pytest.approx(2.5)
    assert m['rmse'] == pytest.approx(np.sqrt(8.5))
    assert m['mape'] == pytest.approx(75.0)


def test_comparacao_com_naive_em_percentual():
    tabela = pd.DataFrame({
        'produto': ['Arroz', 'Arroz', 'Arroz'],
        'modelo': ['naive', 'linear', 'rf'],
        'mae': [2.0, 1.0, 3.0], 'rmse': [3.0, 2.0, 4.0], 'mape': [10.0, 5.0, 20.0],
    })
    comparacao = comparar_com_naive(tabela)
    assert comparacao.query("modelo == 'linear'").melhora_sobre_naive_pct.iloc[0] == pytest.approx(50.0)
    assert comparacao.query("modelo == 'rf'").melhora_sobre_naive_pct.iloc[0] == pytest.approx(-100.0)
    assert comparacao.query("modelo == 'naive'").melhora_sobre_naive_pct.iloc[0] == 0.0


def test_executar_gera_saidas_e_nao_altera_entradas(tmp_path):
    dados_dir = tmp_path / 'dados'
    dados_dir.mkdir()
    serie = serie_sintetica()
    serie.to_csv(dados_dir / 'series_geral.csv', index=False, date_format='%Y-%m-%d')
    pd.DataFrame({'mercado': ['SUP_01'], 'produto': ['Arroz'], 'serie_completa': [True]}).to_csv(
        dados_dir / 'cobertura.csv', index=False)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dados_dir.iterdir()}

    saida = tmp_path / 'saida'
    executar(dados_dir, saida)

    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in dados_dir.iterdir()} == hashes
    for nome in ['previsoes_teste.csv', 'metricas.csv', 'comparacao_modelos.csv',
                 'previsao_proximo_mes.csv', 'questao3.md']:
        assert (saida / nome).is_file()
    assert len(list(saida.glob('*.png'))) >= 2
    previsoes = pd.read_csv(saida / 'previsoes_teste.csv')
    assert set(previsoes.modelo) == {'naive', 'linear', 'rf'}
    assert len(previsoes) == 3 * N_TESTE
    assert previsoes.groupby('modelo').size().tolist() == [N_TESTE] * 3
    proximo = pd.read_csv(saida / 'previsao_proximo_mes.csv')
    assert proximo.mes.iloc[0] == '2026-09-01'
    assert proximo.produto.iloc[0] == 'Arroz'


def test_modelo_e_deterministico_na_mesma_serie():
    serie = dividir_serie(serie_sintetica())
    primeira, _, params1 = ajustar_e_prever(serie)
    segunda, _, params2 = ajustar_e_prever(serie)
    assert primeira.equals(segunda)
    assert params1 == params2


def test_dois_status_no_mesmo_mes_viram_uma_serie(tmp_path):
    dados_dir = tmp_path / 'dados'
    dados_dir.mkdir()
    base = serie_sintetica()
    confirmada = base.assign(unidade_status='confirmada', preco_medio=base.preco_medio + 2)
    pd.concat([base, confirmada], ignore_index=True).to_csv(
        dados_dir / 'series_geral.csv', index=False, date_format='%Y-%m-%d')
    serie = carregar_series(dados_dir)
    assert len(serie) == 48
    assert serie.unidade_status.eq('confirmada').all()
    assert serie.loc[serie.mes.eq('2022-09-01'), 'preco_medio'].iloc[0] == pytest.approx(
        base.preco_medio.iloc[0] + 1)
    assert selecionar_produtos(serie).produto.unique().tolist() == ['Arroz']


def test_carregar_series_exige_colunas_do_contrato(tmp_path):
    p = tmp_path / 'series_geral.csv'
    pd.DataFrame({'mes': ['2024-01-01']}).to_csv(p, index=False)
    with pytest.raises(ValueError, match='ausentes'):
        carregar_series(tmp_path)


def test_previsao_futura_reajusta_sem_alterar_avaliacao(monkeypatch):
    import previsao as modulo
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    serie = dividir_serie(serie_sintetica())
    f = construir_features(serie)
    train = f.loc[f.conjunto.isin(['treino','validacao'])]
    test = f.loc[f.conjunto.eq('teste')]
    scaler = StandardScaler().fit(train[modulo.FEATURES].to_numpy())
    expected = LinearRegression().fit(scaler.transform(train[modulo.FEATURES].to_numpy()),train.preco_medio).predict(scaler.transform(test[modulo.FEATURES].to_numpy()))
    fits = []
    class LinearRegistrada(LinearRegression):
        def fit(self,X,y,**kwargs):
            fits.append(len(y))
            return super().fit(X,y,**kwargs)
    monkeypatch.setattr(modulo,'LinearRegression',LinearRegistrada)
    previsoes,proximo,_ = modulo.ajustar_e_prever(serie)
    assert np.allclose(previsoes.loc[previsoes.modelo.eq('linear'),'preco_previsto'],expected)
    assert fits == [30,36]
    assert proximo.treinado_ate.eq(pd.Timestamp('2026-08-01')).all()


def test_referencia_perfeita_nao_divide_por_zero():
    tabela=pd.DataFrame({'produto':['Arroz']*3,'modelo':['naive','linear','rf'],
                        'mae':[0.,0.,1.],'rmse':[0.,0.,1.],'mape':[0.,0.,10.]})
    r=comparar_com_naive(tabela).set_index('modelo')
    assert r.loc['naive','melhora_sobre_naive_pct']==0
    assert pd.isna(r.loc['rf','melhora_sobre_naive_pct'])


def test_carregar_series_recusa_mistura_de_unidades(tmp_path):
    base=serie_sintetica().assign(preco_medio=10.)
    outra=base.assign(unidade='L',unidade_status='confirmada',preco_medio=100.)
    pd.concat([base,outra],ignore_index=True).to_csv(tmp_path/'series_geral.csv',index=False)
    with pytest.raises(ValueError,match='unidade'):
        carregar_series(tmp_path)
