"""Compara o custo mensal de uma cesta de referência entre mercados."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parent
CONFIG_PADRAO = RAIZ / 'config/cesta_comparacao.json'


def _ler_config(caminho: Path) -> dict:
    config = json.loads(Path(caminho).read_text(encoding='utf-8'))
    itens = config.get('itens', [])
    if not itens or len({item['produto'] for item in itens}) != len(itens):
        raise ValueError('A cesta precisa ter produtos únicos e ao menos um item.')
    if any(float(item['quantidade']) <= 0 for item in itens):
        raise ValueError('As quantidades da cesta precisam ser positivas.')
    if int(config.get('meses_minimos_por_mercado', 0)) < 1:
        raise ValueError('meses_minimos_por_mercado precisa ser positivo.')
    return config


def _salvar_svg_barras(dados: pd.DataFrame, coluna: str, rotulo: str,
                       caminho: Path, titulo: str, limite: int = 20,
                       maiores_primeiro: bool = False) -> None:
    """Escreve gráfico SVG simples sem exigir dependência gráfica adicional."""
    dados = (dados.nlargest(limite, coluna) if maiores_primeiro else dados.nsmallest(limite, coluna))
    dados = dados.sort_values(coluna, ascending=not maiores_primeiro)
    largura, margem_esquerda, margem_direita = 1000, 190, 90
    linha, topo = 30, 78
    altura = topo + max(len(dados), 1) * linha + 42
    maximo = float(dados[coluna].max()) if not dados.empty else 1.0
    escala = (largura - margem_esquerda - margem_direita) / maximo if maximo else 1
    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="24" y="34" font-size="22" font-family="sans-serif" font-weight="bold">{titulo}</text>',
    ]
    for indice, (_, linha_dados) in enumerate(dados.iterrows()):
        y = topo + indice * linha
        valor = float(linha_dados[coluna])
        mercado = str(linha_dados['mercado'])
        partes.extend([
            f'<text x="{margem_esquerda - 12}" y="{y + 17}" text-anchor="end" font-size="13" font-family="sans-serif">{mercado}</text>',
            f'<rect x="{margem_esquerda}" y="{y}" width="{valor * escala:.2f}" height="20" fill="#2878b5"/>',
            f'<text x="{margem_esquerda + valor * escala + 7:.2f}" y="{y + 16}" font-size="12" font-family="sans-serif">{valor:.2f}</text>',
        ])
    partes.append(f'<text x="{margem_esquerda}" y="{altura - 10}" font-size="12" font-family="sans-serif">{rotulo}</text>')
    partes.append('</svg>')
    caminho.write_text('\n'.join(partes), encoding='utf-8')


def _salvar_svg_serie(mensal: pd.DataFrame, caminho: Path) -> None:
    """Compara a cesta média de mercados individuais com a compra distribuída."""
    comum = mensal[['mes', 'custo_distribuido']].drop_duplicates().sort_values('mes')
    media = mensal.groupby('mes', as_index=False).custo_cesta.mean()
    dados = comum.merge(media, on='mes', how='inner').sort_values('mes')
    w, h, ml, mr, mt, mb = 1100, 520, 82, 30, 65, 65
    valores = dados[['custo_cesta', 'custo_distribuido']].to_numpy(dtype=float)
    ymin, ymax = float(np.nanmin(valores)), float(np.nanmax(valores))
    margem = (ymax - ymin) * 0.12 or max(ymax * 0.05, 1.0)
    ymin, ymax = max(0, ymin - margem), ymax + margem
    xspan, yspan = w - ml - mr, h - mt - mb
    def xy(i: int, valor: float) -> tuple[float, float]:
        x = ml + (xspan * i / max(len(dados) - 1, 1))
        y = mt + yspan * (ymax - valor) / (ymax - ymin)
        return x, y
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<text x="25" y="34" font-size="21" font-family="sans-serif" font-weight="bold">Custo mensal: mercado individual e compra distribuída</text>']
    for frac in (0, .25, .5, .75, 1):
        y = mt + yspan * frac
        val = ymax - (ymax - ymin) * frac
        partes.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{w-mr}" y2="{y:.1f}" stroke="#ddd"/>')
        partes.append(f'<text x="{ml-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" font-family="sans-serif">R$ {val:.0f}</text>')
    for col, cor in [('custo_cesta', '#2878b5'), ('custo_distribuido', '#e07a28')]:
        pontos = [xy(i, float(v)) for i, v in enumerate(dados[col])]
        texto = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pontos)
        partes.append(f'<polyline fill="none" stroke="{cor}" stroke-width="2.5" points="{texto}"/>')
    for pos, indice in enumerate(sorted(set([0, len(dados)//2, len(dados)-1]))):
        if len(dados):
            x, _ = xy(indice, ymin)
            partes.append(f'<text x="{x:.1f}" y="{h-34}" text-anchor="middle" font-size="11" font-family="sans-serif">{dados.iloc[indice].mes:%Y-%m}</text>')
    partes.extend([
        f'<line x1="{ml+10}" y1="{h-10}" x2="{ml+42}" y2="{h-10}" stroke="#2878b5" stroke-width="3"/><text x="{ml+48}" y="{h-6}" font-size="12" font-family="sans-serif">Média entre mercados com cesta completa</text>',
        f'<line x1="{ml+390}" y1="{h-10}" x2="{ml+422}" y2="{h-10}" stroke="#e07a28" stroke-width="3"/><text x="{ml+428}" y="{h-6}" font-size="12" font-family="sans-serif">Compra distribuída (menor preço por produto)</text>',
        '</svg>',
    ])
    caminho.write_text('\n'.join(partes), encoding='utf-8')


def executar(dados_dir: Path, saida_dir: Path) -> None:
    """Gera tabelas, gráficos SVG e uma seção interpretativa da questão 1."""
    dados_dir, saida_dir = Path(dados_dir), Path(saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)
    if any(saida_dir.iterdir()):
        raise FileExistsError(f'A pasta de saída não está vazia: {saida_dir}')
    config = _ler_config(CONFIG_PADRAO)
    itens = pd.DataFrame(config['itens'])
    minimo_meses = int(config['meses_minimos_por_mercado'])
    series = pd.read_csv(dados_dir / 'series_mercado.csv', parse_dates=['mes'])
    exigidas = {'mes', 'mercado', 'produto', 'unidade', 'preco_medio', 'observado'}
    faltando = exigidas - set(series.columns)
    if faltando:
        raise ValueError(f'Colunas ausentes em series_mercado.csv: {sorted(faltando)}')
    itens_cfg = itens.set_index('produto')
    unidade_por_produto = series.drop_duplicates('produto').set_index('produto').unidade
    ausentes = set(itens_cfg.index) - set(unidade_por_produto.index)
    if ausentes:
        raise ValueError(f'Produtos da cesta ausentes da série: {sorted(ausentes)}')
    for produto, item in itens_cfg.iterrows():
        if unidade_por_produto.loc[produto] != item.unidade:
            raise ValueError(f'Unidade configurada para {produto} não corresponde à série.')

    serie = series.loc[series.produto.isin(itens_cfg.index)].copy()
    serie['preco_medio'] = pd.to_numeric(serie.preco_medio, errors='coerce')
    serie = serie.loc[serie.observado.astype(str).str.lower().eq('true') &
                       np.isfinite(serie.preco_medio) & serie.preco_medio.gt(0)]
    serie['quantidade_cesta'] = serie.produto.map(itens_cfg.quantidade.astype(float))
    serie['custo_item'] = serie.preco_medio * serie.quantidade_cesta

    # Custo individual exige preço de todos os itens no mesmo mês e mercado.
    chaves = ['mercado', 'mes']
    mercado = serie.pivot_table(index=chaves, columns='produto', values='preco_medio', aggfunc='first')
    mercado = mercado.reindex(columns=itens_cfg.index)
    mercado['n_itens_com_preco'] = mercado[list(itens_cfg.index)].notna().sum(axis=1)
    mercado['custo_cesta'] = mercado[list(itens_cfg.index)].mul(itens_cfg.quantidade.astype(float), axis='columns').sum(axis=1, min_count=len(itens_cfg))
    mercado = mercado.reset_index()
    meses_completos = mercado.loc[mercado.custo_cesta.notna()].groupby('mercado').mes.nunique()
    elegiveis = meses_completos[meses_completos >= minimo_meses].index
    mercado = mercado.loc[mercado.mercado.isin(elegiveis) & mercado.custo_cesta.notna()].copy()
    if mercado.empty:
        raise ValueError('Nenhum mercado atingiu o mínimo de meses com a cesta completa.')
    mercado = mercado.sort_values(['mes', 'custo_cesta', 'mercado'])
    mercado['posicao_mensal'] = mercado.groupby('mes').custo_cesta.rank(method='min').astype(int)
    mercado['n_mercados_mes'] = mercado.groupby('mes').mercado.transform('nunique')

    # Compra distribuída: em cada mês, escolhe o menor preço disponível de cada produto.
    minimos = serie.groupby(['mes', 'produto'], as_index=False).agg(
        preco_minimo=('preco_medio', 'min'), mercados_disponiveis=('mercado', 'nunique'))
    distribuida = minimos.pivot(index='mes', columns='produto', values='preco_minimo').reindex(columns=itens_cfg.index)
    suporte = minimos.pivot(index='mes', columns='produto', values='mercados_disponiveis').reindex(columns=itens_cfg.index)
    distribuida['custo_distribuido'] = distribuida[list(itens_cfg.index)].mul(itens_cfg.quantidade.astype(float), axis='columns').sum(axis=1, min_count=len(itens_cfg))
    distribuida['min_mercados_por_item'] = suporte.min(axis=1)
    distribuida = distribuida.reset_index()[['mes', 'custo_distribuido', 'min_mercados_por_item']]
    mercado = mercado.merge(distribuida, on='mes', how='left', validate='many_to_one')
    mercado['economia_distribuida'] = mercado.custo_cesta - mercado.custo_distribuido
    mercado['economia_distribuida_pct'] = 100 * mercado.economia_distribuida / mercado.custo_cesta

    ranking = mercado.groupby('mercado').agg(
        meses_completos=('mes', 'nunique'), custo_medio=('custo_cesta', 'mean'),
        custo_mediano=('custo_cesta', 'median'), desvio_custo=('custo_cesta', 'std'),
        posicao_media=('posicao_mensal', 'mean'), desvio_posicao=('posicao_mensal', 'std'),
        vezes_entre_tres_menores=('posicao_mensal', lambda x: int(x.le(3).sum())),
        economia_media_distribuida=('economia_distribuida', 'mean'),
        economia_percentual_media=('economia_distribuida_pct', 'mean'),
    ).reset_index()
    ranking['fracao_meses_top3'] = ranking.vezes_entre_tres_menores / ranking.meses_completos
    ranking = ranking.sort_values(['custo_medio', 'mercado']).reset_index(drop=True)
    ranking.insert(0, 'posicao_media_custo', np.arange(1, len(ranking) + 1))

    # Rank anual só é calculado quando o mercado tem ao menos seis cestas mensais.
    mercado['ano'] = mercado.mes.dt.year
    anual = mercado.groupby(['ano', 'mercado']).agg(
        meses_completos=('mes', 'nunique'), custo_medio=('custo_cesta', 'mean')).reset_index()
    anual = anual.loc[anual.meses_completos.ge(6)].copy()
    anual['posicao_anual'] = anual.groupby('ano').custo_medio.rank(method='min').astype(int)
    correlacoes = []
    anos = sorted(anual.ano.unique())
    custos_anuais = {ano: anual.loc[anual.ano.eq(ano)].set_index('mercado').custo_medio for ano in anos}
    for i, ano_a in enumerate(anos):
        for ano_b in anos[i + 1:]:
            comuns = custos_anuais[ano_a].index.intersection(custos_anuais[ano_b].index)
            pos_a = custos_anuais[ano_a].loc[comuns].rank(method='average')
            pos_b = custos_anuais[ano_b].loc[comuns].rank(method='average')
            correlacoes.append({
                'ano_a': int(ano_a), 'ano_b': int(ano_b), 'mercados_comuns': len(comuns),
                # As séries já são posições ordinais; sua correlação de Pearson
                # equivale à correlação de Spearman dos custos originais.
                'spearman_posicao': (float(np.corrcoef(pos_a, pos_b)[0, 1])
                                      if len(comuns) >= 3 and pos_a.nunique() > 1 and pos_b.nunique() > 1 else np.nan),
            })
    estabilidade = pd.DataFrame(correlacoes, columns=['ano_a', 'ano_b', 'mercados_comuns', 'spearman_posicao'])

    mensal = mercado[['mes', 'mercado', 'custo_cesta', 'posicao_mensal', 'n_mercados_mes',
                      'custo_distribuido', 'economia_distribuida', 'economia_distribuida_pct']].copy()
    mensal.to_csv(saida_dir / 'custos_mensais_cesta.csv', index=False, date_format='%Y-%m-%d')
    distribuida.to_csv(saida_dir / 'compra_distribuida_mensal.csv', index=False, date_format='%Y-%m-%d')
    ranking.to_csv(saida_dir / 'ranking_mercados.csv', index=False)
    anual.to_csv(saida_dir / 'ranking_anual.csv', index=False)
    estabilidade.to_csv(saida_dir / 'estabilidade_anual.csv', index=False)
    serie.to_csv(saida_dir / 'precos_itens_cesta.csv', index=False, date_format='%Y-%m-%d')
    itens.to_csv(saida_dir / 'cesta_utilizada.csv', index=False)
    _salvar_svg_barras(ranking, 'custo_medio', 'Custo médio mensal da cesta (R$)',
                       saida_dir / 'ranking_custo_medio.svg', 'Mercados com menor custo médio')
    _salvar_svg_barras(ranking.sort_values('fracao_meses_top3', ascending=False), 'fracao_meses_top3',
                       'Fração de meses entre as três menores cestas', saida_dir / 'estabilidade_top3.svg',
                       'Frequência entre os três menores custos', maiores_primeiro=True)
    _salvar_svg_serie(mensal, saida_dir / 'trajetoria_custos.svg')

    melhor = ranking.iloc[0]
    economias = mensal.groupby('mes').economia_distribuida.mean()
    economia_media = float(economias.mean())
    percentual_medio = float(mensal.economia_distribuida_pct.mean())
    corr_media = estabilidade.spearman_posicao.mean() if not estabilidade.empty else np.nan
    periodo = f"{serie.mes.min():%m/%Y}–{serie.mes.max():%m/%Y}"
    texto_corr = f'{corr_media:.2f}' if pd.notna(corr_media) else 'indisponível'
    linhas = [
        '# Questão 1 — Comparação de mercados', '',
        '## Questão',
        'Quais mercados apresentam o menor custo para uma cesta padronizada ao longo do tempo, e qual seria a economia potencial ao distribuir as compras?', '',
        '## Objetivo',
        'Comparar o custo mensal da cesta de referência nos mercados com cobertura suficiente e estimar o limite superior de economia de uma compra distribuída.', '',
        '## Cesta e critérios',
        str(config['descricao']),
        f"Critério adotado nesta análise: exigir ao menos {minimo_meses} meses com a cesta completa, metade da janela observada de {serie.mes.nunique()} meses. Isso reduz a influência de mercados com poucos registros e mantém uma amostra temporal ampla. Produtos, quantidades e corte podem ser alterados em `config/cesta_comparacao.json` para análise de sensibilidade.",
        'Quantidades usadas e unidades estão em `cesta_utilizada.csv`. As unidades da base são inferidas e ainda precisam ser confirmadas na fonte. Não se somam kg e L como quantidades físicas: cada preço unitário é multiplicado pela quantidade de referência do respectivo produto, e os custos monetários são somados.', '',
        '## Método e avaliação',
        'O preço representativo é a média mensal já agregada por produto e mercado em `series_mercado.csv`. O custo da cesta de um mercado é calculado apenas nos meses em que todos os itens têm preço observado. Mercados entram no ranking se tiverem o mínimo configurado de meses com cesta completa. O ranking geral ordena o custo médio mensal; a estabilidade é descrita pela posição mensal média, desvio das posições, frequência entre os três menores custos e correlação de Spearman entre rankings anuais, para pares de anos com ao menos seis meses por mercado.',
        'A compra distribuída escolhe, em cada mês, o menor preço observado de cada item, mesmo que isso exija visitar vários mercados. A economia é a diferença entre a cesta completa de um único mercado e essa referência distribuída nos mesmos meses. Ela é um limite superior antes de deslocamento e outros custos. A avaliação pode ser reproduzida nos CSVs de custos mensais e rankings.', '',
        '## Resultados desta execução',
        f"Foram avaliados {len(ranking)} mercados elegíveis no período {periodo}. O menor custo médio observado foi de {melhor.mercado}, com R$ {melhor.custo_medio:.2f} por cesta e {int(melhor.meses_completos)} meses completos. A referência de compra distribuída economizou em média R$ {economia_media:.2f} ({percentual_medio:.1f}%) frente aos custos de mercados individuais, nos pares de mercado-mês comparáveis. A correlação média de Spearman entre rankings anuais foi {texto_corr}; veja os coeficientes e tamanhos amostrais em `estabilidade_anual.csv`.", '',
        '## Conclusão e limitações',
        f"Nesta cesta e nos critérios adotados, {melhor.mercado} apresentou o menor custo médio entre os mercados elegíveis. A economia da compra distribuída representa um teto teórico: a decisão real depende de a economia superar o custo adicional total de deslocamento. Os códigos dos mercados não identificam lojas ou endereços, então não é possível estimar distâncias. A cesta unitária é uma referência de comparação, não uma recomendação de consumo familiar; resultados dependem das quantidades escolhidas, da seleção de produtos, da cobertura e das unidades ainda inferidas.",
        'Os preços são nominais e representam a amostra mensal, sem ponderação por vendas ou tamanho da loja. Meses incompletos ficam fora do custo de uma cesta individual; diferenças de período entre mercados podem influenciar médias e posições. O menor preço por item pode vir de mercados e marcas diferentes e a coleta não inclui transporte, disponibilidade no momento da compra ou promoções. Os resultados não identificam causalidade nem representam necessariamente todos os supermercados.', '',
        '## Arquivos gerados',
        '- `ranking_mercados.csv`: custo médio, posição e comparação com compra distribuída.',
        '- `custos_mensais_cesta.csv` e `compra_distribuida_mensal.csv`: resultados mensais e economias pareadas.',
        '- `ranking_anual.csv` e `estabilidade_anual.csv`: comparação de posições entre anos.',
        '- `ranking_custo_medio.svg`, `estabilidade_top3.svg` e `trajetoria_custos.svg`: gráficos vetoriais.',
        '- `cesta_utilizada.csv` e `precos_itens_cesta.csv`: parâmetros e preços usados.', '',
    ]
    (saida_dir / 'questao_1_comparacao.md').write_text('\n'.join(linhas), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dados', type=Path, default=RAIZ / 'dados/preparados')
    parser.add_argument('--saida', type=Path, default=RAIZ / 'dados/analise_comparacao')
    args = parser.parse_args()
    executar(args.dados, args.saida)
    print(f'Análise de comparação concluída: {args.saida.resolve()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
