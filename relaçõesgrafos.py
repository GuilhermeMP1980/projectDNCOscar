import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Arquivos e tipos de ocorrência
arquivos = {
    "devolucao_2025.csv": "Devolução",
    "cancelamento_2025.csv": "Cancelamento",
    "ajustes_estoque_2025.csv": "Ajuste de Estoque"
}

# Cria grafo
G = nx.Graph()

# Função para adicionar arestas com rótulo
def adicionar_relacao(origem, destino, tipo_relacao):
    G.add_edge(origem, destino, label=tipo_relacao)

# Processa cada arquivo
for arquivo, tipo_ocorrencia in arquivos.items():
    try:
        df = pd.read_csv(arquivo)

        for _, row in df.iterrows():
            loja = row.get('Loja', f"Loja_{_}")
            cliente = row.get('Cliente', f"Cliente_{_}")
            sku = row.get('SKU', f"SKU_{_}")
            nf = row.get('NF') or row.get('Transacao') or f"NF_{_}"

            # Define relações (arestas)
            adicionar_relacao(cliente, loja, "atendido_por")
            adicionar_relacao(sku, cliente, "comprado_por")
            adicionar_relacao(sku, loja, "vendido_por")
            adicionar_relacao(sku, tipo_ocorrencia, "envolvido_em")
            adicionar_relacao(tipo_ocorrencia, nf, "registrado_em")
            adicionar_relacao(cliente, nf, "participa_de")
            adicionar_relacao(loja, nf, "emitiu")

    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")

# Visualização do grafo
pos = nx.spring_layout(G, seed=42)
edge_labels = nx.get_edge_attributes(G, 'label')

plt.figure(figsize=(14, 10))
nx.draw(G, pos, with_labels=True, node_color='lightyellow', node_size=2500, font_size=10)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='darkblue')
plt.title("Grafo de Relações Comerciais 2025")
plt.show()
