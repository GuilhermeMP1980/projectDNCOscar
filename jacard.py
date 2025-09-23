import networkx as nx

def jaccard_skus(G, sku1, sku2):
    # Verifica se os SKUs existem
    if sku1 not in G or sku2 not in G:
        return 0.0

    # Estoques que contêm cada SKU (nós predecessores)
    estoques_sku1 = set(G.predecessors(sku1))
    estoques_sku2 = set(G.predecessors(sku2))

    # Interseção e união
    intersecao = estoques_sku1 & estoques_sku2
    uniao = estoques_sku1 | estoques_sku2

    # Evita divisão por zero
    if not uniao:
        return 0.0

    return len(intersecao) / len(uniao)
