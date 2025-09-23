import networkx as nx
import random
import math

# ============================
# 1. Geração de dados simulados
# ============================
def gerar_dados(n_estoques=3, n_skus=6):
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    arestas = []

    for sku in skus:
        estoques_relacionados = random.sample(estoques, random.randint(1, n_estoques))
        for est in estoques_relacionados:
            arestas.append((est, sku))
    return estoques, skus, arestas

# ============================
# 2. Construção do grafo
# ============================
def construir_grafo(estoques, skus, arestas):
    G = nx.DiGraph()
    for est in estoques:
        G.add_node(est, tipo="estoque")
    for sku in skus:
        G.add_node(sku, tipo="sku")
    for origem, destino in arestas:
        G.add_edge(origem, destino, tipo="contém")
    return G

# ============================
# 3. Métricas de similaridade
# ============================
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

def jaccard_skus(G, sku1, sku2):
    e1 = set(G.predecessors(sku1))
    e2 = set(G.predecessors(sku2))
    intersecao = e1 & e2
    uniao = e1 | e2
    return len(intersecao) / len(uniao) if uniao else 0.0

def co_ocorrencia(G, sku1, sku2):
    e1 = set(G.predecessors(sku1))
    e2 = set(G.predecessors(sku2))
    return len(e1 & e2)

# ============================
# 4. Normalização
# ============================
def normalizar(valores):
    min_val = min(valores)
    max_val = max(valores)
    return [(v - min_val) / (max_val - min_val + 1e-9) for v in valores]

# ============================
# 5. Escore composto por par
# ============================
def escore_composto(sku1, sku2, G, pesos):
    aa = adamic_adar_skus(G, sku1, sku2)
    jc = jaccard_skus(G, sku1, sku2)
    co = co_ocorrencia(G, sku1, sku2)
    return {"sku1": sku1, "sku2": sku2, "adamic_adar": aa, "jaccard": jc, "co_ocorrencia": co}

# ============================
# 6. Matriz de similaridade
# ============================
def matriz_similaridade(G, skus, pesos):
    brutos = []
    for i in range(len(skus)):
        for j in range(i + 1, len(skus)):
            brutos.append(escore_composto(skus[i], skus[j], G, pesos))

    aa_vals = normalizar([r["adamic_adar"] for r in brutos])
    jc_vals = normalizar([r["jaccard"] for r in brutos])
    co_vals = normalizar([r["co_ocorrencia"] for r in brutos])

    resultados = []
    for i, r in enumerate(brutos):
        escore = (
            pesos["adamic_adar"] * aa_vals[i] +
            pesos["jaccard"] * jc_vals[i] +
            pesos["co_ocorrencia"] * co_vals[i]
        )
        resultados.append((r["sku1"], r["sku2"], round(escore, 4)))
    return sorted(resultados, key=lambda x: -x[2])

# ============================
# 7. Identificação de casos suspeitos
# ============================
def casos_suspeitos(G, skus, pesos, limiar_similaridade=0.2, limiar_conectividade=1):
    suspeitos = []
    similaridades = matriz_similaridade(G, skus, pesos)

    escore_por_sku = {sku: [] for sku in skus}
    for s1, s2, score in similaridades:
        escore_por_sku[s1].append(score)
        escore_por_sku[s2].append(score)

    for sku in skus:
        media_similaridade = sum(escore_por_sku[sku]) / len(escore_por_sku[sku]) if escore_por_sku[sku] else 0
        grau_entrada = len(list(G.predecessors(sku)))

        if media_similaridade < limiar_similaridade or grau_entrada <= limiar_conectividade:
            suspeitos.append({
                "sku": sku,
                "media_similaridade": round(media_similaridade, 4),
                "estoques_vinculados": grau_entrada
            })

    return sorted(suspeitos, key=lambda x: x["media_similaridade"])

# ============================
# 8. Execução principal
# ============================
if __name__ == "__main__":
    pesos = {"adamic_adar": 0.5, "jaccard": 0.3, "co_ocorrencia": 0.2}
    estoques, skus, arestas = gerar_dados()
    G = construir_grafo(estoques, skus, arestas)

    print("🔗 Similaridade entre pares de SKUs:")
    similaridades = matriz_similaridade(G, skus, pesos)
    for s1, s2, score in similaridades:
        print(f"{s1} ↔ {s2} → Escore: {score}")

    print("\n🚨 SKUs com comportamento suspeito:")
    suspeitos = casos_suspeitos(G, skus, pesos)
    for s in suspeitos:
        print(f"{s['sku']} → Similaridade média: {s['media_similaridade']}, Estoques vinculados: {s['estoques_vinculados']}")
