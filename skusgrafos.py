import networkx as nx
import random
import math

# 1. Gerar dados simulados
def gerar_dados(n_estoques=3, n_skus=6):
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []

    for sku in skus:
        estoques_relacionados = random.sample(estoques, random.randint(1, n_estoques))
        for est in estoques_relacionados:
            arestas.append((est, sku))
    return estoques, skus, arestas

# 2. Construir grafo
def construir_grafo(estoques, skus, arestas):
    G = nx.DiGraph()
    for est in estoques:
        G.add_node(est, tipo="estoque")
    for sku in skus:
        G.add_node(sku, tipo="sku")
    for origem, destino in arestas:
        G.add_edge(origem, destino, tipo="contém")
    return G

# 3. Métrica Adamic-Adar
def adamic_adar_skus(G, sku1, sku2):
    e1 = set(G.predecessors(sku1))
    e2 = set(G.predecessors(sku2))
    comuns = e1 & e2
    score = 0.0
    for estoque in comuns:
        grau = len(list(G.successors(estoque)))
        if grau > 1:
            score += 1 / math.log(grau)
    return score

# 4. Métrica Jaccard
def jaccard_skus(G, sku1, sku2):
    e1 = set(G.predecessors(sku1))
    e2 = set(G.predecessors(sku2))
    intersecao = e1 & e2
    uniao = e1 | e2
    return len(intersecao) / len(uniao) if uniao else 0.0

# 5. Co-ocorrência simples
def co_ocorrencia(G, sku1, sku2):
    e1 = set(G.predecessors(sku1))
    e2 = set(G.predecessors(sku2))
    return len(e1 & e2)

# 6. Normalização
def normalizar(valores):
    min_val = min(valores)
    max_val = max(valores)
    return [(v - min_val) / (max_val - min_val + 1e-9) for v in valores]

# 7. Combinação de métricas
def escore_composto(sku1, sku2, G, pesos):
    aa = adamic_adar_skus(G, sku1, sku2)
    jc = jaccard_skus(G, sku1, sku2)
    co = co_ocorrencia(G, sku1, sku2)
    return {"sku1": sku1, "sku2": sku2, "adamic_adar": aa, "jaccard": jc, "co_ocorrencia": co}

# 8. Matriz de similaridade
def matriz_similaridade(G, skus, pesos):
    brutos = []
    for i in range(len(skus)):
        for j in range(i + 1, len(skus)):
            brutos.append(escore_composto(skus[i], skus[j], G, pesos))

    # Normalizar cada métrica
    aa_vals = normalizar([r["adamic_adar"] for r in brutos])
    jc_vals = normalizar([r["jaccard"] for r in brutos])
    co_vals = normalizar([r["co_ocorrencia"] for r in brutos])

    # Combinar com pesos
    resultados = []
    for i, r in enumerate(brutos):
        escore = (
            pesos["adamic_adar"] * aa_vals[i] +
            pesos["jaccard"] * jc_vals[i] +
            pesos["co_ocorrencia"] * co_vals[i]
        )
        resultados.append((r["sku1"], r["sku2"], round(escore, 4)))
    return sorted(resultados, key=lambda x: -x[2])

# 9. Execução
if __name__ == "__main__":
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    estoques, skus, arestas = gerar_dados()
    G = construir_grafo(estoques, skus, arestas)
    similaridades = matriz_similaridade(G, skus, pesos)

    print("Similaridade entre pares de SKUs:")
    for s1, s2, score in similaridades:
        print(f"{s1} ↔ {s2} → Escore: {score}")
