from langgraph.graph import StateGraph
from typing import TypedDict
import networkx as nx

# Estado compartilhado
class ConsultaState(TypedDict):
    grafo: nx.DiGraph
    resultado: str
    sku1: str
    sku2: str
    estoque: str

# Funções de consulta
def consultar_skus_por_estoque(state: ConsultaState) -> ConsultaState:
    G = state["grafo"]
    estoque = state["estoque"]
    if estoque not in G:
        return {**state, "resultado": f"Estoque '{estoque}' não encontrado."}
    skus = list(G.successors(estoque))
    return {**state, "resultado": f"SKUs em {estoque}: {', '.join(skus)}"}

def consultar_estoques_compartilhados(state: ConsultaState) -> ConsultaState:
    G = state["grafo"]
    s1, s2 = state["sku1"], state["sku2"]
    if s1 not in G or s2 not in G:
        return {**state, "resultado": "Um dos SKUs não existe no grafo."}
    e1 = set(G.predecessors(s1))
    e2 = set(G.predecessors(s2))
    comuns = e1 & e2
    return {**state, "resultado": f"Estoques compartilhados entre {s1} e {s2}: {', '.join(comuns)}"}

def consultar_similaridade(state: ConsultaState) -> ConsultaState:
    from intocaveis.core import adamic_adar_skus, jaccard_similarity
    G = state["grafo"]
    s1, s2 = state["sku1"], state["sku2"]
    aa = adamic_adar_skus(G, s1, s2)
    jc = jaccard_similarity(set(G.predecessors(s1)), set(G.predecessors(s2)))
    return {**state, "resultado": f"Adamic-Adar: {aa:.4f}, Jaccard: {jc:.4f}"}

def listar_suspeitos(state: ConsultaState) -> ConsultaState:
    from intocaveis.core import casos_suspeitos
    G = state["grafo"]
    skus = [n for n, d in G.nodes(data=True) if d.get("tipo") == "sku"]
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    suspeitos = casos_suspeitos(G, skus, pesos)
    linhas = [f"{s['sku']} → Similaridade média: {s['media_similaridade']}, Estoques: {s['estoques_vinculados']}" for s in suspeitos]
    return {**state, "resultado": "\n".join(linhas)}

# Construção do grafo LangGraph
grafo = StateGraph(ConsultaState)
grafo.add_node("consultar_skus_por_estoque", consultar_skus_por_estoque)
grafo.add_node("consultar_estoques_compartilhados", consultar_estoques_compartilhados)
grafo.add_node("consultar_similaridade", consultar_similaridade)
grafo.add_node("listar_suspeitos", listar_suspeitos)

# Você pode definir pontos de entrada diferentes para cada tipo de consulta
grafo.set_entry_point("consultar_skus_por_estoque")  # ou outro conforme o uso

app = grafo.compile()
