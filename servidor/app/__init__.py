from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, database
from pydantic import BaseModel, ConfigDict

# Inicializa o banco de dados
database.init_db()

app = FastAPI(title="API Locadora de Filmes")

# Dependência para pegar a sessão do DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Schemas (Atualizados para V2) ---
class FilmeSchema(BaseModel):
    codigo: Optional[int] = None
    nome: str
    genero: str
    ano: int
    capa: str
    status: str = "Disponível"

    model_config = ConfigDict(from_attributes=True)

class ClienteSchema(BaseModel):
    nome: str
    telefone: str
    email: str

    model_config = ConfigDict(from_attributes=True)

# --- Rotas Filmes ---
@app.get("/filmes", response_model=List[FilmeSchema])
def get_filmes(db: Session = Depends(get_db)):
    return db.query(models.Filme).all()

@app.post("/filmes", response_model=FilmeSchema)
def criar_filme(filme: FilmeSchema, db: Session = Depends(get_db)):
    # Na v2 usamos model_dump() ao invés de dict()
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
    db.delete(db_filme)
    db.commit()
    return {"message": "Filme removido"}

# --- Rotas Clientes ---
@app.get("/clientes", response_model=List[ClienteSchema])
def get_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()

@app.post("/clientes", response_model=ClienteSchema)
def criar_cliente(cliente: ClienteSchema, db: Session = Depends(get_db)):
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente