#!/usr/bin/env python3
"""
gerar_senha_hash.py
Gera o hash SHA-256 de uma senha para usar no data/config.json

Uso:
    python3 scripts/gerar_senha_hash.py <sua-senha>

Exemplo:
    python3 scripts/gerar_senha_hash.py minhaSenha123
"""
import hashlib
import sys


def main():
    if len(sys.argv) < 2:
        print("\n❌  Uso: python3 scripts/gerar_senha_hash.py <sua-senha>\n")
        sys.exit(1)

    senha = sys.argv[1]
    hash_hex = hashlib.sha256(senha.encode("utf-8")).hexdigest()

    sep = "─" * 53
    print(f"\n{sep}")
    print("  Carômetro Escolar — Gerador de Hash de Senha")
    print(sep)
    print(f"  Senha informada : {senha}")
    print(f"  Hash SHA-256    : {hash_hex}")
    print(sep)
    print("\n  Cole o hash acima no campo \"senha_hash\" do usuário")
    print("  em data/config.json\n")


if __name__ == "__main__":
    main()
