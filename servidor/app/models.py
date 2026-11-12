"""Modelos ORM: tabelas do banco de dados da locadora.

Três tabelas relacionadas:
    filmes   (1) ---- (N) alugueis (N) ---- (1) clientes
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def agora_utc() -> datetime:
    """Retorna o instante atual em UTC (valor padrão de ``Aluguel.data_aluguel``)."""
    return datetime.now(timezone.utc)


class Filme(Base):
    """Título do acervo da locadora.

    O estado (Disponível/Alugado) não é gravado: é derivado dos aluguéis em
    aberto, evitando que o status e o histórico fiquem inconsistentes.
    """

    __tablename__ = "filmes"

    codigo: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    genero: Mapped[str] = mapped_column(String(50))
    ano: Mapped[int] = mapped_column(Integer)
    capa: Mapped[str] = mapped_column(String(255), default="")

    alugueis: Mapped[list["Aluguel"]] = relationship(
        back_populates="filme",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def status(self) -> str:
        """"Alugado" se existir aluguel sem devolução; caso contrário, "Disponível"."""
        if any(aluguel.data_devolucao is None for aluguel in self.alugueis):
            return "Alugado"
        return "Disponível"


class Cliente(Base):
    """Pessoa cadastrada que pode alugar filmes."""

    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    telefone: Mapped[str] = mapped_column(String(30), default="")
    email: Mapped[str] = mapped_column(String(120), default="")

    alugueis: Mapped[list["Aluguel"]] = relationship(back_populates="cliente")


class Aluguel(Base):
    """Registro de um aluguel: qual cliente levou qual filme, quando e por quantos dias.

    Um aluguel está "em aberto" enquanto ``data_devolucao`` for nula. O índice
    parcial ``ux_aluguel_filme_aberto`` garante, no próprio banco, que um filme
    nunca tenha dois aluguéis em aberto ao mesmo tempo (mesmo com requisições
    simultâneas de vários clientes).
    """

    __tablename__ = "alugueis"
    __table_args__ = (
        CheckConstraint("dias BETWEEN 1 AND 30", name="ck_aluguel_dias"),
        Index(
            "ux_aluguel_filme_aberto",
            "filme_codigo",
            unique=True,
            postgresql_where=text("data_devolucao IS NULL"),
            sqlite_where=text("data_devolucao IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    filme_codigo: Mapped[int] = mapped_column(
        ForeignKey("filmes.codigo", ondelete="CASCADE"), index=True
    )
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    dias: Mapped[int] = mapped_column(Integer)
    data_aluguel: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    data_devolucao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    filme: Mapped["Filme"] = relationship(back_populates="alugueis")
    cliente: Mapped["Cliente"] = relationship(back_populates="alugueis")

    @property
    def data_prevista(self) -> datetime:
        """Data prevista de devolução (``data_aluguel`` + ``dias``)."""
        return self.data_aluguel + timedelta(days=self.dias)

    @property
    def filme_nome(self) -> str:
        """Nome do filme alugado (atalho para exibição)."""
        return self.filme.nome

    @property
    def cliente_nome(self) -> str:
        """Nome do cliente que alugou (atalho para exibição)."""
        return self.cliente.nome
