#!/usr/bin/env python3
"""
gerenciar_usuarios.py
Carômetro Escolar — SESI 407

Gerencia os usuários de acesso em data/config.json.

Uso (modo interativo):
    python3 scripts/gerenciar_usuarios.py

Uso (modo direto):
    python3 scripts/gerenciar_usuarios.py --listar
    python3 scripts/gerenciar_usuarios.py --adicionar
    python3 scripts/gerenciar_usuarios.py --alterar-senha  <usuario>
    python3 scripts/gerenciar_usuarios.py --remover        <usuario>
    python3 scripts/gerenciar_usuarios.py --ativar-login
    python3 scripts/gerenciar_usuarios.py --desativar-login
    python3 scripts/gerenciar_usuarios.py --verificar-senha <usuario>
"""

from __future__ import annotations

import getpass
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE        = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE / "data" / "config.json"

SEP  = "─" * 58
SEP2 = "═" * 58

# ── Config padrão (se o arquivo não existir) ───────────────────
CONFIG_DEFAULT: dict = {
    "app": {
        "nome":       "Carômetro Escolar",
        "subtitulo":  "Centro Educacional SESI 407",
        "escola":     "SESI 407",
        "cidade":     "São José do Rio Preto — SP",
        "ano_letivo": str(datetime.now().year),
    },
    "auth": {
        "habilitado": True,
        "usuarios":   [],
    },
    "series_ordem": [
        "6º Ano", "7º Ano", "8º Ano", "9º Ano",
        "1º EM", "2º EM", "3º EM",
    ],
}

# ── Hash ───────────────────────────────────────────────────────
def sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).digest().hex()

# ── Carregar / salvar config ───────────────────────────────────
def carregar_config() -> dict:
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return json.loads(json.dumps(CONFIG_DEFAULT))

def salvar_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def usuarios(cfg: dict) -> list[dict]:
    return cfg.setdefault("auth", {}).setdefault("usuarios", [])

# ── Validações ─────────────────────────────────────────────────
def validar_usuario(nome: str) -> str | None:
    if not nome:
        return "Nome de usuário não pode ser vazio."
    if len(nome) < 3:
        return "Nome de usuário deve ter pelo menos 3 caracteres."
    if not re.fullmatch(r"[a-z0-9_.@\-]+", nome.lower()):
        return "Use apenas letras, números, '.', '_', '-', '@'."
    return None

def validar_senha(senha: str) -> str | None:
    if len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres."
    return None

def encontrar_usuario(cfg: dict, nome: str) -> dict | None:
    return next((u for u in usuarios(cfg) if u["usuario"].lower() == nome.lower()), None)

# ── Exibição ───────────────────────────────────────────────────
def cabecalho(titulo: str) -> None:
    print(f"\n{SEP2}")
    print(f"  Carômetro Escolar — {titulo}")
    print(SEP2)

def print_usuarios(cfg: dict) -> None:
    lista = usuarios(cfg)
    auth  = cfg.get("auth", {})
    login_status = "✅  Ativado" if auth.get("habilitado", True) else "❌  Desativado"

    cabecalho("Gerenciamento de Usuários")
    print(f"  Login:  {login_status}")
    print(f"  Total:  {len(lista)} usuário(s)")
    print()

    if not lista:
        print("  ℹ️   Nenhum usuário cadastrado.")
        return

    print(f"  {'#':<4} {'Usuário':<22} {'Nome de Exibição':<28} {'Perfil':<10}")
    print(f"  {SEP}")
    for i, u in enumerate(lista, 1):
        perfil_icon = "🔴" if u.get("perfil") == "admin" else "🔵"
        print(f"  {i:<4} {u['usuario']:<22} {u.get('nome','—'):<28} {perfil_icon} {u.get('perfil','viewer')}")
    print()

# ── Ações ──────────────────────────────────────────────────────
def acao_listar() -> None:
    cfg = carregar_config()
    print_usuarios(cfg)

