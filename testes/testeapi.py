import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_cadastro_e_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/cadastro", json={"email": "teste@exemplo.com", "senha": "123456"})
        assert r.status_code == 200

        r = await ac.post("/login", json={"email": "teste@exemplo.com", "senha": "123456"})
        assert r.status_code == 200
        assert "access_token" in r.json()

@pytest.mark.asyncio
async def test_execucao_agente():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login = await ac.post("/login", json={"email": "teste@exemplo.com", "senha": "123456"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await ac.post("/executar", json={"id_sessao": "sessao_test"}, headers=headers)
        assert r.status_code == 200
        assert "historico" in r.json()
