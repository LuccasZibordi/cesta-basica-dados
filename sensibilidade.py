"""Sensibilidades retrospectivas: duplicatas, cesta/cobertura e composição."""
from copy import deepcopy
import json
from pathlib import Path
import pandas as pd
from preprocessing import carregar_excel, tratar_dados
from series_temporais import construir_series
from comparacao_mercados import calcular_comparacao, CONFIG_PADRAO


def comparar_series(base: pd.DataFrame, alternativa: pd.DataFrame) -> pd.DataFrame:
    """Diferenças alternativa−base em meses e unidades coincidentes, sem imputação."""
    juntos = base.merge(alternativa,on=['mes','produto','unidade'],suffixes=('_base','_alt'),validate='one_to_one')
    juntos = juntos.dropna(subset=['preco_medio_base','preco_medio_alt'])
    juntos['diferenca'] = juntos.preco_medio_alt-juntos.preco_medio_base
    juntos['abs_pct'] = 100*juntos.diferenca.abs()/juntos.preco_medio_base
    return juntos.groupby(['produto','unidade']).agg(meses_comuns=('mes','nunique'),
                diferenca_media=('diferenca','mean'),diferenca_absoluta_media_pct=('abs_pct','mean')).reset_index()



def comparar_sazonalidade(base: pd.DataFrame, alternativa: pd.DataFrame) -> pd.DataFrame:
    """Confronta conclusões na mesma janela, sem escolher a série mais favorável."""
    from sazonalidade import analisar_produto
    linhas=[]
    for produto,g in alternativa.groupby('produto'):
        origem=base.loc[base.produto.eq(produto)].sort_values('mes')
        g=g.sort_values('mes')
        janela=pd.date_range(base.mes.min(),base.mes.max(),freq='MS')
        if len(g)!=len(janela) or len(origem)!=len(janela) or not g.mes.reset_index(drop=True).equals(origem.mes.reset_index(drop=True)):
            continue
        if g.preco_medio.isna().any() or origem.preco_medio.isna().any() or len(g)<24:
            continue
        a=analisar_produto(origem.set_index('mes').preco_medio)['resumo']
        b=analisar_produto(g.set_index('mes').preco_medio)['resumo']
        linhas.append(dict(produto=produto,indicio_base=a['indicio_sazonal'],indicio_painel_fixo=b['indicio_sazonal'],
                           mudou_indicio=a['indicio_sazonal']!=b['indicio_sazonal'],
                           mes_minimo_base=a['mes_mais_barato'],mes_minimo_painel_fixo=b['mes_mais_barato'],
                           forca_base=a['forca_sazonal'],forca_painel_fixo=b['forca_sazonal'],
                           corr_base=a['corr_media_entre_anos'],corr_painel_fixo=b['corr_media_entre_anos']))
    return pd.DataFrame(linhas,columns=['produto','indicio_base','indicio_painel_fixo','mudou_indicio',
                                      'mes_minimo_base','mes_minimo_painel_fixo','forca_base','forca_painel_fixo','corr_base','corr_painel_fixo'])


