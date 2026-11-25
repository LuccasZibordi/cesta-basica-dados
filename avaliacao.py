"""Métricas de previsão e comparação com a referência Naive — integrante 4."""

import numpy as np
import pandas as pd


def metricas(real, previsto) -> dict:
    """MAE, RMSE e MAPE (%) sobre pares finitos com preço real positivo."""
    real = np.asarray(real, dtype=float)
    previsto = np.asarray(previsto, dtype=float)
    if real.shape != previsto.shape or real.size == 0:
        raise ValueError('Vetores de valores reais e previstos incompatíveis.')
    valido = np.isfinite(real) & np.isfinite(previsto) & (real > 0)
    if not valido.any():
        raise ValueError('Nenhum par real/previsto válido para calcular métricas.')
    erro = previsto[valido] - real[valido]
    return {
        'mae': float(np.mean(np.abs(erro))),
        'rmse': float(np.sqrt(np.mean(erro ** 2))),
        'mape': float(np.mean(np.abs(erro / real[valido])) * 100),
        'n': int(valido.sum()),
    }


def avaliar(previsoes: pd.DataFrame) -> pd.DataFrame:
    """Métricas por produto e modelo, calculadas apenas sobre o conjunto de teste."""
    linhas = []
    for (produto, unidade, modelo), grupo in previsoes.groupby(
            ['produto', 'unidade', 'modelo'], sort=True):
        m = metricas(grupo.preco_real, grupo.preco_previsto)
        linhas.append({'produto': produto, 'unidade': unidade, 'modelo': modelo, **m})
    return pd.DataFrame(linhas).sort_values(['produto', 'modelo']).reset_index(drop=True)


def comparar_com_naive(tabela: pd.DataFrame) -> pd.DataFrame:
    """Acréscimo de acerto em relação ao Naive, em porcentagem do MAPE."""
    comparacao = tabela.copy()
    referencia = comparacao.loc[comparacao.modelo.eq('naive')].set_index('produto').mape
    comparacao['melhora_sobre_naive_pct'] = [
        0.0 if modelo == 'naive' else float((referencia[produto] - mape) / referencia[produto] * 100)
        for produto, modelo, mape in zip(comparacao.produto, comparacao.modelo, comparacao.mape)
    ]
    return comparacao
