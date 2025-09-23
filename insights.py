import random
from faker import Faker

fake = Faker('pt_BR')

def gerar_dados(n_estoques=3, n_lojas=3, n_skus=10, n_transacoes=20):
    estoques = [f"Estoque_{i}" for i in range(n_estoques)]
    lojas = [f"Loja_{i}" for i in range(n_lojas)]
    skus = [f"SKU_{i}" for i in range(n_skus)]
    transacoes = []

    for i in range(n_transacoes):
        transacoes.append({
            "id": f"NF_{i}",
            "estoque": random.choice(estoques),
            "loja": random.choice(lojas),
            "sku": random.choice(skus),
            "valor": round(random.uniform(50, 500), 2),
            "ocorrencia": random.choice(["troca", "devolucao", "cancelamento", None])
        })
    return estoques, lojas, skus, transacoes
