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


def calcular_comparacao(series: pd.DataFrame, config: dict) -> dict[str, pd.DataFrame]:
    """Painel integral da janela; comparações adicionais exclusivamente pareadas."""
    from itertools import combinations
    itens = pd.DataFrame(config['itens']).set_index('produto')
    if itens.empty or not itens.index.is_unique or not np.isfinite(itens.quantidade).all() or (itens.quantidade <= 0).any():
        raise ValueError('Cesta inválida.')
    janela = pd.date_range(series.mes.min(), series.mes.max(), freq='MS')
    if len(janela) == 0:
        raise ValueError('Janela vazia.')
    serie = series.loc[series.produto.isin(itens.index)].copy()
    if set(itens.index) - set(serie.produto):
        raise ValueError('Produtos da cesta ausentes da série.')
    if serie.duplicated(['mes','mercado','produto']).any():
        raise ValueError('Chave mensal duplicada; resolver unidades/status antes de comparar.')
    if not serie.unidade.eq(serie.produto.map(itens.unidade)).all():
        raise ValueError('Unidades incompatíveis com a cesta.')
    serie['preco_medio'] = pd.to_numeric(serie.preco_medio, errors='coerce')
    valido = serie.observado.astype(str).str.lower().eq('true') & np.isfinite(serie.preco_medio) & serie.preco_medio.gt(0)
    serie.loc[~valido,'preco_medio'] = np.nan
    precos = serie.pivot(index=['mercado','mes'],columns='produto',values='preco_medio').reindex(columns=itens.index)
    grade = pd.MultiIndex.from_product([sorted(serie.mercado.unique()),janela],names=['mercado','mes'])
    precos = precos.reindex(grade)
    custos = precos.mul(itens.quantidade,axis=1).sum(axis=1,min_count=len(itens)).rename('custo_cesta').reset_index()
    cobertura = custos.groupby('mercado').custo_cesta.count().rename('meses_completos').reset_index()
    cobertura['meses_janela'] = len(janela)
    cobertura['painel_integral'] = cobertura.meses_completos.eq(len(janela))
    cobertura['elegivel_pares'] = cobertura.meses_completos.ge(int(config['meses_minimos_por_mercado']))
    cobertura['motivo'] = np.where(cobertura.painel_integral,'painel integral','cesta ausente em parte da janela')
    painel = cobertura.loc[cobertura.painel_integral,'mercado'].tolist()
    # Um mercado isolado não responde à comparação entre supermercados.
    if len(painel) < 2:
        painel = []
    mensal = custos.loc[custos.mercado.isin(painel)].copy()
    mensal['posicao_mensal'] = mensal.groupby('mes').custo_cesta.rank(method='min')
    mensal['n_mercados_mes'] = len(painel)
    ranking_cols = ['mercado','meses_completos','custo_medio','vezes_menor_custo','fracao_meses_menor','fracao_meses_top3']
    ranking = pd.DataFrame(columns=ranking_cols)
    distribuida = pd.DataFrame(columns=['mes','custo_distribuido','melhor_mercado_unico','economia_melhor_unico','economia_melhor_unico_pct'])
    anual = pd.DataFrame(columns=['ano','mercado','meses_completos','custo_medio','posicao_anual'])
    if painel:
        minimos = serie.loc[serie.mercado.isin(painel)].groupby(['mes','produto']).preco_medio.min().unstack().reindex(columns=itens.index)
        distribuida = minimos.mul(itens.quantidade,axis=1).sum(axis=1,min_count=len(itens)).rename('custo_distribuido').reset_index()
        distribuida['melhor_mercado_unico'] = distribuida.mes.map(mensal.groupby('mes').custo_cesta.min())
        distribuida['economia_melhor_unico'] = distribuida.melhor_mercado_unico - distribuida.custo_distribuido
        distribuida['economia_melhor_unico_pct'] = 100*distribuida.economia_melhor_unico/distribuida.melhor_mercado_unico
        mensal = mensal.merge(distribuida[['mes','custo_distribuido']],on='mes',validate='many_to_one')
        mensal['economia_distribuida'] = mensal.custo_cesta-mensal.custo_distribuido
        mensal['economia_distribuida_pct'] = 100*mensal.economia_distribuida/mensal.custo_cesta
        ranking = mensal.groupby('mercado').agg(
            meses_completos=('mes','nunique'), custo_medio=('custo_cesta','mean'),
            custo_mediano=('custo_cesta','median'),desvio_custo=('custo_cesta','std'),
            posicao_media=('posicao_mensal','mean'),desvio_posicao=('posicao_mensal','std'),
            vezes_menor_custo=('posicao_mensal',lambda x:int(x.eq(1).sum())),
            vezes_entre_tres_menores=('posicao_mensal',lambda x:int(x.le(3).sum())),
            economia_media_distribuida=('economia_distribuida','mean'),
            economia_percentual_media=('economia_distribuida_pct','mean')).reset_index()
        ranking['fracao_meses_menor'] = ranking.vezes_menor_custo/ranking.meses_completos
        ranking['fracao_meses_top3'] = ranking.vezes_entre_tres_menores/ranking.meses_completos
        ranking['posicao_media_custo'] = ranking.custo_medio.rank(method='min').astype(int)
        ranking = ranking.sort_values(['custo_medio','mercado']).reset_index(drop=True)
        anual = mensal.assign(ano=mensal.mes.dt.year).groupby(['ano','mercado']).agg(meses_completos=('mes','nunique'),custo_medio=('custo_cesta','mean')).reset_index()
        anual['posicao_anual'] = anual.groupby('ano').custo_medio.rank(method='min').astype(int)
    estabilidade = []
    # Somente anos completos para evitar comparar estações diferentes entre anos.
    completos = anual.loc[anual.meses_completos.eq(12)]
    for a,b in combinations(sorted(completos.ano.unique()),2):
        x = completos.loc[completos.ano.eq(a)].set_index('mercado').custo_medio.rank()
        y = completos.loc[completos.ano.eq(b)].set_index('mercado').custo_medio.rank().reindex(x.index)
        corr = x.corr(y) if len(x)>=3 and x.nunique()>1 and y.nunique()>1 else np.nan
        estabilidade.append(dict(ano_a=a,ano_b=b,mercados_comuns=len(x),spearman_posicao=corr))
    pares = []
    amplo = custos.pivot(index='mes',columns='mercado',values='custo_cesta')
    elegiveis = cobertura.loc[cobertura.elegivel_pares,'mercado']
    for a,b in combinations(sorted(elegiveis),2):
        comum = amplo[[a,b]].dropna()
        if len(comum)<int(config['meses_minimos_por_mercado']):
            continue
        pares.append(dict(mercado_a=a,mercado_b=b,meses_comuns=len(comum),
                          meses=';'.join(comum.index.strftime('%Y-%m')),
                          custo_medio_a=comum[a].mean(),custo_medio_b=comum[b].mean(),
                          diferenca_media_a_menos_b=(comum[a]-comum[b]).mean()))
    return {'custos_disponiveis':custos,'cobertura_cesta':cobertura,
            'custos_mensais_cesta':mensal,'ranking_mercados':ranking,
            'compra_distribuida_mensal':distribuida,'ranking_anual':anual,
            'estabilidade_anual':pd.DataFrame(estabilidade,columns=['ano_a','ano_b','mercados_comuns','spearman_posicao']),
            'comparacoes_pareadas':pd.DataFrame(pares,columns=['mercado_a','mercado_b','meses_comuns','meses','custo_medio_a','custo_medio_b','diferenca_media_a_menos_b']),
            'precos_itens_cesta':serie,'cesta_utilizada':itens.reset_index()}


