"""Agregação mensal sem imputação; pesos iguais entre mercados na série geral."""

import pandas as pd


def construir_series(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    origem = base.dropna(subset=['mes', 'mercado', 'produto'])
    if origem.empty:
        raise ValueError('Nenhum registro com mês, mercado e produto para construir séries.')
    datas_origem = base.mes.dropna()
    meses = pd.DataFrame({'mes': pd.date_range(datas_origem.min(), datas_origem.max(), freq='MS')})
    chaves = ['mercado', 'produto', 'unidade', 'unidade_status']
    pares = origem[chaves].drop_duplicates()
    grade = pares.merge(meses, how='cross')
    validos = base.loc[base.status.eq('valido')]
    agregados = validos.groupby(['mes'] + chaves, observed=True).agg(
        preco_medio=('preco_unitario', 'mean'),
        preco_mediano=('preco_unitario', 'median'),
        preco_minimo=('preco_unitario', 'min'),
        preco_maximo=('preco_unitario', 'max'),
        n_observacoes=('preco_unitario', 'size'),
        n_marcas=('marca', 'nunique'),
    ).reset_index()
    mercados = grade.merge(agregados, on=['mes'] + chaves, how='left', validate='one_to_one')
    for coluna in ['n_observacoes', 'n_marcas']:
        mercados[coluna] = mercados[coluna].fillna(0).astype(int)
    mercados['observado'] = mercados.n_observacoes.gt(0)
    mercados = mercados.sort_values(['mes', 'produto', 'mercado']).reset_index(drop=True)

    geral = mercados.groupby(['mes', 'produto', 'unidade', 'unidade_status'], observed=True).agg(
        preco_medio=('preco_medio', 'mean'),
        preco_mediano_mercados=('preco_medio', 'median'),
        preco_minimo_mercados=('preco_medio', 'min'),
        preco_maximo_mercados=('preco_medio', 'max'),
        n_mercados=('observado', 'sum'),
        n_observacoes=('n_observacoes', 'sum'),
    ).reset_index().sort_values(['mes', 'produto']).reset_index(drop=True)
    geral['observado'] = geral.n_mercados.gt(0)

    cobertura = mercados.groupby(chaves, observed=True).agg(
        meses_observados=('observado', 'sum'),
        meses_janela=('mes', 'size'),
        n_observacoes=('n_observacoes', 'sum'),
    ).reset_index()
    cobertura['cobertura'] = cobertura.meses_observados / cobertura.meses_janela
    cobertura['serie_completa'] = cobertura.meses_observados.eq(cobertura.meses_janela)
    extremos = mercados.loc[mercados.observado].groupby(chaves, observed=True).agg(
        primeiro_mes_valido=('mes', 'min'), ultimo_mes_valido=('mes', 'max'),
    ).reset_index()
    cobertura = cobertura.merge(extremos, on=chaves, how='left', validate='one_to_one')
    cobertura = cobertura.sort_values(['produto', 'mercado']).reset_index(drop=True)
    return mercados, geral, cobertura
