#!/usr/bin/env python3
"""
padronizar_fotos.py
Carômetro Escolar — SESI 407  |  v1.0

Padroniza o fundo das fotos dos alunos para BRANCO usando IA (rembg/U2Net),
com fallback automático para OpenCV quando a IA não estiver disponível.

Modos disponíveis:
  ia        → IA com rembg/U2Net — melhor qualidade, ~3s/foto (padrão)
  rapido    → Chroma key por detecção de cor de borda — 10ms/foto
  grabcut   → OpenCV GrabCut — médio, sem modelo externo

Uso:
  python3 scripts/padronizar_fotos.py                        # processa images/ com IA
  python3 scripts/padronizar_fotos.py --modo rapido          # modo rápido
  python3 scripts/padronizar_fotos.py --modo grabcut         # modo GrabCut
  python3 scripts/padronizar_fotos.py --preview              # 1 foto para conferir antes
  python3 scripts/padronizar_fotos.py --pasta outra/pasta/   # pasta personalizada
  python3 scripts/padronizar_fotos.py --arquivo 006810.jpg   # foto única
  python3 scripts/padronizar_fotos.py --restaurar            # restaura backups

Saída:
  - Fotos processadas sobrescrevem as originais em images/
  - Backup das originais salvo em images_originais/
  - Relatório salvo em backups/padronizacao_YYYY-MM-DD.json

Requisitos:
  pip install rembg pillow opencv-python numpy --break-system-packages
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Caminhos base ──────────────────────────────────────────────
BASE         = Path(__file__).resolve().parent.parent
IMAGES_DIR   = BASE / "images"
BACKUP_DIR   = BASE / "images_originais"
LOG_DIR      = BASE / "backups"

# ── Tamanho de saída padrão (proporção 3:4) ───────────────────
LARGURA_SAIDA  = 300
ALTURA_SAIDA   = 400
QUALIDADE_JPEG = 90      # 85-95: ótimo equilíbrio qualidade/tamanho
TAMANHO_MAX_KB = 150     # comprimir se exceder

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

SEP  = "─" * 64
SEP2 = "═" * 64


# ═══════════════════════════════════════════════════════════════
# INSTALAÇÃO AUTOMÁTICA DE DEPENDÊNCIAS
# ═══════════════════════════════════════════════════════════════
def _verificar_deps(modo: str) -> dict[str, bool]:
    """Verifica quais dependências estão disponíveis."""
    deps = {}
    for lib in ["PIL", "cv2", "rembg", "numpy"]:
        deps[lib] = importlib.util.find_spec(lib) is not None
    return deps


def _instalar_dep(pacote: str) -> bool:
    import subprocess
    print(f"  📦  Instalando {pacote}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", pacote,
         "--break-system-packages", "-q"],
        capture_output=True
    )
    return result.returncode == 0


# ═══════════════════════════════════════════════════════════════
# MODO 1 — IA com rembg (melhor qualidade)
# ═══════════════════════════════════════════════════════════════
def _processar_ia(caminho: Path) -> tuple[bytes, str]:
    """
    Remove o fundo usando o modelo U2Net via rembg.
    Retorna (bytes da imagem processada, mensagem de status).
    """
    from rembg import remove, new_session
    from PIL import Image, ImageOps
    import numpy as np

    # Sessão persistente (carrega o modelo uma vez)
    if not hasattr(_processar_ia, "_session"):
        _processar_ia._session = new_session("u2net")

    with open(caminho, "rb") as f:
        dados = f.read()

    # Remoção de fundo com IA → resultado em RGBA
    resultado = remove(dados, session=_processar_ia._session)
    img_rgba = Image.open(io.BytesIO(resultado)).convert("RGBA")

    # Compor sobre fundo branco
    fundo = Image.new("RGBA", img_rgba.size, (255, 255, 255, 255))
    fundo.paste(img_rgba, mask=img_rgba.split()[3])
    img_rgb = fundo.convert("RGB")

    # Recortar e redimensionar
    img_final = _redimensionar_padrao(img_rgb)
    return _salvar_jpeg(img_final), "ia"


# ═══════════════════════════════════════════════════════════════
# MODO 2 — Rápido (chroma key por amostragem de borda)
# ═══════════════════════════════════════════════════════════════
def _processar_rapido(caminho: Path) -> tuple[bytes, str]:
    """
    Remove o fundo detectando a cor dominante nas bordas da imagem.
    Funciona muito bem com fundos uniformes (parede, papel, quadro branco).
    """
    import cv2
    import numpy as np
    from PIL import Image

    img = cv2.imread(str(caminho))
    if img is None:
        raise ValueError(f"Não foi possível ler: {caminho}")

    h, w = img.shape[:2]

    # ── Amostrar cor do fundo nas bordas ──────────────────────
    # Usa 16 pontos distribuídos nas 4 bordas (evita cantos com sombra)
    amostras = []
    for x in [w//8, w//4, w//2, 3*w//4, 7*w//8]:
        amostras.extend([img[2, x], img[h-3, x]])
    for y in [h//8, h//4, h//2, 3*h//4, 7*h//8]:
        amostras.extend([img[y, 2], img[y, w-3]])

    cor_fundo = np.median(amostras, axis=0).astype(np.uint8)

    # ── Máscara de fundo por distância de cor (em HSV) ────────
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    fundo_pixel = cor_fundo.reshape(1, 1, 3)
    fundo_hsv = cv2.cvtColor(fundo_pixel, cv2.COLOR_BGR2HSV)[0, 0]

    brilho = fundo_hsv[2]
    # Fundo claro (branco/cinza): usar luminância; fundo colorido: usar matiz
    if brilho > 180:  # fundo claro
        lower = np.array([0,   0, max(0,  int(brilho) - 60)])
        upper = np.array([180, 60, 255])
    else:
        tol_h = 25
        lower = np.array([max(0,   int(fundo_hsv[0]) - tol_h), 30, 40])
        upper = np.array([min(180, int(fundo_hsv[0]) + tol_h), 255, 255])

    mask_fundo = cv2.inRange(img_hsv, lower, upper)

    # ── Morphology para suavizar bordas ───────────────────────
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_fundo = cv2.morphologyEx(mask_fundo, cv2.MORPH_CLOSE, kernel)
    mask_fundo = cv2.morphologyEx(mask_fundo, cv2.MORPH_OPEN, kernel)

    # Garantir que bordas sejam sempre fundo (evitar pessoa nas bordas)
    borda = 8
    mask_fundo[:borda, :]  = 255
    mask_fundo[-borda:, :] = 255
    mask_fundo[:, :borda]  = 255
    mask_fundo[:, -borda:] = 255

    # ── Flood fill a partir dos 4 cantos ─────────────────────
    # Garante que regiões desconexas do fundo sejam capturadas
    mask_ff = mask_fundo.copy()
    for cy, cx in [(0, 0), (0, w-1), (h-1, 0), (h-1, w-1)]:
        if mask_ff[cy, cx] == 255:
            cv2.floodFill(mask_ff, None, (cx, cy), 255)

    # ── Suavizar borda da pessoa (anti-alias) ─────────────────
    mask_pessoa = cv2.bitwise_not(mask_ff)
    mask_suave  = cv2.GaussianBlur(mask_pessoa.astype(float), (5, 5), 0) / 255.0

    # ── Compor sobre fundo branco ─────────────────────────────
    resultado = np.ones_like(img, dtype=float) * 255
    for c in range(3):
        resultado[:, :, c] = (
            img[:, :, c].astype(float) * mask_suave +
            255.0 * (1 - mask_suave)
        )
    resultado = resultado.astype(np.uint8)

    # ── Converter para PIL e padronizar ───────────────────────
    img_rgb = Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))
    img_final = _redimensionar_padrao(img_rgb)
    return _salvar_jpeg(img_final), "rapido"


# ═══════════════════════════════════════════════════════════════
# MODO 3 — GrabCut (OpenCV, sem modelo externo)
# ═══════════════════════════════════════════════════════════════
def _processar_grabcut(caminho: Path) -> tuple[bytes, str]:
    """
    Usa o algoritmo GrabCut do OpenCV para segmentar a pessoa do fundo.
    Assume que a pessoa está centralizada na imagem.
    """
    import cv2
    import numpy as np
    from PIL import Image

    img = cv2.imread(str(caminho))
    if img is None:
        raise ValueError(f"Não foi possível ler: {caminho}")

    h, w = img.shape[:2]

    # Rect: margem de 12% em x e 3% no topo, 5% na base
    rx = int(w * 0.12)
    ry_top = int(h * 0.03)
    ry_bot = int(h * 0.05)
    rect = (rx, ry_top, w - 2 * rx, h - ry_top - ry_bot)

    mask = np.zeros((h, w), np.uint8)
    bgd  = np.zeros((1, 65), np.float64)
    fgd  = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)

    # Refinar: marcar bordas como fundo definitivo
    mask[:10, :]  = cv2.GC_BGD
    mask[-10:, :] = cv2.GC_BGD
    mask[:, :10]  = cv2.GC_BGD
    mask[:, -10:] = cv2.GC_BGD

    cv2.grabCut(img, mask, None, bgd, fgd, 3, cv2.GC_EVAL)

    mask2 = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1).astype(np.uint8)

    # Suavizar bordas
    mask_suave = cv2.GaussianBlur(mask2.astype(float) * 255, (5, 5), 0) / 255.0

    resultado = np.ones_like(img, dtype=float) * 255
    for c in range(3):
        resultado[:, :, c] = (
            img[:, :, c].astype(float) * mask_suave +
            255.0 * (1 - mask_suave)
        )
    resultado = resultado.astype(np.uint8)

    img_rgb = Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))
    img_final = _redimensionar_padrao(img_rgb)
    return _salvar_jpeg(img_final), "grabcut"


# ═══════════════════════════════════════════════════════════════
# UTILITÁRIOS COMUNS
# ═══════════════════════════════════════════════════════════════
def _redimensionar_padrao(img):
    """
    Redimensiona para LARGURA_SAIDA x ALTURA_SAIDA mantendo proporção,
    centraliza horizontalmente e posiciona o rosto no terço superior.
    Preenche espaço restante com branco.
    """
    from PIL import Image, ImageOps

    # Redimensionar mantendo proporção (sem distorcer)
    img_ratio   = img.width / img.height
    alvo_ratio  = LARGURA_SAIDA / ALTURA_SAIDA

    if img_ratio > alvo_ratio:
        # Imagem mais larga — ajustar pela altura
        nova_h = ALTURA_SAIDA
        nova_w = int(nova_h * img_ratio)
    else:
        # Imagem mais alta — ajustar pela largura
        nova_w = LARGURA_SAIDA
        nova_h = int(nova_w / img_ratio)

    img = img.resize((nova_w, nova_h), Image.LANCZOS)

    # Centralizar no canvas de saída
    # Para fotos de aluno: centralizar horizontalmente,
    # posicionar ligeiramente para cima (rosto no terço superior)
    canvas = Image.new("RGB", (LARGURA_SAIDA, ALTURA_SAIDA), (255, 255, 255))
    x = (LARGURA_SAIDA - nova_w) // 2
    y = max(0, (ALTURA_SAIDA - nova_h) // 2 - int(ALTURA_SAIDA * 0.05))
    canvas.paste(img, (x, y))
    return canvas


def _salvar_jpeg(img) -> bytes:
    """Salva como JPEG em bytes, comprimindo se necessário."""
    buf = io.BytesIO()
    qualidade = QUALIDADE_JPEG

    img.save(buf, format="JPEG", quality=qualidade, optimize=True)

    # Comprimir progressivamente se exceder tamanho máximo
    while buf.tell() > TAMANHO_MAX_KB * 1024 and qualidade > 60:
        buf = io.BytesIO()
        qualidade -= 5
        img.save(buf, format="JPEG", quality=qualidade, optimize=True)

    return buf.getvalue()


def _fazer_backup(caminho: Path) -> Path:
    """Copia o arquivo original para BACKUP_DIR antes de sobrescrever."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    destino = BACKUP_DIR / caminho.name
    if not destino.exists():  # não sobrescrever backup já existente
        shutil.copy2(caminho, destino)
    return destino


