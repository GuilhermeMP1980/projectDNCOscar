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
        if sku_selecionado:
            df = df[df["SKU"].isin(sku_selecionado)]

# Métricas principais
st.subheader("Métricas Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Total cancelado (R$)", f"{df['VALORBRUTO'].sum():,.2f}")
col2.metric("Total de cancelamentos", f"{len(df)} registros")
col3.metric("SKUs únicos", f"{df['SKU'].nunique()}")

# Gráfico: cancelamentos por loja
st.subheader("Cancelamentos por loja")
cancel_por_loja = df["LOJA"].value_counts().reset_index()
cancel_por_loja.columns = ["LOJA", "Cancelamentos"]
fig1 = px.bar(cancel_por_loja, x="LOJA", y="Cancelamentos", title="Total de cancelamentos por loja", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico: SKUs mais cancelados
st.subheader("SKUs mais cancelados")
sku_top = df["SKU"].value_counts().reset_index().rename(columns={"index": "SKU", "SKU": "Quantidade"})
fig2 = px.bar(sku_top.head(10), x="SKU", y="Quantidade", title="Top 10 SKUs por cancelamento", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Exportar dados
st.subheader("Exportar dados filtrados")
st.download_button("Exportar CSV", df.to_csv(index=False), file_name="cancelamentos_filtrados.csv")

# Tabela completa
st.subheader("Tabela de dados filtrados")
st.dataframe(df, use_container_width=True)
