import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# Lista de arquivos e tipos de ocorrência
arquivos = {
    "devolucao_2025.csv": "Devolução",
    "cancelamento_2025.csv": "Cancelamento",
    "ajustes_estoque_2025.csv": "Ajuste de Estoque"
}

# Cria grafo
G = nx.Graph()

# Processa cada arquivo
for nome_arquivo, tipo_ocorrencia in arquivos.items():
    if not os.path.exists(nome_arquivo):
        print(f" Arquivo não encontrado: {nome_arquivo}")
        continue

    df = pd.read_csv(nome_arquivo)

    for _, row in df.iterrows():
        loja = row.get('Loja')
        cliente = row.get('Cliente')
        sku = row.get('SKU')
        nf = row.get('NF') or row.get('Transacao') or f"NF_{_}"

        # Adiciona nós e arestas
        G.add_edge(loja, cliente, label="atende")
        G.add_edge(cliente, sku, label="relacionado a")
        G.add_edge(sku, tipo_ocorrencia, label="ocorrência")
        G.add_edge(tipo_ocorrencia, nf, label="registrado em")

# Visualização
pos = nx.spring_layout(G, seed=42)
edge_labels = nx.get_edge_attributes(G, 'label')

plt.figure(figsize=(14, 10))
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2500, font_size=10)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='darkred')
plt.title("Grafo de Ocorrências Comerciais 2025")
plt.show()
