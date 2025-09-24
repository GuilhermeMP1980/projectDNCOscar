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
    acao: str
    tipo: str
    n_estoques: int
    n_skus: int
    pesos: dict
    grafo: nx.DiGraph
    skus: List[str]
    similaridades: List[Any]
    suspeitos: List[Any]
    resultado_bruto: Any
    resposta: str
    modelo_usado: str
    historico: List[str]

# ============================
# 2. Persistência com PostgreSQL
# ============================
Base = declarative_base()

class EstadoAgente(Base):
    __tablename__ = "estado_agente"
    id = Column(String, primary_key=True)
    estado = Column(JSON)

engine = create_engine("postgresql+psycopg2://usuario:senha@localhost:5432/meubanco")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

def salvar_estado(state: AgentState, id_sessao: str = "sessao_001"):
    registro = EstadoAgente(id=id_sessao, estado=dict(state))
    session.merge(registro)
    session.commit()

# ============================
# 3. Funções dos nós
# ============================
def decidir_acao_node(state: AgentState) -> str:
    prompt = state["llm"].lower()
    if "gerar" in prompt:
        state["acao"] = "gerar"
        state["historico"].append("decidir_acao: gerar")
        return "executar_gerar"
    elif "comparar" in prompt:
        state["acao"] = "comparar"
        state["historico"].append("decidir_acao: comparar")
        return "executar_comparar"
    elif "suspeitos" in prompt:
        state["acao"] = "detectar"
        state["historico"].append("decidir_acao: detectar")
        return "executar_detectar"
    else:
        state["acao"] = "desconhecida"
        state["resposta"] = "Não entendi sua solicitação."
        state["historico"].append("decidir_acao: desconhecida")
        return "responder_erro"

def executar_gerar(state: AgentState) -> AgentState:
    tipo = state.get("tipo", "normal")
    n_estoques = state.get("n_estoques", 5)
    n_skus = state.get("n_skus", 10)
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []
    for sku in skus:
        vinculados = nx.utils.random_sequence.sample_without_replacement(estoques, 2 if tipo == "normal" else 1)
        for est in vinculados:
            arestas.append((est, sku))
    G = nx.DiGraph()
    for est in estoques:
        G.add_node(est, tipo="estoque")
    for sku in skus:
        G.add_node(sku, tipo="sku")
    for origem, destino in arestas:
        G.add_edge(origem, destino)
    state["grafo"] = G
    state["skus"] = skus
    state["resultado_bruto"] = f"Grafo gerado com {len(G.nodes)} nós e {len(G.edges)} arestas."
    state["historico"].append("executar_gerar")
    return state

def executar_comparar(state: AgentState) -> AgentState:
    state["resultado_bruto"] = "Comparação executada (simulada)."
    state["similaridades"] = [("SKU_1", "SKU_2", 0.85)]
    state["historico"].append("executar_comparar")
    return state

def executar_detectar(state: AgentState) -> AgentState:
    state["resultado_bruto"] = "Detecção executada (simulada)."
    state["suspeitos"] = [("SKU_3", 0.12, 1)]
    state["historico"].append("executar_detectar")
    return state

def responder_final(state: AgentState) -> AgentState:
    print("\n📋 Resposta final:")
    print(state["resultado_bruto"])
    print("\n📜 Histórico:")
    for h in state["historico"]:
        print("-", h)
    state["historico"].append("responder_final")
    salvar_estado(state)
    return state

def responder_erro(state: AgentState) -> AgentState:
    print("\n⚠️ Erro:")
    print(state["resposta"])
    state["historico"].append("responder_erro")
    salvar_estado(state)
    return state

# ============================
# 4. Construção do grafo LangGraph
# ============================
graph = StateGraph(AgentState)
graph.add_node("decidir_acao", decidir_acao_node)
graph.add_node("executar_gerar", executar_gerar)
graph.add_node("executar_comparar", executar_comparar)
graph.add_node("executar_detectar", executar_detectar)
graph.add_node("responder_final", responder_final)
graph.add_node("responder_erro", responder_erro)

graph.set_entry_point("decidir_acao")
graph.add_edge("executar_gerar", "responder_final")
graph.add_edge("executar_comparar", "responder_final")
graph.add_edge("executar_detectar", "responder_final")

app = graph.compile()

# ============================
# 5. Execução do agente
# ============================
if __name__ == "__main__":
    entrada = input("Digite sua pergunta ou comando: ")
    estado_inicial = {
        "llm": entrada,
        "tipo": "normal",
        "n_estoques": 5,
        "n_skus": 10,
        "pesos": {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2},
        "historico": []
    }
    app.invoke(estado_inicial)
