from pathlib import Path
import re
import unicodedata

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf

PERIODO = 12
MIN_CICLOS = 2
LIMIAR_FORCA_SAZONAL = 0.30   # Fs de Wang/Hyndman: 1 - Var(resto)/Var(sazonal+resto)
LIMIAR_CORR_ANOS = 0.30       # correlacao media do perfil mensal entre anos
MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


def _slug(texto: str) -> str:
    ascii_ = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().casefold()
    return re.sub(r'[^a-z0-9]+', '_', ascii_).strip('_')


def selecionar_series(geral: pd.DataFrame) -> tuple[dict[str, pd.Series], pd.DataFrame]:
    """Séries completas (sem lacunas) por produto + tabela de elegibilidade."""
    janela = pd.date_range(geral.mes.min(), geral.mes.max(), freq='MS')
    series, linhas = {}, []
    for produto, g in geral.groupby('produto'):
        if g.mes.duplicated().any():
            raise ValueError('Produto com chave mensal duplicada; resolver unidades/status.')
        observado = g.set_index('mes').observado.astype(str).str.lower().eq('true')
        s = g.set_index('mes').preco_medio.where(observado)
        unidade_valida = g.unidade.nunique() == 1 and g.unidade.notna().all() and not g.unidade.eq('desconhecida').any()
        s = s.where(np.isfinite(s) & s.gt(0))
        s = s.reindex(janela)
        completa = bool(s.notna().all()) and unidade_valida
        linhas.append({
            'produto': produto, 'unidade': g.unidade.iloc[0], 'unidade_status': g.unidade_status.iloc[0],
            'meses_janela': len(janela), 'meses_com_preco': int(s.notna().sum()),
            'serie_completa': completa,
            'ciclos_anuais': round(len(janela) / PERIODO, 2),
            'stl_aplicavel': completa and len(janela) >= MIN_CICLOS * PERIODO,
        })
        if completa:
            series[produto] = s.astype(float)
    return series, pd.DataFrame(linhas)


def descritivas(s: pd.Series) -> dict:
    retorno = np.log(s).diff().dropna()
    return {
        'preco_medio_periodo': s.mean(),
        'cv_preco': s.std() / s.mean(),
        'amplitude_pct': (s.max() / s.min() - 1) * 100,
        'volatilidade_mensal_pct': retorno.std() * 100,   # desvio-padrao do retorno log mensal
        'variacao_total_pct': (s.iloc[-1] / s.iloc[0] - 1) * 100,
    }


