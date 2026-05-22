# Carômetro Escolar — SESI 407
## Guia Completo de Configuração, Atualização e Manutenção

> **Versão:** 5.1 — Edição GitHub Pages (Frontend Estático)
> **Última revisão:** 2026
> **Ambiente:** Ubuntu 25.04 LTS via WSL2 + Windows 11 + VS Code

---

## Índice

1. [Visão Geral da Aplicação](#1-visão-geral-da-aplicação)
2. [Estrutura do Repositório](#2-estrutura-do-repositório)
3. [Configuração Inicial (uma única vez)](#3-configuração-inicial-uma-única-vez)
4. [Formato dos Dados](#4-formato-dos-dados)
5. [Scripts Utilitários — Referência Completa](#5-scripts-utilitários--referência-completa)
6. [Fluxo de Trabalho Diário](#6-fluxo-de-trabalho-diário)
7. [Operações de Manutenção](#7-operações-de-manutenção)
8. [Comandos Git de Referência](#8-comandos-git-de-referência)
9. [Solução de Problemas](#9-solução-de-problemas)
10. [Segurança](#10-segurança)
11. [Escalabilidade](#11-escalabilidade)

---

## 1. Visão Geral da Aplicação

O **Carômetro Escolar — SESI 407** é uma aplicação web 100% estática hospedada gratuitamente no GitHub Pages. Não há servidor, banco de dados, nem processo de deploy complexo.

### Como funciona

```
Navegador do usuário
        │
        ▼
  GitHub Pages (hospedagem gratuita)
        │
        ├── index.html              ← Toda a lógica da aplicação
        ├── data/alunos.json        ← Dados dos alunos
        ├── data/config.json        ← Configuração e login
        ├── images/<rm>.jpg         ← Fotos (pasta principal)
        └── images_<turma>/<rm>.jpg ← Fotos organizadas por turma
```

### Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Login** | Proteção por usuário/senha (hash SHA-256 no config.json) |
| **Dashboard** | Visão geral com estatísticas e cobertura de fotos por turma |
| **Todos os Alunos** | Grade ou tabela com busca e filtros (série, turma, turno, foto) |
| **Por Turma** | Selecionar turma → ver todos os alunos com fotos |
| **Detalhe do Aluno** | Foto + todos os dados + responsáveis + observações |
| **Dark Mode** | Alternância claro/escuro salva no navegador |
| **Mobile** | Totalmente responsivo para Android e iOS |

### Stack Técnica

- **HTML5 + CSS3 + JavaScript** puro (sem frameworks)
- **GitHub Pages** para hospedagem (gratuito)
- **JSON** para armazenamento de dados (no próprio repositório)
- **Git** para versionamento e deploy (`git push` = publicar)
- **SHA-256** do browser para hash de senhas (Web Crypto API)
- **Python 3** para scripts de manutenção locais

---

## 2. Estrutura do Repositório

```
carometro-sesi407/
│
├── index.html                    ← Aplicação principal (HTML + CSS + JS)
├── README.md                     ← Descrição do repositório
├── .gitignore                    ← Arquivos ignorados pelo Git
├── template_estudantes.csv       ← Template para importação (gerado pelo script)
├── template_estudantes.xlsx      ← Template Excel para importação (gerado pelo script)
│
├── data/
│   ├── alunos.json               ← Lista de todos os alunos (PRINCIPAL arquivo de dados)
│   └── config.json               ← Configuração da escola e usuários de acesso
│
├── images/                       ← Fotos originais dos alunos
│   ├── 006810.jpg                ← Nomeadas pelo RM do estudante
│   └── ...
│
├── images_6ano_A/                ← Fotos organizadas por turma (geradas pelo script)
├── images_6ano_B/
├── images_7ano_A/
├── images_1serie_A/              ← EM → "serie"
├── images_2serie_B/
│   └── ...
│
├── assets/
│   └── img/
│       └── logo_sesi.png
│
├── backups/                      ← Backups automáticos (gerados pelo script)
│
└── scripts/                      ← Utilitários de manutenção (rodam localmente)
    ├── importar_estudantes.py    ← PRINCIPAL: importa dados + organiza imagens
    ├── gerenciar_usuarios.py     ← Gerencia usuários de acesso (config.json)
    ├── verificar_sistema.py      ← Verifica consistência dados ↔ fotos
    ├── atualizar_foto_status.py  ← Sincroniza foto_coletada com a pasta images/
    ├── backup_dados.py           ← Cria backup compactado de data/ e images/
    ├── renomear_fotos.py         ← Renomeia fotos em lote
    └── gerar_senha_hash.py       ← Gera hash SHA-256 de senhas (utilitário)
```

> **Regra de ouro:** qualquer arquivo dentro de `data/` ou `images/` que for editado e commitado, é automaticamente publicado no site após o `git push`.

---

## 3. Configuração Inicial (uma única vez)

### 3.1 Pré-requisitos

| Ferramenta | Verificar |
|---|---|
| Git | `git --version` |
| Python 3 | `python3 --version` |
| pip | `pip3 --version` |
| VS Code | `code --version` |

```bash
# Instalar dependências Python necessárias para os scripts
pip3 install pandas openpyxl --break-system-packages
```

### 3.2 Criar o Repositório no GitHub

1. Acesse **https://github.com/new**
2. Preencha:
   - **Repository name:** `carometro-sesi407`
   - **Visibility:** `Private` ← **IMPORTANTE: deixar privado**
   - Não inicialize com nenhum arquivo
3. Clique em **Create repository**

### 3.3 Configurar Git Local no WSL2

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global init.defaultBranch main
git config --global credential.helper store
```

**Personal Access Token (GitHub):**

1. GitHub → Avatar → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
2. Note: `carometro-sesi407` | Expiration: No expiration | Permissão: **repo**
3. Copie o token gerado (aparece apenas uma vez)

### 3.4 Clonar e Preparar o Projeto

```bash
cd ~
git clone https://github.com/SEU-USUARIO/carometro-sesi407.git
cd carometro-sesi407
```

Copie os arquivos do projeto para esta pasta, adicione as fotos em `images/` e:

```bash
git add .
git commit -m "feat: inicialização do Carômetro Escolar SESI 407"
git push -u origin main
```

### 3.5 Configurar GitHub Pages

1. Repositório → **Settings** → **Pages**
2. Source: Branch `main` | Folder `/ (root)`
3. Clique **Save**
4. Aguarde 1-2 min → URL: `https://SEU-USUARIO.github.io/carometro-sesi407/`

### 3.6 Configurar Usuários de Acesso

```bash
# Modo interativo (recomendado)
python3 scripts/gerenciar_usuarios.py

# Ou direto
python3 scripts/gerenciar_usuarios.py --adicionar
```

Após configurar os usuários, commite o `config.json`:

```bash
git add data/config.json
git commit -m "config: configurar usuários de acesso"
git push
```

---

## 4. Formato dos Dados

### 4.1 Template de importação (template_estudantes)

Gere os templates com:
```bash
python3 scripts/importar_estudantes.py
```

Isso cria `template_estudantes.csv` e `template_estudantes.xlsx` na raiz do projeto.

**Colunas do template:**

| Coluna | Obrig. | Exemplo | Notas |
|---|---|---|---|
| `rm_estudante` | ✅ | `006810` | RM/Matrícula do aluno |
| `ra_estudante` | | `000120628062-1` | Registro do Aluno SESI |
| `nome_estudante` | ✅ | `ANA BEATRIZ SILVA SANTOS` | Nome completo |
| `serie` | ✅ | `6º Ano` | Ver valores válidos abaixo |
| `turma` | ✅ | `A` | Letra da turma |
| `turno` | ✅ | `Manhã` | Manhã \| Tarde \| Integral |
| `data_nascimento` | | `15/03/2012` | Formato DD/MM/AAAA |
| `email_estudante` | | `ana@portalsesisp.org.br` | |
| `status` | | `Ativo` | Ativo \| Inativo \| Transferido |
| `data_ingresso` | | `01/02/2024` | Formato DD/MM/AAAA |
| `mae_nome` | | `MARIA DA SILVA SANTOS` | |
| `mae_telefone` | | `(16) 99999-8888` | |
| `mae_email` | | `maria@email.com` | |
| `pai_nome` | | `JOSÉ CARLOS SANTOS` | |
| `pai_telefone` | | `(16) 98888-7777` | |
| `pai_email` | | `jose@email.com` | |
| `endereco_estudante` | | `Rua das Flores, 123` | |
| `termo_autorizado` | | `Sim` | Sim \| Não |
| `foto_coletada` | | `Não` | Sim \| Não |
| `observacoes` | | `Restrição alimentar` | |

**Séries válidas:** `6º Ano` · `7º Ano` · `8º Ano` · `9º Ano` · `1º EM` · `2º EM` · `3º EM`

### 4.2 data/alunos.json

O arquivo é gerado automaticamente pelo script de importação. Estrutura de cada objeto:

```json
{
  "matricula":        "006810",
  "rm_estudante":     "006810",
  "ra_estudante":     "000120628062-1",
  "nome_completo":    "ANA BEATRIZ SILVA SANTOS",
  "serie":            "6º Ano",
  "turma":            "A",
  "turno":            "Manhã",
  "status":           "Ativo",
  "data_nascimento":  "2012-03-15",
  "data_ingresso":    "2024-02-01",
  "email_estudante":  "ana.santos@portalsesisp.org.br",
  "mae_nome":         "MARIA DA SILVA SANTOS",
  "mae_telefone":     "(16) 99999-8888",
  "mae_email":        "maria.santos@email.com",
  "pai_nome":         "JOSÉ CARLOS SANTOS",
  "pai_telefone":     "(16) 98888-7777",
  "pai_email":        "jose.santos@email.com",
  "endereco":         "Rua das Flores, 123",
  "observacoes":      "Estudante com restrição alimentar",
  "termo_autorizado": true,
  "foto_coletada":    false
}
```

> **Nota:** o campo `rm_estudante` é o identificador principal. O campo `matricula` é mantido por compatibilidade.

### 4.3 data/config.json

```json
{
  "app": {
    "nome":       "Carômetro Escolar",
    "subtitulo":  "Centro Educacional SESI 407",
    "escola":     "SESI 407",
    "cidade":     "São Carlos — SP",
    "ano_letivo": "2026"
  },
  "auth": {
    "habilitado": true,
    "usuarios": [
      {
        "usuario":    "admin",
        "senha_hash": "HASH_SHA256_DA_SENHA",
        "nome":       "Administrador",
        "perfil":     "admin"
      }
    ]
  },
  "series_ordem": ["6º Ano","7º Ano","8º Ano","9º Ano","1º EM","2º EM","3º EM"]
}
```

> ⚠️ **Nunca coloque senhas em texto puro.** Use sempre o hash SHA-256 gerado pelo script.

### 4.4 Fotos dos Alunos

| Regra | Detalhe |
|---|---|
| **Nome do arquivo** | `<rm_estudante>.jpg` (ex: `006810.jpg`) |
| **Localização** | Pasta `images/` na raiz do projeto |
| **Formato** | JPEG preferencial (`.jpg`) |
| **Tamanho recomendado** | 240×320 px (proporção 3:4) — máx 500 KB |
| **Após importar** | O script cria pastas `images_<turma>/` automaticamente |

**Nomenclatura das pastas por turma:**

| Série | Turma | Pasta gerada |
|---|---|---|
| 6º Ano | A | `images_6ano_A/` |
| 7º Ano | B | `images_7ano_B/` |
| 1º EM | A | `images_1serie_A/` |
| 2º EM | B | `images_2serie_B/` |
| 3º EM | C | `images_3serie_C/` |

---

## 5. Scripts Utilitários — Referência Completa

### 5.1 importar_estudantes.py ⭐ (principal)

Script central do workflow. Três modos de uso:

**Modo 1 — Gerar templates (sem argumentos):**
```bash
python3 scripts/importar_estudantes.py
```
Cria `template_estudantes.csv` e `template_estudantes.xlsx` com cabeçalho + linha de exemplo.
Não sobrescreve se já existirem.

**Modo 2 — Importar dados (com arquivo):**
```bash
# Com CSV
python3 scripts/importar_estudantes.py template_estudantes.csv

# Com Excel
python3 scripts/importar_estudantes.py template_estudantes.xlsx

# Com caminho completo
python3 scripts/importar_estudantes.py /home/usuario/planilha_alunos.xlsx
```
O script:
- Lê o arquivo (CSV ou XLSX)
- Pula automaticamente a linha de descrições do template XLSX
- Cria/atualiza `data/alunos.json`
- Organiza fotos de `images/` para as pastas de turma correspondentes
- Exibe relatório detalhado

**Modo 3 — Apenas reorganizar imagens:**
```bash
python3 scripts/importar_estudantes.py --organizar-imagens
```
Reorganiza as fotos baseando-se no `alunos.json` existente, sem reimportar dados.

---

### 5.2 gerenciar_usuarios.py ⭐

Gerencia usuários em `data/config.json`.

```bash
# Modo interativo (menu completo)
python3 scripts/gerenciar_usuarios.py

# Comandos diretos
python3 scripts/gerenciar_usuarios.py --listar
python3 scripts/gerenciar_usuarios.py --adicionar
python3 scripts/gerenciar_usuarios.py --alterar-senha <usuario>
python3 scripts/gerenciar_usuarios.py --remover <usuario>
python3 scripts/gerenciar_usuarios.py --verificar-senha <usuario>
python3 scripts/gerenciar_usuarios.py --ativar-login
python3 scripts/gerenciar_usuarios.py --desativar-login
python3 scripts/gerenciar_usuarios.py --config-escola
```

**Exemplo — adicionar usuário:**
```
python3 scripts/gerenciar_usuarios.py --adicionar
  Usuário (login): prof.silva
  Nome de exibição: Prof. João Silva
  Perfil: 1 → viewer
  Senha: ••••••••
  Confirmar senha: ••••••••
  ✅  Usuário 'prof.silva' adicionado com sucesso!
```

---

### 5.3 verificar_sistema.py

Relatório completo de consistência.

```bash
python3 scripts/verificar_sistema.py            # relatório completo
python3 scripts/verificar_sistema.py --resumo   # só estatísticas
python3 scripts/verificar_sistema.py --json     # saída JSON (para automação)
```

Verifica:
- Alunos com `foto_coletada=true` mas sem imagem em `images/`
- Imagens existentes sem `foto_coletada=true` no JSON
- Imagens sem aluno correspondente no JSON
- Cobertura percentual por turma
- Pastas de turma organizadas

---

### 5.4 atualizar_foto_status.py

Sincroniza o campo `foto_coletada` no JSON com base nas imagens físicas.

```bash
# Ativa foto_coletada=true para quem tem imagem em images/
python3 scripts/atualizar_foto_status.py

# Também desativa foto_coletada=false para quem não tem imagem
python3 scripts/atualizar_foto_status.py --limpar

# Simula sem salvar (dry-run)
python3 scripts/atualizar_foto_status.py --dry-run
```

**Quando usar:** após copiar um lote de fotos para `images/` sem alterar o JSON manualmente.

---

### 5.5 backup_dados.py

Cria backups compactados de `data/` e `images/`.

```bash
# Criar backup (salva em backups/)
python3 scripts/backup_dados.py

# Salvar em pasta específica
python3 scripts/backup_dados.py --destino /home/usuario/meus_backups/

# Listar backups disponíveis
python3 scripts/backup_dados.py --listar

# Restaurar um backup
python3 scripts/backup_dados.py --restaurar backups/carometro_backup_2026-01-01_12-00.zip
```

**Recomendação:** executar antes de grandes atualizações.

---

### 5.6 renomear_fotos.py

Renomeia fotos em lote da nomenclatura original para `<rm_estudante>.jpg`.

```bash
# Renomear e mover para images/
python3 scripts/renomear_fotos.py --pasta fotos_originais/ --destino images/

# Renomear na mesma pasta
python3 scripts/renomear_fotos.py --pasta fotos_originais/
```

Reconhece:
- Arquivos já com RM numérico: `006810.jpg` → copiado diretamente
- Arquivos com nome do aluno: busca no `alunos.json` por correspondência parcial de nome

---

### 5.7 gerar_senha_hash.py

Gera hash SHA-256 de uma senha (utilitário de linha de comando).

```bash
python3 scripts/gerar_senha_hash.py MinhaSenh@123
```

> **Alternativa:** use o `gerenciar_usuarios.py --adicionar` que já faz o hash automaticamente.

---

## 6. Fluxo de Trabalho Diário

### Workflow completo de início de ano letivo

```bash
# 1. Gerar templates
python3 scripts/importar_estudantes.py

# 2. Preencher template_estudantes.xlsx no Excel/LibreOffice

# 3. Importar dados + organizar fotos
python3 scripts/importar_estudantes.py template_estudantes.xlsx

# 4. Verificar consistência
python3 scripts/verificar_sistema.py

# 5. Commitar e publicar
git add .
git commit -m "feat: importar alunos ano letivo 2026"
git push
```

### Workflow de adição de fotos em lote

```bash
# 1. Copiar fotos para images/ (nomeadas como <rm>.jpg)
cp /caminho/fotos/*.jpg images/

# 2. Atualizar status automaticamente
python3 scripts/atualizar_foto_status.py

# 3. Reorganizar por turma
python3 scripts/importar_estudantes.py --organizar-imagens

# 4. Verificar
python3 scripts/verificar_sistema.py --resumo

# 5. Commitar
git add images/ data/alunos.json
git commit -m "feat: adicionar fotos 7º Ano A (28 fotos)"
git push
```

### Via VS Code + WSL2 (qualquer atualização)

```bash
cd ~/carometro-sesi407
git pull                    # sincronizar com GitHub
# ... faz alterações ...
git status                  # ver o que mudou
git add .
git commit -m "descrição"
git push                    # ✅ site atualiza em 30-60s
```

### Diretamente pelo GitHub (navegador)

Para alterações simples sem abrir o terminal:

1. Acesse o repositório no GitHub
2. Navegue até o arquivo desejado
3. Clique em ✏️ (Edit this file)
4. Faça a alteração
5. Clique em **Commit changes** com mensagem descritiva

---

## 7. Operações de Manutenção

### Adicionar novos alunos

```bash
# Opção A: via template (recomendado para vários alunos)
# 1. Edite template_estudantes.xlsx com os novos alunos
python3 scripts/importar_estudantes.py template_estudantes.xlsx
git add data/ && git commit -m "feat: novos alunos" && git push

# Opção B: editar o JSON diretamente (um aluno)
# Edite data/alunos.json e adicione o objeto do aluno
git add data/alunos.json && git commit -m "feat: adicionar aluno RM 006811" && git push
```

### Atualizar dados de um aluno

Edite diretamente `data/alunos.json` (busque pelo `rm_estudante`):
```bash
git add data/alunos.json
git commit -m "fix: corrigir telefone responsável RM 006810"
git push
```

### Adicionar / atualizar foto de aluno

```bash
cp /caminho/foto.jpg images/006810.jpg
python3 scripts/atualizar_foto_status.py          # atualiza foto_coletada
python3 scripts/importar_estudantes.py --organizar-imagens
git add images/ data/alunos.json
git commit -m "feat: foto do aluno RM 006810"
git push
```

### Alterar senha de acesso

```bash
python3 scripts/gerenciar_usuarios.py --alterar-senha admin
# ... digitar senha atual e nova senha ...
git add data/config.json
git commit -m "security: atualizar senha de acesso"
git push
```

### Adicionar novo usuário de acesso

```bash
python3 scripts/gerenciar_usuarios.py --adicionar
# ... preencher usuário, nome, perfil, senha ...
git add data/config.json
git commit -m "config: adicionar usuário prof.silva"
git push
```

### Remover aluno

```bash
# Editar data/alunos.json e remover o objeto do aluno
# Opcionalmente remover a foto:
rm images/006810.jpg
git add data/alunos.json images/
git commit -m "chore: remover aluno RM 006810 (transferido)"
git push
```

### Atualizar ano letivo / configurações da escola

```bash
python3 scripts/gerenciar_usuarios.py --config-escola
git add data/config.json
git commit -m "config: atualizar ano letivo 2026"
git push
```

### Fazer backup antes de atualizações grandes

```bash
python3 scripts/backup_dados.py
# Backup salvo em backups/carometro_backup_YYYY-MM-DD_HH-MM-SS.zip
```

---

## 8. Comandos Git de Referência

```bash
# ── Verificar status ──────────────────────────────────────────
git status                    # Ver o que mudou
git diff                      # Ver diferenças detalhadas
git log --oneline -10         # Últimos 10 commits

# ── Sincronizar ───────────────────────────────────────────────
git pull                      # Baixar atualizações do GitHub
git push                      # Enviar atualizações (publicar no site)

# ── Adicionar e commitar ──────────────────────────────────────
git add .                     # Todos os arquivos modificados
git add data/alunos.json      # Arquivo específico
git add images/               # Toda uma pasta
git commit -m "mensagem"      # Criar commit

# ── Fluxo completo ────────────────────────────────────────────
git pull && git add . && git commit -m "descrição" && git push

# ── Desfazer ─────────────────────────────────────────────────
git restore data/alunos.json  # Descartar alterações não commitadas
git revert HEAD               # Desfazer o último commit (preserva histórico)
```

**Mensagens de commit recomendadas:**

| Tipo | Exemplo |
|---|---|
| Novos alunos | `feat: importar alunos 7º Ano A` |
| Fotos | `feat: fotos 8º Ano B (30 fotos)` |
| Correção de dados | `fix: corrigir RM e telefone RM 006810` |
| Usuários/config | `config: adicionar usuário coordenação` |
| Segurança | `security: renovar senha de acesso` |
| Atualização geral | `chore: atualizar dados início de semestre` |

---

## 9. Solução de Problemas

### Site não atualizou após o push

- Aguarde até 60 segundos (GitHub Pages tem delay)
- Limpe o cache: `Ctrl+Shift+R`
- Verifique em: GitHub → Settings → Pages → status do deploy

### Login não funciona

```bash
# Verificar a senha
python3 scripts/gerenciar_usuarios.py --verificar-senha admin

# Ver usuários cadastrados
python3 scripts/gerenciar_usuarios.py --listar
```

### Foto não aparece

```bash
# Verificar consistência completa
python3 scripts/verificar_sistema.py

# Sincronizar status automaticamente
python3 scripts/atualizar_foto_status.py --dry-run   # simular
python3 scripts/atualizar_foto_status.py              # aplicar
```

### alunos.json com erro de sintaxe

```bash
# Validar o JSON
python3 -c "import json; json.load(open('data/alunos.json')); print('JSON válido ✅')"
```

Erros comuns de JSON:
- Vírgula faltando entre objetos: `} {` → `}, {`
- Vírgula sobrando no final: `},` → `}`
- Aspas simples em vez de duplas: `'nome'` → `"nome"`

### Erro ao fazer git push

```
error: failed to push some refs
```
```bash
git pull --rebase
git push
```

### Script Python com erro de módulo

```bash
pip3 install pandas openpyxl --break-system-packages
```

### Imagens não aparecem nas pastas de turma

```bash
# Verificar se as imagens estão em images/ com o nome correto (RM.jpg)
ls images/

# Reorganizar
python3 scripts/importar_estudantes.py --organizar-imagens
```

---

## 10. Segurança

### Nível de segurança do login embutido

| O que protege | O que NÃO protege |
|---|---|
| Acesso casual ao site | Acesso direto à URL dos arquivos JSON/imagens |
| Usuários sem conhecimento técnico | Download do código-fonte (se repo público) |
| Sessão expira ao fechar o browser | Engenharia reversa do hash de senha |

### Recomendações

1. **Repositório privado** — impede acesso ao código-fonte
2. **Cloudflare Access** (gratuito) — proteção real antes de carregar o site
3. **Nunca coloque senhas em texto puro** no config.json
4. **Rotacione senhas** a cada semestre letivo
5. **Mantenha backups** antes de grandes atualizações

### Sobre LGPD

- Use repositório **privado**
- Limite o acesso ao repositório apenas aos responsáveis
- O campo `termo_autorizado` registra autorização LGPD
- Exclua dados de alunos transferidos/formados periodicamente

---

## 11. Escalabilidade

### Limites práticos

| Recurso | Limite |
|---|---|
| Alunos | Até ~2.000 (JSON carregado inteiro em memória) |
| Fotos | Até ~500 MB no repositório |
| Usuários de acesso | Sem limite |
| Turmas / séries | Sem limite |

### Dicas de performance

```bash
# Comprimir fotos antes de adicionar (ImageMagick)
sudo apt install imagemagick -y
for f in images/*.jpg; do
  convert "$f" -resize 240x320^ -gravity center -extent 240x320 -quality 80 "$f"
done
```

---

*Carômetro Escolar — Centro Educacional SESI 407 — São Carlos — SP*
*Uso interno restrito. Todos os dados são de acesso exclusivo da equipe escolar.*
