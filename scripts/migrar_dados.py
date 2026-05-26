#!/usr/bin/env python3
"""
migrar_dados.py
Carômetro Escolar — SESI 407  |  v5.3

Migra o arquivo data/alunos.json para a versão atual do schema,
adicionando os novos campos com valor vazio nos registros existentes.

Campos adicionados nesta versão (v5.3):
  - nu_chamada      → Número de chamada na turma
  - rg_estudante    → RG do estudante
  - uf_rg           → UF do RG
  - org_emissor_rg  → Órgão emissor do RG
  - cpf_estudante   → CPF do estudante

O script:
  1. Lê o alunos.json atual
  2. Cria backup automático em backups/
  3. Adiciona campos faltantes com valor padrão
  4. Salva o JSON atualizado mantendo todos os dados existentes

Uso:
  python3 scripts/migrar_dados.py
  python3 scripts/migrar_dados.py --dry-run   (simula sem salvar)
"""

from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

BASE        = Path(__file__).resolve().parent.parent
JSON_PATH   = BASE / "data" / "alunos.json"
BACKUP_DIR  = BASE / "backups"

SEP  = "─" * 60
SEP2 = "═" * 60

# Schema completo v5.3 com valor padrão para cada campo
SCHEMA_V53: dict[str, object] = {
    # Identificação escolar
    "matricula":        "",      # legado
    "rm_estudante":     "",
    "ra_estudante":     "",
    "nu_chamada":       "",      # NOVO
    "nome_completo":    "",
    # Turma
    "serie":            "",
    "turma":            "",
    "turno":            "",
    "status":           "Ativo",
    # Dados pessoais
    "data_nascimento":  "",
    "data_ingresso":    "",
    "email_estudante":  "",
    # Documentos — NOVOS
    "rg_estudante":     "",
    "uf_rg":            "",
    "org_emissor_rg":   "",
    "cpf_estudante":    "",
    # Responsáveis
    "mae_nome":         "",
    "mae_telefone":     "",
    "mae_email":        "",
    "pai_nome":         "",
    "pai_telefone":     "",
    "pai_email":        "",
    # Endereço / sistema
    "endereco":         "",
    "observacoes":      "",
    "termo_autorizado": False,
    "foto_coletada":    False,
    # Campos especiais
    "avisos":            [],
    "educacao_inclusiva": False,
    "diagnostico":       "",
}

CAMPOS_NOVOS = ["nu_chamada", "rg_estudante", "uf_rg", "org_emissor_rg", "cpf_estudante"]


def criar_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = BACKUP_DIR / f"carometro_pre_migracao_{ts}.zip"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(JSON_PATH, "data/alunos.json")
    return dest


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Migração de Dados  |  v5.3")
    print(SEP2)

    if not JSON_PATH.is_file():
        print(f"  ❌  Arquivo não encontrado: {JSON_PATH}\n")
        sys.exit(1)

    with open(JSON_PATH, encoding="utf-8") as f:
        alunos = json.load(f)

    print(f"  Alunos encontrados : {len(alunos)}")

    # Detectar campos já presentes
    campos_existentes = set(alunos[0].keys()) if alunos else set()
    campos_faltando   = [c for c in CAMPOS_NOVOS if c not in campos_existentes]

    if not campos_faltando:
        print(f"\n  ✅  JSON já está na versão v5.3 — nenhuma migração necessária.")
        print(f"      Campos novos já presentes: {', '.join(CAMPOS_NOVOS)}\n")
        return

    print(f"\n  Campos a adicionar:")
    for c in campos_faltando:
        print(f"       + {c}")
    print()

    # Backup antes de alterar
    if not dry_run:
        bkp = criar_backup()
        print(f"  💾  Backup criado: {bkp.name}")

    # Migrar cada aluno
    migrados = 0
    for a in alunos:
        # Garantir rm_estudante
        if "rm_estudante" not in a and "matricula" in a:
            a["rm_estudante"] = a["matricula"]

        # Adicionar campos faltantes com valor padrão
        for campo in campos_faltando:
            if campo not in a:
                a[campo] = SCHEMA_V53[campo]
                migrados += 1

    # Reordenar campos conforme SCHEMA_V53
    def reordenar(a: dict) -> dict:
        ordered = {}
        for k in SCHEMA_V53:
            ordered[k] = a.get(k, SCHEMA_V53[k])
        # Campos extras não previstos no schema (preservar)
        for k, v in a.items():
            if k not in ordered:
                ordered[k] = v
        return ordered

    alunos_migrados = [reordenar(a) for a in alunos]

    # Salvar
    if not dry_run:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(alunos_migrados, f, ensure_ascii=False, indent=2)
        print(f"  💾  JSON atualizado: {JSON_PATH}")

    print(f"\n  {SEP}")
    print(f"  {'📋  Alunos migrados':<30}: {len(alunos)}")
    print(f"  {'🆕  Campos adicionados':<30}: {len(campos_faltando)} campos × {len(alunos)} alunos = {migrados} células")
    if campos_faltando:
        for c in campos_faltando:
            print(f"       • {c}")
    if dry_run:
        print(f"\n  ℹ️  Modo simulação — nenhuma alteração salva.")
        print(f"      Execute sem --dry-run para aplicar.")
    else:
        print(f"\n  ✅  Migração concluída com sucesso!")
        print(f"      Preencha os novos campos via template ou editando o JSON.")
    print(f"  {SEP}\n")


if __name__ == "__main__":
    main()
