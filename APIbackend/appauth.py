from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "sua-chave-secreta"
ALGORITHM = "HS256"
EXP_MIN = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha): return pwd_context.hash(senha)
def verificar_senha(senha, hash): return pwd_context.verify(senha, hash)
def criar_token(email):
    exp = datetime.utcnow() + timedelta(minutes=EXP_MIN)
    return jwt.encode({"sub": email, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)
def validar_token(token): 
    try: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    except JWTError: return None
