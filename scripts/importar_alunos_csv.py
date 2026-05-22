#!/usr/bin/env python3
"""
importar_alunos_csv.py
Importa alunos de um CSV para data/alunos.json

Uso:
    python3 scripts/importar_alunos_csv.py <arquivo.csv>

O CSV deve ter as colunas abaixo (nomes exatos, maiúsculas/minúsculas irrelevantes):
    matricula, nome_completo, serie, turma, turno,
    data_nascimento (YYYY-MM-DD ou DD/MM/YYYY),
    data_ingresso   (YYYY-MM-DD ou DD/MM/YYYY),
    status, ra_estudante, email_estudante,
    mae_nome, mae_telefone, mae_email,
    pai_nome, pai_telefone, pai_email,
    endereco, observacoes,
    termo_autorizado (sim/nao/true/false/1/0),
    foto_coletada    (sim/nao/true/false/1/0)

Colunas obrigatórias: matricula, nome_completo, serie, turma, turno
"""
import csv
import json
import os
import re
import sys
from datetime import datetime

# ── Colunas obrigatórias ────────────────────────────────────────
REQUIRED = ["matricula", "nome_completo", "serie", "turma", "turno"]

# ── Colunas opcionais com valor padrão ─────────────────────────
DEFAULTS = {
    "status":           "Ativo",
    "ra_estudante":     "",
    "nu_chamada":       "",
    "email_estudante":  "",
    "data_nascimento":  "",
    "data_ingresso":    "",
    "rg_estudante":     "",
    "uf_rg":            "",
    "org_emissor_rg":   "",
    "cpf_estudante":    "",
    "mae_nome":         "",
    "mae_telefone":     "",
    "mae_email":        "",
    "pai_nome":         "",
    "pai_telefone":     "",
    "pai_email":        "",
    "endereco":         "",
    "observacoes":      "",
    "termo_autorizado": False,
    "foto_coletada":    False,
}


def parse_bool(val: str) -> bool:
    return str(val).strip().lower() in ("sim", "true", "1", "s", "yes")


def parse_date(val: str) -> str:
    """Normaliza datas para YYYY-MM-DD."""
    val = val.strip()
    if not val:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    print(f"  ⚠️  Data não reconhecida: '{val}' — mantida como texto")
    return val


def normalize_header(h: str) -> str:
    return h.strip().lower().replace(" ", "_").replace("-", "_")


def main():
    if len(sys.argv) < 2:
        print("\n❌  Uso: python3 scripts/importar_alunos_csv.py <arquivo.csv>\n")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.isfile(csv_path):
        print(f"\n❌  Arquivo não encontrado: {csv_path}\n")
        sys.exit(1)

    # ── Ler CSV ───────────────────────────────────────────────
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = [normalize_header(h) for h in reader.fieldnames or []]
        rows = list(reader)

    # Verificar colunas obrigatórias
    missing = [c for c in REQUIRED if c not in headers]
    if missing:
        print(f"\n❌  Colunas obrigatórias ausentes: {', '.join(missing)}")
        print(f"    Colunas encontradas: {', '.join(headers)}\n")
        sys.exit(1)

    # ── Carregar JSON existente ───────────────────────────────
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "alunos.json")
    json_path = os.path.normpath(json_path)

    if os.path.isfile(json_path):
        with open(json_path, encoding="utf-8") as f:
            existentes = {a["matricula"]: a for a in json.load(f)}
    else:
        existentes = {}

    # ── Processar linhas ──────────────────────────────────────
    novos = 0
    atualizados = 0
    ignorados = 0
    erros = []

    for i, row in enumerate(rows, start=2):
        norm = {normalize_header(k): v.strip() if v else "" for k, v in row.items()}

        mat = norm.get("matricula", "").strip()
        if not mat:
            erros.append(f"  Linha {i}: matrícula vazia — ignorada")
            ignorados += 1
            continue

        nome = norm.get("nome_completo", "").strip()
        if not nome:
            erros.append(f"  Linha {i}: nome_completo vazio (mat={mat}) — ignorada")
            ignorados += 1
            continue

        aluno = dict(DEFAULTS)
        aluno.update({
            "matricula":     mat,
            "nome_completo": nome,
            "serie":         norm.get("serie", ""),
            "turma":         norm.get("turma", ""),
            "turno":         norm.get("turno", ""),
            "status":        norm.get("status", "Ativo") or "Ativo",
            "ra_estudante":  norm.get("ra_estudante", ""),
            "nu_chamada":    norm.get("nu_chamada", ""),
            "rg_estudante":  norm.get("rg_estudante", ""),
            "uf_rg":         norm.get("uf_rg", "").upper(),
            "org_emissor_rg":norm.get("org_emissor_rg", "").upper(),
            "cpf_estudante": norm.get("cpf_estudante", ""),
            "email_estudante": norm.get("email_estudante", ""),
            "data_nascimento": parse_date(norm.get("data_nascimento", "")),
            "data_ingresso":   parse_date(norm.get("data_ingresso", "")),
            "mae_nome":      norm.get("mae_nome", ""),
            "mae_telefone":  norm.get("mae_telefone", ""),
            "mae_email":     norm.get("mae_email", ""),
            "pai_nome":      norm.get("pai_nome", ""),
            "pai_telefone":  norm.get("pai_telefone", ""),
            "pai_email":     norm.get("pai_email", ""),
            "endereco":      norm.get("endereco", ""),
            "observacoes":   norm.get("observacoes", ""),
            "termo_autorizado": parse_bool(norm.get("termo_autorizado", "false")),
            "foto_coletada":    parse_bool(norm.get("foto_coletada", "false")),
        })

        if mat in existentes:
            existentes[mat] = aluno
            atualizados += 1
        else:
            existentes[mat] = aluno
            novos += 1

    # ── Salvar ────────────────────────────────────────────────
    resultado = list(existentes.values())
    resultado.sort(key=lambda a: (a.get("serie",""), a.get("turma",""), a.get("nome_completo","")))

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    # ── Relatório ─────────────────────────────────────────────
    sep = "─" * 53
    print(f"\n{sep}")
    print("  Carômetro Escolar — Importação de Alunos")
    print(sep)
    print(f"  CSV lido         : {csv_path}")
    print(f"  Linhas no CSV    : {len(rows)}")
    print(f"  ✅  Novos         : {novos}")
    print(f"  🔄  Atualizados   : {atualizados}")
    print(f"  ⏭️  Ignorados      : {ignorados}")
    print(f"  Total no JSON    : {len(resultado)}")
    print(f"  Salvo em         : {json_path}")
    print(sep)
    if erros:
        print("\n  ⚠️  Avisos:")
        for e in erros:
            print(e)
    print()


if __name__ == "__main__":
    main()
