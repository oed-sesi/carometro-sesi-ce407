#!/usr/bin/env python3
"""
verificar_sistema.py
Carômetro Escolar — SESI 407

Verifica a consistência entre:
  - data/alunos.json
  - pasta images/ (fotos originais)
  - pastas images_<turma>/ (fotos organizadas por turma)
  - data/config.json

Uso:
    python3 scripts/verificar_sistema.py
    python3 scripts/verificar_sistema.py --resumo    (apenas estatísticas)
    python3 scripts/verificar_sistema.py --json      (saída em JSON)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE        = Path(__file__).resolve().parent.parent
JSON_PATH   = BASE / "data" / "alunos.json"
CONFIG_PATH = BASE / "data" / "config.json"
IMAGES_DIR  = BASE / "images"
EXTENSOES   = {".jpg", ".jpeg", ".png", ".webp"}

SEP  = "─" * 60
SEP2 = "═" * 60


def coletar_imagens_dir(pasta: Path) -> set[str]:
    if not pasta.is_dir():
        return set()
    return {f.stem for f in pasta.iterdir()
            if f.is_file() and f.suffix.lower() in EXTENSOES}


def main() -> None:
    modo_resumo = "--resumo" in sys.argv
    modo_json   = "--json"   in sys.argv

    # ── Carregar dados ────────────────────────────────────────
    if not JSON_PATH.is_file():
        msg = f"❌  Arquivo não encontrado: {JSON_PATH}"
        if modo_json:
            print(json.dumps({"erro": msg}))
        else:
            print(f"\n{msg}\n")
        sys.exit(1)

    with open(JSON_PATH, encoding="utf-8") as f:
        alunos = json.load(f)

    # Normalizar: suporte a campo legado "matricula"
    for a in alunos:
        if "rm_estudante" not in a:
            a["rm_estudante"] = a.get("matricula", "")

    # Imagens na pasta principal
    imgs_principal = coletar_imagens_dir(IMAGES_DIR)

    # Pastas de turmas (images_Xano_Y / images_Xserie_Y)
    pastas_turma: dict[str, set[str]] = {}
    for item in sorted(BASE.iterdir()):
        if item.is_dir() and item.name.startswith("images_") and item.name != "images":
            pastas_turma[item.name] = coletar_imagens_dir(item)

    # ── Analisar ─────────────────────────────────────────────
    flag_sem_imagem : list[dict] = []   # foto_coletada=true, sem arquivo
    flag_sem_flag   : list[dict] = []   # arquivo existe, foto_coletada=false
    sem_foto        : list[dict] = []   # foto_coletada=false (esperado)
    imgs_orfas      : set[str]   = set()
    turma_stats     : dict       = {}

    matriculas_json = set()

    for a in alunos:
        rm  = a["rm_estudante"]
        matriculas_json.add(rm)
        key = (a.get("serie",""), a.get("turma",""), a.get("turno",""))
        if key not in turma_stats:
            turma_stats[key] = {"total": 0, "com_foto": 0, "img_ok": 0}
        turma_stats[key]["total"] += 1

        tem_img = rm in imgs_principal
        flag    = a.get("foto_coletada", False)

        if flag:
            turma_stats[key]["com_foto"] += 1
            if tem_img:
                turma_stats[key]["img_ok"] += 1
            else:
                flag_sem_imagem.append(a)
        else:
            if tem_img:
                flag_sem_flag.append(a)
            else:
                sem_foto.append(a)

    imgs_orfas = imgs_principal - matriculas_json

    # ── Saída JSON ────────────────────────────────────────────
    if modo_json:
        resultado = {
            "total_alunos":        len(alunos),
            "imgs_principal":      len(imgs_principal),
            "flag_sem_imagem":     [a["rm_estudante"] for a in flag_sem_imagem],
            "flag_sem_flag":       [a["rm_estudante"] for a in flag_sem_flag],
            "sem_foto":            [a["rm_estudante"] for a in sem_foto],
            "imgs_orfas":          sorted(imgs_orfas),
            "pastas_turma":        {k: len(v) for k, v in pastas_turma.items()},
            "inconsistencias":     len(flag_sem_imagem) + len(flag_sem_flag) + len(imgs_orfas),
        }
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    # ── Saída texto ───────────────────────────────────────────
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Verificação do Sistema")
    print(SEP2)
    print(f"  Alunos no JSON      : {len(alunos)}")
    print(f"  Imagens em images/  : {len(imgs_principal)}")
    print(f"  Pastas de turma     : {len(pastas_turma)}")
    print()

    # Inconsistências
    total_inconsist = len(flag_sem_imagem) + len(flag_sem_flag) + len(imgs_orfas)
    if total_inconsist == 0:
        print(f"  ✅  Nenhuma inconsistência encontrada!\n")
    else:
        if flag_sem_imagem:
            print(f"  ⚠️  [{len(flag_sem_imagem)}] foto_coletada=true MAS imagem não existe em images/:")
            for a in flag_sem_imagem:
                print(f"      • {a['rm_estudante']} — {a.get('nome_completo','?')} ({a.get('serie','')} {a.get('turma','')})")
                print(f"        → Adicione: images/{a['rm_estudante']}.jpg")
            print()

        if flag_sem_flag:
            print(f"  ℹ️  [{len(flag_sem_flag)}] Imagem existe MAS foto_coletada=false no JSON:")
            for a in flag_sem_flag:
                print(f"      • {a['rm_estudante']} — {a.get('nome_completo','?')}")
                print(f"        → Atualize no JSON: \"foto_coletada\": true")
            print()

        if imgs_orfas:
            print(f"  ❓  [{len(imgs_orfas)}] Imagens sem aluno correspondente no JSON:")
            for rm in sorted(imgs_orfas):
                print(f"      • images/{rm}.jpg")
            print()

    if not modo_resumo:
        # Pastas de turma
        if pastas_turma:
            print(f"  {SEP}")
            print("  Pastas de turma organizadas:")
            for nome_pasta, imgs in sorted(pastas_turma.items()):
                print(f"      📁 {nome_pasta}/  ({len(imgs)} foto(s))")
            print()

    # Estatísticas por turma
    print(f"  {SEP}")
    print("  Cobertura por turma:")
    print(f"  {SEP}")
    print(f"  {'Turma':<28} {'Total':>6} {'c/Foto':>7} {'OK':>5} {'%':>5}")
    print(f"  {SEP}")

    total_g = com_g = ok_g = 0
    for key in sorted(turma_stats.keys()):
        s   = turma_stats[key]
        pct = round(s["img_ok"] / s["total"] * 100) if s["total"] > 0 else 0
        ico = "✅" if pct >= 90 else ("⚠️ " if pct >= 50 else "❌")
        lbl = f"{key[0]} {key[1]} — {key[2]}"
        print(f"  {ico} {lbl:<25} {s['total']:>6} {s['com_foto']:>7} {s['img_ok']:>5} {pct:>4}%")
        total_g += s["total"]; com_g += s["com_foto"]; ok_g += s["img_ok"]

    print(f"  {SEP}")
    pct_g = round(ok_g / total_g * 100) if total_g > 0 else 0
    print(f"  {'TOTAL':<28} {total_g:>6} {com_g:>7} {ok_g:>5} {pct_g:>4}%")
    print(f"  {SEP}\n")

    if not modo_resumo and sem_foto:
        print(f"  📋  [{len(sem_foto)}] Alunos sem foto (foto_coletada=false):")
        for a in sorted(sem_foto, key=lambda x: (x.get("serie",""), x.get("turma",""), x.get("nome_completo",""))):
            print(f"      • {a['rm_estudante']} — {a.get('nome_completo','?')} ({a.get('serie','')} {a.get('turma','')} {a.get('turno','')})")
        print()


if __name__ == "__main__":
    main()
