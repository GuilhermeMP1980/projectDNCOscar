import streamlit as st
import pandas as pd
import os

# Título da aplicação
st.title(" Inteligência de Estoque - Calçados 2025")

# Lista de arquivos e seus tipos
arquivos = {
    "devolucao_2025.csv": "devolucao",
    "cancelamento_2025.csv": "cancelamento",
    "ajustes_estoque_2025.csv": "ajustes",
    "inventario_012025.csv": "inventario",
    "inventario_022025.csv": "inventario",
    "inventario_032025.csv": "inventario",
    "inventario_042025.csv": "inventario",
    "inventario_052025.csv": "inventario",
    "inventario_062025.csv": "inventario"
}

# Perguntas disponíveis por tipo
perguntas_possiveis = {
    "inventario": [
        "Qual foi o valor total movimentado por loja?",
        "Qual SKU teve maior movimentação?"
    ],
    "devolucao": [
        "Qual foi o valor total devolvido por loja?",
        "Qual SKU teve mais devoluções?"
    ],
    "cancelamento": [
        "Qual loja teve mais cancelamentos?",
        "Qual foi o valor bruto total cancelado?"
    ],
    "ajustes": [
        "Qual foi o tipo de ajuste mais comum?",
        "Qual loja realizou mais ajustes de estoque?"
    ]
}

# Seleção do tipo de operação
tipo = st.selectbox("Selecione o tipo de operação:", list(set(arquivos.values())))

# Filtrar arquivos do tipo selecionado
arquivos_filtrados = [arq for arq, t in arquivos.items() if t == tipo]

# Seleção do arquivo
arquivo_escolhido = st.selectbox("Selecione o arquivo:", arquivos_filtrados)

# Seleção da pergunta
pergunta = st.selectbox("Escolha uma pergunta:", perguntas_possiveis[tipo])

# Carregar dados
try:
    df = pd.read_csv(arquivo_escolhido)
    st.success(f"Arquivo {arquivo_escolhido} carregado com sucesso.")
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
    st.stop()

# Responder à pergunta
if pergunta == "Qual foi o valor total movimentado por loja?" and "VALOR" in df.columns and "LOJA" in df.columns:
    resultado = df.groupby("LOJA")["VALOR"].sum()
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual SKU teve maior movimentação?" and "SKU" in df.columns and "QTDEMOVIMENTADA" in df.columns:
    resultado = df.groupby("SKU")["QTDEMOVIMENTADA"].sum().sort_values(ascending=False).head(1)
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual foi o valor total devolvido por loja?" and "VALORDEVPRODUTO" in df.columns and "LOJA" in df.columns:
    resultado = df.groupby("LOJA")["VALORDEVPRODUTO"].sum()
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual SKU teve mais devoluções?" and "SKU" in df.columns:
    resultado = df["SKU"].value_counts().head(1)
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual loja teve mais cancelamentos?" and "LOJA" in df.columns:
    resultado = df["LOJA"].value_counts()
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual foi o valor bruto total cancelado?" and "VALORBRUTO" in df.columns:
    resultado = df["VALORBRUTO"].sum()
    st.write(f"Resposta: R$ {resultado:.2f}")

elif pergunta == "Qual foi o tipo de ajuste mais comum?" and "TIPO_AJUSTE" in df.columns:
    resultado = df["TIPO_AJUSTE"].value_counts().head(1)
    st.write("Resposta:")
    st.dataframe(resultado)

elif pergunta == "Qual loja realizou mais ajustes de estoque?" and "LOJA" in df.columns:
    resultado = df["LOJA"].value_counts().head(1)
    st.write("Resposta:")
    st.dataframe(resultado)

else:
    st.warning("Não foi possível responder à pergunta com os dados disponíveis.")

