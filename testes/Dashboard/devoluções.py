import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Devoluções", layout="wide")
st.title("🔄 Análise de Devoluções")

# Carregar arquivos de devolução
arquivos = [f for f in os.listdir("data") if "devolucao" in f]
arquivo = st.selectbox("Selecione o arquivo de devoluções", arquivos)
df = pd.read_csv(f"data/{arquivo}")

# Conversão de data
df["DATA_DEVOLUCAO"] = pd.to_datetime(df["DATA_DEVOLUCAO"], errors='coerce')

# Filtros
with st.sidebar:
    st.header("🔍 Filtros")
    # Data
    data_range = st.date_input("Período da devolução", [df["DATA_DEVOLUCAO"].min(), df["DATA_DEVOLUCAO"].max()])
    df = df[(df["DATA_DEVOLUCAO"] >= pd.to_datetime(data_range[0])) & (df["DATA_DEVOLUCAO"] <= pd.to_datetime(data_range[1]))]

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
st.subheader("📊 Métricas Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Total devolvido", f"R$ {df['VALORDEVPRODUTO'].sum():,.2f}")
col2.metric("Total de devoluções", f"{len(df)} registros")
col3.metric("SKUs únicos", f"{df['SKU'].nunique()}")

# Gráfico: valor devolvido por loja
st.subheader("💰 Valor devolvido por loja")
valor_por_loja = df.groupby("LOJA")["VALORDEVPRODUTO"].sum().reset_index()
fig1 = px.bar(valor_por_loja, x="LOJA", y="VALORDEVPRODUTO", title="Valor total devolvido por loja", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico: SKUs mais devolvidos
st.subheader("📦 SKUs mais devolvidos")
sku_top = df["SKU"].value_counts().reset_index().rename(columns={"index": "SKU", "SKU": "Quantidade"})
fig2 = px.bar(sku_top.head(10), x="SKU", y="Quantidade", title="Top 10 SKUs por devolução", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Exportar dados
st.subheader("📥 Exportar dados filtrados")
st.download_button("Exportar CSV", df.to_csv(index=False), file_name="devolucoes_filtradas.csv")

# Tabela completa
st.subheader("📄 Tabela de dados filtrados")
st.dataframe(df, use_container_width=True)

