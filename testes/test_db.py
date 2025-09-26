from app.models import Usuario, Sessao
from sqlalchemy.orm import Session
from app.main import SessionLocal

def test_usuario_criacao():
    db: Session = SessionLocal()
    user = Usuario(email="teste@db.com", senha_hash="hash")
    db.add(user)
    db.commit()
    assert db.query(Usuario).filter_by(email="teste@db.com").first() is not None
    db.close()
