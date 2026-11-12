"""Configuração da conexão com o banco de dados (SQLAlchemy)."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Em produção (Docker) a URL vem da variável de ambiente DATABASE_URL, apontando
# para o contêiner PostgreSQL. O SQLite local serve apenas para desenvolvimento.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./locadora_dev.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


def get_db() -> Iterator[Session]:
    """Dependência do FastAPI: abre uma sessão por requisição e a fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
