# Sistema de Locadora de Filmes

Aplicação desktop desenvolvida em Python (**PySide6**) integrada a uma API REST (**FastAPI**) com banco de dados relacional (**PostgreSQL**) em contêineres **Docker**.

## Tecnologias Utilizadas
- **Frontend:** Python 3, PySide6, Requests
- **Backend:** FastAPI, Uvicorn, SQLAlchemy ORM
- **Banco de Dados:** PostgreSQL 16
- **Infraestrutura:** Docker e Docker Compose

## Estrutura do Projeto
```text
.
├── capas/                  # Imagens de capa dos filmes
├── servidor/               # Código da API (FastAPI, modelos e conexão com o banco)
├── docker-compose.yml      # Configuração dos contêineres da API e do PostgreSQL
├── locadora_de_filmes.py   # Interface gráfica desktop (PySide6)
└── README.md               # Documentação do projeto
```

## Como Executar o Projeto

### 1. Subir a API e o Banco de Dados (Docker)
Com o Docker Desktop em execução, abra o terminal na pasta raiz do projeto e execute:
```bash
docker compose up -d --build
```
A API ficará disponível em `http://127.0.0.1:8000` e a documentação interativa (Swagger) em `http://127.0.0.1:8000/docs`.

### 2. Executar a Interface Desktop
Instale as dependências do frontend (caso ainda não tenha):
```bash
pip install PySide6 requests
```
Em seguida, execute a aplicação:
```bash
python locadora_de_filmes.py
```

## Funcionalidades
- Cadastro, listagem, busca por nome/gênero e remoção de filmes.
- Cadastro e listagem de clientes.
- Registro de aluguéis e devoluções com histórico persistido no PostgreSQL.
- Sincronização de status em tempo real entre a interface e o banco de dados.