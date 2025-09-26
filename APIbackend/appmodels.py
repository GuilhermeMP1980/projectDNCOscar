from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    email = Column(String, primary_key=True)
    senha_hash = Column(String)

class Sessao(Base):
    __tablename__ = "sessoes"
    id = Column(String, primary_key=True)
    estado = Column(JSON)
