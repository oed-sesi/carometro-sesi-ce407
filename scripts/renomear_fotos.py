#!/usr/bin/env python3
"""
renomear_fotos.py
Renomeia fotos de alunos para o padrão <matricula>.jpg

Problema que resolve:
    Você tem fotos nomeadas como "Ana Clara.jpg", "123456_Ana.png", etc.
    Este script as renomeia para "123456.jpg" (padrão do sistema).

Uso:
    python3 scripts/renomear_fotos.py --pasta <pasta_origem> [--destino <pasta_destino>]

Exemplos:
    # Renomear na mesma pasta (cuidado: sobrescreve)
    python3 scripts/renomear_fotos.py --pasta fotos_originais/

    # Mover para pasta images/ já renomeadas
    python3 scripts/renomear_fotos.py --pasta fotos_originais/ --destino images/

O script usa o arquivo data/alunos.json para encontrar a matrícula pelo nome.
A busca é por nome parcial (ignora acentos e maiúsculas).

Também aceita arquivos já nomeados com matrícula:
    123456.jpg, 123456.png, 123456.jpeg → copiado como 123456.jpg
"""
import argparse
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "alunos.json")


def normalizar(texto: str) -> str:
    """Remove acentos e converte para minúsculas."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def carregar_alunos():
    path = os.path.normpath(JSON_PATH)
    if not os.path.isfile(path):
        print(f"❌  Arquivo não encontrado: {path}")
        return {}
    with open(path, encoding="utf-8") as f:
        alunos = json.load(f)
    return {normalizar(a["nome_completo"]): a["matricula"] for a in alunos}


def encontrar_matricula(nome_arquivo: str, alunos_por_nome: dict) -> str | None:
    """Tenta encontrar matrícula a partir do nome do arquivo."""
    stem = Path(nome_arquivo).stem

    # Já é uma matrícula numérica?
    if re.fullmatch(r"\d{4,10}", stem):
        return stem

    # Busca parcial por nome
    stem_norm = normalizar(stem)
    for nome_norm, mat in alunos_por_nome.items():
        if stem_norm in nome_norm or nome_norm in stem_norm:
            return mat

    # Busca por palavras (2 ou mais palavras em comum)
    palavras_stem = set(stem_norm.split())
    melhor = None
    melhor_score = 0
    for nome_norm, mat in alunos_por_nome.items():
        palavras_nome = set(nome_norm.split())
        score = len(palavras_stem & palavras_nome)
        if score >= 2 and score > melhor_score:
            melhor_score = score
            melhor = mat

    return melhor


def main():
    parser = argparse.ArgumentParser(description="Renomeia fotos de alunos para <matricula>.jpg")
    parser.add_argument("--pasta",   required=True, help="Pasta com as fotos originais")
    parser.add_argument("--destino", default=None,  help="Pasta destino (padrão: images/)")
    args = parser.parse_args()

    pasta = Path(args.pasta)
    destino = Path(args.destino) if args.destino else Path(os.path.join(os.path.dirname(__file__), "..", "images"))
    destino = destino.resolve()
    destino.mkdir(parents=True, exist_ok=True)

    if not pasta.is_dir():
        print(f"❌  Pasta não encontrada: {pasta}")
        return

    alunos = carregar_alunos()
    if not alunos:
        return

    arquivos = [f for f in pasta.iterdir()
                if f.is_file() and f.suffix.lower() in EXTENSOES]

    print(f"\n{'─'*55}")
    print("  Carômetro Escolar — Renomeador de Fotos")
    print(f"{'─'*55}")
    print(f"  Pasta de origem : {pasta}")
    print(f"  Pasta destino   : {destino}")
    print(f"  Fotos encontradas: {len(arquivos)}")
    print(f"{'─'*55}\n")

    renomeados = 0
    nao_encontrados = []

    for arquivo in sorted(arquivos):
        mat = encontrar_matricula(arquivo.name, alunos)
        if mat:
            dest_file = destino / f"{mat}.jpg"
            shutil.copy2(arquivo, dest_file)
            print(f"  ✅  {arquivo.name:40s} → {mat}.jpg")
            renomeados += 1
        else:
            print(f"  ❓  {arquivo.name:40s} → matrícula não encontrada")
            nao_encontrados.append(arquivo.name)

    print(f"\n{'─'*55}")
    print(f"  ✅  Renomeados    : {renomeados}")
    print(f"  ❓  Não encontrados: {len(nao_encontrados)}")
    print(f"{'─'*55}")

    if nao_encontrados:
        print("\n  Arquivos não identificados:")
        for f in nao_encontrados:
            print(f"    • {f}")
        print("\n  Dica: renomeie manualmente como <matricula>.jpg e")
        print("        copie para a pasta images/")
    print()


if __name__ == "__main__":
    main()
