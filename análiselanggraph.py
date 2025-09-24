# agente_llm_skus.py
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
    resultado_bruto: any
    resposta: str

# ============================
# 2. Funções de cada nó
# ============================
def decidir_acao_node(state: AgentState) -> AgentState:
    prompt = state["llm"].lower()
    if "gerar cenário" in prompt:
        state["acao"] = "gerar"
    elif "comparar" in prompt or "similaridade" in prompt:
        state["acao"] = "comparar"
    elif "suspeitos" in prompt:
        state["acao"] = "detectar"
    else:
        state["acao"] = "desconhecida"
    return state

def executar_ferramenta_node(state: AgentState) -> AgentState:
    acao = state["acao"]
    tipo = state.get("tipo", "normal")
    n_estoques = state.get("n_estoques", 5)
    n_skus = state.get("n_skus", 10)
    pesos = state.get("pesos", {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2})

    def gerar_cenario():
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
        return G, skus

    def calcular_similaridade(G, skus):
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
        return sorted(resultados, key=lambda x: -x[2])

    def detectar_suspeitos(G, skus, similaridades):
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
        return sorted(suspeitos, key=lambda x: x[1])

    if acao == "gerar":
        G, skus = gerar_cenario()
        state["grafo"] = G
        state["resultado_bruto"] = f"Grafo gerado com {len(G.nodes)} nós e {len(G.edges)} arestas."
    elif acao == "comparar":
        G, skus = gerar_cenario()
        sim = calcular_similaridade(G, skus)
        state["resultado_bruto"] = sim
    elif acao == "detectar":
        G, skus = gerar_cenario()
        sim = calcular_similaridade(G, skus)
        suspeitos = detectar_suspeitos(G, skus, sim)
        state["resultado_bruto"] = suspeitos
    else:
        state["resultado_bruto"] = "Desculpe, não entendi sua solicitação."
    return state

def sumarizar_resultado_node(state: AgentState) -> AgentState:
    bruto = state.get("resultado_bruto", "")
    if isinstance(bruto, list):
        linhas = [f"- {linha}" for linha in bruto]
        state["resposta"] = "\n".join(linhas)
    else:
        state["resposta"] = str(bruto)
    return state

def responder_node(state: AgentState) -> AgentState:
    print("\n🧠 Resposta do agente:\n")
    print(state["resposta"])
    return state

# ============================
# 3. Construção do grafo LangGraph
# ============================
graph = StateGraph(AgentState)
graph.add_node("decidir_acao", decidir_acao_node)
graph.add_node("executar_ferramenta", executar_ferramenta_node)
graph.add_node("sumarizar_resultado", sumarizar_resultado_node)
graph.add_node("responder", responder_node)

graph.set_entry_point("decidir_acao")
graph.add_edge("decidir_acao", "executar_ferramenta")
graph.add_edge("executar_ferramenta", "sumarizar_resultado")
graph.add_edge("sumarizar_resultado", "responder")

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
