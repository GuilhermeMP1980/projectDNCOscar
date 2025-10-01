import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os 
import io
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from duckdbrunnerAnalytics import cruzar_dados
from database import SessionLocal, criar_tabelas
from models.historico import HistoricoIA

# 🔧 Configuração inicial
load_dotenv()
criar_tabelas()
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/perguntar")

# 🔗 Conexão com Neo4j
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
    username=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password")
)
qa_chain = GraphCypherQAChain.from_llm(llm=ChatOpenAI(model="gpt-4", temperature=0.3), graph=graph)

# 🔮 Modelo LLM
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente de estoque. Responda com clareza e objetividade."),
    ("human", "{pergunta}")
])
llm = ChatOpenAI(model="gpt-4", temperature=0.3)
resposta_llm = prompt | llm | StrOutputParser()

st.sidebar.header("📁 Upload de Arquivo CSV")
arquivo_csv = st.sidebar.file_uploader("Envie um arquivo CSV para análise", type=["csv"])

def carregar_dados_upload():
    if arquivo_csv is not None:
        try:
            df = pd.read_csv(arquivo_csv)
            st.success("Arquivo carregado com sucesso!")
            return df
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return pd.DataFrame()
    else:
        return cruzar_dados() if isinstance(cruzar_dados(), pd.DataFrame) else pd.DataFrame()

# 📊 Função para carregar dados
def carregar_dados():
    try:
        df = cruzar_dados()
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Função para responder perguntas sobre colunas
def responder_sobre_colunas(pergunta, df):
    pergunta = pergunta.lower()
    if "colunas" in pergunta:
        return f"O DataFrame possui as seguintes colunas:\n\n- " + "\n- ".join(df.columns)
    for col in df.columns:
        if col.lower() in pergunta:
            if "tipo" in pergunta:
                return f"A coluna '{col}' possui tipo de dado: {df[col].dtype}"
            if "valores únicos" in pergunta or "valores distintos" in pergunta:
                valores = df[col].dropna().unique().tolist()
                resposta = f"A coluna '{col}' possui {len(valores)} valores únicos:\n\n- " + "\n- ".join(map(str, valores[:10]))
                if len(valores) > 10:
                    resposta += "\n- ... (mais valores ocultos)"
                return resposta
    return "Desculpe, não consegui entender a pergunta sobre as colunas."

# Classificador de perguntas
def classificar(pergunta):
    pergunta = pergunta.lower()
    if "devolução" in pergunta or "cancelamento" in pergunta:
        if "loja" in pergunta: return "devolucao_por_loja"
        if "cliente" in pergunta: return "devolucao_por_cliente"
        return "analisar_devolucoes"
    if "diferença" in pergunta: return "diferenca_valor_por_sku"
    if "movimentação" in pergunta: return "movimentacao_por_tipo"
    if "estoque" in pergunta or "quantidade" in pergunta: return "analisar_dados"
    if "fluxo" in pergunta or "acionar" in pergunta: return "acionar_fluxo"
    return "responder_geral"

# 📈 Funções de análise
def analisar_dados(df): return df.head(5).to_markdown(index=False)
def gerar_grafico(df, x, y, titulo): return px.bar(df, x=x, y=y, title=titulo)

