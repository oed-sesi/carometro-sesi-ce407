#!/usr/bin/env python3
"""
atualizar_foto_status.py
Carômetro Escolar — SESI 407

Sincroniza automaticamente o campo foto_coletada no alunos.json
com base nas imagens presentes na pasta images/.

  - Se images/<rm>.jpg existe → foto_coletada = true
  - Se images/<rm>.jpg não existe → foto_coletada = false (apenas se --limpar)

Uso:
    python3 scripts/atualizar_foto_status.py          (ativa quem tem foto)
    python3 scripts/atualizar_foto_status.py --limpar (também desativa quem não tem)
    python3 scripts/atualizar_foto_status.py --dry-run (simula sem salvar)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE       = Path(__file__).resolve().parent.parent
JSON_PATH  = BASE / "data" / "alunos.json"
IMAGES_DIR = BASE / "images"
EXTENSOES  = {".jpg", ".jpeg", ".png", ".webp"}

SEP = "─" * 55


def main() -> None:
    limpar  = "--limpar"  in sys.argv
    dry_run = "--dry-run" in sys.argv

    if not JSON_PATH.is_file():
        print(f"\n❌  {JSON_PATH} não encontrado.\n")
        sys.exit(1)

    with open(JSON_PATH, encoding="utf-8") as f:
        alunos = json.load(f)

    # Normalizar campo legado
    for a in alunos:
        if "rm_estudante" not in a:
            a["rm_estudante"] = a.get("matricula", "")

    # Imagens existentes
    imgs = set()
    if IMAGES_DIR.is_dir():
        imgs = {f.stem for f in IMAGES_DIR.iterdir()
                if f.is_file() and f.suffix.lower() in EXTENSOES}

    ativados    = 0
    desativados = 0
    sem_mudanca = 0

    for a in alunos:
        rm       = a["rm_estudante"]
        tem_foto = rm in imgs
        atual    = a.get("foto_coletada", False)

        if tem_foto and not atual:
            if not dry_run:
                a["foto_coletada"] = True
            ativados += 1
        elif not tem_foto and atual and limpar:
            if not dry_run:
                a["foto_coletada"] = False
            desativados += 1
        else:
            sem_mudanca += 1

    if not dry_run and (ativados or desativados):
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(alunos, f, ensure_ascii=False, indent=2)

    modo = "[DRY-RUN] " if dry_run else ""
    print(f"\n  {SEP}")
    print(f"  {modo}Carômetro Escolar — Atualizar Status de Fotos")
    print(f"  {SEP}")
    print(f"  Total de alunos      : {len(alunos)}")
    print(f"  Imagens em images/   : {len(imgs)}")
    print(f"  ✅  Ativados          : {ativados}")
    print(f"  ❌  Desativados       : {desativados}  {'(use --limpar para ativar)' if not limpar else ''}")
    print(f"  ➖  Sem mudança        : {sem_mudanca}")
    if dry_run:
        print(f"\n  ℹ️   Modo simulação — nenhuma alteração salva.")
    elif ativados or desativados:
        print(f"\n  💾  JSON atualizado: {JSON_PATH}")
    print(f"  {SEP}\n")


if __name__ == "__main__":
    main()