def acao_adicionar(interativo: bool = True) -> None:
    cabecalho("Adicionar Usuário")
    cfg = carregar_config()

    # Usuário
    while True:
        nome = input("  Usuário (login): ").strip().lower()
        erro = validar_usuario(nome)
        if erro:
            print(f"  ❌  {erro}")
            continue
        if encontrar_usuario(cfg, nome):
            print(f"  ❌  Usuário '{nome}' já existe. Use --alterar-senha para mudar a senha.")
            continue
        break

    # Nome de exibição
    nome_exibicao = input("  Nome de exibição (ex: Prof. João Silva): ").strip()
    if not nome_exibicao:
        nome_exibicao = nome.capitalize()

    # Perfil
    print("  Perfil:")
    print("    1 → viewer  (visualizador — padrão)")
    print("    2 → admin   (exibe como Administrador)")
    escolha = input("  Escolha [1/2, padrão=1]: ").strip()
    perfil = "admin" if escolha == "2" else "viewer"

    # Senha
    while True:
        senha = getpass.getpass("  Senha (não aparece ao digitar): ")
        erro  = validar_senha(senha)
        if erro:
            print(f"  ❌  {erro}")
            continue
        confirma = getpass.getpass("  Confirmar senha: ")
        if senha != confirma:
            print("  ❌  Senhas não conferem. Tente novamente.")
            continue
        break

    novo = {
        "usuario":    nome,
        "senha_hash": sha256(senha),
        "nome":       nome_exibicao,
        "perfil":     perfil,
    }
    usuarios(cfg).append(novo)
    salvar_config(cfg)

    print(f"\n  ✅  Usuário '{nome}' adicionado com sucesso!")
    print(f"      Perfil : {perfil}")
    print(f"      Nome   : {nome_exibicao}\n")

def acao_alterar_senha(nome_arg: str | None = None) -> None:
    cabecalho("Alterar Senha")
    cfg = carregar_config()

    if not usuarios(cfg):
        print("  ℹ️   Nenhum usuário cadastrado.\n")
        return

    if nome_arg:
        nome = nome_arg.lower()
    else:
        print_usuarios(cfg)
        nome = input("  Usuário para alterar senha: ").strip().lower()

    usuario = encontrar_usuario(cfg, nome)
    if not usuario:
        print(f"  ❌  Usuário '{nome}' não encontrado.\n")
        return

    # Confirmar senha atual
    atual = getpass.getpass("  Senha atual (Enter para pular verificação): ")
    if atual and sha256(atual) != usuario.get("senha_hash", ""):
        print("  ❌  Senha atual incorreta.\n")
        return

    while True:
        nova   = getpass.getpass("  Nova senha: ")
        erro   = validar_senha(nova)
        if erro:
            print(f"  ❌  {erro}")
            continue
        confirma = getpass.getpass("  Confirmar nova senha: ")
        if nova != confirma:
            print("  ❌  Senhas não conferem.")
            continue
        break

    usuario["senha_hash"] = sha256(nova)
    salvar_config(cfg)
    print(f"\n  ✅  Senha de '{nome}' alterada com sucesso!\n")

def acao_remover(nome_arg: str | None = None) -> None:
    cabecalho("Remover Usuário")
    cfg = carregar_config()

    if not usuarios(cfg):
        print("  ℹ️   Nenhum usuário cadastrado.\n")
        return

    if nome_arg:
        nome = nome_arg.lower()
    else:
        print_usuarios(cfg)
        nome = input("  Usuário a remover: ").strip().lower()

    usuario = encontrar_usuario(cfg, nome)
    if not usuario:
        print(f"  ❌  Usuário '{nome}' não encontrado.\n")
        return

    confirmacao = input(f"  Confirmar remoção de '{nome}'? [s/N]: ").strip().lower()
    if confirmacao not in ("s", "sim", "y", "yes"):
        print("  ↩️  Operação cancelada.\n")
        return

    cfg["auth"]["usuarios"] = [u for u in usuarios(cfg) if u["usuario"].lower() != nome]
    salvar_config(cfg)
    print(f"\n  ✅  Usuário '{nome}' removido.\n")

