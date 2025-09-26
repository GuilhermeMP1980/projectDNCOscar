from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, Usuario, Sessao
from app.auth import *
from app.loader import load_and_clean_data
from app.consolidator import consolidate_data
from langgraph.graph import StateGraph

DATABASE_URL = "postgresql+psycopg2://usuario:senha@db:5432/meubanco"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()

class Credenciais(BaseModel):
    email: str
    senha: str

class Entrada(BaseModel):
    id_sessao: str

def get_db(): db = SessionLocal(); try: yield db; finally: db.close()

# LangGraph
def agente_node(state: dict) -> dict:
    load_and_clean_data()
    df = consolidate_data()
    state["consolidado"] = df.to_dict()
    state["linhas"] = len(df)
    state["historico"].append("agente_executado")
    return state

graph = StateGraph(dict)
graph.add_node("agente", agente_node)
graph.set_entry_point("agente")
agente = graph.compile()

@app.post("/cadastro")
def cadastrar(cred: Credenciais, db: Session = Depends(get_db)):
    if db.query(Usuario).filter_by(email=cred.email).first():
        raise HTTPException(400, "Usuário já existe")
    db.add(Usuario(email=cred.email, senha_hash=gerar_hash(cred.senha)))
    db.commit()
    return {"msg": "Cadastro realizado"}

@app.post("/login")
def login(cred: Credenciais, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(email=cred.email).first()
    if not user or not verificar_senha(cred.senha, user.senha_hash):
        raise HTTPException(401, "Credenciais inválidas")
    return {"access_token": criar_token(user.email), "token_type": "bearer"}

@app.post("/executar")
def executar(entrada: Entrada, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = validar_token(token)
    if not email:
        raise HTTPException(401, "Token inválido")
    estado = {"historico": [], "usuario": email}
    final = agente.invoke(estado)
    db.merge(Sessao(id=entrada.id_sessao, estado=final))
    db.commit()
    return final

@app.get("/sessao/{id}")
def sessao(id: str, db: Session = Depends(get_db)):
    s = db.get(Sessao, id)
    if not s: raise HTTPException(404, "Sessão não encontrada")
    return s.estado

@app.get("/saude")
def saude(): return {"status": "ok"}
