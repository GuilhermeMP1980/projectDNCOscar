from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("POSTGRES_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Registro(Base):
    __tablename__ = "registros"
    id = Column(Integer, primary_key=True, index=True)
    pergunta = Column(Text)
    resposta = Column(Text)
    fontes = Column(Text)  # Pode ser JSON serializado

Base.metadata.create_all(bind=engine)

def salvar_em_postgres(pergunta, resposta, fontes):
    db = SessionLocal()
    registro = Registro(pergunta=pergunta, resposta=resposta, fontes=str(fontes))
    db.add(registro)
    db.commit()
    db.close()