def acao_toggle_login(ativar: bool) -> None:
    cfg = carregar_config()
    cfg.setdefault("auth", {})["habilitado"] = ativar
    salvar_config(cfg)
    estado = "ativado" if ativar else "desativado"
    icone  = "✅" if ativar else "❌"
    print(f"\n  {icone}  Login {estado} no config.json\n")

def acao_verificar_senha(nome_arg: str | None = None) -> None:
    cabecalho("Verificar Senha")
    cfg = carregar_config()

    if nome_arg:
        nome = nome_arg.lower()
    else:
        nome = input("  Usuário: ").strip().lower()

    usuario = encontrar_usuario(cfg, nome)
    if not usuario:
        print(f"  ❌  Usuário '{nome}' não encontrado.\n")
        return

    senha = getpass.getpass("  Senha a verificar: ")
    if sha256(senha) == usuario.get("senha_hash", ""):
        print(f"\n  ✅  Senha correta para o usuário '{nome}'.\n")
    else:
        print(f"\n  ❌  Senha incorreta para o usuário '{nome}'.\n")

def acao_editar_app() -> None:
    cabecalho("Configurações da Escola")
    cfg = carregar_config()
    app = cfg.setdefault("app", {})

    campos = [
        ("nome",       "Nome da aplicação",  app.get("nome", "Carômetro Escolar")),
        ("subtitulo",  "Subtítulo",          app.get("subtitulo", "Centro Educacional SESI 407")),
        ("escola",     "Nome da escola",     app.get("escola", "SESI 407")),
        ("cidade",     "Cidade/Estado",      app.get("cidade", "São José do Rio Preto — SP")),
        ("ano_letivo", "Ano letivo",         app.get("ano_letivo", str(datetime.now().year))),
    ]

    print("  Pressione Enter para manter o valor atual.\n")
    for chave, label, atual in campos:
        novo = input(f"  {label} [{atual}]: ").strip()
        app[chave] = novo if novo else atual

    salvar_config(cfg)
    print("\n  ✅  Configurações da escola atualizadas.\n")

# ── Menu interativo ────────────────────────────────────────────
def menu_interativo() -> None:
    while True:
        cfg = carregar_config()
        print_usuarios(cfg)
        print("  Opções:")
        print("    1 → Adicionar usuário")
        print("    2 → Alterar senha")
        print("    3 → Remover usuário")
        print("    4 → Verificar senha")
        print("    5 → Ativar/Desativar login")
        print("    6 → Configurações da escola")
        print("    0 → Sair")
        print()
        op = input("  Escolha: ").strip()
        print()

        if   op == "1": acao_adicionar()
        elif op == "2": acao_alterar_senha()
        elif op == "3": acao_remover()
        elif op == "4": acao_verificar_senha()
        elif op == "5":
            atual = cfg.get("auth", {}).get("habilitado", True)
            acao_toggle_login(not atual)
        elif op == "6": acao_editar_app()
        elif op == "0":
            print("  Até logo!\n")
            break
        else:
            print("  ❌  Opção inválida.\n")

# ── Entry point ────────────────────────────────────────────────
def main() -> None:
    args = sys.argv[1:]

    if not args:
        menu_interativo()
        return

    cmd = args[0].lower()
    arg2 = args[1] if len(args) > 1 else None

    if   cmd in ("--listar",          "-l"):  acao_listar()
    elif cmd in ("--adicionar",       "-a"):  acao_adicionar()
    elif cmd in ("--alterar-senha",   "-s"):  acao_alterar_senha(arg2)
    elif cmd in ("--remover",         "-r"):  acao_remover(arg2)
    elif cmd in ("--ativar-login",):          acao_toggle_login(True)
    elif cmd in ("--desativar-login",):       acao_toggle_login(False)
    elif cmd in ("--verificar-senha", "-v"):  acao_verificar_senha(arg2)
    elif cmd in ("--config-escola",   "-c"):  acao_editar_app()
    else:
        print(f"\n  ❌  Comando desconhecido: {cmd}")
        print("      Use --listar, --adicionar, --alterar-senha <usuario>,")
        print("          --remover <usuario>, --ativar-login, --desativar-login\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