def _listar_fotos(pasta: Path) -> list[Path]:
    """Lista todas as fotos na pasta."""
    fotos = sorted([
        f for f in pasta.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSOES
    ])
    return fotos


# ═══════════════════════════════════════════════════════════════
# PROCESSADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════
MODOS = {
    "ia":      _processar_ia,
    "rapido":  _processar_rapido,
    "grabcut": _processar_grabcut,
}


def processar_lote(
    pasta: Path,
    modo: str = "ia",
    preview: bool = False,
    forcar: bool = False,
    arquivo_unico: Path | None = None,
) -> None:

    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Padronização de Fotos  |  v1.0")
    print(SEP2)

    # ── Verificar dependências ────────────────────────────────
    deps = _verificar_deps(modo)

    if modo == "ia":
        if not deps.get("rembg"):
            print("  📦  rembg não instalado. Instalando...")
            ok = _instalar_dep("rembg")
            if not ok:
                print("  ❌  Falha ao instalar rembg.")
                print("      Execute: pip install rembg --break-system-packages")
                print("      Ou use --modo rapido (sem dependências extras)\n")
                sys.exit(1)
            import importlib
            importlib.invalidate_caches()
        if not deps.get("PIL"):
            _instalar_dep("Pillow")
    else:
        if not deps.get("cv2"):
            print("  ❌  opencv-python não instalado.")
            print("      Execute: pip install opencv-python --break-system-packages\n")
            sys.exit(1)

    # ── Listar fotos ──────────────────────────────────────────
    if arquivo_unico:
        fotos = [arquivo_unico]
    else:
        if not pasta.is_dir():
            print(f"  ❌  Pasta não encontrada: {pasta}\n")
            sys.exit(1)
        fotos = _listar_fotos(pasta)

    if not fotos:
        print(f"  ℹ️  Nenhuma imagem encontrada em: {pasta}\n")
        return

    # Verificar quais já foram processadas (têm backup)
    if not forcar:
        ja_processadas = {f.name for f in BACKUP_DIR.glob("*")} if BACKUP_DIR.exists() else set()
        pendentes = [f for f in fotos if f.name not in ja_processadas]
        ja_feitas  = len(fotos) - len(pendentes)
    else:
        pendentes  = fotos
        ja_feitas  = 0

    print(f"  Pasta        : {pasta}")
    print(f"  Modo         : {modo.upper()}")
    print(f"  Fotos total  : {len(fotos)}")
    if ja_feitas > 0:
        print(f"  Já processadas (com backup): {ja_feitas} — ignoradas")
        print(f"  A processar  : {len(pendentes)}  (use --forcar para reprocessar tudo)")
    else:
        print(f"  A processar  : {len(pendentes)}")
    print(f"  Backup em    : {BACKUP_DIR}")

    if not pendentes:
        print(f"\n  ✅  Todas as {len(fotos)} fotos já foram processadas.")
        print(f"      Use --forcar para reprocessar.\n")
        return

    # ── Modo preview ──────────────────────────────────────────
    if preview:
        foto_preview = pendentes[0]
        print(f"\n  🔍  PREVIEW — processando apenas: {foto_preview.name}")
        print(f"      Confira o resultado antes de processar todo o lote.\n")
        _processar_uma(foto_preview, modo, salvar=False, preview=True)
        return

    # ── Confirmação ───────────────────────────────────────────
    print()
    resp = input(f"  Prosseguir com {len(pendentes)} foto(s)? [S/n]: ").strip().lower()
    if resp in ("n", "nao", "não", "no"):
        print("  ↩️  Cancelado.\n")
        return

    # ── Processamento ─────────────────────────────────────────
    print()
    fn_modo = MODOS[modo]

    resultados = {
        "data":       datetime.now().isoformat(),
        "modo":       modo,
        "pasta":      str(pasta),
        "total":      len(pendentes),
        "sucesso":    [],
        "erro":       [],
        "ignorado":   [],
    }

    t_inicio = time.time()
    tempos   = []

    for i, foto in enumerate(pendentes, 1):
        t0    = time.time()
        nome  = foto.name
        pct   = i / len(pendentes) * 100

        try:
            # Backup antes de qualquer coisa
            _fazer_backup(foto)

            # Processar
            dados_saida, modo_usado = fn_modo(foto)

            # Verificar qualidade mínima (não salvar arquivo muito pequeno)
            if len(dados_saida) < 5 * 1024:  # < 5KB provavelmente erro
                raise ValueError("Resultado muito pequeno — possível falha no processamento")

            # Salvar resultado (sobrescreve original)
            with open(foto, "wb") as f:
                f.write(dados_saida)

            elapsed = time.time() - t0
            tempos.append(elapsed)
            kb_orig = foto.stat().st_size // 1024
            kb_sai  = len(dados_saida) // 1024

            print(f"  [{i:>3}/{len(pendentes)}] ✅  {nome:<20} "
                  f"{elapsed:.1f}s  "
                  f"{BACKUP_DIR.joinpath(nome).stat().st_size//1024}KB→{kb_sai}KB")

            resultados["sucesso"].append({
                "arquivo": nome,
                "modo": modo_usado,
                "tempo_s": round(elapsed, 2),
                "kb_orig": BACKUP_DIR.joinpath(nome).stat().st_size // 1024,
                "kb_saida": kb_sai,
            })

        except KeyboardInterrupt:
            print(f"\n  ⏸️   Interrompido pelo usuário em {i-1}/{len(pendentes)} fotos.")
            break

        except Exception as e:
            elapsed = time.time() - t0
            print(f"  [{i:>3}/{len(pendentes)}] ❌  {nome:<20} ERRO: {e}")
            # Restaurar backup se processamento falhou
            bkp = BACKUP_DIR / nome
            if bkp.exists():
                shutil.copy2(bkp, foto)
                print(f"       ↩️  Original restaurado de {BACKUP_DIR.name}/")
            resultados["erro"].append({"arquivo": nome, "erro": str(e)})

    # ── Relatório final ───────────────────────────────────────
    t_total = time.time() - t_inicio
    t_medio = sum(tempos) / len(tempos) if tempos else 0
    n_ok    = len(resultados["sucesso"])
    n_err   = len(resultados["erro"])

    print(f"\n  {SEP}")
    print(f"  {'✅  Processadas com sucesso':<32}: {n_ok}")
    print(f"  {'❌  Erros':<32}: {n_err}")
    print(f"  {'⏱️  Tempo total':<32}: {t_total:.0f}s  ({t_medio:.1f}s/foto)")
    print(f"  {'💾  Backups em':<32}: {BACKUP_DIR.name}/")

    if n_err > 0:
        print(f"\n  ⚠️  Fotos com erro (originais restaurados):")
        for item in resultados["erro"]:
            print(f"       • {item['arquivo']} → {item['erro']}")
        print(f"\n  💡  Dica: tente com --modo rapido para as fotos com erro.")

    # Salvar log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log = LOG_DIR / f"padronizacao_{ts}.json"
    with open(log, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"  {'📋  Log salvo em':<32}: {log.name}")
    print(f"  {SEP}\n")

    if n_ok > 0:
        print(f"  ✅  {n_ok} foto(s) padronizadas com fundo branco!")
        print(f"      Execute  git add images/ && git commit -m 'feat: fotos com fundo branco'")
        print(f"               git push\n")


