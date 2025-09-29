import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Estoque Inteligente", layout="wide")
st.title("📦 Inteligência de Estoque - Calçados 2025")

# Seleção do tipo de operação
tipo = st.sidebar.selectbox("Tipo de operação", ["inventario", "devolucao", "cancelamento", "ajustes"])

# Mapeamento de arquivos
arquivos = {arq: tipo for arq in os.listdir() if tipo in arq and arq.endswith(".csv")}
arquivo_escolhido = st.sidebar.selectbox("Arquivo", list(arquivos.keys()))

# Carregar dados
df = pd.read_csv(arquivo_escolhido)

# Filtros dinâmicos
if "DATA" in df.columns or "DATACANCELAMENTO" in df.columns or "DATA_DEVOLUCAO" in df.columns:
    data_col = [col for col in df.columns if "DATA" in col.upper()][0]
    df[data_col] = pd.to_datetime(df[data_col], errors='coerce')
    data_min, data_max = df[data_col].min(), df[data_col].max()
    data_range = st.sidebar.date_input("Filtrar por data", [data_min, data_max])
    df = df[(df[data_col] >= pd.to_datetime(data_range[0])) & (df[data_col] <= pd.to_datetime(data_range[1]))]

if "LOJA" in df.columns:
    lojas = df["LOJA"].dropna().unique()
    loja_selecionada = st.sidebar.multiselect("Filtrar por loja", lojas, default=lojas)
    df = df[df["LOJA"].isin(loja_selecionada)]

# Pergunta selecionada
pergunta = st.selectbox("Escolha uma pergunta", [
    "Qual foi o valor total movimentado por loja?",
    "Qual SKU teve maior movimentação?",
    "Qual foi o tipo de ajuste mais comum?",
    "Qual loja teve mais cancelamentos?",
    "Qual SKU teve mais devoluções?"
])

# Resposta e visualização
if pergunta == "Qual foi o valor total movimentado por loja?" and "VALOR" in df.columns:
    resultado = df.groupby("LOJA")["VALOR"].sum().reset_index()
    fig = px.bar(resultado, x="LOJA", y="VALOR", title="Valor total movimentado por loja")
    st.plotly_chart(fig)

elif pergunta == "Qual SKU teve maior movimentação?" and "QTDEMOVIMENTADA" in df.columns:
    resultado = df.groupby("SKU")["QTDEMOVIMENTADA"].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(resultado.head(10), x="SKU", y="QTDEMOVIMENTADA", title="Top 10 SKUs por movimentação")
    st.plotly_chart(fig)

elif pergunta == "Qual foi o tipo de ajuste mais comum?" and "TIPO_AJUSTE" in df.columns:
    resultado = df["TIPO_AJUSTE"].value_counts().reset_index()
    fig = px.pie(resultado, names="index", values="TIPO_AJUSTE", title="Distribuição dos tipos de ajuste")
    st.plotly_chart(fig)

elif pergunta == "Qual loja teve mais cancelamentos?" and "LOJA" in df.columns:
    resultado = df["LOJA"].value_counts().reset_index()
    fig = px.bar(resultado, x="index", y="LOJA", title="Cancelamentos por loja")
    st.plotly_chart(fig)

elif pergunta == "Qual SKU teve mais devoluções?" and "SKU" in df.columns:
    resultado = df["SKU"].value_counts().reset_index()
    fig = px.bar(resultado.head(10), x="index", y="SKU", title="Top 10 SKUs por devolução")
    st.plotly_chart(fig)

# Exportar relatório
st.download_button("Exportar dados filtrados", df.to_csv(index=False), file_name=f"relatorio_{tipo}.csv")

# Estatísticas rápidas
st.subheader("Estatísticas")
st.write(df.describe(include='all'))
