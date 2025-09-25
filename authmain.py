from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Usuario, Base
from auth import gerar_hash, verificar_senha, criar_token, validar_token

Base.metadata.create_all(bind=engine)
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Credenciais(BaseModel):
    email: str
    senha: str

@app.post("/cadastro")
def cadastrar_usuario(cred: Credenciais, db: Session = Depends(get_db)):
    if db.query(Usuario).filter_by(email=cred.email).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    novo = Usuario(email=cred.email, senha_hash=gerar_hash(cred.senha))
    db.add(novo)
    db.commit()
    return {"msg": "Usuário cadastrado com sucesso"}

@app.post("/login")
def login(cred: Credenciais, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter_by(email=cred.email).first()
    if not usuario or not verificar_senha(cred.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token(usuario.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protegido")
def rota_protegida(token: str = Depends(oauth2_scheme)):
    email = validar_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return {"msg": f"Acesso autorizado para {email}"}