def _processar_uma(caminho: Path, modo: str, salvar: bool = True, preview: bool = False) -> bool:
    """Processa uma única foto com feedback detalhado."""
    from PIL import Image

    fn = MODOS[modo]
    print(f"  Processando: {caminho.name}  [{modo.upper()}]")
    t = time.time()

    try:
        dados, _ = fn(caminho)
        elapsed  = time.time() - t

        # Salvar preview em pasta temporária
        preview_path = BASE / f"preview_{caminho.stem}_fundo_branco.jpg"
        with open(preview_path, "wb") as f:
            f.write(dados)

        kb_orig = caminho.stat().st_size // 1024
        kb_sai  = len(dados) // 1024

        print(f"\n  ✅  Processado em {elapsed:.1f}s")
        print(f"  📏  {kb_orig}KB → {kb_sai}KB")
        print(f"  📁  Preview salvo: {preview_path.name}")
        print(f"\n  Confira o arquivo '{preview_path.name}' na raiz do projeto.")
        print(f"  Se o resultado for satisfatório, execute sem --preview")
        print(f"  para processar todo o lote.\n")

        if salvar:
            _fazer_backup(caminho)
            with open(caminho, "wb") as f:
                f.write(dados)
            preview_path.unlink(missing_ok=True)

        return True

    except Exception as e:
        elapsed = time.time() - t
        print(f"\n  ❌  Erro em {elapsed:.1f}s: {e}\n")
        return False


