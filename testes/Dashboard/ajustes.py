import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Ajustes de Estoque", layout="wide")
st.title("Análise de Ajustes de Estoque")

# Carregar arquivos de ajustes
arquivos = [f for f in os.listdir("data") if "ajustes_estoque" in f]
arquivo = st.selectbox("Selecione o arquivo de ajustes", arquivos)
df = pd.read_csv(f"data/{arquivo}")

# Conversão de data
df["DATA"] = pd.to_datetime(df["DATA"], errors='coerce')

# Filtros
with st.sidebar:
    st.header("Filtros")
    # Data
    data_range = st.date_input("Período do ajuste", [df["DATA"].min(), df["DATA"].max()])
    df = df[(df["DATA"] >= pd.to_datetime(data_range[0])) & (df["DATA"] <= pd.to_datetime(data_range[1]))]

    # Loja
    lojas = df["LOJA"].dropna().unique()
    loja_selecionada = st.multiselect("Filtrar por loja", lojas, default=lojas)
    df = df[df["LOJA"].isin(loja_selecionada)]

    # SKU
    if "SKU" in df.columns:
        skus = df["SKU"].dropna().unique()
        sku_selecionado = st.multiselect("Filtrar por SKU", skus)
        if sku_selecionado:
            df = df[df["SKU"].isin(sku_selecionado)]

# Métricas principais
st.subheader("Métricas Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Total de ajustes", f"{len(df)} registros")
col2.metric("SKUs únicos ajustados", f"{df['SKU'].nunique()}")
col3.metric("Tipos de ajuste", f"{df['TIPO_AJUSTE'].nunique()}")

# Gráfico: tipo de ajuste mais comum
st.subheader("Tipos de Ajuste")
ajuste_tipo = df["TIPO_AJUSTE"].value_counts().reset_index()
ajuste_tipo.columns = ["Tipo de Ajuste", "Quantidade"]
fig1 = px.pie(ajuste_tipo, names="Tipo de Ajuste", values="Quantidade", title="Distribuição dos tipos de ajuste")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico: ajustes por loja
st.subheader("Ajustes por Loja")
ajuste_loja = df["LOJA"].value_counts().reset_index()
ajuste_loja.columns = ["LOJA", "Quantidade"]
fig2 = px.bar(ajuste_loja, x="LOJA", y="Quantidade", title="Total de ajustes por loja", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Exportar dados
st.subheader("Exportar dados filtrados")
st.download_button("Exportar