def analisar_produto(s: pd.Series) -> dict:
    """STL, ACF e consistência entre anos para uma série completa."""
    if len(s) < MIN_CICLOS * PERIODO or not np.isfinite(s).all() or (s <= 0).any():
        raise ValueError('STL exige ao menos dois ciclos completos com preços finitos positivos.')
    if not s.index.equals(pd.date_range(s.index.min(), periods=len(s), freq='MS')):
        raise ValueError('Série precisa ser mensal e sem lacunas.')
    y = np.log(s)
    res = STL(y, period=PERIODO, robust=True).fit()
    var_r, var_sr, var_tr = res.resid.var(), (res.seasonal + res.resid).var(), (res.trend + res.resid).var()
    forca_sazonal = max(0.0, 1 - var_r / var_sr) if var_sr > 1e-12 else 0.0
    forca_tendencia = max(0.0, 1 - var_r / var_tr) if var_tr > 1e-12 else 0.0

    # ACF da serie sem tendencia (diferenca de log): lag 12 alto => padrao anual.
    dif = y.diff().dropna()
    nlags = min(PERIODO, len(dif) // 2 - 1)
    ac = acf(dif, nlags=nlags, fft=False) if dif.var() > 1e-12 else np.r_[1., np.zeros(nlags)]
    limite = 1.96 / np.sqrt(len(dif))
    acf12 = float(ac[PERIODO]) if nlags >= PERIODO else np.nan

    # Perfil mensal por ano: log(preço) - tendência (sazonal + resíduo).
    desvio = (y - res.trend).to_frame('desvio')
    desvio['ano'], desvio['mes_ano'] = desvio.index.year, desvio.index.month
    tabela_ano = desvio.pivot(index='ano', columns='mes_ano', values='desvio').reindex(columns=range(1, 13))
    corr = tabela_ano.T.corr(min_periods=6).to_numpy()
    correlacoes = corr[np.triu_indices_from(corr, k=1)]
    corr_media = float(np.nanmean(correlacoes)) if np.isfinite(correlacoes).any() else np.nan

    perfil = res.seasonal.groupby(res.seasonal.index.month).mean().reindex(range(1, 13))
    indice_pct = (np.exp(perfil) - 1) * 100
    mes_barato, mes_caro = int(indice_pct.idxmin()), int(indice_pct.idxmax())
    meio_ano_barato = tabela_ano.idxmin(axis=1)  # mês mais barato de cada ano (ano incompleto: parcial)

    indicio = (forca_sazonal >= LIMIAR_FORCA_SAZONAL) and (np.nan_to_num(corr_media, nan=-1) >= LIMIAR_CORR_ANOS)
    return {
        'resultado': res, 'perfil_pct': indice_pct, 'tabela_ano': tabela_ano, 'acf': ac, 'acf_limite': limite,
        'resumo': {
            'forca_sazonal': forca_sazonal, 'forca_tendencia': forca_tendencia,
            'acf_lag12': acf12, 'acf_limite_95': limite,
            'acf_lag12_significativo': bool(abs(acf12) > limite) if not np.isnan(acf12) else False,
            'corr_media_entre_anos': corr_media,
            'mes_mais_barato': MESES[mes_barato - 1] if var_sr > 1e-12 else 'não aplicável', 'mes_mais_caro': MESES[mes_caro - 1] if var_sr > 1e-12 else 'não aplicável',
            'amplitude_sazonal_pp': float(indice_pct.max() - indice_pct.min()),
            'mes_barato_por_ano': ', '.join(f'{a}:{MESES[int(m) - 1]}' for a, m in meio_ano_barato.items() if pd.notna(m)),
            'indicio_sazonal': bool(indicio),
        },
    }


def grafico_stl(produto: str, s: pd.Series, a: dict, destino: Path) -> None:
    res = a['resultado']
    fig, ax = plt.subplots(4, 1, figsize=(9, 9), sharex=True)
    ax[0].plot(s.index, s, marker='o', ms=3, label='Preço médio')
    ax[0].plot(s.index, s.rolling(3).mean(), label='Média móvel 3m (retrospectiva)')
    ax[0].plot(s.index, s.rolling(12, center=True).mean(), label='Média móvel 12m (centrada)')
    ax[0].set_ylabel('R$/unidade'); ax[0].legend(fontsize=8); ax[0].set_title(f'{produto}: decomposição STL (escala log)')
    ax[1].plot(res.trend.index, res.trend); ax[1].set_ylabel('Tendência (log)')
    ax[2].plot(res.seasonal.index, res.seasonal); ax[2].axhline(0, color='gray', lw=.5); ax[2].set_ylabel('Sazonal (log)')
    ax[3].bar(res.resid.index, res.resid, width=20); ax[3].axhline(0, color='gray', lw=.5); ax[3].set_ylabel('Resíduo (log)')
    fig.tight_layout(); fig.savefig(destino, dpi=130); plt.close(fig)


def grafico_acf(produto: str, a: dict, destino: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.5))
    lags = np.arange(len(a['acf']))
    ax.bar(lags, a['acf'], width=.4)
    ax.axhline(a['acf_limite'], color='r', ls='--', lw=.8); ax.axhline(-a['acf_limite'], color='r', ls='--', lw=.8)
    ax.set_xlabel('Defasagem (meses)'); ax.set_ylabel('ACF')
    ax.set_title(f'{produto}: autocorrelação da variação mensal (log); linha = IC 95%')
    fig.tight_layout(); fig.savefig(destino, dpi=130); plt.close(fig)


def grafico_calendario(perfis: pd.DataFrame, destino: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 0.45 * len(perfis) + 2))
    lim = np.nanmax(np.abs(perfis.to_numpy()))
    im = ax.imshow(perfis.to_numpy(), cmap='RdYlGn_r', vmin=-lim, vmax=lim, aspect='auto')
    ax.set_xticks(range(12), MESES); ax.set_yticks(range(len(perfis)), perfis.index)
    for i in range(perfis.shape[0]):
        for j in range(12):
            ax.text(j, i, f'{perfis.iat[i, j]:+.1f}', ha='center', va='center', fontsize=7)
    fig.colorbar(im, label='Desvio sazonal vs. tendência (%)  [verde = mais barato]')
    ax.set_title('Calendário de preços: componente sazonal estimado por mês')
    fig.tight_layout(); fig.savefig(destino, dpi=130); plt.close(fig)


