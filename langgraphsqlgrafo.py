from langgraph.graph import StateGraph
from typing import TypedDict, List, Any
import networkx as nx
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Estado do agente
class AgentState(TypedDict):
    llm: str
    tipo: str
    n_estoques: int
    n_skus: int
    grafo: nx.DiGraph
    skus: List[str]
    resposta: str
    consistencia: str
    historico: List[str]

# Persistência
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
    registro = EstadoAgente(id=id_sessao, estado=dict(state), consistencia=state.get("consistencia", "⚠️"))
    session.merge(registro)
    session.commit()

# Nós do LangGraph
def gerar_grafo(state: AgentState) -> AgentState:
    estoques = [f"Estoque_{i}" for i in range(state["n_estoques"])]
    skus = [f"SKU_{i}" for i in range(state["n_skus"])]
    G = nx.DiGraph()
    for est in estoques:
        G.add_node(est, tipo="estoque")
    for sku in skus:
        G.add_node(sku, tipo="sku")
        G.add_edge(estoques[sku.__hash__() % state["n_estoques"]], sku)
    state["grafo"] = G
    state["skus"] = skus
    state["historico"].append("grafo_gerado")
    return state

def gerar_resposta(state: AgentState) -> AgentState:
    sku = state["skus"][0]
    grau = len(list(state["grafo"].predecessors(sku)))
    state["resposta"] = f"{sku} está em {grau} estoques."
    state["historico"].append("resposta_gerada")
    return state

def checar_consistencia(state: AgentState) -> AgentState:
    resposta = state["resposta"].lower()
    sku = state["skus"][0]
    grau = len(list(state["grafo"].predecessors(sku)))
    if f"{sku.lower()} está em 3 estoques" in resposta and grau != 3:
        state["consistencia"] = "❌"
    else:
        state["consistencia"] = "✅"
    state["historico"].append(f"consistencia: {state['consistencia']}")
    return state

# Construção do grafo
graph = StateGraph(AgentState)
graph.add_node("gerar_grafo", gerar_grafo)
graph.add_node("gerar_resposta", gerar_resposta)
graph.add_node("checar_consistencia", checar_consistencia)

graph.set_entry_point("gerar_grafo")
graph.add_edge("gerar_grafo", "gerar_resposta")
graph.add_edge("gerar_resposta", "checar_consistencia")

app = graph.compile()
