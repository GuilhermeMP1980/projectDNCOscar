from langgraph.graph import StateGraph
from typing import TypedDict, List, Any
import networkx as nx
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================
# 1. Estado compartilhado
# ============================
class AgentState(TypedDict):
    llm: str
    resposta: str
    grafo: nx.DiGraph
    skus: List[str]
    suspeitos: List[Any]
    consistencia: str
    inconsistencias: List[str]
    historico: List[str]

# ============================
# 2. Persistência com PostgreSQL
# ============================
Base = declarative_base()

class EstadoAgente(Base):
    __tablename__ = "estado_agente"
    id = Column(String, primary_key=True)
    estado = Column(JSON)
    consistencia = Column(String)

engine = create_engine("postgresql+psycopg2://usuario:senha@localhost:5432/meubanco")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def salvar_estado(state: AgentState, id_sessao: str = "sessao_001"):
    registro = EstadoAgente(
        id=id_sessao,
        estado=dict(state),
        consistencia=state.get("consistencia", "⚠️")
    )
    session.merge(registro)
    session.commit()

# ============================
# 3. Função de checagem de consistência
# ============================
def checar_consistencia(state: AgentState) -> AgentState:
    resposta = state["resposta"].lower()
    inconsistencias = []

    for sku, media, grau in state.get("suspeitos", []):
        if f"{sku.lower()} está em 3 estoques" in resposta and grau != 3:
            inconsistencias.append(f"Inconsistência: {sku} tem grau {grau}, não 3.")

    state["consistencia"] = "✅" if not inconsistencias else "❌"
    state["inconsistencias"] = inconsistencias
    state["historico"].append(f"checagem_consistencia: {state['consistencia']}")
    return state

# ============================
# 4. Nó de resposta final
# ============================
def responder_final(state: AgentState) -> AgentState:
    print("\n Resposta do agente:")
    print(state["resposta"])
    print("\n Consistência:", state["consistencia"])
    if state["inconsistencias"]:
        print("\n Inconsistências detectadas:")
        for inc in state["inconsistencias"]:
            print("-", inc)
    print("\n Histórico:")
    for h in state["historico"]:
        print("-", h)
    salvar_estado(state)
    return state

# ============================
# 5. Simulação de resposta do LLM
# ============================
def gerar_resposta_simulada(state: AgentState) -> AgentState:
    state["resposta"] = "SKU_3 está em 3 estoques e tem escore baixo."
    state["historico"].append("resposta_simulada")
    return state

# ============================
# 6. Construção do grafo LangGraph
# ============================
graph = StateGraph(AgentState)
graph.add_node("resposta_simulada", gerar_resposta_simulada)
graph.add_node("checar_consistencia", checar_consistencia)
graph.add_node("responder_final", responder_final)

graph.set_entry_point("resposta_simulada")
graph.add_edge("resposta_simulada", "checar_consistencia")
graph.add_edge("checar_consistencia", "responder_final")

app = graph.compile()

# ============================
# 7. Execução do agente
# ============================
if __name__ == "__main__":
    G = nx.DiGraph()
    G.add_node("SKU_3", tipo="sku")
    G.add_edge("Estoque_1", "SKU_3")

    estado_inicial = {
        "llm": "Explique o status do SKU_3",
        "grafo": G,
        "skus": ["SKU_3"],
        "suspeitos": [("SKU_3", 0.12, 1)],
        "historico": []
    }

    app.invoke(estado_inicial)
