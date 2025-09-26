import pytest
from httpx import AsyncClient
from app.main import app
from app.models import SessionLocal, Sessao

@pytest.mark.asyncio
async def test_fluxo_fraude_e2e():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Cadastro e login
        email = "fraude@teste.com"
        senha = "fraude123"
        await ac.post("/cadastro", json={"email": email, "senha": senha})
        login = await ac.post("/login", json={"email": email, "senha": senha})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Executar agente com dados suspeitos
        id_sessao = "sessao_fraude"
        execucao = await ac.post("/executar", json={"id_sessao": id_sessao}, headers=headers)
        assert execucao.status_code == 200
        estado = execucao.json()

        # 3. Verificar se há padrões suspeitos nos dados consolidados
        df = estado.get("consolidado", [])
        suspeitos = [linha for linha in df if linha.get("valor", 0) > 10000 or linha.get("quantidade", 0) > 100]
        assert len(suspeitos) > 0, "Nenhum padrão suspeito encontrado"

        # 4. Consultar sessão e validar persistência
        consulta = await ac.get(f"/sessao/{id_sessao}", headers=headers)
        assert consulta.status_code == 200
        estado_salvo = consulta.json()
        assert estado_salvo["usuario"] == email
        assert "agente_executado" in estado_salvo["historico"]

        # 5. Verificar persistência no banco
        db = SessionLocal()
        sessao = db.query(Sessao).filter_by(id=id_sessao).first()
        assert sessao is not None
        assert "agente_executado" in sessao.estado["historico"]
        db.close()
