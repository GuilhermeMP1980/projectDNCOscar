# api.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from security import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_token(token: str = Depends(oauth2_scheme)):
    # decodificar e validar token
    return True  # ou lançar HTTPException