def executar(dados_dir: Path, saida_dir: Path) -> None:
    saida_dir = Path(saida_dir)
    saida_dir.mkdir(parents=True,exist_ok=True)
    if any(saida_dir.iterdir()):
        raise FileExistsError('Saída não vazia.')
    config = _ler_config(CONFIG_PADRAO)
    series = pd.read_csv(Path(dados_dir)/'series_mercado.csv',parse_dates=['mes'])
    tabelas = calcular_comparacao(series,config)
    for nome,df in tabelas.items():
        df.to_csv(saida_dir/f'{nome}.csv',index=False,date_format='%Y-%m-%d')
    (saida_dir/'config_utilizada.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
    r = tabelas['ranking_mercados']; d = tabelas['compra_distribuida_mensal']
    texto = ['# Questão 1 — Comparação econômica', '', '## Questão',
             'Quais mercados têm menor custo de uma cesta equivalente e qual economia potencial de distribuir as compras?', '',
             '## Objetivo e motivação',
             'Apoiar a comparação de alternativas de compra. A aplicação direta depende de identificar as lojas, conhecer os itens consumidos e descontar transporte.', '',
             '## Método e avaliação', config['descricao'],
             'Os cinco itens básicos não perecíveis ou de compra frequente permitem uma comparação reduzida com cobertura longitudinal; não representam a composição nutricional oficial de uma cesta básica. Quantidades unitárias isolam a comparação de preços sem inventar consumo familiar.',
             'Preço representativo: média mensal das ofertas válidas em cada mercado. O custo é a soma de preço por unidade × quantidade da cesta. Item ausente torna a cesta incompleta, nunca custo zero.',
             'O ranking principal usa somente mercados com cesta completa em TODOS os meses da janela global, selecionados pela cobertura, sem olhar os menores preços. Todas as médias comparam os mesmos meses. É um painel restrito, não uma classificação de todas as lojas.',
             f"A análise complementar compara pares com pelo menos {config['meses_minimos_por_mercado']} meses comuns. A diferença A−B usa somente a interseção exportada em comparacoes_pareadas.csv. Pares com períodos distintos não formam um ranking global. O corte reduz comparações com pouco histórico; a sensibilidade ao corte consta no relatório coletivo.",
             'Empates recebem a mesma posição mínima; cada empatado conta como vencedor do mês. A frequência divide vitórias pelos meses do painel. Top-3 é complementar e pouco informativo se o painel tem apenas três lojas.',
             'Rankings anuais usam o mesmo painel e os mesmos meses dentro de cada ano. A correlação de Spearman entre anos usa apenas anos com 12 meses, evitando comparar estações distintas. Não há inferência causal.',
             'Compra distribuída escolhe o mínimo por item apenas entre lojas do mesmo painel, no mesmo mês. Apresentamos a economia frente a cada loja e frente ao melhor mercado único. São mínimos de médias mensais, não ofertas garantidas disponíveis simultaneamente. Deslocamento não entra no cálculo.', '', '## Resultados']
    if not r.empty:
        melhor = r.iloc[0]
        texto += [f'Painel: {len(r)} mercados, {int(melhor.meses_completos)} meses, {series.mes.min():%m/%Y}–{series.mes.max():%m/%Y}. Menor custo médio neste painel: {melhor.mercado}, R$ {melhor.custo_medio:.2f}.',
                  f'Economia média da distribuição frente ao melhor mercado único: R$ {d.economia_melhor_unico.mean():.2f} ({d.economia_melhor_unico_pct.mean():.2f}%, média dos percentuais mensais).',
                  '', '| Mercado | Meses | Custo médio (R$) | Meses com menor custo |', '| --- | ---: | ---: | ---: |']
        texto += [f'| {x.mercado} | {x.meses_completos} | {x.custo_medio:.2f} | {x.vezes_menor_custo} |' for x in r.itertuples()]
        _salvar_svg_barras(r,'custo_medio','R$ por cesta comparativa',saida_dir/'ranking_custo_medio.svg','Custos no mesmo painel e período')
        _salvar_svg_barras(r,'fracao_meses_menor','Fração de meses (empates incluídos)',saida_dir/'frequencia_menor.svg','Frequência de menor custo',maiores_primeiro=True)
        _salvar_svg_serie(tabelas['custos_mensais_cesta'],saida_dir/'trajetoria_custos.svg')
        texto += ['', '![Custos no painel](ranking_custo_medio.svg)', '![Trajetória](trajetoria_custos.svg)',
                  '', '## Conclusão e discussão',
                  f'{melhor.mercado} tem o menor custo médio entre as lojas do painel, não necessariamente entre todas as lojas da cidade. A redução do painel é o preço da comparação temporal rigorosa; os demais mercados são examinados apenas em pares.',
                  'A economia calculada é bruta: só compensa distribuir compras se superar transporte e outros custos. Não equivale a economia mensal de uma família sem informar sua cesta e frequência de compra.']
    else:
        texto += ['Não há pelo menos duas lojas com cobertura integral. Não foi calculado ranking global nem economia distribuída do painel.', '', '## Conclusão e discussão',
                  'A questão só pode ser respondida nos pares com suporte temporal suficiente. Se não houver pares elegíveis, a base não sustenta a comparação com os critérios atuais.']
    texto += [f"Comparações pareadas elegíveis: {len(tabelas['comparacoes_pareadas'])}; veja meses e diferenças no CSV.",
              'Unidades são inferidas, códigos SUP_* não identificam endereços e preços são nominais. Marcas, cobertura e quantidades afetam as conclusões. Não há custo de transporte, ponderação por vendas ou garantia de disponibilidade.',
              'Cobertura/exclusões: cobertura_cesta.csv; cestas completas e incompletas: custos_disponiveis.csv; parâmetros: config_utilizada.json; estabilidade: ranking_anual.csv e estabilidade_anual.csv.']
    (saida_dir/'questao_1_comparacao.md').write_text('\n'.join(texto)+'\n',encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dados',type=Path,default=RAIZ/'dados/preparados')
    parser.add_argument('--saida',type=Path,default=RAIZ/'dados/analise_comparacao')
    args=parser.parse_args()
    executar(args.dados,args.saida)