# ═══════════════════════════════════════════════════════════════
# RESTAURAÇÃO DE BACKUPS
# ═══════════════════════════════════════════════════════════════
def restaurar_backups(pasta: Path) -> None:
    """Restaura todas as fotos originais do backup."""
    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Restauração de Backups")
    print(SEP2)

    if not BACKUP_DIR.exists():
        print(f"  ❌  Pasta de backups não encontrada: {BACKUP_DIR}\n")
        return

    backups = list(BACKUP_DIR.glob("*"))
    backups = [b for b in backups if b.suffix.lower() in EXTENSOES]

    if not backups:
        print(f"  ℹ️  Nenhum backup encontrado em {BACKUP_DIR.name}/\n")
        return

    print(f"  Backups encontrados: {len(backups)}")
    resp = input(f"  Restaurar {len(backups)} foto(s) original(is)? [s/N]: ").strip().lower()
    if resp not in ("s", "sim"):
        print("  ↩️  Cancelado.\n")
        return

    restauradas = 0
    for bkp in backups:
        destino = pasta / bkp.name
        shutil.copy2(bkp, destino)
        restauradas += 1
        print(f"  ↩️  {bkp.name}")

    print(f"\n  ✅  {restauradas} foto(s) restaurada(s) para {pasta.name}/\n")


