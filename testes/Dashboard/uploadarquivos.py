import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Upload de Arquivos", layout="wide")
st.title("Upload de Arquivos CSV")

# Pasta onde os arquivos serão salvos
PASTA_DESTINO = "data"
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Upload
uploaded_file = st.file_uploader("Selecione um arquivo CSV para enviar", type=["csv"])

if uploaded_file is not None:
    nome_arquivo = uploaded_file.name
    caminho_completo = os.path.join(PASTA_DESTINO, nome_arquivo)

    # Salvar arquivo
    with open(caminho_completo, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Arquivo '{nome_arquivo}' enviado com sucesso para a pasta '{PASTA_DESTINO}'.")

    # Visualizar conteúdo
    try:
        df = pd.read_csv(caminho_completo)
        st.subheader("Pré-visualização dos dados")
        st.dataframe(df.head(50), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
