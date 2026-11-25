import hashlib
import csv
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from test_preprocessing import ROOT, amostra


def excel(tmp_path):
    p = tmp_path / 'origem.xlsx'
    pd.DataFrame([amostra(), amostra(), amostra(Produto='Farinha')]).to_excel(p, sheet_name='ACUMUL_DESAGREG', index=False)
    return p


def test_pipeline_preserva_origem_e_produz_saidas_reproduziveis(tmp_path):
    from main import executar_pipeline
    origem = excel(tmp_path)
    antes = hashlib.sha256(origem.read_bytes()).hexdigest()
    manifestos = [executar_pipeline(origem, tmp_path / nome, ROOT / 'config/tratamento.json') for nome in ['a', 'b']]
    assert hashlib.sha256(origem.read_bytes()).hexdigest() == antes
    assert manifestos[0]['status'] == 'concluido'
    assert manifestos[0]['modulos'] == {}
    for nome, hash_arquivo in manifestos[0]['artefatos_sha256'].items():
        assert manifestos[1]['artefatos_sha256'][nome] == hash_arquivo
    d = json.loads((tmp_path / 'a/diagnostico.json').read_text())
    assert d['registros'] == 3
    assert d['status'] == {'valido': 1, 'duplicata': 1, 'quarentena': 1}
    b = pd.read_csv(tmp_path / 'a/base_tratada.csv')
    assert len(b) == 1
    assert len(pd.read_csv(tmp_path / 'a/base_auditada.csv')) == 3
    assert len(pd.read_csv(tmp_path / 'a/series_mercado.csv')) == 2


def test_modulo_solicitado_ausente_falha_sem_declarar_conclusao(tmp_path, monkeypatch):
    from main import executar_pipeline
    import main as pipeline
    original = pipeline.importlib.import_module
    def importar(nome, *args, **kwargs):
        if nome == 'comparacao_mercados':
            raise ModuleNotFoundError(nome)
        return original(nome, *args, **kwargs)
    monkeypatch.setattr(pipeline.importlib, 'import_module', importar)
    with pytest.raises(ModuleNotFoundError):
        executar_pipeline(excel(tmp_path), tmp_path / 'saida', ROOT / 'config/tratamento.json', ('comparacao_mercados',))
    m = json.loads((tmp_path / 'saida/manifesto.json').read_text())
    assert m['status'] == 'falhou'
    assert m['modulos']['comparacao_mercados']['status'] == 'falhou'


def test_contrato_de_integracao_e_propagacao_de_erros(tmp_path, monkeypatch):
    from main import executar_pipeline
    p = tmp_path / 'comparacao_mercados.py'
    p.write_text('def executar(dados_dir, saida_dir):\n    import pandas as pd\n    b = pd.read_csv(dados_dir / "series_mercado.csv")\n    (saida_dir / "contagem.txt").write_text(str(len(b)))\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop('comparacao_mercados', None)
    try:
        m = executar_pipeline(excel(tmp_path), tmp_path / 'saida', ROOT / 'config/tratamento.json', ('comparacao_mercados',))
        assert (tmp_path / 'saida/analises/comparacao_mercados/contagem.txt').read_text() == '2'
        assert m['modulos']['comparacao_mercados']['status'] == 'concluido'
    finally:
        sys.modules.pop('comparacao_mercados', None)
    (tmp_path / 'previsao.py').write_text('def executar(dados_dir, saida_dir):\n    raise RuntimeError("falha analitica")\n')
    sys.modules.pop('previsao', None)
    try:
        with pytest.raises(RuntimeError, match='falha analitica'):
            executar_pipeline(excel(tmp_path), tmp_path / 'erro', ROOT / 'config/tratamento.json', ('previsao',))
        assert json.loads((tmp_path / 'erro/manifesto.json').read_text())['status'] == 'falhou'
    finally:
        sys.modules.pop('previsao', None)


def test_cli_funciona_fora_da_pasta_do_projeto(tmp_path):
    origem = excel(tmp_path)
    r = subprocess.run([sys.executable, str(ROOT / 'main.py'), '--entrada', str(origem), '--saida', str(tmp_path / 'saida')], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / 'saida/manifesto.json').is_file()


def test_pipeline_recusa_sobrescrever_origem_ou_resultados_existentes(tmp_path):
    from main import executar_pipeline
    origem = excel(tmp_path)
    with pytest.raises(ValueError):
        executar_pipeline(origem, tmp_path, ROOT / 'config/tratamento.json')
    saida = tmp_path / 'saida'
    saida.mkdir()
    (saida / 'anotacao.txt').write_text('preservar')
    with pytest.raises(FileExistsError):
        executar_pipeline(origem, saida, ROOT / 'config/tratamento.json')
    assert (saida / 'anotacao.txt').read_text() == 'preservar'


def test_exportacao_nao_arredonda_ppk_original(tmp_path):
    from main import executar_pipeline
    origem = tmp_path / 'origem.xlsx'
    pd.DataFrame([amostra(Produto='Óleo', Preco=8.99, Quantidade=.9, PPK=9.98888888888889)]).to_excel(origem, sheet_name='ACUMUL_DESAGREG', index=False)
    executar_pipeline(origem, tmp_path / 'saida', ROOT / 'config/tratamento.json')
    with (tmp_path / 'saida/base_auditada.csv').open() as f:
        linha = next(csv.DictReader(f))
    assert float(linha['PPK']) == 9.98888888888889


def test_manifesto_registra_codigo_e_configuracoes_analiticas(tmp_path):
    from main import executar_pipeline,sha256
    m=executar_pipeline(excel(tmp_path),tmp_path/'saida',ROOT/'config/tratamento.json')
    assert m['codigo_sha256']['previsao.py'] == sha256(ROOT/'previsao.py')
    assert m['configuracoes_sha256']['config/cesta_comparacao.json'] == sha256(ROOT/'config/cesta_comparacao.json')
