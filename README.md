# ShopBox

> Sistema de vendas (POS) feito com **Flask** + **SQLite**.

O **ShopBox** é uma aplicação web simples para gestão de vendas (carrinho), stock, utilizadores e relatórios. O projeto usa sessões (Flask-Session) para autenticação e mantém os dados num ficheiro **SQLite** (`database/cripeel.db`).

## Sumário

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como executar localmente](#como-executar-localmente)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Executar](#executar)
- [Acesso e autenticação](#acesso-e-autenticação)
- [Rotas principais (visão geral)](#rotas-principais-visão-geral)
- [Base de dados](#base-de-dados)
- [Notas importantes / boas práticas](#notas-importantes--boas-práticas)
- [Troubleshooting](#troubleshooting)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Funcionalidades

- **Login** por username/password e também por **código/cartão** (`/login2`).
- **Sessões** persistidas em filesystem com `Flask-Session`.
- **Vendas / Carrinho**:
  - Criar novo carrinho (gera `id_vendas` na sessão).
  - Adicionar produtos ao carrinho via barcode (com suporte a `qtd+barcode`).
  - Remover itens do carrinho.
  - Concluir venda com forma de pagamento e cálculo de troco.
  - (Opcional) impressão de ticket (há código para `win32print`, mas está comentado o import).
- **Stock** (módulo dedicado em `route/stock.py`).
- **Admin**:
  - Dashboard.
  - Gestão de utilizadores (criação de user e upload de imagem).
- **Relatórios / gráficos** (blueprints `report` e `chart`).

## Tecnologias

- **Python**
- **Flask**
- **Flask-Session**
- **SQLite** (ficheiro `.db` em `database/cripeel.db`)
- **HTML/Jinja2** (templates)
- **CSS/JS** (assets em `static/`)

## Estrutura do projeto

Visão geral (pode variar conforme a versão do repositório):

- `app.py` — ponto de entrada da aplicação Flask.
- `classes/`
  - `easyLite.py` — classe `SQLiteDB` com helpers para login e queries.
- `route/` — blueprints (módulos de rotas):
  - `admin.py` — rotas administrativas e gestão de utilizadores.
  - `vendas.py` — fluxo principal de vendas/carrinho.
  - `stock.py` — gestão de stock.
  - `report.py` — relatórios.
  - `chart.py` / `chart_.py` — gráficos/estatísticas.
  - `revenda.py` — rotas relacionadas a revenda.
  - `js_routes.py` — endpoints auxiliares consumidos via JS.
- `templates/` — páginas HTML.
- `static/` — assets (CSS/JS/libs/imagens).
- `database/`
  - `cripeel.db` — base de dados SQLite.

## Como executar localmente

### Pré-requisitos

- **Python 3.10+** (recomendado 3.11)
- (Opcional, Windows) se quiser imprimir tickets: dependências do `pywin32` e impressora configurada.

### Instalação

1) Clonar o repositório:

```bash
git clone https://github.com/mr-body/ShopBox.git
cd ShopBox
```

2) Criar e ativar um ambiente virtual:

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Instalar dependências

> Observação: o repositório não possui `requirements.txt` no momento. Instale manualmente:

```bash
pip install flask flask-session
```

Se você identificar outras libs em uso no projeto (por ex. `werkzeug` já vem com Flask), adicione aqui.

### Executar

O servidor é inicializado em `app.py`:

```bash
python app.py
```

Por padrão, a aplicação inicia em:

- `http://localhost:1913`

> Nota: `debug=True` está ativo em `app.py`. Para produção, desative.

## Acesso e autenticação

O projeto usa uma verificação simples de sessão:

- Ao autenticar, define `session['logged_in'] = True` e `session['user'] = user_data`.
- Rotas protegidas usam um decorator `login_required`.
- Rotas admin verificam também `session['user']['accounttype'] == "admin"`.

Rotas principais de autenticação:

- `GET /login` — tela de login.
- `POST /login` — login por username/password.
- `POST /login2` — login por código (busca `username/password` pelo `id` na tabela `users`).
- `POST /logout` — encerra sessão.

## Rotas principais (visão geral)

> **Nota:** abaixo é uma visão geral baseada nos blueprints registados em `app.py`. Veja os ficheiros em `route/` para detalhes.

- `/` — redireciona para dashboard (admin).

### Blueprint: Admin (`/admin`)

- `GET /admin/dashboard/<id>` — dashboard do admin.
- `GET /admin/users` — lista utilizadores.
- `POST /admin/newuser` — cria utilizador (com upload de imagem).

### Blueprint: Vendas (`/vendas`)

- `GET /vendas/` — página principal de vendas.
- `POST /vendas/pesquisa` — pesquisa produtos por nome ou barcode.
- `GET /vendas/new` — cria novo carrinho (session `id_vendas`).
- `GET /vendas/carrinho` — lista itens do carrinho.
- `POST /vendas/totalVendido` — total do carrinho (AJAX).
- `POST /vendas/add_carrinho` — adiciona produto ao carrinho.
- `POST /vendas/lista` — lista itens do carrinho (AJAX).
- `POST /vendas/delete` — remove item do carrinho.
- `GET /vendas/deleteVenda/<id>` — apaga uma venda (exceto a venda ativa da sessão).
- `GET /vendas/pagamento` — tela de pagamento.
- `GET /vendas/concluir/<forma>/<clinete>/<check>` — conclui venda e calcula troco.
- `POST /vendas/feicho` — fecho (resumo) e impressão.
- `POST /vendas/relatorio` — relatório e impressão.

### Outros blueprints

- `/stock/*` — gestão de stock (`route/stock.py`).
- `/report/*` — relatórios (`route/report.py`).
- `/chart/*` — gráficos (`route/chart.py`).
- `/revenda/*` — revenda (`route/revenda.py`).

## Base de dados

A aplicação usa SQLite via a classe `SQLiteDB` (`classes/easyLite.py`).

- Ficheiro: `database/cripeel.db`
- Operações:
  - `login(username, password)` — consulta tabela `users`.
  - `select_data(query)` — queries SELECT.
  - `execute_query(query)` — INSERT/UPDATE/DELETE.

Tabelas vistas no código (podem existir mais):

- `users` — utilizadores
- `stock` — produtos/itens
- `vendas` — vendas
- `vendidos` — itens vendidos por venda
- `abertura` — status de abertura/fecho
- `entrada` — entradas/itens auxiliares
- `cliente` / `lista_divitas` — gestão de clientes/dívidas (ver `app.py` rota `/clienteAdd`)

## Notas importantes / boas práticas

- **Segurança**:
  - O `secret_key` está hardcoded em `app.py`. Em produção, use variáveis de ambiente.
  - Há várias queries SQL construídas com f-strings (risco de SQL injection). Preferir parâmetros (`?`) como no método `login()`.
- **Ambiente virtual no repositório**:
  - Existe uma pasta `venv/` versionada no repo. Recomenda-se **não** versionar ambientes virtuais (adicione ao `.gitignore`).
- **Deploy**:
  - Para produção use `gunicorn`/`uwsgi` e configure `debug=False`.

## Troubleshooting

- **Erro: módulo não encontrado**
  - Certifique-se que o venv está ativo e que instalou `flask` e `flask-session`.

- **Não consegue fazer login**
  - Verifique se o ficheiro `database/cripeel.db` existe e contém a tabela `users`.

- **Impressão de ticket (Windows)**
  - O `import win32print` está comentado em `route/vendas.py`. Para usar:
    1) Instale `pywin32`.
    2) Descomente o import.
    3) Garanta impressora padrão configurada.

## Contribuição

1. Faça um fork
2. Crie uma branch com a sua feature/correção
3. Abra um Pull Request

Sugestões de melhorias (boas primeiras issues):

- Criar `requirements.txt` / `pyproject.toml`
- Melhorar segurança (SQL parametrizado, passwords com hash)
- Configuração via `.env`
- Remover `venv/` do repositório

## Licença

Este projeto não possui licença definida no repositório. Se desejar, adicione um ficheiro `LICENSE` (por ex. MIT).
