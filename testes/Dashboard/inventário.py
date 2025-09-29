
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("📦 Inventário")

# Carregar arquivos de inventário
arquivos = [f for f in os.listdir("data") if "inventario" in f]
arquivo = st.selectbox("Selecione o arquivo", arquivos)
df = pd.read_csv(f"data/{arquivo}")

# Filtros
df["DATA"] = pd.to_datetime(df["DATA"], errors='coerce')
data_range = st.date_input("Filtrar por data", [df["DATA"].min(), df["DATA"].max()])
df = df[(df["DATA"] >= pd.to_datetime(data_range[0])) & (df["DATA"] <= pd.to_datetime(data_range[1]))]

lojas = df["LOJA"].unique()
loja = st.multiselect("Filtrar por loja", lojas, default=lojas)
df = df[df["LOJA"].isin(loja)]

# Gráfico de movimentação por loja
if "VALOR" in df.columns:
    resumo = df.groupby("LOJA")["VALOR"].sum().reset_index()
    fig = px.bar(resumo, x="LOJA", y="VALOR", title="Valor movimentado por loja")
    st.plotly_chart(fig)

# Exportar
st.download_button("Exportar dados filtrados", df.to_csv(index=False), file_name=f"relatorio_inventario.csv")
