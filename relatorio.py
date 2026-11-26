"""Consolida seções geradas e exporta HTML independente para leitura/impressão."""
import base64
import json
import mimetypes
from pathlib import Path
import re
import markdown


def exportar_html(caminho: Path) -> None:
    caminho=Path(caminho)
    texto=caminho.read_text(encoding='utf-8')
    def imagem(match):
        destino=(caminho.parent/match.group(2)).resolve()
        mime=mimetypes.guess_type(destino.name)[0] or 'application/octet-stream'
        encoded=base64.b64encode(destino.read_bytes()).decode('ascii')
        return f'![{match.group(1)}](data:{mime};base64,{encoded})'
    texto=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',imagem,texto)
    corpo=markdown.markdown(texto,extensions=['tables','fenced_code','toc'])
    estilo='''body{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;padding:0 28px;color:#182534;line-height:1.55}h1,h2,h3{line-height:1.2;color:#153d56}h1{margin-top:2em}table{border-collapse:collapse;width:100%;font-size:.9em;margin:20px 0}th,td{border:1px solid #ccd6df;padding:7px;text-align:left}th{background:#eaf1f5}img{max-width:100%;height:auto}code{overflow-wrap:anywhere}pre{white-space:pre-wrap} @media print{body{margin:0;padding:0;font-size:10pt}h1{break-before:page}h1:first-child{break-before:auto}tr,img{break-inside:avoid}a{color:inherit}}'''
    caminho.with_suffix('.html').write_text('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>PI — Cesta básica</title><style>'+estilo+'</style></head><body>'+corpo+'</body></html>',encoding='utf-8')