def executar(entrada: Path, regras: dict, dados_dir: Path, saida_dir: Path) -> None:
    saida_dir=Path(saida_dir); saida_dir.mkdir(parents=True,exist_ok=True)
    if any(saida_dir.iterdir()):
        raise FileExistsError('Saída não vazia.')
    mercado=pd.read_csv(Path(dados_dir)/'series_mercado.csv',parse_dates=['mes'])
    geral=pd.read_csv(Path(dados_dir)/'series_geral.csv',parse_dates=['mes'])
    alternativa=deepcopy(regras);alternativa['remover_duplicatas']=False
    base=tratar_dados(carregar_excel(entrada,regras['aba']),alternativa)
    m_alt,g_alt,_=construir_series(base)
    # Base e regras alternativas entregues para rastrear cada estatística.
    g_alt.to_csv(saida_dir/'series_geral_com_duplicatas.csv',index=False,date_format='%Y-%m-%d')
    m_alt.to_csv(saida_dir/'series_mercado_com_duplicatas.csv',index=False,date_format='%Y-%m-%d')
    (saida_dir/'tratamento_com_duplicatas.json').write_text(json.dumps(alternativa,ensure_ascii=False,indent=2)+'\n')
    dup=comparar_series(geral,g_alt)
    dup.to_csv(saida_dir/'impacto_duplicatas.csv',index=False)
    contagem=mercado.groupby(['produto','mercado']).observado.agg(['sum','size'])
    pares=contagem.index[contagem['sum'].eq(contagem['size'])]
    fixo=mercado.set_index(['produto','mercado']).loc[pares].reset_index()
    fixo=fixo.groupby(['mes','produto','unidade']).agg(preco_medio=('preco_medio','mean'),n_mercados=('mercado','nunique')).reset_index()
    fixo.to_csv(saida_dir/'series_painel_fixo_por_produto.csv',index=False,date_format='%Y-%m-%d')
    composicao=comparar_series(geral,fixo)
    composicao.to_csv(saida_dir/'impacto_composicao.csv',index=False)
    sazonal=comparar_sazonalidade(geral,fixo)
    sazonal.to_csv(saida_dir/'sensibilidade_sazonalidade.csv',index=False)
    config=json.loads(CONFIG_PADRAO.read_text())
    cenarios=[]
    for nome, dados, corte, multiplicador in [('base',mercado,24,1),('cobertura_12',mercado,12,1),('cobertura_36',mercado,36,1),('arroz_peso_2',mercado,24,2),('com_duplicatas',m_alt,24,1)]:
        cfg=deepcopy(config);cfg['meses_minimos_por_mercado']=corte
        for item in cfg['itens']:
            if item['produto']=='Arroz':item['quantidade']*=multiplicador
        r=calcular_comparacao(dados,cfg)
        pasta=saida_dir/nome;pasta.mkdir()
        (pasta/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
        for chave in ('ranking_mercados','comparacoes_pareadas','cobertura_cesta','compra_distribuida_mensal'):
            r[chave].to_csv(pasta/f'{chave}.csv',index=False,date_format='%Y-%m-%d')
        ranking=r['ranking_mercados'];d=r['compra_distribuida_mensal']
        cenarios.append(dict(cenario=nome,mercados_painel=len(ranking),pares=len(r['comparacoes_pareadas']),
            menor_custo=ranking.iloc[0].mercado if len(ranking) else 'sem painel',
            economia_vs_melhor=d.economia_melhor_unico.mean()))
    pd.DataFrame(cenarios).to_csv(saida_dir/'cenarios_comparacao.csv',index=False)
    linhas=['# Sensibilidade das decisões','',
      'Análises retrospectivas, sem selecionar o cenário que favorece um modelo. Alteramos uma decisão por vez.',
      'Duplicatas: mantemos todas as repetições e reaplicamos as demais regras. As séries alternativas e a configuração estão nesta pasta. A quarentena continua ativa.',
      'Composição: para cada produto, comparamos a média dos mercados disponíveis com a média de lojas observadas em todos os meses. São painéis específicos por produto; itens sem loja completa não têm comparação. Isso mede sensibilidade, não estima o efeito causal de entrada/saída de lojas.',
      '| Produto | Meses pareados | Diferença absoluta média (%) — composição |','| --- | ---: | ---: |']
    linhas += [f'| {x.produto} | {x.meses_comuns} | {x.diferenca_absoluta_media_pct:.3f} |' for x in composicao.itertuples()]
    linhas += ['',f'Duplicatas: maior diferença absoluta média percentual por produto = {dup.diferenca_absoluta_media_pct.max():.3f}%. Veja impacto_duplicatas.csv.',
      '', '| Cenário | Lojas no painel | Pares elegíveis | Menor custo no painel | Economia vs melhor único (R$) |',
      '| --- | ---: | ---: | --- | ---: |']
    linhas += [f"| {x['cenario']} | {x['mercados_painel']} | {x['pares']} | {x['menor_custo']} | {x['economia_vs_melhor']:.3f} |" for x in cenarios]
    linhas += ['', '## A composição altera as conclusões sazonais?',
      '| Produto | Indício na base | Indício no painel fixo | Mínimo na base | Mínimo no painel fixo |',
      '| --- | --- | --- | --- | --- |']
    linhas += [f'| {x.produto} | {x.indicio_base} | {x.indicio_painel_fixo} | {x.mes_minimo_base} | {x.mes_minimo_painel_fixo} |' for x in sazonal.itertuples()]
    mudou=sazonal.loc[sazonal.mudou_indicio,'produto'].tolist()
    linhas += ['', 'Mudança de classificação: '+(', '.join(mudou) or 'nenhuma nas séries comparáveis')+'.',
      'Meses mínimos só sugerem época favorável quando há indício e consistência. Divergências entre as duas séries mostram que a conclusão depende da composição; não escolhemos a versão com sazonalidade mais forte. Produtos sem painel fixo completo não puderam ser confrontados.',
      'A questão 2 deve ser lida junto deste confronto: os padrões não são robustos universalmente ao conjunto de lojas. Não reavaliamos modelos preditivos sobre esses painéis; sua avaliação continua condicionada à série geral original.']
    linhas += ['', 'Os cortes 12/24/36 mudam o suporte das comparações pareadas; o painel principal continua exigindo a janela inteira. Peso 2 para arroz é cenário ilustrativo de preferência, não consumo familiar observado.',
      'Estabilidade nesses cenários não valida unidades inferidas, aliases ou observações em quarentena. Não foi feita busca exaustiva de cestas nem reavaliação prospectiva dos modelos. Mudanças de composição podem afetar sazonalidade e previsão; seus resultados permanecem condicionados à série de mercados disponíveis.']
    (saida_dir/'sensibilidade.md').write_text('\n'.join(linhas)+'\n')
