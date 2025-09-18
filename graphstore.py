import networkx as nx
import uuid

# Grafo em memória
GRAFO = nx.DiGraph()

def adicionar_ao_grafo(pergunta: str, resposta: str, fontes: list):
    node_id = str(uuid.uuid4())
    GRAFO.add_node(node_id, tipo="pergunta", texto=pergunta)
    
    resposta_id = str(uuid.uuid4())
    GRAFO.add_node(resposta_id, tipo="resposta", texto=resposta)
    GRAFO.add_edge(node_id, resposta_id, relacao="responde")

    for fonte in fontes:
        fonte_id = str(uuid.uuid4())
        GRAFO.add_node(fonte_id, tipo="fonte", texto=fonte)
        GRAFO.add_edge(resposta_id, fonte_id, relacao="baseado_em")

def obter_grafo():
    return GRAFO