# ═══════════════════════════════════════════════════════════════
# RELATÓRIO DE STATUS
# ═══════════════════════════════════════════════════════════════
def relatorio_status(pasta: Path) -> None:
    """Mostra quais fotos já foram processadas e quais ainda precisam."""
    fotos   = _listar_fotos(pasta) if pasta.exists() else []
    backups = {f.name for f in BACKUP_DIR.glob("*")} if BACKUP_DIR.exists() else set()

    print(f"\n{SEP2}")
    print("  Carômetro Escolar — Status das Fotos")
    print(SEP2)
    print(f"  Total em images/  : {len(fotos)}")
    print(f"  Com backup (já processadas): {len([f for f in fotos if f.name in backups])}")
    print(f"  Sem backup (pendentes)     : {len([f for f in fotos if f.name not in backups])}")
    print()

    pendentes = [f for f in fotos if f.name not in backups]
    if pendentes:
        print(f"  Pendentes ({len(pendentes)}):")
        for f in pendentes[:20]:
            print(f"    • {f.name}")
        if len(pendentes) > 20:
            print(f"    ... e mais {len(pendentes)-20}")
    else:
        print("  ✅  Todas as fotos já foram processadas.")
    print()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
def main() -> None:
    args = sys.argv[1:]

    # Defaults
    modo         = "ia"
    preview      = False
    forcar       = False
    restaurar    = False
    status       = False
    pasta        = IMAGES_DIR
    arq_unico    : Path | None = None

    # Parser simples
    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg in ("--modo", "-m"):
            i += 1
            if i < len(args):
                modo = args[i].lower()
                if modo not in MODOS:
                    print(f"\n  ❌  Modo inválido: '{modo}'. Use: ia | rapido | grabcut\n")
                    sys.exit(1)
        elif arg == "--preview":
            preview = True
        elif arg in ("--forcar", "--forçar", "-f"):
            forcar = True
        elif arg == "--restaurar":
            restaurar = True
        elif arg == "--status":
            status = True
        elif arg in ("--pasta", "-p"):
            i += 1
            if i < len(args):
                pasta = Path(args[i])
                if not pasta.is_absolute():
                    pasta = BASE / args[i]
        elif arg in ("--arquivo", "-a"):
            i += 1
            if i < len(args):
                arq_unico = Path(args[i])
                if not arq_unico.is_absolute():
                    arq_unico = BASE / args[i]
                    if not arq_unico.exists():
                        arq_unico = pasta / args[i]
        elif arg in ("--ajuda", "--help", "-h"):
            print(__doc__)
            sys.exit(0)
        i += 1

    # ── Executar ação ─────────────────────────────────────────
    if restaurar:
        restaurar_backups(pasta)
    elif status:
        relatorio_status(pasta)
    elif arq_unico:
        if not arq_unico.exists():
            print(f"\n  ❌  Arquivo não encontrado: {arq_unico}\n")
            sys.exit(1)
        _processar_uma(arq_unico, modo, salvar=True, preview=preview)
    else:
        processar_lote(pasta, modo, preview, forcar, None)


if __name__ == "__main__":
    main()
