from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Filme(Base):
    __tablename__ = "filmes"

    codigo = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    genero = Column(String)
    ano = Column(Integer)
    capa = Column(String)
    status = Column(String, default="Disponível")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    telefone = Column(String)
    email = Column(String)