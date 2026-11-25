"""Previsão de preços no mês seguinte — integrante 4 (questão 3).

Consome series_geral.csv preparada pelo integrante 1. Nenhuma transformação é
ajustada com dados posteriores ao bloco de treino; o teste é o último período.
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from avaliacao import avaliar, comparar_com_naive, metricas


MESES_MINIMOS = 48
N_TREINO = 36
N_VALIDACAO = 6
N_TESTE = 6
LAGS = (1, 2, 3, 12)
JANELAS_MM = (3, 6)
GRID_RF = tuple((n, d, f) for n in (100, 300) for d in (None, 5) for f in (1, 3))
SEED = 0
COLUNAS_SERIE = ['mes', 'produto', 'unidade', 'unidade_status', 'preco_medio', 'observado']
PRIORIDADE_STATUS = {'confirmada': 0, 'inferida': 1, 'pendente': 2}
FEATURES = [f'lag_{k}' for k in LAGS] + [f'mm_{w}' for w in JANELAS_MM] + ['seno_mes', 'cosseno_mes']
MODELOS = ('naive', 'linear', 'rf')
CONJUNTOS = ('treino', 'validacao', 'teste')


def carregar_series(dados_dir: Path) -> pd.DataFrame:
    serie = pd.read_csv(Path(dados_dir) / 'series_geral.csv', parse_dates=['mes'])
    faltantes = set(COLUNAS_SERIE) - set(serie.columns)
    if faltantes:
        raise ValueError(f'Colunas obrigatórias ausentes em series_geral.csv: {sorted(faltantes)}')
    if serie.groupby('produto').unidade.nunique(dropna=False).gt(1).any() or serie.unidade.isna().any():
        raise ValueError('Cada produto deve ter uma única unidade antes da agregação.')
    serie['observado'] = serie.observado.astype(str).str.lower().eq('true')
    # Um produto pode aparecer com mais de um unidade_status no mesmo mês quando a fonte
    # confirma unidades; uma linha por produto/mês evita duplicar a grade temporal.
    serie['prioridade'] = serie.unidade_status.map(PRIORIDADE_STATUS).fillna(3)
    serie = (serie.sort_values(['produto', 'mes', 'prioridade'])
             .groupby(['produto', 'mes'], sort=False, as_index=False)
             .agg(unidade=('unidade', 'first'), unidade_status=('unidade_status', 'first'),
                  preco_medio=('preco_medio', 'mean'), observado=('observado', 'any')))
    return serie


def selecionar_produtos(geral: pd.DataFrame) -> pd.DataFrame:
    """Série mensal completa, sem lacunas e com unidade conhecida."""
    resumo = geral.groupby('produto', sort=True).agg(
        meses=('mes', 'nunique'), observados=('observado', 'sum'),
        unidades=('unidade', lambda s: pd.unique(s.dropna()).tolist()))
    elegiveis = resumo.loc[
        resumo.meses.eq(MESES_MINIMOS)
        & resumo.observados.eq(MESES_MINIMOS)
        & resumo.unidades.map(lambda u: len(u) == 1 and u[0] != 'desconhecida')
    ].index
    selecionada = geral.loc[geral.produto.isin(elegiveis)].sort_values(['produto', 'mes']).reset_index(drop=True)
    if selecionada.empty:
        raise ValueError('Nenhum produto com série completa para previsão.')
    return selecionada


def dividir_serie(serie: pd.DataFrame) -> pd.DataFrame:
    """Marca cada mês como aquecimento, treino, validação ou teste, nessa ordem."""
    s = serie.sort_values('mes').reset_index(drop=True).copy()
    s['conjunto'] = 'aquecimento'
    s.loc[s.index[:N_TREINO], 'conjunto'] = 'treino'
    s.loc[s.index[N_TREINO:N_TREINO + N_VALIDACAO], 'conjunto'] = 'validacao'
    s.loc[s.index[N_TREINO + N_VALIDACAO:N_TREINO + N_VALIDACAO + N_TESTE], 'conjunto'] = 'teste'
    return s


def construir_features(serie: pd.DataFrame) -> pd.DataFrame:
    """Lags, médias móveis e sazonalidade calculados só com preços até t-1."""
    s = serie.sort_values('mes').reset_index(drop=True)
    f = pd.DataFrame({
        'mes': s.mes, 'produto': s.produto, 'unidade': s.unidade,
        'preco_medio': s.preco_medio, 'conjunto': s['conjunto'],
    })
    for k in LAGS:
        f[f'lag_{k}'] = s.preco_medio.shift(k)
    for w in JANELAS_MM:
        f[f'mm_{w}'] = s.preco_medio.shift(1).rolling(w).mean()
    mes = s.mes.dt.month
    f['seno_mes'] = np.sin(2 * np.pi * mes / 12)
    f['cosseno_mes'] = np.cos(2 * np.pi * mes / 12)
    elegiveis = f.conjunto.isin(CONJUNTOS) & f[FEATURES].notna().all(axis=1)
    return f.loc[elegiveis].reset_index(drop=True)


def _matriz(dados: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    return dados[FEATURES].to_numpy(dtype=float), dados.preco_medio.to_numpy(dtype=float)


def _rf(parametros: tuple) -> RandomForestRegressor:
    return RandomForestRegressor(n_estimators=parametros[0], max_depth=parametros[1],
                                 min_samples_leaf=parametros[2], random_state=SEED, n_jobs=1)


def _selecionar_parametros(X: np.ndarray, y: np.ndarray, Xv: np.ndarray, yv: np.ndarray) -> tuple:
    melhor_erro, melhores = np.inf, GRID_RF[0]
    for parametros in GRID_RF:
        candidato = _rf(parametros).fit(X, y)
        erro = metricas(yv, candidato.predict(Xv))['mape']
        if erro < melhor_erro:
            melhor_erro, melhores = erro, parametros
    return melhores


def _proximo_mes(serie: pd.DataFrame) -> pd.DataFrame:
    s = serie.sort_values('mes').reset_index(drop=True)
    futuro = pd.DataFrame({
        'mes': [s.mes.max() + pd.offsets.MonthBegin(1)],
        'produto': [s.produto.iloc[0]], 'unidade': [s.unidade.iloc[0]],
        'preco_medio': [np.nan], 'conjunto': ['teste'],
    })
    completo = pd.concat([s[['mes', 'produto', 'unidade', 'preco_medio', 'conjunto']], futuro], ignore_index=True)
    return construir_features(completo).tail(1).reset_index(drop=True)


def ajustar_e_prever(serie: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, tuple]:
    """Ajusta no treino, escolhe hiperparâmetros na validação e prevê o teste e t+1."""
    features = construir_features(serie)
    treino = features.loc[features.conjunto.eq('treino')]
    validacao = features.loc[features.conjunto.eq('validacao')]
    teste = features.loc[features.conjunto.eq('teste')]

    Xt, yt = _matriz(treino)
    Xv, yv = _matriz(validacao)
    escala_treino = StandardScaler().fit(Xt)
    parametros = _selecionar_parametros(escala_treino.transform(Xt), yt, escala_treino.transform(Xv), yv)

    final = pd.concat([treino, validacao], ignore_index=True)
    Xf, yf = _matriz(final)
    escala = StandardScaler().fit(Xf)
    Xf = escala.transform(Xf)
    linear = LinearRegression().fit(Xf, yf)
    floresta = _rf(parametros).fit(Xf, yf)

    X_teste, real = _matriz(teste)
    X_teste = escala.transform(X_teste)
    previstos = {
        'naive': teste.lag_1.to_numpy(dtype=float),
        'linear': linear.predict(X_teste),
        'rf': floresta.predict(X_teste),
    }
    linhas = []
    for modelo in MODELOS:
        for (mes, produto, unidade), y, yhat in zip(
                zip(teste.mes, teste.produto, teste.unidade), real, previstos[modelo]):
            erro = float(yhat - y)
            linhas.append({
                'produto': produto, 'unidade': unidade, 'mes': mes, 'modelo': modelo,
                'preco_real': float(y), 'preco_previsto': float(yhat),
                'erro': erro, 'erro_absoluto': abs(erro),
                'erro_percentual': abs(erro / y) * 100,
            })

    # A avaliação acima fica congelada. Reajuste operacional com todo o histórico.
    X_total, y_total = _matriz(features)
    escala = StandardScaler().fit(X_total)
    linear = LinearRegression().fit(escala.transform(X_total), y_total)
    floresta = _rf(parametros).fit(escala.transform(X_total), y_total)
    futuro = _proximo_mes(serie)
    X_proximo = escala.transform(futuro[FEATURES].to_numpy(dtype=float))
    estimativas = {
        'naive': float(futuro.lag_1.iloc[0]),
        'linear': float(linear.predict(X_proximo)[0]),
        'rf': float(floresta.predict(X_proximo)[0]),
    }
    proximo = pd.DataFrame([
        {'produto': futuro.produto.iloc[0], 'unidade': futuro.unidade.iloc[0],
         'mes': futuro.mes.iloc[0], 'modelo': modelo, 'preco_previsto': valor,
         'treinado_ate': serie.mes.max()}
        for modelo, valor in estimativas.items()
    ])
    return pd.DataFrame(linhas), proximo, parametros


def _graficos(previsoes: pd.DataFrame, metricas_por_modelo: pd.DataFrame, saida: Path) -> None:
    produtos = sorted(previsoes.produto.unique())
    linhas = int(np.ceil(len(produtos) / 3))
    fig, eixos = plt.subplots(linhas, 3, figsize=(15, 3.5 * linhas), squeeze=False, sharex=True)
    for ax, produto in zip(eixos.ravel(), produtos):
        grupo = previsoes.loc[previsoes.produto.eq(produto)]
        ax.plot(grupo.loc[grupo.modelo.eq('naive'), 'mes'], grupo.loc[grupo.modelo.eq('naive'), 'preco_real'],
                'ko-', label='real', linewidth=1.5)
        for modelo, estilo in [('naive', 'b--'), ('linear', 'g-.'), ('rf', 'r:')]:
            parte = grupo.loc[grupo.modelo.eq(modelo)]
            ax.plot(parte.mes, parte.preco_previsto, estilo, label=modelo, linewidth=1.5)
        ax.set_title(produto, fontsize=9)
        ax.grid(alpha=0.2)
    for ax in eixos.ravel()[len(produtos):]:
        ax.set_visible(False)
    eixos.ravel()[0].legend(fontsize=8)
    fig.autofmt_xdate()
    fig.suptitle('Preço real e previsto — meses de teste')
    fig.tight_layout()
    fig.savefig(saida / 'precos_reais_vs_previstos.png', dpi=120)
    plt.close(fig)

    macro = metricas_por_modelo.groupby('modelo', sort=True).mape.mean().reindex(MODELOS)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(macro.index, macro.values, color=['tab:blue', 'tab:green', 'tab:red'])
    ax.set_ylabel('MAPE médio (%)')
    ax.set_title('Erro relativo médio por modelo')
    ax.grid(axis='y', alpha=0.2)
    fig.tight_layout()
    fig.savefig(saida / 'comparacao_modelos.png', dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    for modelo in MODELOS:
        serie = previsoes.loc[previsoes.modelo.eq(modelo)].groupby('mes').erro_percentual.mean()
        ax.plot(serie.index, serie.values, marker='o', label=modelo)
    ax.set_ylabel('MAPE médio do mês (%)')
    ax.set_title('Erro ao longo do período de teste')
    ax.grid(alpha=0.2)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(saida / 'erros_no_tempo.png', dpi=120)
    plt.close(fig)


def _relatorio(previsoes: pd.DataFrame, metricas_por_modelo: pd.DataFrame,
               proximo: pd.DataFrame) -> str:
    macro = metricas_por_modelo.groupby('modelo', sort=True)[['mae', 'rmse', 'mape']].mean().reindex(MODELOS)
    vitorias = metricas_por_modelo.loc[metricas_por_modelo.groupby('produto').mape.idxmin()].modelo.value_counts()
    melhor_geral = macro.mape.idxmin()
    referencia = macro.loc['naive', 'mape']
    linhas = [
        '# Questão 3 — previsão de preços da cesta básica', '',
        '## Questão e objetivo', '',
        'É possível prever o preço médio dos produtos da cesta básica no mês seguinte usando dados históricos? '
        'O objetivo é avaliar se a previsão ajuda a reservar recursos para a compra do próximo mês.', '',
        '## Método', '',
        f'- Entrada: `series_geral.csv` ({len(previsoes.produto.unique())} produtos com {MESES_MINIMOS}/{MESES_MINIMOS} meses válidos e unidade conhecida). '
        'Produtos com lacunas, poucos meses ou unidade desconhecida foram excluídos sem imputação.',
        f'- Variáveis: lags {", ".join(str(k) for k in LAGS)}, médias móveis {", ".join(str(w) for w in JANELAS_MM)} '
        'calculadas com deslocamento de um mês, seno/cosseno do mês. Toda feature usa apenas preços até t-1.',
        f'- Divisão cronológica: {N_TREINO} meses marcados como treino, dos quais {N_TREINO - max(LAGS)} entram '
        f'no modelo após o aquecimento do lag {max(LAGS)}; {N_VALIDACAO} de validação e {N_TESTE} de teste '
        '(2026-03 a 2026-08). O grid do Random Forest foi escolhido pelo MAPE na validação; os modelos finais '
        'foram reajustados em treino+validação e avaliados uma única vez no teste.',
        '- Modelos: Naive (último preço observado), regressão linear padronizada e Random Forest. '
        'Métricas: MAE, RMSE e MAPE, comparadas com o Naive.', '',
        '## Avaliação', '',
        '| Modelo | MAE médio (R$/unidade) | RMSE médio | MAPE médio (%) | Diferença de MAPE vs Naive (p.p.) |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for modelo in MODELOS:
        m = macro.loc[modelo]
        linhas.append(f'| {modelo} | {m.mae:.4f} | {m.rmse:.4f} | {m.mape:.2f} | {m.mape - referencia:+.2f} |')
    linhas += [
        '',
        f'Modelo de menor MAPE médio: **{melhor_geral}**. '
        f'Vitórias por produto (menor MAPE): {", ".join(f"{k}={v}" for k, v in vitorias.items())}.',
        'MAE e RMSE são agregados apenas para referência: as unidades são kg, L e unidade, então o MAPE é a '
        'medida comparável entre produtos.', '',
        '## Conclusão', '',
        f'No período de teste, o modelo **{melhor_geral}** apresentou o menor erro relativo médio. '
        + ('Ao menos um modelo superou a referência Naive em média.' if melhor_geral != 'naive'
           else 'Nenhum modelo superou a referência Naive em média, o que indica pouco ganho previsível '
                'com as variáveis utilizadas.'),
        'A previsão do próximo mês é um ponto estimado; o erro histórico do modelo é a medida de incerteza '
        'disponível, não um intervalo de confiança.', '',
        '## Previsão para o mês seguinte', '',
        '| Produto | Unidade | Mês | Modelo | Preço previsto |',
        '| --- | --- | --- | --- | ---: |',
    ]
    for _, linha in proximo.iterrows():
        linhas.append(f"| {linha.produto} | {linha.unidade} | {linha.mes:%Y-%m} | {linha.modelo} | {linha.preco_previsto:.4f} |")
    linhas += ['', '## Interpretação por produto', '',
               '| Produto | Menor MAPE no teste | MAPE (%) | MAE (R$/unidade) |',
               '| --- | --- | ---: | ---: |']
    for produto, g in metricas_por_modelo.groupby('produto'):
        melhor = g.loc[g.mape.idxmin()]
        linhas.append(f'| {produto} | {melhor.modelo} | {melhor.mape:.2f} | {melhor.mae:.4f} |')
    linhas += ['', 'O vencedor por produto é uma descrição posterior do teste, não uma seleção validada para implantação. Não selecionar hiperparâmetros por essas vitórias.',
               'Os lags 1–3 capturam persistência recente; lag 12 representa o mesmo mês do ano anterior. Médias 3/6 suavizam ruído; seno/cosseno preservam continuidade do calendário. São escolhas parcimoniosas para apenas 48 meses.',
               'Grid RF: 100/300 árvores, profundidade livre/5, mínimo 1/3 observações por folha. A validação temporal escolhe MAPE; profundidade e tamanho de folha controlam complexidade. Há poucos exemplos para modelos flexíveis.',
               'Teste: previsões sequenciais a um passo com preços reais conhecidos até o mês anterior, sem reajustar pesos dentro do bloco. Não é previsão simultânea de seis meses.',
               'Depois de congelar métricas, modelos operacionais são reajustados em todo o histórico com os mesmos hiperparâmetros. A coluna treinado_ate documenta o corte. O mês seguinte é relativo ao fim da base, não à data em que este relatório é lido.',
               'Aplicação: para uma quantidade explicitada q de um único produto, q × MAE ilustra a magnitude média histórica do erro monetário. Isso não é margem garantida nem intervalo de confiança; combinar erros de produtos exige avaliar a cesta conjunta. Sem consumo familiar informado não estimamos orçamento mensal.',
               '![Comparação dos modelos](comparacao_modelos.png)',
               '![Preços reais e previstos](precos_reais_vs_previstos.png)',
               '![Erros no tempo](erros_no_tempo.png)']
    linhas += [
        '',
        '## Limitações', '',
        '- A janela tem apenas 48 meses (cerca de quatro ciclos anuais) e 12 meses de aquecimento para o lag 12.',
        '- Unidades são inferidas e não confirmadas pela fonte; preços são nominais.',
        '- Selecionar séries completas é viés de sobrevivência: produtos com histórico curto ficam de fora.',
        '- A série geral pondera mercados igualmente; mudanças na composição de lojas afetam o preço médio.',
        '- Hiperparâmetros foram escolhidos retrospectivamente na validação; não houve avaliação prospectiva cega.',
        '- Sem pesos de consumo, inflação ou promoções: a previsão não substitui o orçamento familiar.', '',
    ]
    return '\n'.join(linhas)


def executar(dados_dir: Path, saida_dir: Path) -> None:
    dados_dir, saida_dir = Path(dados_dir), Path(saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)
    if any(saida_dir.iterdir()):
        raise FileExistsError('Saída não vazia.')
    geral = carregar_series(dados_dir)
    selecionadas = selecionar_produtos(geral)

    previsoes, proximos, parametros = [], [], {}
    for produto, serie in selecionadas.groupby('produto', sort=True):
        previsao, proximo, params = ajustar_e_prever(dividir_serie(serie.reset_index(drop=True)))
        previsoes.append(previsao)
        proximos.append(proximo)
        parametros[produto] = {'n_estimators': params[0], 'max_depth': params[1], 'min_samples_leaf': params[2]}

    previsoes = pd.concat(previsoes, ignore_index=True)
    proximo = pd.concat(proximos, ignore_index=True).sort_values(['produto', 'modelo']).reset_index(drop=True)
    metricas_por_modelo = avaliar(previsoes)
    comparacao = comparar_com_naive(metricas_por_modelo)

    previsoes.to_csv(saida_dir / 'previsoes_teste.csv', index=False, date_format='%Y-%m-%d')
    metricas_por_modelo.to_csv(saida_dir / 'metricas.csv', index=False)
    comparacao.to_csv(saida_dir / 'comparacao_modelos.csv', index=False)
    proximo.to_csv(saida_dir / 'previsao_proximo_mes.csv', index=False, date_format='%Y-%m-%d')
    (saida_dir / 'parametros_rf.json').write_text(
        pd.Series(parametros).to_json(force_ascii=False, indent=2) + '\n', encoding='utf-8')
    (saida_dir / 'questao3.md').write_text(
        _relatorio(previsoes, metricas_por_modelo, proximo), encoding='utf-8')
    _graficos(previsoes, metricas_por_modelo, saida_dir)
