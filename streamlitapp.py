# streamlit_app.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from random import sample, randint
import math

# ============================
# Funções principais
# ============================
def gerar_cenario_simulado(tipo="normal", n_estoques=5, n_skus=10):
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []
    for sku in skus:
        vinculados = sample(estoques, randint(2, 3)) if tipo == "normal" else sample(estoques, 1)
        for est in vinculados:
            arestas.append((est, sku))
    return estoques, skus, arestas

def construir_grafo(estoques, skus, arestas):
    G = nx.DiGraph()
    for est in estoques:
        G.add_node(est, tipo="estoque")
    for sku in skus:
        G.add_node(sku, tipo="sku")
    for origem, destino in arestas:
        G.add_edge(origem, destino)
    return G

def adamic_adar(G, s1, s2):
    e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
    comuns = e1 & e2
    score = 0.0
    for est in comuns:
        grau = len(list(G.successors(est)))
        if grau > 1:
            score += 1 / math.log(grau)
    return score

def jaccard(G, s1, s2):
    e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
    inter, uniao = e1 & e2, e1 | e2
    return len(inter) / len(uniao) if uniao else 0.0

def co_ocorrencia(G, s1, s2):
    e1, e2 = set(G.predecessors(s1)), set(G.predecessors(s2))
    return len(e1 & e2)

def normalizar(valores):
    min_val, max_val = min(valores), max(valores)
    return [(v - min_val) / (max_val - min_val + 1e-9) for v in valores]

def matriz_similaridade(G, skus, pesos):
    brutos = []
    for i in range(len(skus)):
        for j in range(i + 1, len(skus)):
            aa = adamic_adar(G, skus[i], skus[j])
            jc = jaccard(G, skus[i], skus[j])
            co = co_ocorrencia(G, skus[i], skus[j])
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

def casos_suspeitos(G, skus, pesos, limiar_sim=0.2, limiar_con=1):
    sim = matriz_similaridade(G, skus, pesos)
    mapa = {sku: [] for sku in skus}
    for s1, s2, score in sim:
        mapa[s1].append(score)
        mapa[s2].append(score)
    suspeitos = []
    for sku in skus:
        media = sum(mapa[sku]) / len(mapa[sku]) if mapa[sku] else 0
        grau = len(list(G.predecessors(sku)))
        if media < limiar_sim or grau <= limiar_con:
            suspeitos.append((sku, round(media, 4), grau))
    return sorted(suspeitos, key=lambda x: x[1])

# ============================
# Interface Streamlit
# ============================
st.title("Análise de SKUs com Grafos")
tipo = st.selectbox("Escolha o tipo de cenário:", ["normal", "suspeito"])
n_estoques = st.slider("Número de estoques", 3, 10, 5)
n_skus = st.slider("Número de SKUs", 5, 20, 10)

if st.button("Gerar cenário"):
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    estoques, skus, arestas = gerar_cenario_simulado(tipo, n_estoques, n_skus)
    G = construir_grafo(estoques, skus, arestas)

    st.subheader("Similaridade entre SKUs")
    sim = matriz_similaridade(G, skus, pesos)
    for s1, s2, score in sim:
        st.write(f"{s1} ↔ {s2} → Escore: {score}")

    st.subheader("SKUs suspeitos")
    suspeitos = casos_suspeitos(G, skus, pesos)
    for sku, media, grau in suspeitos:
        st.write(f"{sku} → Similaridade média: {media}, Estoques vinculados: {grau}")

    st.subheader("Visualização do Grafo")
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", node_size=800, font_size=10)
    st.pyplot(plt)
