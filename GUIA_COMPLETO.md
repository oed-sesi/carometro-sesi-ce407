# Carômetro Escolar — SESI 407
## Guia Completo de Configuração, Atualização e Manutenção

> **Versão:** 5.0 — Edição GitHub Pages (Frontend Estático)\
> **Última revisão:** 2025\
> **Ambiente:** Ubuntu 25.04 LTS via WSL2 + Windows 11 + VS Code

---

## Índice

1. [Visão Geral da Aplicação](#1-visão-geral-da-aplicação)
2. [Estrutura do Repositório](#2-estrutura-do-repositório)
3. [Configuração Inicial (uma única vez)](#3-configuração-inicial-uma-única-vez)
   - 3.1 [Pré-requisitos](#31-pré-requisitos)
   - 3.2 [Criar o Repositório no GitHub](#32-criar-o-repositório-no-github)
   - 3.3 [Configurar Git Local no WSL2](#33-configurar-git-local-no-wsl2)
   - 3.4 [Clonar e Preparar o Projeto](#34-clonar-e-preparar-o-projeto)
   - 3.5 [Configurar GitHub Pages](#35-configurar-github-pages)
   - 3.6 [Configurar a Proteção com Login](#36-configurar-a-proteção-com-login)
   - 3.7 [Configurar Cloudflare Access (recomendado)](#37-configurar-cloudflare-access-recomendado)
4. [Formato dos Dados](#4-formato-dos-dados)
   - 4.1 [data/alunos.json](#41-dataalunosjson)
   - 4.2 [data/config.json](#42-dataconfigjson)
   - 4.3 [Fotos dos Alunos (images/)](#43-fotos-dos-alunos-images)
5. [Fluxo de Trabalho Diário](#5-fluxo-de-trabalho-diário)
   - 5.1 [Via VS Code + WSL2 (recomendado)](#51-via-vs-code--wsl2-recomendado)
   - 5.2 [Diretamente no GitHub (navegador)](#52-diretamente-no-github-navegador)
6. [Scripts Utilitários](#6-scripts-utilitários)
   - 6.1 [Gerar Hash de Senha](#61-gerar-hash-de-senha)
   - 6.2 [Importar Alunos por CSV](#62-importar-alunos-por-csv)
   - 6.3 [Renomear Fotos em Lote](#63-renomear-fotos-em-lote)
   - 6.4 [Verificar Consistência do Sistema](#64-verificar-consistência-do-sistema)
7. [Operações de Manutenção](#7-operações-de-manutenção)
   - 7.1 [Adicionar um Novo Aluno](#71-adicionar-um-novo-aluno)
   - 7.2 [Atualizar Dados de um Aluno](#72-atualizar-dados-de-um-aluno)
   - 7.3 [Adicionar / Atualizar Foto de Aluno](#73-adicionar--atualizar-foto-de-aluno)
   - 7.4 [Remover um Aluno](#74-remover-um-aluno)
   - 7.5 [Adicionar / Remover Turma](#75-adicionar--remover-turma)
   - 7.6 [Alterar Senha de Acesso](#76-alterar-senha-de-acesso)
   - 7.7 [Adicionar Novo Usuário de Acesso](#77-adicionar-novo-usuário-de-acesso)
   - 7.8 [Atualizar o Logo](#78-atualizar-o-logo)
   - 7.9 [Atualizar o Ano Letivo](#79-atualizar-o-ano-letivo)
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
        ├── index.html  ← Toda a lógica da aplicação
        ├── data/alunos.json  ← Dados dos alunos
        ├── data/config.json  ← Configuração e login
        └── images/<matricula>.jpg  ← Fotos
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
- **Lucide Icons** via CDN

---

## 2. Estrutura do Repositório

```
carometro-sesi-ce407/
│
├── index.html              ← Aplicação principal (HTML + CSS + JS em um arquivo)
├── README.md               ← Descrição do repositório
├── .gitignore              ← Arquivos ignorados pelo Git
│
├── data/
│   ├── alunos.json         ← Lista de todos os alunos (PRINCIPAL arquivo de dados)
│   └── config.json         ← Configuração da escola e usuários de acesso
│
├── images/                 ← Fotos dos alunos
│   ├── 123456.jpg          ← Nomeadas pelo número de matrícula
│   ├── 123457.jpg
│   └── ...
│
├── assets/
│   └── img/
│       └── logo_sesi.png   ← Logo da escola
│
└── scripts/                ← Utilitários de manutenção (rodam localmente)
    ├── gerar_senha_hash.py        ← Gera hash de senha
    ├── gerar-senha-hash.js        ← Versão Node.js
    ├── importar_alunos_csv.py     ← Importa alunos de planilha CSV
    ├── renomear_fotos.py          ← Renomeia fotos em lote
    └── verificar_sistema.py       ← Verifica consistência dos dados
```

> **Regra de ouro:** qualquer arquivo dentro de `data/` ou `images/` que for editado e commitado, é automaticamente publicado no site após o `git push`.

---

## 3. Configuração Inicial (uma única vez)

### 3.1 Pré-requisitos

| Ferramenta | Onde instalar | Verificar |
|---|---|---|
| Git | Já instalado no WSL2 | `git --version` |
| Python 3 | Já instalado no WSL2 | `python3 --version` |
| VS Code | Windows ou WSL2 | `code --version` |
| Conta GitHub | https://github.com | — |

No WSL2 (Ubuntu 25.04), instale o Git se necessário:
```bash
sudo apt update && sudo apt install git -y
```

### 3.2 Criar o Repositório no GitHub

1. Acesse **https://github.com/new**
2. Preencha:
   - **Repository name:** `carometro-sesi-ce407`
   - **Visibility:** `Private` ← **IMPORTANTE: deixar privado**
   - Não marque nenhuma opção de inicialização (README, .gitignore)
3. Clique em **Create repository**
4. Anote a URL: `https://github.com/SEU-USUARIO/carometro-sesi-ce407.git`

### 3.3 Configurar Git Local no WSL2

Abra o terminal WSL2 e configure:

```bash
# Configurar identidade (use seus dados reais)
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Configurar branch padrão como 'main'
git config --global init.defaultBranch main

# Verificar configurações
git config --list
```

**Autenticação com o GitHub (Personal Access Token):**

1. No GitHub: clique no avatar → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**
2. Em **Note**: coloque `carometro-sesi-ce407`
3. **Expiration**: escolha `No expiration` (ou 1 year)
4. Marque a permissão: **repo** (acesso completo)
5. Clique **Generate token** e **copie o token** (só aparece uma vez)

No WSL2, configure o armazenamento de credenciais:
```bash
git config --global credential.helper store
```

Na primeira vez que usar `git push`, o Git pedirá usuário e senha:
- **Username:** seu usuário do GitHub
- **Password:** cole o Personal Access Token (não sua senha do GitHub)

### 3.4 Clonar e Preparar o Projeto

```bash
# Ir para a pasta home do WSL2
cd ~

# Clonar o repositório (ainda vazio)
git clone https://github.com/SEU-USUARIO/carometro-sesi-ce407.git

# Entrar na pasta
cd carometro-sesi-ce407
```

Agora copie os arquivos do projeto para dentro desta pasta:
- `index.html`
- `README.md`
- `.gitignore`
- `data/alunos.json`
- `data/config.json`
- `assets/img/logo_sesi.png`
- `scripts/` (todos os arquivos)

Adicione as fotos dos alunos na pasta `images/` com o nome `<matricula>.jpg`.

Faça o primeiro commit:
```bash
# Verificar o que será commitado
git status

# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "feat: inicialização do Carômetro Escolar SESI 407"

# Enviar para o GitHub
git push -u origin main
```

### 3.5 Configurar GitHub Pages

1. No repositório do GitHub, clique em **Settings**
2. No menu lateral, clique em **Pages**
3. Em **Source**, selecione:
   - Branch: `main`
   - Folder: `/ (root)`
4. Clique em **Save**
5. Aguarde 1-2 minutos. O link aparecerá como:
   `https://SEU-USUARIO.github.io/carometro-sesi-ce407/`

> ⚠️ **Atenção:** Para repositórios **privados**, o GitHub Pages só funciona com planos pagos (GitHub Pro, Team, ou Enterprise). Se precisar gratuito, o repositório precisa ser **público**.
>
> Se o repositório for público, qualquer pessoa pode ver o código-fonte — mas não conseguirá fazer login sem as credenciais.

### 3.6 Configurar a Proteção com Login

A aplicação já vem com sistema de login embutido. Para configurar:

1. Gere o hash da sua senha (veja [seção 6.1](#61-gerar-hash-de-senha))
2. Edite `data/config.json` e substitua a senha:

```json
{
  "auth": {
    "habilitado": true,
    "usuarios": [
      {
        "usuario": "admin",
        "senha_hash": "SEU_HASH_AQUI",
        "nome": "Administrador",
        "perfil": "admin"
      }
    ]
  }
}
```

3. Commite e faça push (o login estará ativo imediatamente)

> **Nível de segurança:** O login em JavaScript impede acesso casual. Para proteção mais robusta (bloqueia acesso ao código-fonte), use o Cloudflare Access descrito abaixo.

### 3.7 Configurar Cloudflare Access (recomendado)

O Cloudflare Access adiciona uma tela de login **antes** que o navegador carregue qualquer arquivo do site. É gratuito para até 50 usuários.

**Pré-requisito:** Ter um domínio no Cloudflare (ex: `sesi407.com.br`).

**Passos:**

1. Acesse **https://dash.cloudflare.com** → **Zero Trust** → **Access** → **Applications**
2. Clique **Add an application** → **SaaS**...

   *(Alternativamente, use o subdomain de pages.dev do Cloudflare Pages como proxy — mais simples)*

**Alternativa mais simples — Cloudflare Pages como proxy:**

1. Acesse **https://dash.cloudflare.com** → **Pages**
2. **Create a project** → **Connect to Git** → selecione seu repositório
3. Em **Build settings**: deixe vazio (não há build)
4. Publique. O Cloudflare Pages servirá o site em `carometro-sesi-ce407.pages.dev`
5. Em **Settings** → **Access Policy** → Adicione uma política de acesso por e-mail

---

## 4. Formato dos Dados

### 4.1 data/alunos.json

Array JSON com um objeto por aluno. Todos os campos de texto vazios devem ser `""`.

```json
[
  {
    "matricula":      "123456",         ← OBRIGATÓRIO - único, 4-10 dígitos
    "nome_completo":  "Ana Clara Santos",← OBRIGATÓRIO
    "serie":          "7º Ano",          ← OBRIGATÓRIO
    "turma":          "A",               ← OBRIGATÓRIO
    "turno":          "Manhã",           ← OBRIGATÓRIO
    "status":         "Ativo",           ← "Ativo" ou "Inativo"
    "ra_estudante":   "12345678901234",  ← RA (pode ser vazio "")
    "email_estudante":"ana@sesi.org.br", ← E-mail (pode ser vazio "")
    "data_nascimento":"2010-03-15",      ← formato YYYY-MM-DD (pode ser "")
    "data_ingresso":  "2023-02-01",      ← formato YYYY-MM-DD (pode ser "")
    "mae_nome":       "Maria Santos",    ← pode ser ""
    "mae_telefone":   "(17) 99999-0001", ← pode ser ""
    "mae_email":      "maria@email.com", ← pode ser ""
    "pai_nome":       "Carlos Santos",   ← pode ser ""
    "pai_telefone":   "(17) 99999-0002", ← pode ser ""
    "pai_email":      "",                ← pode ser ""
    "endereco":       "Rua das Flores, 123 — SJRP",  ← pode ser ""
    "observacoes":    "",                ← pode ser ""
    "termo_autorizado": true,            ← true ou false
    "foto_coletada":    true             ← true = tem foto em images/
  }
]
```

**Campos obrigatórios:** `matricula`, `nome_completo`, `serie`, `turma`, `turno`

**Séries válidas (exemplos):** `6º Ano`, `7º Ano`, `8º Ano`, `9º Ano`, `1º EM`, `2º EM`, `3º EM`

**Turnos válidos:** `Manhã`, `Tarde`, `Integral`

### 4.2 data/config.json

```json
{
  "app": {
    "nome":       "Carômetro Escolar",
    "subtitulo":  "Centro Educacional SESI 407",
    "escola":     "SESI 407",
    "cidade":     "São José do Rio Preto — SP",
    "ano_letivo": "2025"
  },
  "auth": {
    "habilitado": true,              ← false = desativa o login
    "usuarios": [
      {
        "usuario":    "admin",       ← nome de login
        "senha_hash": "HASH_SHA256", ← hash da senha
        "nome":       "Administrador",← nome exibido no sistema
        "perfil":     "admin"        ← "admin" ou "viewer" (ambos só visualizam)
      }
    ]
  },
  "series_ordem": [                  ← ordem de exibição das séries
    "6º Ano", "7º Ano", "8º Ano", "9º Ano",
    "1º EM", "2º EM", "3º EM"
  ]
}
```

### 4.3 Fotos dos Alunos (images/)

| Requisito | Detalhe |
|---|---|
| **Nome do arquivo** | `<matricula>.jpg` (ex: `123456.jpg`) |
| **Formato** | JPEG preferencialmente (`.jpg`) |
| **Tamanho recomendado** | 240×320 px (3×4) — máximo 500KB por foto |
| **Proporção** | 3:4 (retrato) — o sistema recorta automaticamente |
| **Quando não existe** | O sistema exibe ícone de "sem foto" automaticamente |

> **Conversão de PNG para JPG** (no WSL2):
> ```bash
> # Instalar ImageMagick se necessário
> sudo apt install imagemagick -y
>
> # Converter todas as PNG para JPG na pasta images/
> for f in images/*.png; do convert "$f" "${f%.png}.jpg"; done
>
> # Remover os PNG originais após verificar
> rm images/*.png
> ```

---

## 5. Fluxo de Trabalho Diário

### 5.1 Via VS Code + WSL2 (recomendado)

Este é o fluxo para qualquer atualização local (dados, fotos, configuração):

```bash
# 1. Abrir o terminal WSL2 e ir para a pasta do projeto
cd ~/carometro-sesi-ce407

# 2. Verificar o status atual
git status

# 3. Sincronizar com o GitHub (puxar atualizações)
git pull

# 4. Fazer as alterações necessárias
#    - Editar data/alunos.json no VS Code
#    - Adicionar/substituir fotos em images/
#    - Editar data/config.json

# 5. Verificar o que mudou
git diff

# 6. Adicionar os arquivos modificados
git add .

# 7. Criar o commit com mensagem descritiva
git commit -m "feat: adicionar alunos do 7º Ano A"

# 8. Enviar para o GitHub (publicar no site)
git push

# ✅ O site é atualizado automaticamente em 30-60 segundos.
```

**Abrindo o projeto no VS Code direto do WSL2:**
```bash
cd ~/carometro-sesi-ce407
code .
```

**Mensagens de commit recomendadas:**

| Tipo | Exemplo |
|---|---|
| Adicionar alunos | `feat: adicionar turmas do 8º Ano` |
| Atualizar dados | `fix: corrigir data de nascimento aluno 123456` |
| Adicionar fotos | `feat: fotos dos alunos do 9º Ano A` |
| Alterar configuração | `config: atualizar ano letivo 2026` |
| Atualizar logo | `assets: atualizar logo da escola` |

### 5.2 Diretamente no GitHub (navegador)

Para alterações simples sem precisar do computador local:

**Editar dados de um aluno:**
1. Acesse o repositório: `https://github.com/SEU-USUARIO/carometro-sesi-ce407`
2. Clique em `data/` → `alunos.json`
3. Clique no ícone de lápis ✏️ (Edit this file)
4. Faça a alteração desejada
5. No final da página, em **Commit changes**:
   - Escreva uma mensagem descritiva (ex: `fix: atualizar telefone aluno 123456`)
   - Clique em **Commit changes**
6. ✅ O site atualiza em 30-60 segundos

**Adicionar uma foto pelo navegador:**
1. Vá para a pasta `images/`
2. Clique em **Add file** → **Upload files**
3. Arraste a foto renomeada como `<matricula>.jpg`
4. Escreva a mensagem de commit
5. Clique em **Commit changes**

---

## 6. Scripts Utilitários

Todos os scripts ficam na pasta `scripts/` e são executados localmente no WSL2.

### 6.1 Gerar Hash de Senha

Use este script para criar o hash SHA-256 de uma senha antes de colocá-la no `config.json`.

```bash
# Com Python (recomendado)
python3 scripts/gerar_senha_hash.py SuaSenhaAqui

# Com Node.js (alternativa)
node scripts/gerar-senha-hash.js SuaSenhaAqui
```

**Saída:**
```
─────────────────────────────────────────────────────
  Carômetro Escolar — Gerador de Hash de Senha
─────────────────────────────────────────────────────
  Senha informada : SuaSenhaAqui
  Hash SHA-256    : a1b2c3d4e5f6...
─────────────────────────────────────────────────────

  Cole o hash acima no campo "senha_hash" do usuário
  em data/config.json
```

### 6.2 Importar Alunos por CSV

Importa uma planilha de alunos diretamente para `data/alunos.json`.

**Preparar o CSV:**

Crie um arquivo `.csv` com as colunas (o nome da coluna não diferencia maiúsculas/minúsculas):

```csv
matricula,nome_completo,serie,turma,turno,data_nascimento,status,mae_nome,mae_telefone,termo_autorizado,foto_coletada
123456,Ana Clara Santos,7º Ano,A,Manhã,2010-03-15,Ativo,Maria Santos,(17) 99999-0001,sim,nao
123457,Bruno Lima,7º Ano,A,Manhã,2010-07-22,Ativo,Fernanda Lima,(17) 99999-0003,sim,nao
```

**Executar:**
```bash
python3 scripts/importar_alunos_csv.py meus_alunos.csv
```

O script:
- Mantém alunos já existentes no JSON (atualiza se a matrícula já existir)
- Adiciona novos alunos
- Exibe relatório detalhado
- Não remove alunos existentes que não estão no CSV

Após importar, faça o commit:
```bash
git add data/alunos.json
git commit -m "feat: importar alunos do 7º Ano"
git push
```

### 6.3 Renomear Fotos em Lote

Renomeia fotos da nomenclatura original para `<matricula>.jpg`.

```bash
# Renomear e mover para images/ automaticamente
python3 scripts/renomear_fotos.py --pasta fotos_originais/ --destino images/

# Ou renomear na mesma pasta
python3 scripts/renomear_fotos.py --pasta fotos_originais/
```

O script reconhece:
- Arquivos já nomeados com matrícula: `123456.jpg` → copiado direto
- Arquivos com nome do aluno: `Ana Clara Santos.jpg` → busca no JSON pelo nome

Após renomear, lembre de atualizar `foto_coletada: true` nos alunos correspondentes e commitar tudo.

### 6.4 Verificar Consistência do Sistema

Verifica se os dados do JSON estão coerentes com as fotos na pasta `images/`.

```bash
python3 scripts/verificar_sistema.py
```

**Saída de exemplo:**
```
═══════════════════════════════════════════════════════
  Carômetro Escolar — Verificação do Sistema
═══════════════════════════════════════════════════════
  Alunos no JSON    : 120
  Imagens em images/: 87

  ⚠️  [3] foto_coletada=true MAS imagem não encontrada:
      • 123460 — Eduarda Martins Souza (8º Ano A)
        → Crie ou copie: images/123460.jpg

  ─────────────────────────────────────────────────────
  Cobertura por Turma:
  ─────────────────────────────────────────────────────
  Turma                     Total  c/Foto    OK    %
  ─────────────────────────────────────────────────────
  ✅  7º Ano A — Manhã          28      26    26   93%
  ⚠️  8º Ano A — Manhã          30      20    20   67%
  ❌  9º Ano B — Tarde          25       5     5   20%
```

---

## 7. Operações de Manutenção

### 7.1 Adicionar um Novo Aluno

**Opção A — Editar o JSON no VS Code:**

1. Abra `data/alunos.json` no VS Code
2. Adicione um novo objeto ao array (copie um existente como modelo)
3. Preencha todos os campos obrigatórios
4. Defina `"foto_coletada": false` (se ainda não tiver foto)
5. Salve e faça commit

**Opção B — Pelo navegador no GitHub:**

1. Acesse `data/alunos.json` no repositório
2. Clique em ✏️ para editar
3. Adicione o objeto JSON no array
4. Clique em **Commit changes**

**Opção C — Via CSV:**

Crie um CSV com o novo aluno e use o script de importação (seção 6.2).

### 7.2 Atualizar Dados de um Aluno

1. Abra `data/alunos.json`
2. Use `Ctrl+F` para buscar pela matrícula ou nome
3. Edite os campos necessários
4. Salve e commite

```bash
git add data/alunos.json
git commit -m "fix: atualizar dados do aluno 123456"
git push
```

### 7.3 Adicionar / Atualizar Foto de Aluno

1. Renomeie a foto para `<matricula>.jpg` (ex: `123456.jpg`)
2. Coloque-a na pasta `images/`
3. No `data/alunos.json`, atualize o aluno: `"foto_coletada": true`
4. Commite tudo:

```bash
git add images/123456.jpg data/alunos.json
git commit -m "feat: foto do aluno 123456 — Ana Clara Santos"
git push
```

**Adicionar várias fotos de uma vez:**
```bash
# Após colocar todas as fotos na pasta images/
git add images/
git add data/alunos.json
git commit -m "feat: fotos dos alunos do 7º Ano A (26 fotos)"
git push
```

### 7.4 Remover um Aluno

1. Abra `data/alunos.json`
2. Encontre e delete o objeto JSON do aluno
3. Opcionalmente, remova a foto: `rm images/123456.jpg`
4. Commite:

```bash
git add data/alunos.json
git rm images/123456.jpg   # se quiser remover a foto também
git commit -m "chore: remover aluno 123456 (transferido)"
git push
```

### 7.5 Adicionar / Remover Turma

As turmas são criadas automaticamente conforme os dados dos alunos. Para adicionar uma nova turma, basta adicionar alunos com a nova combinação de `serie + turma + turno`.

Para controlar a **ordem de exibição** das séries, edite `data/config.json`:

```json
"series_ordem": ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "1º EM", "2º EM", "3º EM"]
```

### 7.6 Alterar Senha de Acesso

1. Gere o hash da nova senha:
   ```bash
   python3 scripts/gerar_senha_hash.py NovaSenha123
   ```

2. Copie o hash gerado

3. Edite `data/config.json` e substitua o campo `senha_hash` do usuário:
   ```json
   "senha_hash": "NOVO_HASH_AQUI"
   ```

4. Commite:
   ```bash
   git add data/config.json
   git commit -m "security: atualizar senha de acesso"
   git push
   ```

> ⚠️ **Atenção:** Após o push, a senha antiga para de funcionar imediatamente. Se tiver sessão aberta, precisará fazer login novamente.

### 7.7 Adicionar Novo Usuário de Acesso

1. Gere o hash da senha do novo usuário
2. Edite `data/config.json` e adicione um objeto ao array `usuarios`:

```json
"usuarios": [
  {
    "usuario":    "admin",
    "senha_hash": "hash_existente",
    "nome":       "Administrador",
    "perfil":     "admin"
  },
  {
    "usuario":    "professor.silva",
    "senha_hash": "HASH_DO_NOVO_USUARIO",
    "nome":       "Prof. João Silva",
    "perfil":     "viewer"
  }
]
```

3. Commite e faça push.

### 7.8 Atualizar o Logo

1. Substitua o arquivo `assets/img/logo_sesi.png` pelo novo logo
2. Mantenha o mesmo nome de arquivo (`logo_sesi.png`)
3. Commite:
   ```bash
   git add assets/img/logo_sesi.png
   git commit -m "assets: atualizar logo da escola"
   git push
   ```

### 7.9 Atualizar o Ano Letivo

Edite `data/config.json` e altere o campo `ano_letivo`:
```json
"ano_letivo": "2026"
```

---

## 8. Comandos Git de Referência

```bash
# ── Verificar status ──────────────────────────────────────────
git status                    # Ver o que mudou
git diff                      # Ver as diferenças detalhadas
git log --oneline -10         # Ver os últimos 10 commits

# ── Sincronizar ───────────────────────────────────────────────
git pull                      # Baixar atualizações do GitHub
git push                      # Enviar atualizações para o GitHub

# ── Adicionar e commitar ──────────────────────────────────────
git add .                     # Adicionar TODOS os arquivos modificados
git add data/alunos.json      # Adicionar um arquivo específico
git add images/               # Adicionar toda uma pasta
git commit -m "mensagem"      # Criar o commit

# ── Desfazer (use com cuidado) ────────────────────────────────
git restore data/alunos.json  # Descartar alterações não commitadas
git revert HEAD               # Desfazer o último commit (cria commit inverso)

# ── Verificar diferenças antes de commitar ────────────────────
git diff data/alunos.json     # Ver o que mudou num arquivo específico
git diff --staged              # Ver o que está preparado para commit
```

**Fluxo completo mais comum:**
```bash
git pull
# ... faz as alterações ...
git add .
git commit -m "descrição clara do que foi feito"
git push
```

---

## 9. Solução de Problemas

### Site não atualizou após o push

- Aguarde até 60 segundos (GitHub Pages tem delay)
- Limpe o cache do navegador: `Ctrl+Shift+R` (ou `Cmd+Shift+R` no Mac)
- Verifique o status do deploy em: **GitHub → Settings → Pages**
- Se houver erro, clique no link do deploy para ver os detalhes

### Login não funciona

1. Verifique se o `config.json` tem `"habilitado": true`
2. Confirme que o hash está correto:
   ```bash
   python3 scripts/gerar_senha_hash.py SuaSenha
   ```
   Compare com o `senha_hash` no `config.json`
3. Confirme que o `config.json` foi commitado e pusheado

### Foto não aparece

1. Verifique se o arquivo existe: `ls images/123456.jpg`
2. Verifique se o campo `"foto_coletada": true` está no JSON
3. Verifique se o nome do arquivo é exatamente `<matricula>.jpg`
4. Execute: `python3 scripts/verificar_sistema.py`

### Aluno não aparece no sistema

1. Verifique se o `alunos.json` é um JSON válido:
   ```bash
   python3 -c "import json; json.load(open('data/alunos.json'))"
   ```
   Se não mostrar nada, o JSON está válido. Se mostrar erro, há problema de formatação.
2. Verifique se os campos obrigatórios estão preenchidos

### Erro de JSON inválido

Se editar o JSON manualmente e cometer um erro de formatação, o site ficará em branco ou exibirá aviso.

Para verificar:
```bash
# Verificar JSON
python3 -c "
import json
with open('data/alunos.json') as f:
    data = json.load(f)
print(f'OK: {len(data)} alunos carregados')
"
```

Erros comuns:
- Vírgula faltando entre objetos: `} {` → `}, {`
- Vírgula sobrando após o último objeto: `},` → `}`
- Aspas faltando em campos: `nome_completo: "Ana"` → `"nome_completo": "Ana"`

### Erro ao fazer git push

```
error: failed to push some refs
```

Solução: alguém editou o arquivo direto no GitHub. Execute:
```bash
git pull --rebase
git push
```

---

## 10. Segurança

### Nível de segurança do login embutido

O login em JavaScript no `index.html` **não é segurança real de servidor** — é uma barreira de acesso casual. Um usuário técnico que inspecione o código-fonte e a rede consegue contornar.

| O que o login protege | O que NÃO protege |
|---|---|
| Acesso casual/direto ao site | Acesso direto à URL dos arquivos JSON |
| Usuários sem conhecimento técnico | Download das fotos por URL direta |
| Sessão (expira ao fechar o browser) | Engenharia reversa do código |

### Recomendações

1. **Use repositório privado** — impede que o código-fonte fique público
2. **Configure o Cloudflare Access** — bloqueia o site antes de carregar qualquer arquivo (nível de segurança real)
3. **Não coloque dados sensíveis** que não devam jamais ser acessados por alguém tecnicamente habilidoso
4. **Não inclua senhas em texto puro** — use sempre o hash SHA-256
5. **Rotacione as senhas** periodicamente (a cada semestre letivo, por exemplo)

### Sobre os dados de alunos (LGPD)

Os dados ficam armazenados em arquivos JSON no repositório GitHub. Recomendações:

- Use repositório **privado**
- Limite o acesso ao repositório apenas aos responsáveis
- Mantenha apenas os dados necessários para a função do sistema
- O campo `termo_autorizado` controla o registro de autorização LGPD
- Documente o uso de dados conforme exigência da LGPD

---

## 11. Escalabilidade

### Limites do sistema atual

| Recurso | Limite prático |
|---|---|
| Número de alunos | Até ~2.000 (o JSON inteiro carrega na memória) |
| Fotos | Até ~500MB no repositório (GitHub impõe 1GB por repo) |
| Usuários de acesso | Sem limite (todos no `config.json`) |
| Turmas | Sem limite |

### Dicas para manter o sistema rápido

1. **Comprima as fotos** antes de adicionar ao repositório:
   ```bash
   # Instalar ImageMagick
   sudo apt install imagemagick -y

   # Redimensionar e comprimir todas as fotos para 240x320px
   for f in images/*.jpg; do
     convert "$f" -resize 240x320^ -gravity center -extent 240x320 -quality 80 "$f"
   done
   ```

2. **Mantenha apenas alunos ativos** — remova alunos transferidos/formados periodicamente

3. **Use o campo `status: "Inativo"`** para alunos que não devem aparecer sem removê-los do sistema

### Evolução futura (se necessário)

Se o sistema crescer muito ou precisar de mais funcionalidades:

| Necessidade | Solução |
|---|---|
| Edição pelo navegador sem Git | Netlify CMS ou Decap CMS |
| Mais de 2.000 alunos | Paginar o JSON em múltiplos arquivos |
| Busca muito lenta | Gerar índice de busca no build |
| Upload de fotos sem Git | Cloudinary ou Imgur API (gratuito) |
| Relatórios PDF | Adicionar biblioteca jsPDF ao index.html |

---

*Carômetro Escolar — Centro Educacional SESI 407 — São José do Rio Preto — SP*
*Desenvolvido para uso interno. Todos os dados são restritos à equipe escolar.*