def executar(dados_dir: Path, saida_dir: Path) -> None:
    dados_dir, saida_dir = Path(dados_dir), Path(saida_dir)
    if saida_dir.exists() and any(saida_dir.iterdir()):
        raise FileExistsError('Saída não vazia.')
    graficos = saida_dir / 'graficos'
    graficos.mkdir(parents=True, exist_ok=True)
    geral = pd.read_csv(dados_dir / 'series_geral.csv', parse_dates=['mes'])

    series, elegibilidade = selecionar_series(geral)
    elegibilidade.to_csv(saida_dir / 'elegibilidade.csv', index=False, encoding='utf-8')
    if not series:
        raise ValueError('Nenhum produto com série completa na janela; revisar cobertura.csv.')

    linhas, perfis, tabelas_ano = [], {}, []
    for produto, s in series.items():
        linha = {'produto': produto, **descritivas(s)}
        s.rolling(3).mean().to_frame('mm3').assign(mm12_centrada=s.rolling(12, center=True).mean(), preco=s) \
            .to_csv(saida_dir / f'medias_moveis_{_slug(produto)}.csv', encoding='utf-8', date_format='%Y-%m-%d')
        if len(s) >= MIN_CICLOS * PERIODO:
            a = analisar_produto(s)
            linha.update(a['resumo'])
            perfis[produto] = a['perfil_pct']
            tabelas_ano.append(a['tabela_ano'].assign(produto=produto).reset_index())
            grafico_stl(produto, s, a, graficos / f'stl_{_slug(produto)}.png')
            grafico_acf(produto, a, graficos / f'acf_{_slug(produto)}.png')
        linhas.append(linha)

    resumo = pd.DataFrame(linhas)
    resumo.to_csv(saida_dir / 'resumo_sazonalidade.csv', index=False, encoding='utf-8')
    if perfis:
        perfil_df = pd.DataFrame(perfis).T
        perfil_df.columns = MESES
        perfil_df.to_csv(saida_dir / 'calendario_precos.csv', encoding='utf-8-sig', float_format='%.3f')
        pd.concat(tabelas_ano).to_csv(saida_dir / 'perfil_mensal_por_ano.csv', index=False, encoding='utf-8')
        grafico_calendario(perfil_df, graficos / 'calendario_precos.png')

    linhas_texto = [
        '# Questão 2 — Sazonalidade dos preços', '', '## Questão',
        'Há padrões recorrentes que indiquem épocas potencialmente mais econômicas para adquirir os produtos?', '',
        '## Objetivo e motivação',
        'Apoiar o planejamento de compras, distinguindo tendência de longo prazo e oscilações recorrentes. Um mês historicamente favorável não garante desconto futuro.', '',
        '## Método e avaliação',
        'Selecionamos séries mensais gerais completas com preços positivos e unidade única conhecida (ainda inferida). A média geral atribui peso igual aos mercados disponíveis; a composição pode mudar. Elegibilidade e exclusões estão no CSV.',
        'STL robusta no log do preço, período 12, janela sazonal padrão 7. O log expressa variações proporcionais. Médias móveis 3 meses retrospectiva e 12 centrada são apenas descritivas e não entram em previsão. Volatilidade: desvio-padrão das diferenças mensais do log.',
        'Força sazonal: máximo entre zero e 1 − Var(resíduo)/Var(sazonal+resíduo). ACF sobre diferenças do log reduz tendência; linhas ±1,96/raiz(n) são referências aproximadas de ruído branco, sem correção para múltiplas comparações, não um teste confirmatório.',
        'Comparamos perfis anuais sem tendência por correlação, exigindo ao menos seis meses comuns por par de anos. Anos parciais são identificados nas tabelas. Indício exploratório: força sazonal e correlação média ≥0,30. Esses cortes buscam sinais não triviais, são escolhas operacionais e não níveis de significância; a sensibilidade é apresentada abaixo.', '',
        '## Resultados e avaliação',
        f'{len(resumo)} produtos completos analisados. A classificação e meses extremos descrevem esta amostra, não recomendações universais.',
        '',
        '| Produto | Força sazonal | Correlação entre anos | Indício | Mês de menor componente |',
        '| --- | ---: | ---: | --- | --- |',
    ]
    for x in resumo.itertuples():
        if hasattr(x, 'forca_sazonal'):
            linhas_texto.append(f'| {x.produto} | {x.forca_sazonal:.3f} | {x.corr_media_entre_anos:.3f} | {"sim" if x.indicio_sazonal else "não"} | {x.mes_mais_barato} |')
    if 'forca_sazonal' in resumo:
        linhas_texto.append('')
        for limiar in (0.2, 0.3, 0.5):
            n = int((resumo.forca_sazonal.ge(limiar) & resumo.corr_media_entre_anos.ge(limiar)).sum())
            linhas_texto.append(f'Corte exploratório {limiar:.1f} em ambas as medidas: {n} produtos com indício.')
        indicios = resumo.loc[resumo.indicio_sazonal, 'produto'].tolist()
        linhas_texto += ['', '![Calendário sazonal](graficos/calendario_precos.png)', '',
                         '## Conclusão e discussão',
                         'Indícios pelos critérios principais: ' + (', '.join(indicios) or 'nenhum produto') + '.',
                         'O objetivo de explorar épocas favoráveis foi atendido de forma descritiva. Produtos sem consistência suficiente não sustentam indicação de um mês de compra. ACF, força e comparação entre anos são evidências complementares, não prova causal.',
                         'Há apenas quatro ciclos na base original; o ajuste e a avaliação descritiva usam a mesma amostra. Clima, inflação e entrada/saída de lojas podem alterar os perfis. Não extrapolar para anos futuros sem novas observações.',
                         'Mesmo com indício, antecipar compras depende de conservação, espaço, necessidade e capital disponível; especialmente perecíveis não devem ser estocados só pelo calendário.']
    else:
        linhas_texto += ['', '## Conclusão e discussão', 'Histórico insuficiente para avaliar sazonalidade anual; não é possível indicar meses favoráveis.']
    linhas_texto += ['', 'Os CSVs de médias móveis, perfil por ano e resumo sustentam a análise. Figuras stl_* e acf_* mostram cada produto; as unidades de preço constam em elegibilidade.csv.']
    (saida_dir / 'questao_2_sazonalidade.md').write_text('\n'.join(linhas_texto)+'\n', encoding='utf-8')
