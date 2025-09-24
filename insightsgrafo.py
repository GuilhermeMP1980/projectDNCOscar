# Importações
from langchain.llms import Ollama
from typing import List, Tuple
import networkx as nx

# Função para extrair insights do grafo
def extrair_insights_grafo(
    G: nx.DiGraph,
    skus: List[str],
    similaridades: List[Tuple[str, str, float]],
    suspeitos: List[Tuple[str, float, int]]
) -> str:
    linhas = []
    for sku in skus:
        grau = len(list(G.predecessors(sku)))
        linhas.append(f"{sku} está vinculado a {grau} estoques.")
    for s1, s2, score in similaridades[:5]:
        linhas.append(f"{s1} e {s2} têm escore de similaridade {score}.")
    for sku, media, grau in suspeitos:
        linhas.append(f"{sku} é suspeito: média {media}, grau {grau}.")
    return "\n".join(linhas)

# Função para construir o prompt com contexto
def construir_prompt_com_contexto(pergunta_usuario: str, contexto_grafo: str) -> str:
    return f"""
Você é um especialista em logística e análise de SKUs.

Contexto extraído do grafo:
{contexto_grafo}

Pergunta do usuário:
{pergunta_usuario}

Responda com base no contexto acima, de forma clara e objetiva.
"""

# Função para gerar resposta com LLM
def responder_com_contexto(
    pergunta: str,
    G: nx.DiGraph,
    skus: List[str],
    similaridades: List[Tuple[str, str, float]],
    suspeitos: List[Tuple[str, float, int]],
    modelo
) -> str:
    contexto = extrair_insights_grafo(G, skus, similaridades, suspeitos)
    prompt = construir_prompt_com_contexto(pergunta, contexto)
    resposta = modelo.invoke(prompt)
    return resposta

# Nó para LangGraph
def responder_com_grafo_node(state: dict) -> dict:
    modelo = Ollama(model="mistral")
    resposta = responder_com_contexto(
        state["llm"],
        state["grafo"],
        state["skus"],
        state["similaridades"],
        state["suspeitos"],
        modelo
    )
    state["resposta"] = resposta
    return state
