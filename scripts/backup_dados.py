#!/usr/bin/env python3
"""
backup_dados.py
Carômetro Escolar — SESI 407

Cria um backup compactado de data/ e images/ com timestamp.

Uso:
    python3 scripts/backup_dados.py
    python3 scripts/backup_dados.py --destino /caminho/backup/
    python3 scripts/backup_dados.py --listar
    python3 scripts/backup_dados.py --restaurar backups/carometro_backup_2025-01-01_12-00-00.zip
"""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

BASE        = Path(__file__).resolve().parent.parent
BACKUP_DIR  = BASE / "backups"
SEP         = "─" * 58

INCLUIR = ["data", "assets/img"]  # pastas incluídas no backup


def criar_backup(destino_dir: Path | None = None) -> Path:
    pasta = destino_dir or BACKUP_DIR
    pasta.mkdir(parents=True, exist_ok=True)

    ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome = f"carometro_backup_{ts}.zip"
    dest = pasta / nome

    total = 0
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for subpasta in INCLUIR:
            p = BASE / subpasta
            if not p.exists():
                continue
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    arcname = f.relative_to(BASE)
                    zf.write(f, arcname)
                    total += 1

        # Incluir images/ (sem subpastas de turma)
        img_dir = BASE / "images"
        if img_dir.is_dir():
            for f in sorted(img_dir.iterdir()):
                if f.is_file():
                    zf.write(f, f.relative_to(BASE))
                    total += 1

    tamanho = dest.stat().st_size / 1024
    print(f"\n  {SEP}")
    print("  Carômetro Escolar — Backup")
    print(f"  {SEP}")
    print(f"  ✅  Backup criado : {dest.name}")
    print(f"  📁  Destino      : {pasta}")
    print(f"  📦  Arquivos     : {total}")
    print(f"  💾  Tamanho      : {tamanho:.1f} KB")
    print(f"  {SEP}\n")
    return dest


def listar_backups() -> None:
    if not BACKUP_DIR.is_dir():
        print("\n  ℹ️   Nenhum backup encontrado.\n")
        return

    arquivos = sorted(BACKUP_DIR.glob("carometro_backup_*.zip"), reverse=True)
    print(f"\n  {SEP}")
    print("  Carômetro Escolar — Backups Disponíveis")
    print(f"  {SEP}")
    if not arquivos:
        print("  ℹ️   Nenhum backup encontrado.")
    else:
        for f in arquivos:
            ts  = f.stat().st_mtime
            dt  = datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
            kb  = f.stat().st_size / 1024
            print(f"  📦  {f.name:<45} {kb:>8.1f} KB  {dt}")
    print(f"  {SEP}\n")


def restaurar_backup(caminho_str: str) -> None:
    caminho = Path(caminho_str)
    if not caminho.is_absolute():
        caminho = BASE / caminho_str
    if not caminho.exists():
        print(f"\n  ❌  Arquivo não encontrado: {caminho}\n")
        sys.exit(1)

    confirmacao = input(
        f"\n  ⚠️  Isso sobrescreverá os dados atuais!\n"
        f"  Restaurar de '{caminho.name}'? [s/N]: "
    ).strip().lower()
    if confirmacao not in ("s", "sim"):
        print("  ↩️  Operação cancelada.\n")
        return

    with zipfile.ZipFile(caminho, "r") as zf:
        zf.extractall(BASE)

    print(f"\n  ✅  Dados restaurados de: {caminho.name}\n")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        criar_backup()
        return

    if args[0] in ("--listar", "-l"):
        listar_backups()
    elif args[0] in ("--restaurar", "-r") and len(args) > 1:
        restaurar_backup(args[1])
    elif args[0] in ("--destino", "-d") and len(args) > 1:
        criar_backup(Path(args[1]))
    else:
        print("\n  Uso:")
        print("    python3 scripts/backup_dados.py")
        print("    python3 scripts/backup_dados.py --destino /caminho/")
        print("    python3 scripts/backup_dados.py --listar")
        print("    python3 scripts/backup_dados.py --restaurar backups/arquivo.zip\n")


if __name__ == "__main__":
    main()
