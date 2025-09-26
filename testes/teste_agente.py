from app.main import agente

def test_agente_execucao():
    estado = {"historico": [], "usuario": "teste@exemplo.com"}
    resultado = agente.invoke(estado)
    assert "consolidado" in resultado
    assert isinstance(resultado["consolidado"], list)
    assert "agente_executado" in resultado["historico"]
