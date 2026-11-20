import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
COLUNAS = ['Mes_Ano_Data', 'Data_Coleta', 'Estab', 'Produto', 'Marca', 'Preco', 'Quantidade', 'PPK']


def amostra(**alteracoes):
    linha = dict(zip(COLUNAS, [pd.Timestamp('2024-01-01'), pd.NaT, 'SUP_01', 'Arroz', 'A', 25., 5., 5.]))
    linha.update(alteracoes)
    return linha


def tratar(linhas, **opcoes):
    from preprocessing import tratar_dados
    regras = json.loads((ROOT / 'config/tratamento.json').read_text())
    regras.update(opcoes)
    return tratar_dados(pd.DataFrame(linhas), regras)


def test_repeticao_exata_tem_origem_mas_marca_distinta_permanece():
    b = tratar([amostra(), amostra(), amostra(Marca='B')])
    assert b.status.tolist() == ['valido', 'duplicata', 'valido']
    assert b.linha_origem.tolist() == [2, 3, 4]
    assert b.loc[1, 'duplicata_de'] == 2
    assert b.Preco.tolist() == [25., 25., 25.]


def test_opcao_manter_repeticoes_para_analise_de_sensibilidade():
    b = tratar([amostra(), amostra()], remover_duplicatas=False)
    assert b.status.tolist() == ['valido', 'valido']
    assert 'repeticao_exata' in b.loc[1, 'motivos']


@pytest.mark.parametrize('mudanca,motivo', [
    ({'Quantidade': 0}, 'quantidade_invalida'),
    ({'Preco': -1}, 'preco_invalido'),
    ({'Preco': float('inf')}, 'preco_invalido'),
    ({'PPK': 42}, 'ppk_incoerente'),
    ({'Mes_Ano_Data': None}, 'mes_invalido'),
    ({'Data_Coleta': pd.Timestamp('2024-02-01')}, 'coleta_fora_mes'),
    ({'Produto': 'Farinha'}, 'nome_ambiguo'),
    ({'Produto': 'Desconhecido'}, 'unidade_desconhecida'),
    ({'Estab': ' '}, 'mercado_ausente'),
    ({'Preco': .1, 'Quantidade': 1, 'PPK': .1}, 'preco_suspeito'),
    ({'Produto': 'Tomate', 'Quantidade': 20, 'Preco': 8.99, 'PPK': .4495}, 'quantidade_suspeita'),
])
def test_quarentena_preserva_valores_e_explica_motivo(mudanca, motivo):
    b = tratar([amostra(**mudanca)])
    assert b.loc[0, 'status'] == 'quarentena'
    assert motivo in b.loc[0, 'motivos']


def test_unidade_inferida_data_ausente_e_alias_explicitos():
    b = tratar([amostra(Produto=' Carne Coxão Mole ', Quantidade=1, Preco=40, PPK=40)])
    assert b.loc[0, 'produto'] == 'Carne Bovina Coxão Mole'
    assert b.loc[0, 'Produto'] == ' Carne Coxão Mole '
    assert b.loc[0, 'unidade'] == 'kg'
    assert b.loc[0, 'unidade_status'] == 'inferida'
    assert b.loc[0, 'status'] == 'valido'
    assert 'coleta_ausente' in b.loc[0, 'motivos']


def test_preco_unitario_recalculado_na_unidade_da_embalagem():
    b = tratar([amostra(Produto='Óleo', Quantidade=.9, Preco=9, PPK=10)])
    assert b.loc[0, 'preco_unitario'] == 10
    assert b.loc[0, 'unidade'] == 'L'


def test_leitura_preserva_linha_excel_e_rejeita_coluna_extra_preenchida(tmp_path):
    from preprocessing import carregar_excel
    p = tmp_path / 'dados.xlsx'
    pd.DataFrame([amostra(), {c: None for c in COLUNAS}, amostra(Marca='B')]).to_excel(p, sheet_name='ACUMUL_DESAGREG', index=False)
    b = carregar_excel(p)
    assert b.linha_origem.tolist() == [2, 4]
    pd.DataFrame([amostra()]).assign(Inesperada=10).to_excel(p, sheet_name='ACUMUL_DESAGREG', index=False)
    with pytest.raises(ValueError, match='coluna'):
        carregar_excel(p)


def test_esquema_incompleto_e_base_vazia_falham(tmp_path):
    from preprocessing import carregar_excel
    p = tmp_path / 'dados.xlsx'
    pd.DataFrame({'Produto': ['Arroz']}).to_excel(p, sheet_name='ACUMUL_DESAGREG', index=False)
    with pytest.raises(ValueError):
        carregar_excel(p)
    with pytest.raises(ValueError):
        tratar([])


@pytest.mark.parametrize('marcas', [('NA', None), ('001', '1')])
def test_marca_literal_na_nao_vira_ausencia_e_duplicata(tmp_path, marcas):
    from preprocessing import carregar_excel, tratar_dados
    p = tmp_path / 'marcas.xlsx'
    pd.DataFrame([amostra(Marca=m) for m in marcas]).to_excel(p, sheet_name='ACUMUL_DESAGREG', index=False)
    regras = json.loads((ROOT / 'config/tratamento.json').read_text())
    base = tratar_dados(carregar_excel(p), regras)
    assert base.status.tolist() == ['valido', 'valido']
    assert base.loc[0, 'Marca'] == marcas[0]
    if marcas[1] is None:
        assert pd.isna(base.loc[1, 'Marca'])
    else:
        assert base.loc[1, 'Marca'] == marcas[1]
