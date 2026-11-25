"""Preparação dos dados e integração explícita dos módulos dos integrantes 2–4."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

import pandas as pd

from preprocessing import COLUNAS, carregar_excel, tratar_dados
from series_temporais import construir_series


RAIZ = Path(__file__).resolve().parent
MODULOS = ('comparacao_mercados', 'sazonalidade', 'previsao')


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def salvar_json(caminho: Path, dados: dict) -> None:
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def diagnosticar(base: pd.DataFrame, cobertura: pd.DataFrame) -> dict:
    motivos = Counter(m for lista in base.motivos for m in lista.split(';') if m)
    datas = base.mes.dropna()
    return {
        'registros': len(base),
        'status': {str(k): int(v) for k, v in base.status.value_counts().items()},
        'motivos': dict(sorted(motivos.items())),
        'ausentes_originais': {c: int(base[c].isna().sum()) for c in COLUNAS},
        'primeiro_mes': datas.min().strftime('%Y-%m-%d'),
        'ultimo_mes': datas.max().strftime('%Y-%m-%d'),
        'meses_distintos_origem': int(datas.nunique()),
        'mercados': int(base.mercado.nunique()),
        'rotulos_produtos_originais': int(base.Produto.nunique()),
        'produtos_normalizados': int(base.produto.nunique()),
        'pares_mercado_produto': len(cobertura),
        'pares_completos': int(cobertura.serie_completa.sum()),
        'unidades_confirmadas': sorted(base.loc[base.unidade_status.eq('confirmada'), 'produto'].dropna().unique().tolist()),
        'limitacoes': [
            'Unidades inferidas exigem confirmação no dicionário da coleta.',
            'Quarentena indica revisão pendente, não erro comprovado. Regras não detectam todos os erros.',
            'Repetições exatas são excluídas por hipótese configurável; todas preservadas na auditoria.',
            'Média geral usa mercados disponíveis; mudanças de composição podem afetar a série.',
            'Cobertura usa a janela global e não comprova que a loja esteve ativa durante todo o período.',
            'Esta etapa prepara dados sem imputação; resultados dos módulos solicitados estão em analises/.',
        ],
    }


def relatorio_diagnostico(d: dict) -> str:
    linhas = [
        '# Diagnóstico da preparação', '',
        f"Origem: {d['registros']} registros; {d['mercados']} mercados; {d['meses_distintos_origem']} meses observados.",
        f"Período: {d['primeiro_mes']} a {d['ultimo_mes']}.", '',
        '## Destino das linhas', '', '| Status | Linhas |', '| --- | ---: |',
    ]
    linhas += [f'| {k} | {v} |' for k, v in d['status'].items()]
    linhas += ['', '## Ocorrências de motivos', '', 'Uma linha pode ter vários motivos; avisos não implicam exclusão.', '', '| Motivo | Linhas |', '| --- | ---: |']
    linhas += [f'| {k} | {v} |' for k, v in d['motivos'].items()]
    linhas += ['', '## Cobertura e decisões pendentes', '',
               f"{d['pares_completos']} de {d['pares_mercado_produto']} pares possuem preço válido em todos os meses da janela.", '']
    linhas += ['- ' + s for s in d['limitacoes']]
    linhas += ['', 'Consultar base_quarentena.csv, base_duplicatas.csv, cobertura.csv e regras_aplicadas.json para revisar as decisões.', '']
    return '\n'.join(linhas)


def executar_pipeline(entrada: Path, saida: Path, config: Path, modulos: tuple[str, ...] = ()) -> dict:
    entrada, saida, config = Path(entrada).resolve(), Path(saida).resolve(), Path(config).resolve()
    if entrada.is_relative_to(saida) or config.is_relative_to(saida):
        raise ValueError('Diretório de saída não pode conter a origem ou a configuração.')
    if any(m not in MODULOS for m in modulos) or len(modulos) != len(set(modulos)):
        raise ValueError(f'Módulos devem ser únicos e pertencer a {MODULOS}.')
    if saida.exists() and (not saida.is_dir() or any(saida.iterdir())):
        raise FileExistsError('Saída já contém arquivos. Escolha outro diretório com --saida.')
    regras = json.loads(config.read_text(encoding='utf-8'))
    origem_hash = sha256(entrada)
    saida.mkdir(parents=True, exist_ok=True)
    manifesto = {
        'status': 'em_execucao',
        'inicio_utc': datetime.now(timezone.utc).isoformat(),
        'entrada': str(entrada), 'entrada_sha256': origem_hash,
        'config_sha256': sha256(config),
        'python': platform.python_version(),
        'dependencias': {p: version(p) for p in ['pandas', 'openpyxl', 'numpy']},
        'codigo_sha256': {p.name: sha256(p) for p in sorted(RAIZ.glob('*.py'))},
        'configuracoes_sha256': {str(p.relative_to(RAIZ)): sha256(p) for p in sorted((RAIZ/'config').glob('*.json'))},
        'modulos': {},
        'artefatos_sha256': {},
    }
    if modulos:
        manifesto['dependencias'].update({p: version(p) for p in ['matplotlib','scikit-learn','statsmodels','Markdown']})
    salvar_json(saida / 'manifesto.json', manifesto)
    try:
        base = tratar_dados(carregar_excel(entrada, regras['aba']), regras)
        mercado, geral, cobertura = construir_series(base)
        tabelas = {
            'base_auditada.csv': base,
            'base_tratada.csv': base.loc[base.status.eq('valido')],
            'base_quarentena.csv': base.loc[base.status.eq('quarentena')],
            'base_duplicatas.csv': base.loc[base.status.eq('duplicata')],
            'series_mercado.csv': mercado, 'series_geral.csv': geral,
            'cobertura.csv': cobertura,
            'cobertura_mensal.csv': base.groupby(['mes', 'status'], dropna=False).size().rename('registros').reset_index(),
        }
        for nome, tabela in tabelas.items():
            tabela.to_csv(saida / nome, index=False, encoding='utf-8', date_format='%Y-%m-%d')
        diagnostico = diagnosticar(base, cobertura)
        salvar_json(saida / 'diagnostico.json', diagnostico)
        salvar_json(saida / 'regras_aplicadas.json', regras)
        (saida / 'diagnostico.md').write_text(relatorio_diagnostico(diagnostico), encoding='utf-8')
        for nome in modulos:
            manifesto['modulos'][nome] = {'status': 'em_execucao'}
            try:
                modulo = importlib.import_module(nome)
                destino = saida / 'analises' / nome
                destino.mkdir(parents=True)
                modulo.executar(dados_dir=saida, saida_dir=destino)
                manifesto['modulos'][nome] = {'status': 'concluido'}
            except Exception as exc:
                manifesto['modulos'][nome] = {'status': 'falhou', 'erro': f'{type(exc).__name__}: {exc}'}
                raise
        if set(modulos) == set(MODULOS):
            from sensibilidade import executar as executar_sensibilidade
            from relatorio import gerar
            manifesto['complementos'] = {'status': 'em_execucao'}
            executar_sensibilidade(entrada, regras, saida, saida/'analises/sensibilidade')
            gerar(saida)
            manifesto['complementos'] = {'status': 'concluido'}
        if sha256(entrada) != origem_hash:
            raise RuntimeError('Arquivo de origem mudou durante a execução.')
        manifesto['artefatos_sha256'] = {
            str(p.relative_to(saida)): sha256(p)
            for p in sorted(saida.rglob('*')) if p.is_file() and p != saida / 'manifesto.json'
        }
        manifesto['status'] = 'concluido'
    except Exception as exc:
        manifesto['status'] = 'falhou'
        manifesto['erro'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        manifesto['fim_utc'] = datetime.now(timezone.utc).isoformat()
        salvar_json(saida / 'manifesto.json', manifesto)
    return manifesto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, default=RAIZ / 'ICB_DADOS_2026.xlsx')
    parser.add_argument('--saida', type=Path, default=RAIZ / 'dados/preparados')
    parser.add_argument('--config', type=Path, default=RAIZ / 'config/tratamento.json')
    parser.add_argument('--modulos', nargs='*', choices=MODULOS, default=[])
    args = parser.parse_args()
    try:
        m = executar_pipeline(args.entrada, args.saida, args.config, tuple(args.modulos))
    except Exception as exc:
        print(f'Falha: {exc}', file=sys.stderr)
        return 1
    print(f'Preparação concluída: {args.saida.resolve()}')
    print(f"Módulos analíticos executados: {', '.join(m['modulos']) or 'nenhum (somente integrante 1)'}")
    print('Leia diagnostico.md: unidades inferidas e quarentenas ainda exigem revisão metodológica.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
