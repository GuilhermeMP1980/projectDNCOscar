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
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from neo4jfraude import GraphDatabase
from dotenv import load_dotenv

load_dotenv()
# Inicializa conexão com Neo4j via LangChain
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI") or "bolt://127.0.0.1:7687",
    username=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key="SUA_CHAVE_OPENAI"
)

# Cria a cadeia de perguntas/respostas com geração de Cypher
qa_chain = GraphCypherQAChain.from_llm(llm=llm, graph=graph)

def responder_com_grafo(pergunta):
    try:
        resposta = qa_chain.run(pergunta)
        return {"resposta": resposta}
    except Exception as e:
        return {"resposta": f"Erro ao consultar grafo: {e}"}


criar_tabelas()
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/perguntar")

# Prompt e modelo
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de estoque. Responda com clareza e objetividade."),
    ("human", "{pergunta}")
])

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.3,
    openai_api_key="SUA_CHAVE_OPENAI"
)

# Resposta com LLM
def responder_llm(state):
    resposta = prompt | llm | StrOutputParser()
    texto = resposta.invoke({"pergunta": state["pergunta"]})
    return {**state, "resposta": texto}

# Classificador inteligente
def classificar(state):
    pergunta = state["pergunta"].lower()

    if "devolução" in pergunta or "cancelamento" in pergunta:
        if "loja" in pergunta:
            return "devolucao_por_loja"
        elif "cliente" in pergunta:
            return "devolucao_por_cliente"
        else:
            return "analisar_devolucoes"

    elif "diferença" in pergunta or "diferença de valor" in pergunta:
        return "diferenca_valor_por_sku"

    elif "movimentação" in pergunta or "tipo de movimentação" in pergunta:
        return "movimentacao_por_tipo"

    elif "estoque" in pergunta or "quantidade" in pergunta:
        return "analisar_dados"

    elif "acionar" in pergunta or "fluxo" in pergunta:
        return "acionar_fluxo"

    return "responder_geral"

# Análises
def analisar_dados(state):
    df = carregar_dados()
    if df.empty:
        resposta = "Não foi possível realizar a análise. Os dados estão incompletos ou ausentes."
    else:
        top = df.head(5).to_markdown(index=False)
        resposta = f"Análise concluída com base nos dados cruzados:\n\n{top}"
    return {**state, "resposta": resposta}

def analisar_devolucoes(state):
    df = cruzar_dados()
    if df.empty or "DATA_DEVOLUCAO" not in df.columns or "VALORDEVPRODUTO" not in df.columns:
        state["grafico"] = None
        state["resposta"] = "Não foi possível gerar análise de devoluções por falta de dados."
        return state

    df["DATA_DEVOLUCAO"] = pd.to_datetime(df["DATA_DEVOLUCAO"], errors="coerce")
    df_mes = df[df["DATA_DEVOLUCAO"].dt.month == datetime.now().month]

    if df_mes.empty:
        state["grafico"] = None
        state["resposta"] = "Nenhuma devolução registrada neste mês."
        return state

    top_devolucoes = df_mes.groupby("SKU")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
    fig = px.bar(top_devolucoes, x="SKU", y="VALORDEVPRODUTO", title="Top 5 Produtos Mais Devolvidos no Mês")
    state["grafico"] = fig
    state["resposta"] = "Análise de devoluções gerada com sucesso."
    return state

def devolucao_por_loja(state):
    df = cruzar_dados()
    if df.empty or "LOJA" not in df.columns or "VALORDEVPRODUTO" not in df.columns:
        state["resposta"] = "Dados insuficientes para análise por loja."
        return state

    devolucoes = df.groupby("LOJA")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
    fig = px.bar(devolucoes, x="LOJA", y="VALORDEVPRODUTO", title="Top 5 Lojas com Mais Devoluções")
    state["grafico"] = fig
    state["resposta"] = "Análise por loja gerada com sucesso."
    return state

def devolucao_por_cliente(state):
    df = cruzar_dados()
    if df.empty or "CLIENTE" not in df.columns or "VALORDEVPRODUTO" not in df.columns:
        state["resposta"] = "Dados insuficientes para análise por cliente."
        return state

    devolucoes = df.groupby("CLIENTE")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
    fig = px.bar(devolucoes, x="CLIENTE", y="VALORDEVPRODUTO", title="Top 5 Clientes com Mais Devoluções")
    state["grafico"] = fig
    state["resposta"] = "Análise por cliente gerada com sucesso."
    return state

