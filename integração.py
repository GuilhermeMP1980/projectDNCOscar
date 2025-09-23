from langgraph.graph import StateGraph
from typing import TypedDict
import networkx as nx

# ============================
# 1. Definição do estado
# ============================
class SKUState(TypedDict):
    estoques: list
    skus: list
    arestas: list
    grafo: nx.DiGraph
    similaridades: list
    suspeitos: list

# ============================
# 2. Funções de cada nó
# ============================
def gerar_dados_node(state: SKUState) -> SKUState:
    estoques, skus, arestas = gerar_dados()
    return {**state, "estoques": estoques, "skus": skus, "arestas": arestas}

def construir_grafo_node(state: SKUState) -> SKUState:
    G = construir_grafo(state["estoques"], state["skus"], state["arestas"])
    return {**state, "grafo": G}

def calcular_similaridade_node(state: SKUState) -> SKUState:
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    sim = matriz_similaridade(state["grafo"], state["skus"], pesos)
    return {**state, "similaridades": sim}

def detectar_suspeitos_node(state: SKUState) -> SKUState:
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    suspeitos = casos_suspeitos(state["grafo"], state["skus"], pesos)
    return {**state, "suspeitos": suspeitos}

def responder_node(state: SKUState) -> str:
    resposta = "🔗 Similaridades:\n"
    for s1, s2, score in state["similaridades"]:
        resposta += f"{s1} ↔ {s2} → Escore: {score}\n"
    resposta += "\n Casos suspeitos:\n"
    for s in state["suspeitos"]:
        resposta += f"{s['sku']} → Similaridade média: {s['media_similaridade']}, Estoques vinculados: {s['estoques_vinculados']}\n"
    return resposta

# ============================
# 3. Construção do grafo LangGraph
# ============================
graph = StateGraph(SKUState)
graph.add_node("gerar_dados", gerar_dados_node)
graph.add_node("construir_grafo", construir_grafo_node)
graph.add_node("calcular_similaridade", calcular_similaridade_node)
graph.add_node("detectar_suspeitos", detectar_suspeitos_node)
graph.add_node("responder", responder_node)

graph.set_entry_point("gerar_dados")
graph.add_edge("gerar_dados", "construir_grafo")
graph.add_edge("construir_grafo", "calcular_similaridade")
graph.add_edge("calcular_similaridade", "detectar_suspeitos")
graph.add_edge("detectar_suspeitos", "responder")

app = graph.compile()

# ============================
# 4. Execução
# ============================
resposta_final = app.invoke({})
print(resposta_final)
