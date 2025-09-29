import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Cancelamentos", layout="wide")
st.title("Análise de Cancelamentos")

# Carregar arquivos de cancelamento
arquivos = [f for f in os.listdir("data") if "cancelamento" in f]
arquivo = st.selectbox("Selecione o arquivo de cancelamentos", arquivos)
df = pd.read_csv(f"data/{arquivo}")

# Conversão de data
df["DATACANCELAMENTO"] = pd.to_datetime(df["DATACANCELAMENTO"], errors='coerce')

# Filtros
with st.sidebar:
    st.header("Filtros")
    # Data
    data_range = st.date_input("Período do cancelamento", [df["DATACANCELAMENTO"].min(), df["DATACANCELAMENTO"].max()])
    df = df[(df["DATACANCELAMENTO"] >= pd.to_datetime(data_range[0])) & (df["DATACANCELAMENTO"] <= pd.to_datetime(data_range[1]))]

    # Loja
    lojas = df["LOJA"].dropna().unique()
    loja_selecionada = st.multiselect("Filtrar por loja", lojas, default=lojas)
    df = df[df["LOJA"].isin(loja_selecionada)]

    # SKU
    if "SKU" in df.columns:
        skus = df["SKU"].dropna().unique()
        sku_selecionado = st.multiselect("Filtrar por SKU", skus)
