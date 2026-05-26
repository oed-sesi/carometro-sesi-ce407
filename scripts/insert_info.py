#!/usr/bin/env python3
"""
insert_info.py
Carômetro Escolar — SESI 407  |  v1.0

Gerencia AVISOS e EDUCAÇÃO INCLUSIVA no arquivo data/alunos.json.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AVISOS (badge vermelho + borda no card)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adicionar aviso:
  python3 scripts/insert_info.py --aviso --rm 6650
  python3 scripts/insert_info.py --aviso --rm 6650 --texto "Afastado das atividades físicas" --dias 60
  python3 scripts/insert_info.py --aviso --rm 6650 --texto "Afastado das atividades físicas" --inicio 2026-05-21 --fim 2026-07-20

Remover aviso ativo:
  python3 scripts/insert_info.py --remover-aviso --rm 6650
  python3 scripts/insert_info.py --remover-aviso --rm 6650 --todos

Listar avisos ativos:
  python3 scripts/insert_info.py --listar-avisos
  python3 scripts/insert_info.py --listar-avisos --rm 6650

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTAR OBSERVAÇÕES DE TODOS OS ALUNOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Importar observações (preserva existentes):
  python3 scripts/insert_info.py --importar-obs planilha_estudantes.csv
  python3 scripts/insert_info.py --importar-obs planilha_estudantes.xlsx

Sobrescrever mesmo quem já tem observação:
  python3 scripts/insert_info.py --importar-obs planilha_estudantes.csv --sobrescrever
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Importar da planilha (recomendado):
  python3 scripts/insert_info.py --importar-ei planilha_estudantes.csv

Marcar manualmente:
  python3 scripts/insert_info.py --ei --rm 6650 --diagnostico "TEA Nível 2"
  python3 scripts/insert_info.py --ei --rm 6650  (interativo)

Remover marcação EI:
  python3 scripts/insert_info.py --remover-ei --rm 6650

Listar EI:
  python3 scripts/insert_info.py --listar-ei
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

BASE      = Path(__file__).resolve().parent.parent
JSON_PATH = BASE / "data" / "alunos.json"

SEP  = "─" * 64
SEP2 = "═" * 64

TIPOS_AVISO = {
    "saude":       "🏥  Saúde",
    "disciplinar": "⚠️  Disciplinar",
    "academico":   "📚  Acadêmico",
    "geral":       "ℹ️  Geral",
}

# ── Utilitários ────────────────────────────────────────────────
def carregar() -> list[dict]:
    if not JSON_PATH.is_file():
        print(f"  ❌  {JSON_PATH} não encontrado.\n"); sys.exit(1)
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)

def salvar(alunos: list[dict]) -> None:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(alunos, f, ensure_ascii=False, indent=2)

def encontrar(alunos: list[dict], rm: str) -> dict | None:
    return next(
        (a for a in alunos if str(a.get("rm_estudante") or a.get("matricula","")) == str(rm)),
        None
    )

def garantir_campos(aluno: dict) -> None:
    """Garante que os campos novos existam no registro."""
    aluno.setdefault("avisos", [])
    aluno.setdefault("educacao_inclusiva", False)
    aluno.setdefault("diagnostico", "")

def hoje() -> str:
    return date.today().isoformat()

def avisos_ativos(aluno: dict) -> list[dict]:
    """Retorna apenas avisos cujo período ainda está ativo."""
    hoje_str = hoje()
    result = []
    for av in aluno.get("avisos", []):
        fim = av.get("data_fim", "")
        if not fim or fim >= hoje_str:
            result.append(av)
    return result

def formatar_aviso(av: dict) -> str:
    texto    = av.get("texto", "—")
    inicio   = av.get("data_inicio", "")
    fim      = av.get("data_fim", "")
    tipo_key = av.get("tipo", "geral")
    tipo_lab = TIPOS_AVISO.get(tipo_key, tipo_key)
    periodo  = ""
    if inicio and fim:
        periodo = f"  {inicio} → {fim}"
    elif inicio:
        periodo = f"  a partir de {inicio}"
    return f"{tipo_lab}  {texto}{periodo}"

# ══════════════════════════════════════════════════════════════
# AVISOS
# ══════════════════════════════════════════════════════════════
def acao_adicionar_aviso(
    rm: str,
    texto: str | None,
    tipo: str,
    inicio: str | None,
    fim: str | None,
    dias: int | None,
) -> None:
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Adicionar Aviso")
    print(SEP2)

    alunos = carregar()
    aluno  = encontrar(alunos, rm)
    if not aluno:
        print(f"  ❌  Aluno com RM {rm} não encontrado.\n"); sys.exit(1)

    garantir_campos(aluno)
    print(f"  Aluno : {aluno['nome_completo']}")
    print(f"  Turma : {aluno['serie']} {aluno['turma']} — {aluno['turno']}")
    print()

    # Coletar dados interativamente se não fornecidos
    if not texto:
        texto = input("  Texto do aviso: ").strip()
        if not texto:
            print("  ❌  Texto obrigatório.\n"); sys.exit(1)

    if not inicio:
        inp = input(f"  Data de início [hoje = {hoje()}]: ").strip()
        inicio = inp if inp else hoje()

    if not fim and not dias:
        inp = input("  Data de fim [YYYY-MM-DD] ou número de dias (ex: 60): ").strip()
        if inp.isdigit():
            dias = int(inp)
        elif inp:
            fim = inp

    if dias and not fim:
        fim = (datetime.strptime(inicio, "%Y-%m-%d") + timedelta(days=dias)).strftime("%Y-%m-%d")

    print()
    print("  Tipo do aviso:")
    for i, (k, v) in enumerate(TIPOS_AVISO.items(), 1):
        print(f"    {i} → {v}")
    inp = input("  Escolha [1-4, padrão=1 (Saúde)]: ").strip()
    tipos_keys = list(TIPOS_AVISO.keys())
    if inp.isdigit() and 1 <= int(inp) <= len(tipos_keys):
        tipo = tipos_keys[int(inp)-1]
    else:
        tipo = tipo or "saude"

    aviso = {
        "texto":       texto,
        "data_inicio": inicio,
        "data_fim":    fim or "",
        "tipo":        tipo,
        "criado_em":   hoje(),
    }
    aluno["avisos"].append(aviso)
    salvar(alunos)

    print(f"\n  ✅  Aviso adicionado para {aluno['nome_completo']}")
    print(f"  📋  {formatar_aviso(aviso)}\n")


def acao_remover_aviso(rm: str, todos: bool) -> None:
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Remover Aviso")
    print(SEP2)

    alunos = carregar()
    aluno  = encontrar(alunos, rm)
    if not aluno:
        print(f"  ❌  Aluno com RM {rm} não encontrado.\n"); sys.exit(1)

    garantir_campos(aluno)
    avisos = aluno.get("avisos", [])
    ativos = avisos_ativos(aluno)

    if not avisos:
        print(f"  ℹ️  {aluno['nome_completo']} não tem avisos.\n"); return

    print(f"  Aluno : {aluno['nome_completo']}")
    print()

    if todos:
        aluno["avisos"] = []
        salvar(alunos)
        print(f"  ✅  Todos os {len(avisos)} aviso(s) removidos.\n"); return

    if len(avisos) == 1:
        av = avisos[0]
        print(f"  Aviso: {formatar_aviso(av)}")
        resp = input("  Remover? [s/N]: ").strip().lower()
        if resp in ("s","sim"):
            aluno["avisos"] = []
            salvar(alunos)
            print("  ✅  Aviso removido.\n")
        else:
            print("  ↩️  Cancelado.\n")
        return

    print("  Avisos:")
    for i, av in enumerate(avisos, 1):
        ativo = "(ativo)" if av in ativos else "(expirado)"
        print(f"    {i}. {formatar_aviso(av)} {ativo}")

    inp = input("  Número a remover (ou 'todos'): ").strip()
    if inp.lower() == "todos":
        aluno["avisos"] = []
    elif inp.isdigit() and 1 <= int(inp) <= len(avisos):
        avisos.pop(int(inp)-1)
    else:
        print("  ↩️  Cancelado.\n"); return

    salvar(alunos)
    print("  ✅  Aviso(s) removido(s).\n")


def acao_listar_avisos(rm: str | None) -> None:
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Avisos Ativos")
    print(SEP2)

    alunos = carregar()

    if rm:
        aluno = encontrar(alunos, rm)
        if not aluno:
            print(f"  ❌  RM {rm} não encontrado.\n"); sys.exit(1)
        alvo = [aluno]
    else:
        alvo = alunos

    total = 0
    for a in alvo:
        garantir_campos(a)
        ativos = avisos_ativos(a)
        if not ativos:
            continue
        print(f"  {a['nome_completo']}  ({a['serie']} {a['turma']}  RM {a.get('rm_estudante','')})")
        for av in ativos:
            print(f"    • {formatar_aviso(av)}")
        total += 1

    if total == 0:
        print("  ℹ️  Nenhum aviso ativo encontrado.\n")
    else:
        print(f"\n  Total: {total} aluno(s) com aviso ativo\n")


# ══════════════════════════════════════════════════════════════
# EDUCAÇÃO INCLUSIVA
# ══════════════════════════════════════════════════════════════
def acao_marcar_ei(rm: str, diagnostico: str | None) -> None:
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Marcar Educação Inclusiva")
    print(SEP2)

    alunos = carregar()
    aluno  = encontrar(alunos, rm)
    if not aluno:
        print(f"  ❌  RM {rm} não encontrado.\n"); sys.exit(1)

    garantir_campos(aluno)
    print(f"  Aluno  : {aluno['nome_completo']}")
    print(f"  EI atual: {aluno['educacao_inclusiva']}")
    if aluno.get("diagnostico"):
        print(f"  Diagnóstico atual: {aluno['diagnostico']}")
    print()

    if not diagnostico:
        diagnostico = input("  Diagnóstico: ").strip()

    aluno["educacao_inclusiva"] = True
    aluno["diagnostico"]        = diagnostico

    # Atualizar observações com diagnóstico
    obs_atual = aluno.get("observacoes", "") or ""
    prefixo   = "Educação Inclusiva"
    if prefixo not in obs_atual:
        nova_obs = f"{prefixo}: {diagnostico}"
        if obs_atual and obs_atual.lower() not in ("não se aplica", ""):
            nova_obs = f"{obs_atual} | {nova_obs}"
        aluno["observacoes"] = nova_obs

    salvar(alunos)
    print(f"  ✅  {aluno['nome_completo']} marcado como Educação Inclusiva")
    print(f"  📋  Diagnóstico: {diagnostico}\n")


def acao_remover_ei(rm: str) -> None:
    alunos = carregar()
    aluno  = encontrar(alunos, rm)
    if not aluno:
        print(f"  ❌  RM {rm} não encontrado.\n"); sys.exit(1)
    garantir_campos(aluno)
    aluno["educacao_inclusiva"] = False
    aluno["diagnostico"]        = ""
    salvar(alunos)
    print(f"  ✅  Marcação EI removida de {aluno['nome_completo']}\n")


def acao_listar_ei() -> None:
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Estudantes de Educação Inclusiva")
    print(SEP2)

    alunos = carregar()
    ei     = [a for a in alunos if a.get("educacao_inclusiva")]

    if not ei:
        print("  ℹ️  Nenhum estudante marcado como EI.\n"); return

    print(f"  Total: {len(ei)} estudante(s)\n")
    print(f"  {'RM':<10} {'Nome':<40} {'Série/Turma':<14} {'Diagnóstico'}")
    print(f"  {SEP}")
    for a in ei:
        rm   = a.get("rm_estudante", a.get("matricula",""))
        nome = a["nome_completo"][:39]
        st   = f"{a['serie']} {a['turma']}"
        diag = a.get("diagnostico","")[:55]
        print(f"  {rm:<10} {nome:<40} {st:<14} {diag}")
    print()


def acao_importar_ei(caminho_arg: str) -> None:
    """Importa educação inclusiva da planilha CSV/XLSX."""
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Importar Educação Inclusiva da Planilha")
    print(SEP2)

    caminho = Path(caminho_arg)
    if not caminho.is_absolute():
        caminho = BASE / caminho_arg
    if not caminho.exists():
        print(f"  ❌  Arquivo não encontrado: {caminho}\n"); sys.exit(1)

    df = _ler_planilha(caminho)

    if "rm_estudante" not in df.columns:
        print("  ❌  Coluna 'rm_estudante' não encontrada.\n"); sys.exit(1)
    if "estudante_elegiveis" not in df.columns:
        print("  ❌  Coluna 'estudante_elegiveis' não encontrada.\n"); sys.exit(1)

    # Filtrar elegíveis
    elegíveis = df[df["estudante_elegiveis"].str.strip().str.lower() == "sim"].copy()
    print(f"  Planilha : {caminho.name}")
    print(f"  Elegíveis encontrados: {len(elegíveis)}")
    print()

    alunos = carregar()
    rm_map = {
        str(a.get("rm_estudante") or a.get("matricula", "")): a
        for a in alunos
    }

    marcados   = []
    nao_achado = []

    for _, row in elegíveis.iterrows():
        rm   = str(row.get("rm_estudante", "")).strip()
        diag = str(row.get("diagnostico", "")).strip()
        if not diag or diag.lower() in ("nan", "none", ""):
            diag = "Educação Inclusiva — diagnóstico a confirmar"

        aluno = rm_map.get(rm)
        if not aluno:
            nao_achado.append(rm)
            continue

        garantir_campos(aluno)
        aluno["educacao_inclusiva"] = True
        aluno["diagnostico"]        = diag

        # Atualizar observações
        obs_atual = aluno.get("observacoes", "") or ""
        prefixo   = "Educação Inclusiva"
        if prefixo not in obs_atual:
            nova_obs = f"{prefixo}: {diag}"
            if obs_atual and obs_atual.lower() not in ("não se aplica", "nan", ""):
                nova_obs = f"{obs_atual} | {nova_obs}"
            aluno["observacoes"] = nova_obs

        marcados.append((rm, aluno["nome_completo"], diag[:60]))

    salvar(alunos)

    print(f"  {SEP}")
    print(f"  {'✅  Marcados':<30}: {len(marcados)}")
    print(f"  {'⚠️  RM não encontrado no JSON':<30}: {len(nao_achado)}")
    print(f"  {SEP}")

    if marcados:
        print(f"\n  Marcados ({len(marcados)}):")
        for rm, nome, diag in marcados[:20]:
            print(f"    🟣 {rm:<8} {nome[:38]:<38} {diag}")
        if len(marcados) > 20:
            print(f"    ... e mais {len(marcados)-20}")

    if nao_achado:
        print(f"\n  RMs não encontrados no JSON:")
        for rm in nao_achado[:10]:
            print(f"    • {rm}")
        if len(nao_achado) > 10:
            print(f"    ... e mais {len(nao_achado)-10}")

    print(f"\n  ✅  Importação concluída! Execute git push para publicar.\n")


def _ensure_pandas():
    """
    Garante que o pandas instalado via pip (versão compatível com numpy atual)
    seja importado, e não a versão do sistema (/usr/lib/python3/dist-packages)
    que pode estar compilada com uma versão diferente do numpy.
    """
    import importlib.util, subprocess, site

    # Priorizar pacotes do pip sobre os do sistema operacional
    # Isso evita o erro: "numpy.dtype size changed, may indicate binary incompatibility"
    pip_paths = [p for p in site.getsitepackages()
                 if "local" in p or "dist-packages" in p]
    for p in reversed(pip_paths):
        if p not in sys.path:
            sys.path.insert(0, p)

    if importlib.util.find_spec("pandas") is None:
        print("  📦  Instalando pandas...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pandas",
             "--break-system-packages", "-q"]
        )


def _ler_planilha(caminho: Path):
    """Lê CSV ou XLSX retornando um DataFrame com colunas normalizadas."""
    _ensure_pandas()
    import pandas as pd

    ext = caminho.suffix.lower()
    try:
        if ext in (".xlsx", ".xlsm", ".xls"):
            df = pd.read_excel(caminho, dtype=str)
        else:
            try:
                df = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig")
            except UnicodeDecodeError:
                df = pd.read_csv(caminho, dtype=str, encoding="latin-1")
    except Exception as e:
        print(f"  ❌  Erro ao ler arquivo: {e}\n")
        sys.exit(1)

    # Normalizar nomes das colunas
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


# ══════════════════════════════════════════════════════════════
# IMPORTAR OBSERVAÇÕES DE TODOS OS ALUNOS
# ══════════════════════════════════════════════════════════════
def acao_importar_obs(caminho_arg: str, sobrescrever: bool = False) -> None:
    """
    Importa o campo 'observacoes' da planilha para todos os alunos no JSON.

    Regras de atualização:
      - Valores vazios ou "Não se aplica" na planilha → campo preservado no JSON
      - Se o aluno já tem observação no JSON → preservada (a menos que --sobrescrever)
      - Se --sobrescrever → substitui sempre que a planilha tiver valor não-vazio
    """
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Importar Observações da Planilha")
    print(SEP2)

    caminho = Path(caminho_arg)
    if not caminho.is_absolute():
        caminho = BASE / caminho_arg
    if not caminho.exists():
        print(f"  ❌  Arquivo não encontrado: {caminho}\n")
        sys.exit(1)

    df = _ler_planilha(caminho)

    if "rm_estudante" not in df.columns:
        print("  ❌  Coluna 'rm_estudante' não encontrada.\n")
        sys.exit(1)

    if "observacoes" not in df.columns:
        print("  ❌  Coluna 'observacoes' não encontrada na planilha.\n")
        sys.exit(1)

    IGNORAR = {"não se aplica", "nao se aplica", "nan", "none", "n/a", "-", ""}

    alunos = carregar()
    rm_map = {
        str(a.get("rm_estudante") or a.get("matricula", "")): a
        for a in alunos
    }

    print(f"  Planilha  : {caminho.name}")
    print(f"  Alunos    : {len(df)} linhas")
    print(f"  Modo      : {'Sobrescrever sempre' if sobrescrever else 'Preservar existente'}")
    print()

    atualizados  = []
    preservados  = []
    sem_valor    = []
    nao_achado   = []

    for _, row in df.iterrows():
        rm  = str(row.get("rm_estudante", "")).strip()
        obs = str(row.get("observacoes", "")).strip()

        if not rm:
            continue

        aluno = rm_map.get(rm)
        if not aluno:
            nao_achado.append(rm)
            continue

        garantir_campos(aluno)

        # Ignorar valores vazios/inválidos da planilha
        if obs.lower() in IGNORAR:
            sem_valor.append(rm)
            continue

        obs_atual = (aluno.get("observacoes") or "").strip()

        if obs_atual and not sobrescrever:
            # Já tem valor no JSON e não foi pedido para sobrescrever
            preservados.append((rm, aluno["nome_completo"][:35], obs_atual[:40]))
            continue

        aluno["observacoes"] = obs
        atualizados.append((rm, aluno["nome_completo"][:35], obs[:50]))

    salvar(alunos)

    print(f"  {SEP}")
    print(f"  {'✅  Atualizados':<32}: {len(atualizados)}")
    print(f"  {'⏭️  Preservados (já tinham valor)':<32}: {len(preservados)}")
    print(f"  {'➖  Sem valor na planilha':<32}: {len(sem_valor)}")
    print(f"  {'⚠️  RM não encontrado no JSON':<32}: {len(nao_achado)}")
    print(f"  {SEP}")

    if atualizados:
        print(f"\n  Atualizados ({len(atualizados)}):")
        for rm, nome, obs in atualizados[:15]:
            print(f"    • {rm:<8} {nome:<36} {obs}")
        if len(atualizados) > 15:
            print(f"    ... e mais {len(atualizados)-15}")

    if preservados:
        print(f"\n  Preservados — já tinham observação no JSON ({len(preservados)}):")
        for rm, nome, obs in preservados[:10]:
            print(f"    • {rm:<8} {nome:<36} {obs}")
        if len(preservados) > 10:
            print(f"    ... e mais {len(preservados)-10}")
        print(f"\n  💡  Use --sobrescrever para substituir todos os valores existentes.")

    if nao_achado:
        print(f"\n  ⚠️  {len(nao_achado)} RM(s) da planilha não encontrados no JSON.")
        print(f"      Execute importar_estudantes.py primeiro para importar esses alunos.")

    print(f"\n  ✅  Observações importadas. Execute git push para publicar.\n")
def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    # Parser
    cmd         = None
    rm          = None
    texto       = None
    tipo        = "saude"
    inicio      = None
    fim         = None
    dias        = None
    todos       = False
    diagnostico = None
    arquivo     = None
    sobrescrever = False

    i = 0
    while i < len(args):
        a = args[i]
        if   a in ("--aviso",          "-av"):  cmd = "aviso"
        elif a in ("--remover-aviso",):          cmd = "remover-aviso"
        elif a in ("--listar-avisos",  "-la"):   cmd = "listar-avisos"
        elif a in ("--ei",):                     cmd = "ei"
        elif a in ("--remover-ei",):             cmd = "remover-ei"
        elif a in ("--listar-ei",      "-le"):   cmd = "listar-ei"
        elif a in ("--importar-ei",    "-ie"):
            cmd = "importar-ei"
            i += 1
            if i < len(args): arquivo = args[i]
        elif a in ("--importar-obs",   "-io"):
            cmd = "importar-obs"
            i += 1
            if i < len(args): arquivo = args[i]
        elif a in ("--sobrescrever",   "-s"):    sobrescrever = True
        elif a in ("--rm",             "-r"):
            i += 1
            if i < len(args): rm = args[i]
        elif a in ("--texto",          "-t"):
            i += 1
            if i < len(args): texto = args[i]
        elif a in ("--tipo"):
            i += 1
            if i < len(args): tipo = args[i]
        elif a in ("--inicio"):
            i += 1
            if i < len(args): inicio = args[i]
        elif a in ("--fim"):
            i += 1
            if i < len(args): fim = args[i]
        elif a in ("--dias",           "-d"):
            i += 1
            if i < len(args): dias = int(args[i])
        elif a in ("--todos"):               todos = True
        elif a in ("--diagnostico"):
            i += 1
            if i < len(args): diagnostico = args[i]
        i += 1

    if   cmd == "aviso":
        if not rm:
            rm = input("  RM do estudante: ").strip()
        acao_adicionar_aviso(rm, texto, tipo, inicio, fim, dias)
    elif cmd == "remover-aviso":
        if not rm:
            rm = input("  RM do estudante: ").strip()
        acao_remover_aviso(rm, todos)
    elif cmd == "listar-avisos":
        acao_listar_avisos(rm)
    elif cmd == "ei":
        if not rm:
            rm = input("  RM do estudante: ").strip()
        acao_marcar_ei(rm, diagnostico)
    elif cmd == "remover-ei":
        if not rm:
            rm = input("  RM do estudante: ").strip()
        acao_remover_ei(rm)
    elif cmd == "listar-ei":
        acao_listar_ei()
    elif cmd == "importar-ei":
        if not arquivo:
            arquivo = input("  Caminho da planilha: ").strip()
        acao_importar_ei(arquivo)
    elif cmd == "importar-obs":
        if not arquivo:
            arquivo = input("  Caminho da planilha: ").strip()
        acao_importar_obs(arquivo, sobrescrever=sobrescrever)
    else:
        print(f"  ❌  Comando desconhecido: {cmd}")
        print("  Use --help para ver os comandos disponíveis.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