def gerar(dados_dir: Path) -> None:
    dados_dir=Path(dados_dir)
    destino=dados_dir/'relatorios';destino.mkdir()
    d=json.loads((dados_dir/'diagnostico.json').read_text())
    texto=['# Análise comparativa e preditiva de preços da cesta básica',
      'Relatório coletivo de PI e extensão — 2º semestre de 2026.\n\n**Instituição:** PUC-Campinas · Escola Politécnica  \n**Curso:** Engenharia de Computação  \n**Turma:** 218040  \n**Disciplina:** Sistemas Inteligentes e Aprendizado de Máquina  \n**Professor:** Fernando Soares de Aguiar Neto\n\n| Integrante | RA |\n| --- | --- |\n| Luccas Gomes Zibordi | 24007138 |\n| Bruno Vinicius Selingardi | 24004238 |\n| João Vitor Bombo Guimarães | 24018551 |\n| Vinícius de Moraes Chaves | 24007303 |',
      '## Introdução e aplicação esperada',
      'O estudo explora onde comprar, quando comprar e como interpretar previsões para o mês seguinte. O público potencial são consumidores e famílias interessados em organizar compras. O produto é uma análise acessível com gráficos e tabelas; não se afirma que houve atendimento comunitário ou economia efetivamente obtida.',
      'O professor solicita ao menos uma questão com objetivo/motivação, método/avaliação e conclusão. O grupo desenvolve as três questões previstas no planejamento. Os relatórios individuais seguem exigência institucional separada.',
      '## Fonte, preparação e decisões',
      f"Base fornecida ao grupo: ICB_DADOS_2026.xlsx, aba ACUMUL_DESAGREG; {d['registros']} registros, {d['mercados']} códigos de mercado, {d['meses_distintos_origem']} meses ({d['primeiro_mes']} a {d['ultimo_mes']}). Não há documentação institucional detalhada da coleta disponível nesta entrega.",
      f"Tratamento: {d['status'].get('valido',0)} linhas válidas, {d['status'].get('duplicata',0)} duplicatas e {d['status'].get('quarentena',0)} quarentenas. A planilha original é preservada; base_auditada.csv mantém a linha de origem e motivos.",
      'Mês de referência é a chave temporal; ausência de data exata não elimina preço mensal. Marcas ausentes são admitidas. Duplicatas exatas são removidas por hipótese operacional e preservadas separadamente. Nomes genéricos e valores suspeitos ficam em quarentena, sem correções presumidas.',
      'Preço normalizado é Preco/Quantidade quando coerente com PPK (tolerância absoluta 0,011). Limites inclusivos ≤0,10 ou ≥999 e combinações suspeitas de produto/quantidade são regras fixas motivadas pela auditoria. Não são prova de erro. Aliases de carnes são propostas semânticas explícitas.',
      'Unidades kg/L/unidade foram inferidas; nenhuma foi confirmada documentalmente. Isso limita interpretações monetárias por quantidade. Os cenários e resultados são condicionais a essas hipóteses, não validação da coleta.',
      'Agregação: média das ofertas por produto/mercado/mês; série geral é média dessas médias com pesos iguais por loja. Sem imputação e sem preço zero para ausências. Preços são nominais, sem deflação, pesos de vendas ou consumo familiar. Detalhes das regras estão em regras_aplicadas.json e docs/metodologia.md do código entregue.',
      'A base foi inspecionada retrospectivamente; selecionar cobertura de 48 meses pode excluir produtos que não sobreviveram até o fim. A avaliação não é uma experiência prospectiva cega.']
    fontes=[('comparacao_mercados','questao_1_comparacao.md'),('sazonalidade','questao_2_sazonalidade.md'),('previsao','questao3.md'),('sensibilidade','sensibilidade.md')]
    for modulo,nome in fontes:
        secao=(dados_dir/'analises'/modulo/nome).read_text()
        secao=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',lambda m:f'![{m.group(1)}](../analises/{modulo}/{m.group(2)})',secao)
        texto.append(secao)
    # Figures for trend/seasonality/residuals and ACF are part of the submitted report.
    texto += ['# Apêndice — decomposição e autocorrelação por produto',
              'As figuras abaixo usam a janela da base. Preço observado está em R$ por unidade inferida do produto; componentes STL estão em log. A tabela de elegibilidade identifica a unidade.']
    for f in sorted((dados_dir/'analises/sazonalidade/graficos').glob('stl_*.png')):
        texto += [f'![{f.stem}](../analises/sazonalidade/graficos/{f.name})',
                  f'![ACF {f.stem}](../analises/sazonalidade/graficos/{f.name.replace("stl_","acf_")})']
    texto += ['# Síntese e limites de uso',
      'A comparação responde à questão dentro de um painel pequeno com períodos equivalentes; pares ampliam a exploração sem permitir ranking global. Sazonalidade oferece indícios exploratórios, não garantia de meses baratos. A previsão é julgada contra o último preço observado: resultados negativos continuam informativos para evitar complexidade sem ganho.',
      'Não é possível recomendar lojas reais pelos códigos SUP_* nem estimar economia líquida sem transporte. A cesta de cinco itens é comparativa, não orçamento nutricional ou familiar. Para uso social direto, comunicar essas restrições e conferir preços atuais com os consumidores.',
      '## Reproduzir',
      'Na raiz do código, instalar requirements.txt e executar em pasta vazia:',
      '```bash\npython main.py --saida dados/reproducao --modulos comparacao_mercados sazonalidade previsao\n```',
      'O manifesto registra versões, hashes do código/configurações/origem e artefatos. O relatório deriva da mesma execução das tabelas e gráficos. A validação computacional não substitui validação dos dados ou aprovação acadêmica.',
      '## Referências e fontes',
      '- Enunciado do professor fornecido por Luccas e Planejamento_PI_Cesta_Basica.pdf (quatro páginas), consultados em 25/11/2026. Modelo institucional dos relatórios individuais recebido em 25/11/2026 e preservado em docs/modelos. Cada integrante elabora e submete seu próprio relatório de extensão, acompanhado dos arquivos de suporte.',
      '- ICB_DADOS_2026.xlsx, base fornecida ao grupo, identificação detalhada da instituição/coleta pendente.',
      '- [STL — documentação oficial statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html). Decomposição sazonal por LOESS; opções utilizadas documentadas na questão 2.',
      '- [RandomForestRegressor — documentação oficial scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html). Parâmetros utilizados documentados na questão 3.',
      '- [Validação temporal — documentação oficial scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split). Aqui usamos blocos cronológicos fixos, sem afirmar uso de TimeSeriesSplit.',
      'Documentações consultadas em 25/11/2026.']
    p=destino/'relatorio_coletivo.md';p.write_text('\n\n'.join(texto)+'\n',encoding='utf-8');exportar_html(p)
