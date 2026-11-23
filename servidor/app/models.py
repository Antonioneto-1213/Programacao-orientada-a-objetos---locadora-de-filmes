from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Filme(Base):
    __tablename__ = "filmes"

    codigo = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    genero = Column(String)
    ano = Column(Integer)
    capa = Column(String)
    status = Column(String, default="Disponível")

    alugueis = relationship("Aluguel", back_populates="filme")

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    telefone = Column(String)
    email = Column(String)

    alugueis = relationship("Aluguel", back_populates="cliente")

class Aluguel(Base):
    __tablename__ = "alugueis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filme_codigo = Column(Integer, ForeignKey("filmes.codigo"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    data_aluguel = Column(DateTime, default=datetime.utcnow)
    data_devolucao = Column(DateTime, nullable=True)
    status = Column(String, default="Ativo")

    filme = relationship("Filme", back_populates="alugueis")
    cliente = relationship("Cliente", back_populates="alugueis")