# 💬 Função principal de resposta
def responder(pergunta, usar_grafo=False, **kwargs):
    df = carregar_dados()
    entrada = {"pergunta": pergunta, **kwargs}
    if usar_grafo:
        try:
            entrada["resposta"] = qa_chain.run(pergunta)
        except Exception as e:
            entrada["resposta"] = f"Erro ao consultar grafo: {e}"
        return entrada

    tipo = classificar(pergunta)
    if tipo == "analisar_dados":
        entrada["resposta"] = analisar_dados(df)
    elif tipo == "analisar_devolucoes" and "DATA_DEVOLUCAO" in df.columns:
        df["DATA_DEVOLUCAO"] = pd.to_datetime(df["DATA_DEVOLUCAO"], errors="coerce")
        df_mes = df[df["DATA_DEVOLUCAO"].dt.month == datetime.now().month]
        if not df_mes.empty:
            top = df_mes.groupby("SKU")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
            entrada["grafico"] = gerar_grafico(top, "SKU", "VALORDEVPRODUTO", "Top 5 Produtos Mais Devolvidos")
            entrada["resposta"] = "Análise de devoluções gerada com sucesso."
        else:
            entrada["resposta"] = "Nenhuma devolução registrada neste mês."
    elif tipo == "devolucao_por_loja" and "LOJA" in df.columns:
        top = df.groupby("LOJA")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
        entrada["grafico"] = gerar_grafico(top, "LOJA", "VALORDEVPRODUTO", "Top 5 Lojas com Mais Devoluções")
        entrada["resposta"] = "Análise por loja gerada com sucesso."
    elif tipo == "devolucao_por_cliente" and "CLIENTE" in df.columns:
        top = df.groupby("CLIENTE")["VALORDEVPRODUTO"].sum().nlargest(5).reset_index()
        entrada["grafico"] = gerar_grafico(top, "CLIENTE", "VALORDEVPRODUTO", "Top 5 Clientes com Mais Devoluções")
        entrada["resposta"] = "Análise por cliente gerada com sucesso."
    elif tipo == "diferenca_valor_por_sku" and "DIFERENCA_VALOR" in df.columns:
        top = df.groupby("SKU")["DIFERENCA_VALOR"].sum().nlargest(5).reset_index()
        entrada["grafico"] = gerar_grafico(top, "SKU", "DIFERENCA_VALOR", "Top 5 SKUs com Maior Diferença de Valor")
        entrada["resposta"] = "Análise de diferença de valor gerada com sucesso."
    elif tipo == "movimentacao_por_tipo" and "TIPOMOVIMENTACAO" in df.columns:
        mov = df["TIPOMOVIMENTACAO"].value_counts().reset_index()
        mov.columns = ["TIPOMOVIMENTACAO", "Quantidade"]
        entrada["grafico"] = gerar_grafico(mov, "TIPOMOVIMENTACAO", "Quantidade", "Distribuição de Movimentações")
        entrada["resposta"] = "Análise de movimentações gerada com sucesso."
    elif tipo == "acionar_fluxo":
        entrada["resposta"] = resposta_llm.invoke({"pergunta": pergunta})
        try: requests.post(N8N_WEBHOOK_URL, json=entrada)
        except: pass
    else:
        entrada["resposta"] = resposta_llm.invoke({"pergunta": pergunta})

    # Salvar histórico
    db = SessionLocal()
    registro = HistoricoIA(
        pergunta=entrada["pergunta"],
        resposta=entrada["resposta"],
        tipo_ocorrencia="dados" if "estoque" in pergunta.lower() else "geral",
        sku=entrada.get("sku"),
        loja=entrada.get("loja"),
        cliente=entrada.get("cliente"),
        nota_fiscal=entrada.get("nota_fiscal"),
        timestamp=datetime.utcnow()
    )
    db.add(registro)
    db.commit()
    db.close()

    return entrada
 

if df is not None and not df.empty:
    st.markdown("### 📤 Exportar dados")
    formato = st.selectbox("Escolha o formato de exportação", ["Excel", "CSV"])
    if st.button("Exportar"):
        if formato == "Excel":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Dados")
            st.download_button("📥 Baixar Excel", data=buffer.getvalue(), file_name="dados_estoque.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar CSV", data=csv_data, file_name="dados_estoque.csv", mime="text/csv")

# 🎯 Interface Streamlit
st.set_page_config(page_title="Assistente de Estoque", layout="wide")
st.title("📦 Assistente de Estoque Inteligente")
usar_grafo = st.checkbox("Usar inteligência de grafo (Neo4j + LangChain)?", value=False)

df = carregar_dados()
st.write("Pré-visualização dos dados carregados:")
st.write(df.head())
st.write("Colunas disponíveis:", df.columns.tolist())
st.write("Quantidade de linhas:", len(df))

if df.empty:
    st.warning("Os dados ainda não estão disponíveis para análise.")
else:
    sku_opcoes = df["SKU"].dropna().unique().tolist() if "SKU" in df.columns else []
        loja_opcoes = df["LOJA"].dropna().unique().tolist() if "LOJA" in df.columns else []
    cliente_opcoes = df["CLIENTE"].dropna().unique().tolist() if "CLIENTE" in df.columns else []
    tipo_mov_opcoes = df["TIPOMOVIMENTACAO"].dropna().unique().tolist() if "TIPOMOVIMENTACAO" in df.columns else []

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

    if pergunta:
        if "coluna" in pergunta or "colunas" in pergunta:
            resposta_coluna = responder_sobre_colunas(pergunta, df)
            st.markdown(f"### Resposta sobre colunas:\n{resposta_coluna}")
        else:
            resultado = responder(
                pergunta,
                usar_grafo,
                sku=sku if sku else None,
                loja=loja if loja else None,
                cliente=cliente if cliente else None,
                nota_fiscal=nota_fiscal if nota_fiscal else None
            )
            st.markdown(f"### 🤖 Resposta:\n{resultado['resposta']}")
            if resultado.get("grafico"):
                st.plotly_chart(resultado["grafico"])
