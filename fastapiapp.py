# fastapi_app.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from agente import app as agente_grafo, salvar_estado, session, EstadoAgente

app = FastAPI()

class Entrada(BaseModel):
    llm: str
    tipo: str = "normal"
    n_estoques: int = 5
    n_skus: int = 10

@app.post("/executar")
def executar_agente(entrada: Entrada):
    estado_inicial = {
        "llm": entrada.llm,
        "tipo": entrada.tipo,
        "n_estoques": entrada.n_estoques,
        "n_skus": entrada.n_skus,
        "pesos": {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2},
        "historico": []
    }
    final_state = agente_grafo.invoke(estado_inicial)
    salvar_estado(final_state)
    return {"resposta": final_state["resposta"], "consistencia": final_state.get("consistencia", "⚠️")}

@app.get("/sessao/{id}")
def recuperar_sessao(id: str):
    sessao = session.get(EstadoAgente, id)
    if not sessao:
        return {"erro": "Sessão não encontrada"}
    return {"estado": sessao.estado, "consistencia": sessao.consistencia}

@app.get("/saude")
def saude():
    return {"status": "ok"}
