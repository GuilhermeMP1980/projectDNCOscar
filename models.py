from sqlalchemy import Column, String
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    email = Column(String, primary_key=True, index=True)
    senha_hash = Column(String)
