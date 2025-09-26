import pytest
from httpx import AsyncClient
from app.main import app
from app.models import SessionLocal, Usuario, Sessao

@pytest.mark.asyncio
async def test_fluxo_completo():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Cadastro
        email = "integ@teste.com"
        senha = "123456"
        await ac.post("/cadastro", json={"email": email, "senha": senha})

        # 2. Login
        login = await ac.post("/login", json={"email": email, "senha": senha})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Executar agente
        id_sessao = "sessao_integ"
        execucao = await ac.post("/executar", json={"id_sessao": id_sessao}, headers=headers)
        assert execucao.status_code == 200
        assert "consolidado" in execucao.json()
        assert "agente_executado" in execucao.json()["historico"]

        # 4. Consultar sessão
        consulta = await ac.get(f"/sessao/{id_sessao}", headers=headers)
        assert consulta.status_code == 200
        estado = consulta.json()
        assert estado["usuario"] == email
        assert len(estado["consolidado"]) > 0

        # 5. Verificar persistência no banco
        db = SessionLocal()
        sessao = db.query(Sessao).filter_by(id=id_sessao).first()
        assert sessao is not None
        assert "agente_executado" in sessao.estado["historico"]
        db.close()