def diferenca_valor_por_sku(state):
    df = cruzar_dados()
    if df.empty or "SKU" not in df.columns or "DIFERENCA_VALOR" not in df.columns:
        state["resposta"] = "Dados insuficientes para análise de diferença de valor."
        return state

    impacto = df.groupby("SKU")["DIFERENCA_VALOR"].sum().nlargest(5).reset_index()
    fig = px.bar(impacto, x="SKU", y="DIFERENCA_VALOR", title="Top 5 SKUs com Maior Diferença de Valor")
    state["grafico"] = fig
    state["resposta"] = "Análise de diferença de valor gerada com sucesso."
    return state

def movimentacao_por_tipo(state):
    df = cruzar_dados()
    if df.empty or "TIPOMOVIMENTACAO" not in df.columns:
        state["resposta"] = "Dados insuficientes para análise de movimentações."
        return state

    movimentacoes = df["TIPOMOVIMENTACAO"].value_counts().reset_index()
    movimentacoes.columns = ["TIPOMOVIMENTACAO", "Quantidade"]
    fig = px.bar(movimentacoes, x="TIPOMOVIMENTACAO", y="Quantidade", title="Distribuição de Tipos de Movimentação")
    state["grafico"] = fig
    state["resposta"] = "Análise de movimentações gerada com sucesso."
    return state

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

# Função pública
def responder(pergunta: str, usar_grafo=False, **kwargs) -> dict:
    entrada = {"pergunta": pergunta, **kwargs}

    if usar_grafo:
        resultado = responder_com_grafo(pergunta)
        entrada.update(resultado)
    else:
        tipo = classificar(entrada)

        if tipo == "analisar_dados":
            entrada = analisar_dados(entrada)
        elif tipo == "analisar_devolucoes":
            entrada = analisar_devolucoes(entrada)
        elif tipo == "devolucao_por_loja":
            entrada = devolucao_por_loja(entrada)
        elif tipo == "devolucao_por_cliente":
            entrada = devolucao_por_cliente(entrada)
        elif tipo == "diferenca_valor_por_sku":
            entrada = diferenca_valor_por_sku(entrada)
        elif tipo == "movimentacao_por_tipo":
            entrada = movimentacao_por_tipo(entrada)
        elif tipo == "acionar_fluxo":
            entrada = responder_llm(entrada)
            entrada = acionar_fluxo(entrada)
        else:
            entrada = responder_llm(entrada)

    entrada = salvar_historico(entrada)
    return entrada


# Interface Streamlit
st.set_page_config(page_title="Assistente de Estoque", layout="wide")
st.title("📦 Assistente de Estoque Inteligente")
usar_grafo = st.checkbox("Usar inteligência de grafo (Neo4j + LangChain)?", value=False)


# Função para carregar os dados
def carregar_dados():
    try:
        df = cruzar_dados()
        if isinstance(df, pd.DataFrame):
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados()
st.write("Pré-visualização dos dados carregados:")
st.write(df.head())
st.write("Colunas disponíveis:", df.columns.tolist())
st.write("Quantidade de linhas:", len(df))

if df.empty:
    st.warning("Os dados ainda não estão disponíveis para análise.")
else:
    # Extrai opções únicas para os filtros
    sku_opcoes = df["SKU"].dropna().unique().tolist()
    loja_opcoes = df["LOJA"].dropna().unique().tolist()
    cliente_opcoes = df["CLIENTE"].dropna().unique().tolist() if "CLIENTE" in df.columns else []
    tipo_mov_opcoes = df["TIPOMOVIMENTACAO"].dropna().unique().tolist()

    pergunta = st.text_input("Digite sua pergunta sobre o estoque:")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        sku = st.selectbox("SKU (opcional)", options=[""] + sku_opcoes)
    with col2:
        loja = st.selectbox("Loja (opcional)", options=[""] + loja_opcoes)
    with col3:
        cliente = st.selectbox("Cliente (opcional)", options=[""] + cliente_opcoes)
    with col4:
        nota_fiscal = st.text_input("Nota Fiscal (opcional)")

    col5, col6 = st.columns(2)
    with col5:
        tipo_mov = st.selectbox("Tipo de Movimentação (opcional)", options=[""] + tipo_mov_opcoes)
    with col6:
        st.markdown("")

    if st.button("Consultar"):
        if pergunta.strip() == "":
            st.warning("Por favor, digite uma pergunta.")
        else:
            with st.spinner("Analisando..."):
                resultado = responder(
                    pergunta,
                    usar_grafo=usar_grafo,  # ← esta é a linha que faltava
                    sku=sku or None,
                    loja=loja or None,
                    cliente=cliente or None,
                    nota_fiscal=nota_fiscal or None,
                    tipo_movimentacao=tipo_mov or None
)

                
            st.success("Resposta gerada:")
            st.markdown(resultado["resposta"])

            if "grafico" in resultado and resultado["grafico"]:
                st.plotly_chart(resultado["grafico"], use_container_width=True)


                        