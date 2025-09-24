from langgraph.graph import StateGraph
from typing import TypedDict
import networkx as nx
import random
import math

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
    skus: list
    resultado_bruto: any
    resposta: str

# ============================
# 2. Funções de decisão e execução
# ============================
def decidir_acao_node(state: AgentState) -> str:
    prompt = state["llm"].lower()
    if "gerar" in prompt:
        state["acao"] = "gerar"
        return "executar_gerar"
    elif "comparar" in prompt or "similaridade" in prompt:
        state["acao"] = "comparar"
        return "executar_comparar"
    elif "suspeitos" in prompt or "detectar" in prompt:
        state["acao"] = "detectar"
        return "executar_detectar"
    else:
        state["acao"] = "desconhecida"
        state["resposta"] = "Desculpe, não entendi sua solicitação."
        return "responder_erro"

def executar_gerar(state: AgentState) -> AgentState:
    tipo = state.get("tipo", "normal")
    n_estoques = state.get("n_estoques", 5)
    n_skus = state.get("n_skus", 10)
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []
    for sku in skus:
        vinculados = random.sample(estoques, random.randint(2, 3)) if tipo == "normal" else random.sample(estoques, 1)
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
    return state

def executar_comparar(state: AgentState) -> AgentState:
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
    state["resultado_bruto"] = sorted(resultados, key=lambda x: -x[2])
    return state

def executar_detectar(state: AgentState) -> AgentState:
    G = state["grafo"]
    skus = state["skus"]
    pesos = state["pesos"]
    sim = executar_comparar(state)["resultado_bruto"]
    mapa = {sku: [] for sku in skus}
    for s1, s2, score in sim:
        mapa[s1].append(score)
        mapa[s2].append(score)
    suspeitos = []
    for sku in skus:
        media = sum(mapa[sku]) / len(mapa[sku]) if mapa[sku] else 0
        grau = len(list(G.predecessors(sku)))
        if media < 0.2 or grau <= 1:
            suspeitos.append((sku, round(media, 4), grau))
    state["resultado_bruto"] = sorted(suspeitos, key=lambda x: x[1])
    return state

def sumarizar_resultado(state: AgentState) -> AgentState:
    bruto = state.get("resultado_bruto", "")
    if isinstance(bruto, list):
        linhas = [f"- {linha}" for linha in bruto]
        state["resposta"] = "\n".join(linhas)
    else:
        state["resposta"] = str(bruto)
    return state

def responder_final(state: AgentState) -> AgentState:
    print("\n Resposta do agente:\n")
    print(state["resposta"])
    return state

def responder_erro(state: AgentState) -> AgentState:
    print("\n Erro de interpretação:\n")
    print(state["resposta"])
    return state

# ============================
# 3. Construção do grafo LangGraph
# ============================
graph = StateGraph(AgentState)
graph.add_node("decidir_acao", decidir_acao_node)
graph.add_node("executar_gerar", executar_gerar)
graph.add_node("executar_comparar", executar_comparar)
graph.add_node("executar_detectar", executar_detectar)
graph.add_node("sumarizar_resultado", sumarizar_resultado)
graph.add_node("responder_final", responder_final)
graph.add_node("responder_erro", responder_erro)

graph.set_entry_point("decidir_acao")
graph.add_edge("executar_gerar", "sumarizar_resultado")
graph.add_edge("executar_comparar", "sumarizar_resultado")
graph.add_edge("executar_detectar", "sumarizar_resultado")
graph.add_edge("sumarizar_resultado", "responder_final")

app = graph.compile()

# ============================
# 4. Execução do agente
# ============================
if __name__ == "__main__":
    entrada = input("Digite sua pergunta ou comando: ")
    estado_inicial = {
        "llm": entrada,
        "tipo": "suspeito",
        "n_estoques": 5,
        "n_skus": 10,
        "pesos": {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    }
    app.invoke(estado_inicial)
