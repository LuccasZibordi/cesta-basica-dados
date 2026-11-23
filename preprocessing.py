"""Importação e tratamento rastreável; nenhuma alteração no Excel de origem."""

from pathlib import Path

import numpy as np
import pandas as pd


COLUNAS = ['Mes_Ano_Data', 'Data_Coleta', 'Estab', 'Produto', 'Marca', 'Preco', 'Quantidade', 'PPK']


def carregar_excel(caminho: Path, aba: str = 'ACUMUL_DESAGREG') -> pd.DataFrame:
    base = pd.read_excel(caminho, sheet_name=aba, engine='openpyxl',
                         dtype=object, keep_default_na=False, na_values=[''])
    faltantes = set(COLUNAS) - set(base.columns)
    extras = [c for c in base if c not in COLUNAS and base[c].notna().any()]
    if faltantes or extras:
        raise ValueError(f'Esquema de colunas inválido: faltantes={sorted(faltantes)}, extras={extras}')
    base['linha_origem'] = np.arange(2, len(base) + 2)
    base = base.loc[base[COLUNAS].notna().any(axis=1), COLUNAS + ['linha_origem']].copy()
    if base.empty:
        raise ValueError('Planilha sem registros.')
    return base.reset_index(drop=True)


def _texto(serie: pd.Series) -> pd.Series:
    return serie.astype('string').str.strip().str.replace(r'\s+', ' ', regex=True).replace('', pd.NA)


def tratar_dados(brutos: pd.DataFrame, regras: dict) -> pd.DataFrame:
    if brutos.empty or not set(COLUNAS).issubset(brutos.columns):
        raise ValueError('Base vazia ou esquema incompleto.')
    b = brutos.copy().reset_index(drop=True)
    if 'linha_origem' not in b:
        b['linha_origem'] = np.arange(2, len(b) + 2)
    motivos = pd.Series('', index=b.index, dtype='string')
    bloqueado = pd.Series(False, index=b.index)

    def marcar(mascara: pd.Series, motivo: str, impedir: bool = False) -> None:
        mascara = mascara.fillna(False).astype(bool)
        motivos.loc[mascara] += motivo + ';'
        if impedir:
            bloqueado.loc[mascara] = True

    for original, destino in [('Mes_Ano_Data', 'mes'), ('Data_Coleta', 'data_coleta')]:
        # Números sem tipo de data não são interpretados como nanossegundos de 1970.
        valores = b[original].mask(b[original].map(lambda x: isinstance(x, (int, float))))
        b[destino] = pd.to_datetime(valores, errors='coerce', format='mixed')
    b['mes'] = b['mes'].dt.to_period('M').dt.to_timestamp()
    marcar(b.mes.isna(), 'mes_invalido', True)
    marcar(b.Data_Coleta.isna(), 'coleta_ausente')
    marcar(b.Data_Coleta.notna() & b.data_coleta.isna(), 'coleta_invalida', True)
    marcar(b.data_coleta.notna() & (b.data_coleta.dt.to_period('M') != b.mes.dt.to_period('M')), 'coleta_fora_mes', True)
    b['mercado'] = _texto(b.Estab).str.upper()
    b['marca'] = _texto(b.Marca)
    b['produto'] = _texto(b.Produto)
    canonicos = {p.casefold(): p for p in regras['unidades']}
    aliases = {p.casefold(): v for p, v in regras['aliases'].items()}
    lookup = canonicos | aliases
    b['produto'] = b.produto.map(lambda p: lookup.get(p.casefold(), p) if pd.notna(p) else pd.NA).astype('string')
    marcar(b.mercado.isna(), 'mercado_ausente', True)
    marcar(b.produto.isna(), 'produto_ausente', True)
    marcar(b.marca.isna(), 'marca_ausente')
    marcar(b.Marca.map(lambda x: isinstance(x, (int, float)) and pd.notna(x)), 'marca_numerica')
    marcar(b.produto.ne(_texto(b.Produto)), 'nome_normalizado')
    ambiguos = {p.casefold() for p in regras['nomes_ambiguos']}
    marcar(b.produto.str.casefold().isin(ambiguos), 'nome_ambiguo', True)
    b['unidade'] = b.produto.map(regras['unidades']).astype('string').fillna('desconhecida')
    b['unidade_status'] = 'inferida'
    b.loc[b.produto.isin(regras['unidades_confirmadas']), 'unidade_status'] = 'confirmada'
    b.loc[b.unidade.eq('desconhecida'), 'unidade_status'] = 'pendente'
    marcar(b.unidade.eq('desconhecida'), 'unidade_desconhecida', True)

    for original, destino in [('Preco', 'preco_embalagem'), ('Quantidade', 'quantidade'), ('PPK', 'ppk_informado')]:
        b[destino] = pd.to_numeric(b[original], errors='coerce')
        motivo = {'Preco': 'preco_invalido', 'Quantidade': 'quantidade_invalida', 'PPK': 'ppk_invalido'}[original]
        marcar(~np.isfinite(b[destino]) | b[destino].le(0), motivo, True)
    denominador = b.quantidade.where(np.isfinite(b.quantidade) & b.quantidade.gt(0))
    b['preco_unitario'] = b.preco_embalagem / denominador
    marcar((b.preco_unitario - b.ppk_informado).abs().gt(regras['tolerancia_ppk']), 'ppk_incoerente', True)
    marcar(b.preco_unitario.le(regras['preco_unitario_minimo_suspeito']) | b.preco_unitario.ge(regras['preco_unitario_maximo_suspeito']), 'preco_suspeito', True)
    for produto, quantidades in regras['quantidades_suspeitas'].items():
        marcar(b.produto.eq(produto) & b.quantidade.isin(quantidades), 'quantidade_suspeita', True)

    repetida = b.duplicated(COLUNAS, keep='first')
    primeira = b.groupby(COLUNAS, dropna=False, sort=False)['linha_origem'].transform('first')
    b['duplicata_de'] = primeira.where(repetida).astype('Int64')
    marcar(repetida, 'repeticao_exata')
    b['status'] = np.where(bloqueado, 'quarentena', 'valido')
    if regras['remover_duplicatas']:
        b.loc[repetida, 'status'] = 'duplicata'
    b['motivos'] = motivos.str.rstrip(';')
    return b
