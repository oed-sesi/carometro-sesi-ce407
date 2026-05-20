#!/usr/bin/env python3
"""
verificar_sistema.py
Verifica a consistência entre data/alunos.json e a pasta images/

Relatório:
    - Alunos com foto_coletada=true mas sem imagem em images/
    - Alunos com foto_coletada=false mas com imagem em images/
    - Alunos sem foto (foto_coletada=false)
    - Imagens em images/ sem aluno correspondente no JSON
    - Estatísticas por turma

Uso:
    python3 scripts/verificar_sistema.py
"""
import json
import os
from pathlib import Path

BASE = Path(__file__).parent.parent
JSON_PATH   = BASE / "data" / "alunos.json"
IMAGES_PATH = BASE / "images"
EXTENSOES   = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    sep = "═" * 55

    # ── Carregar dados ────────────────────────────────────────
    if not JSON_PATH.is_file():
        print(f"\n❌  Arquivo não encontrado: {JSON_PATH}\n")
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        alunos = json.load(f)

    # Imagens existentes (stem = matrícula)
    imagens = set()
    if IMAGES_PATH.is_dir():
        for f in IMAGES_PATH.iterdir():
            if f.is_file() and f.suffix.lower() in EXTENSOES:
                imagens.add(f.stem)

    print(f"\n{sep}")
    print("  Carômetro Escolar — Verificação do Sistema")
    print(sep)
    print(f"  Alunos no JSON    : {len(alunos)}")
    print(f"  Imagens em images/: {len(imagens)}")
    print(sep)

    # ── Análise ───────────────────────────────────────────────
    flag_sem_imagem  = []  # foto_coletada=true mas arquivo não existe
    flag_sem_flag    = []  # imagem existe mas foto_coletada=false
    sem_foto         = []  # foto_coletada=false (esperado)
    matriculas_json  = set()

    turma_stats = {}  # {(serie,turma,turno): {total,com_foto,imagem_ok}}

    for a in alunos:
        mat = a["matricula"]
        matriculas_json.add(mat)
        key = (a["serie"], a["turma"], a["turno"])
        if key not in turma_stats:
            turma_stats[key] = {"total": 0, "com_foto": 0, "imagem_ok": 0}
        turma_stats[key]["total"] += 1

        tem_imagem = mat in imagens
        flag = a.get("foto_coletada", False)

        if flag:
            turma_stats[key]["com_foto"] += 1
            if tem_imagem:
                turma_stats[key]["imagem_ok"] += 1
            else:
                flag_sem_imagem.append(a)
        else:
            if tem_imagem:
                flag_sem_flag.append(a)
            else:
                sem_foto.append(a)

    # Imagens sem aluno
    imagens_orfas = imagens - matriculas_json

    # ── Relatório de inconsistências ─────────────────────────
    print()
    if flag_sem_imagem:
        print(f"  ⚠️  [{len(flag_sem_imagem)}] foto_coletada=true MAS imagem não encontrada em images/:")
        for a in flag_sem_imagem:
            print(f"      • {a['matricula']} — {a['nome_completo']} ({a['serie']} {a['turma']})")
            print(f"        → Crie ou copie: images/{a['matricula']}.jpg")
        print()

    if flag_sem_flag:
        print(f"  ℹ️  [{len(flag_sem_flag)}] Imagem existe MAS foto_coletada=false no JSON:")
        for a in flag_sem_flag:
            print(f"      • {a['matricula']} — {a['nome_completo']}")
            print(f"        → Edite data/alunos.json: \"foto_coletada\": true")
        print()

    if imagens_orfas:
        print(f"  ❓  [{len(imagens_orfas)}] Imagens sem aluno no JSON:")
        for m in sorted(imagens_orfas):
            print(f"      • images/{m}.jpg — nenhum aluno com esta matrícula")
        print()

    if not flag_sem_imagem and not flag_sem_flag and not imagens_orfas:
        print("  ✅  Nenhuma inconsistência encontrada!\n")

    # ── Estatísticas por turma ────────────────────────────────
    print(f"\n  {'─'*51}")
    print("  Cobertura por Turma:")
    print(f"  {'─'*51}")
    print(f"  {'Turma':<25} {'Total':>6} {'c/Foto':>7} {'OK':>5} {'%':>5}")
    print(f"  {'─'*51}")

    total_g = com_foto_g = ok_g = 0
    for key in sorted(turma_stats.keys(), key=lambda k: (k[0], k[1], k[2])):
        s = turma_stats[key]
        pct = round(s['imagem_ok'] / s['total'] * 100) if s['total'] > 0 else 0
        label = f"{key[0]} {key[1]} — {key[2]}"
        status = "✅" if pct >= 90 else ("⚠️ " if pct >= 50 else "❌")
        print(f"  {status} {label:<22} {s['total']:>6} {s['com_foto']:>7} {s['imagem_ok']:>5} {pct:>4}%")
        total_g    += s['total']
        com_foto_g += s['com_foto']
        ok_g       += s['imagem_ok']

    print(f"  {'─'*51}")
    pct_g = round(ok_g / total_g * 100) if total_g > 0 else 0
    print(f"  {'TOTAL':<25} {total_g:>6} {com_foto_g:>7} {ok_g:>5} {pct_g:>4}%")
    print(f"  {'─'*51}\n")

    # ── Alunos sem foto ───────────────────────────────────────
    if sem_foto:
        print(f"  📋  [{len(sem_foto)}] Alunos sem foto (foto_coletada=false):")
        for a in sorted(sem_foto, key=lambda x: (x['serie'], x['turma'], x['nome_completo'])):
            print(f"      • {a['matricula']} — {a['nome_completo']} ({a['serie']} {a['turma']} {a['turno']})")
        print()


if __name__ == "__main__":
    main()
