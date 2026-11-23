from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, database
from pydantic import BaseModel, ConfigDict


database.init_db()

app = FastAPI(title="API Locadora de Filmes")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FilmeSchema(BaseModel):
    codigo: Optional[int] = None
    nome: str
    genero: str
    ano: int
    capa: str
    status: str = "Disponível"

    model_config = ConfigDict(from_attributes=True)

class ClienteSchema(BaseModel):
    id: Optional[int] = None
    nome: str
    telefone: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class AluguelCreateSchema(BaseModel):
    filme_codigo: int
    cliente_id: int

class AluguelSchema(BaseModel):
    id: int
    filme_codigo: int
    cliente_id: int
    data_aluguel: datetime
    data_devolucao: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


@app.get("/filmes", response_model=List[FilmeSchema])
def get_filmes(db: Session = Depends(get_db)):
    return db.query(models.Filme).all()

@app.post("/filmes", response_model=FilmeSchema)
def criar_filme(filme: FilmeSchema, db: Session = Depends(get_db)):
    db_filme = models.Filme(**filme.model_dump())
    db.add(db_filme)
    db.commit()
    db.refresh(db_filme)
    return db_filme

@app.put("/filmes/{codigo}")
def atualizar_status_filme(codigo: int, status: str, db: Session = Depends(get_db)):
    db_filme = db.query(models.Filme).filter(models.Filme.codigo == codigo).first()
    if not db_filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    db_filme.status = status
    db.commit()
    return {"message": "Status atualizado"}

@app.delete("/filmes/{codigo}")
def remover_filme(codigo: int, db: Session = Depends(get_db)):
    db_filme = db.query(models.Filme).filter(models.Filme.codigo == codigo).first()
    if not db_filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
 
    db.query(models.Aluguel).filter(models.Aluguel.filme_codigo == codigo).delete()
    
    db.delete(db_filme)
    db.commit()
    return {"message": "Filme removido com sucesso"}

@app.get("/clientes", response_model=List[ClienteSchema])
def get_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()

@app.post("/clientes", response_model=ClienteSchema)
def criar_cliente(cliente: ClienteSchema, db: Session = Depends(get_db)):
    db_cliente = models.Cliente(**cliente.model_dump(exclude={"id"}))
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@app.get("/alugueis", response_model=List[AluguelSchema])
def get_alugueis(db: Session = Depends(get_db)):
    return db.query(models.Aluguel).all()

@app.post("/alugueis", response_model=AluguelSchema)
def criar_aluguel(aluguel: AluguelCreateSchema, db: Session = Depends(get_db)):
    db_filme = db.query(models.Filme).filter(models.Filme.codigo == aluguel.filme_codigo).first()
    if not db_filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    if db_filme.status != "Disponível":
        raise HTTPException(status_code=400, detail="Filme já está alugado")

    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == aluguel.cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    novo_aluguel = models.Aluguel(
        filme_codigo=aluguel.filme_codigo,
        cliente_id=aluguel.cliente_id
    )
    db_filme.status = "Alugado"
    db.add(novo_aluguel)
    db.commit()
    db.refresh(novo_aluguel)
    return novo_aluguel

@app.put("/alugueis/{aluguel_id}/devolver", response_model=AluguelSchema)
def devolver_aluguel(aluguel_id: int, db: Session = Depends(get_db)):
    db_aluguel = db.query(models.Aluguel).filter(models.Aluguel.id == aluguel_id).first()
    if not db_aluguel:
        raise HTTPException(status_code=404, detail="Aluguel não encontrado")
    if db_aluguel.status == "Devolvido":
        raise HTTPException(status_code=400, detail="Este aluguel já foi devolvido")

    db_aluguel.status = "Devolvido"
    db_aluguel.data_devolucao = datetime.utcnow()

    db_filme = db.query(models.Filme).filter(models.Filme.codigo == db_aluguel.filme_codigo).first()
    if db_filme:
        db_filme.status = "Disponível"

    db.commit()
    db.refresh(db_aluguel)
    return db_aluguel