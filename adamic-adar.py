import networkx as nx
import math

def adamic_adar_skus(G, sku1, sku2):
    # Verifica se os SKUs existem
    if sku1 not in G or sku2 not in G:
        return 0.0

    # Estoques que contêm cada SKU
    estoques_sku1 = set(G.predecessors(sku1))
    estoques_sku2 = set(G.predecessors(sku2))

    # Estoques comuns
    estoques_comuns = estoques_sku1 & estoques_sku2
    score = 0.0

    for estoque in estoques_comuns:
        skus_no_estoque = set(G.successors(estoque))
        grau = len(skus_no_estoque)
        if grau > 1:
            score += 1 / math.log(grau)
    return score
