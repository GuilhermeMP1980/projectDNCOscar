# agente_skus.py
from langgraph.graph import StateGraph
from typing import TypedDict
import networkx as nx
import random
import math

# ============================
# 1. Estado compartilhado
# ============================
class AgentState(TypedDict):
    tipo: str
    n_estoques: int
    n_skus: int
    pesos: dict
    estoques: list
    skus: list
    arestas: list
    grafo: nx.DiGraph
    similaridades: list
    suspeitos: list
    resposta: str

# ============================
# 2. Funções de cada nó
# ============================
def gerar_cenario_node(state: AgentState) -> AgentState:
    tipo = state["tipo"]
    n_estoques = state["n_estoques"]
    n_skus = state["n_skus"]
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []
    for sku in skus:
        vinculados = random.sample(estoques, random.randint(2, 3)) if tipo == "normal" else random.sample(estoques, 1)
        for est in vinculados:
            arestas.append((est, sku))
    return {**state, "estoques": estoques, "skus": skus, "arestas": arestas}

def construir_grafo_node(state: AgentState) -> AgentState:
    G = nx.DiGraph()
    for est in state["estoques"]:
        G.add_node(est, tipo="estoque")
    for sku in state["skus"]:
        G.add_node(sku, tipo="sku")
    for origem, destino in state["arestas"]:
        G.add_edge(origem, destino)
    return {**state, "grafo": G}

def calcular_similaridade_node(state: AgentState) -> AgentState:
    G = state["grafo"]
    skus = state["skus"]
    pesos = state["pesos"]

    def adamic_adar(s1, s2):
        e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
        comuns = e1 & e2
        score = 0.0
        for est in comuns:
            grau = len(list(G.successors(est)))
            if grau > 1:
                score += 1 / math.log(grau)
        return score

    def jaccard(s1, s2):
        e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
        inter, uniao = e1 & e2, e1 | e2
        return len(inter) / len(uniao) if uniao else 0.0

    def co_ocorrencia(s1, s2):
        e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
        return len(e1 & e2)

    def normalizar(valores):
        min_val, max_val = min(valores), max(valores)
        return [(v - min_val) / (max_val - min_val + 1e-9) for v in valores]

    brutos = []
    for i in range(len(skus)):
        for j in range(i + 1, len(skus)):
            aa = adamic_adar(skus[i], skus[j])
            jc = jaccard(skus[i], skus[j])
            co = co_ocorrencia(skus[i], skus[j])
            brutos.append((skus[i], skus[j], aa, jc, co))

    aa_vals = normalizar([b[2] for b in brutos])
    jc_vals = normalizar([b[3] for b in brutos])
    co_vals = normalizar([b[4] for b in brutos])

    resultados = []
    for i, b in enumerate(brutos):
        escore = (
            pesos["adamic_adar"] * aa_vals[i] +
            pesos["jaccard"] * jc_vals[i] +
            pesos["co_ocorrencia"] * co_vals[i]
        )
        resultados.append((b[0], b[1], round(escore, 4)))

    return {**state, "similaridades": sorted(resultados, key=lambda x: -x[2])}

def detectar_suspeitos_node(state: AgentState) -> AgentState:
    G = state["grafo"]
    skus = state["skus"]
    pesos = state["pesos"]
    similaridades = state["similaridades"]

    mapa = {sku: [] for sku in skus}
    for s1, s2, score in similaridades:
        mapa[s1].append(score)
        mapa[s2].append(score)

    suspeitos = []
    for sku in skus:
        media = sum(mapa[sku]) / len(mapa[sku]) if mapa[sku] else 0
        grau = len(list(G.predecessors(sku)))
        if media < 0.2 or grau <= 1:
            suspeitos.append((sku, round(media, 4), grau))

    return {**state, "suspeitos": sorted(suspeitos, key=lambda x: x[1])}

def responder_node(state: AgentState) -> AgentState:
    linhas = ["🔗 Similaridades entre SKUs:"]
    for s1, s2, score in state["similaridades"]:
        linhas.append(f"{s1} ↔ {s2} → Escore: {score}")
    linhas.append("\n🚨 SKUs suspeitos:")
    for sku, media, grau in state["suspeitos"]:
        linhas.append(f"{sku} → Similaridade média: {media}, Estoques vinculados: {grau}")
    return {**state, "resposta": "\n".join(linhas)}

# ============================
# 3. Construção do grafo LangGraph
# ============================
graph = StateGraph(AgentState)
graph.add_node("gerar_cenario", gerar_cenario_node)
graph.add_node("construir_grafo", construir_grafo_node)
graph.add_node("calcular_similaridade", calcular_similaridade_node)
graph.add_node("detectar_suspeitos", detectar_suspeitos_node)
graph.add_node("responder", responder_node)

graph.set_entry_point("gerar_cenario")
graph.add_edge("gerar_cenario", "construir_grafo")
graph.add_edge("construir_grafo", "calcular_similaridade")
graph.add_edge("calcular_similaridade", "detectar_suspeitos")
graph.add_edge("detectar_suspeitos", "responder")

app = graph.compile()

# ============================
# 4. Execução do agente
# ============================
if __name__ == "__main__":
    estado_inicial = {
        "tipo": "suspeito",  # ou "normal"
        "n_estoques": 5,
        "n_skus": 10,
        "pesos": {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    }
    resultado = app.invoke(estado_inicial)
    print(resultado["resposta"])
