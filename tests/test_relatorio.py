import importlib.util
from pathlib import Path


def test_html_embute_figuras_e_preserva_tabelas(tmp_path):
    assert importlib.util.find_spec('relatorio') is not None
    from relatorio import exportar_html
    (tmp_path/'grafico.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    p=tmp_path/'relatorio.md'
    p.write_text('# Exemplo\n\n| Item | Valor |\n| --- | --- |\n| Arroz | 2 |\n\n![Figura](grafico.svg)\n')
    exportar_html(p)
    html=p.with_suffix('.html').read_text()
    assert '<table>' in html
    assert 'data:image/svg+xml;base64,' in html
    assert 'src="grafico.svg"' not in html
