from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatOpenAI
from duckdbrunnerAnalytics import cruzar_dados
import plotly.express as px
import pandas as pd
from database import SessionLocal, criar_tabelas
from models.historico import HistoricoIA
from datetime import datetime
import os
import requests
import streamlit as st

criar_tabelas()
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/perguntar")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de estoque. Responda com clareza e objetividade."),
    ("human", "{pergunta}")
])

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key="SUA_CHAVE_OPENAI"
)


# Nó de análise com DuckDB
def analisar_dados(state):
    df = cruzar_dados()
    if df.empty:
        resposta = "Não foi possível realizar a análise. Os dados estão incompletos ou ausentes."
    else:
        top = df.head(5).to_markdown(index=False)
        resposta = f"Análise concluída com base nos dados cruzados:\n\n{top}"
    return {**state, "resposta": resposta}

# Classificador
def classificar(state):
    pergunta = state["pergunta"].lower()
    if any(p in pergunta for p in ["cancelamento", "devolução", "estoque", "ajuste", "produto", "quantidade"]):
        return "analisar_dados"
    elif "acionar" in pergunta or "fluxo" in pergunta:
        return "acionar_fluxo"
    return "responder_geral"

# Resposta com LLM
def responder_llm(state):
    resposta = prompt | llm | StrOutputParser()
    texto = resposta.invoke({"pergunta": state["pergunta"]})
    return {**state, "resposta": texto}

# Acionar n8n
def acionar_fluxo(state):
    payload = {
        "pergunta": state["pergunta"],
        "resposta": state.get("resposta", ""),
        "sku": state.get("sku", ""),
        "loja": state.get("loja", ""),
        "cliente": state.get("cliente", ""),
        "nota_fiscal": state.get("nota_fiscal", "")
    }
    try:
        requests.post(N8N_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Erro ao acionar n8n: {e}")
    return state

# Persistência
def salvar_historico(state):
    db = SessionLocal()
    registro = HistoricoIA(
        pergunta=state["pergunta"],
        resposta=state["resposta"],
        tipo_ocorrencia="dados" if "estoque" in state["pergunta"].lower() else "geral",
        sku=state.get("sku"),
        loja=state.get("loja"),
        cliente=state.get("cliente"),
        nota_fiscal=state.get("nota_fiscal"),
        timestamp=datetime.utcnow()
    )
    db.add(registro)
    db.commit()
    db.close()
    return state
    
def gerar_grafico(state):
    df = cruzar_dados()
    if df.empty or "produto" not in df.columns or "quantidade_vendida" not in df.columns:
        state["grafico"] = None
        state["resposta"] += "\n\nNão foi possível gerar o gráfico por falta de dados."
        return state

    top_produtos = df.groupby("produto")["quantidade_vendida"].sum().nlargest(5).reset_index()
    fig = px.bar(top_produtos, x="produto", y="quantidade_vendida", title="Top 5 Produtos Vendidos")
    state["grafico"] = fig
    state["resposta"] += "\n\nGráfico gerado com sucesso."
    return state

# Função pública
def responder(pergunta: str, **kwargs) -> dict:
    entrada = {"pergunta": pergunta, **kwargs}
    resultado = responder.invoke(entrada)
    return resultado

# Interface Streamlit
st.set_page_config(page_title="Assistente de Estoque", layout="wide")
st.title("Assistente de Estoque Inteligente")

pergunta = st.text_input("Digite sua pergunta sobre o estoque:")

col1, col2, col3, col4 = st.columns(4)
with col1:
    sku = st.text_input("SKU (opcional)")
with col2:
    loja = st.text_input("Loja (opcional)")
with col3:
    cliente = st.text_input("Cliente (opcional)")
with col4:
    nota_fiscal = st.text_input("Nota Fiscal (opcional)")

if st.button("Enviar"):
    if pergunta.strip() == "":
        st.warning("Por favor, digite uma pergunta.")
    else:
        with st.spinner("Analisando..."):
            resultado = responder(
                pergunta,
                sku=sku or None,
                loja=loja or None,
                cliente=cliente or None,
                nota_fiscal=nota_fiscal or None
            )
        st.success("Resposta gerada:")
        st.markdown(resultado["resposta"])

        if "grafico" in resultado and resultado["grafico"]:
            st.plotly_chart(resultado["grafico"], use_container_width=True)
