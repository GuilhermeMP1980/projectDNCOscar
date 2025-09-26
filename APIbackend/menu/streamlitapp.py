import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

# ============================
# Sessão de autenticação
# ============================
if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = ""

# ============================
# Funções de API
# ============================
def login(email, senha):
    r = requests.post(f"{API_URL}/login", json={"email": email, "senha": senha})
    if r.status_code == 200:
        st.session_state.token = r.json()["access_token"]
        st.session_state.email = email
        return True
    return False

def cadastro(email, senha):
    r = requests.post(f"{API_URL}/cadastro", json={"email": email, "senha": senha})
    return r.status_code == 200

def executar_agente(id_sessao):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.post(f"{API_URL}/executar", json={"id_sessao": id_sessao}, headers=headers)
    return r.json()

def consultar_sessao(id_sessao):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.get(f"{API_URL}/sessao/" + id_sessao, headers=headers)
    return r.json()

# ============================
# Interface principal
# ============================
st.set_page_config(page_title="Agente Inteligente", layout="wide")
st.sidebar.title("🧭 Navegação")
menu = st.sidebar.radio("Escolha uma opção:", ["🏠 Início", "🔐 Login/Cadastro", "🚀 Executar Agente", "📊 Consultar Sessão"])

st.title("🧠 Sistema de Agentes Inteligentes")

# ============================
# Tela de boas-vindas
# ============================
if menu == "🏠 Início":
    st.markdown("""
    ### Bem-vindo!
    Este sistema permite que você:
    - Faça login ou crie uma conta
    - Execute agentes inteligentes que consolidam dados operacionais
    - Visualize sessões e resultados diretamente na interface

    Use o menu lateral para navegar pelas funcionalidades.
    """)

# ============================
# Login e Cadastro
# ============================
elif menu == "🔐 Login/Cadastro":
    st.subheader("🔐 Autenticação")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if login(email, senha):
                st.success("✅ Login realizado com sucesso!")
            else:
                st.error("❌ Credenciais inválidas")
    with col2:
        if st.button("Cadastrar"):
            if cadastro(email, senha):
                st.success("✅ Cadastro realizado!")
            else:
                st.error("❌ Erro ao cadastrar")

# ============================
# Execução do agente
# ============================
elif menu == "🚀 Executar Agente":
    st.subheader("🚀 Executar agente inteligente")
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão", value="sessao_001")
        if st.button("Executar"):
            resultado = executar_agente(id_sessao)
            st.success("✅ Execução concluída")
            st.json(resultado)
    else:
        st.warning("⚠️ Você precisa estar logado para executar o agente.")

# ============================
# Consulta de sessão
# ============================
elif menu == "📊 Consultar Sessão":
    st.subheader("📊 Visualizar sessão consolidada")
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão para consulta", value="sessao_001")
        if st.button("Consultar"):
            sessao = consultar_sessao(id_sessao)
            if "historico" in sessao:
                st.write("📜 Histórico:", sessao["historico"])
            if "consolidado" in sessao:
                df = pd.DataFrame(sessao["consolidado"])
                st.dataframe(df)
            else:
                st.warning("⚠️ Nenhum dado consolidado encontrado.")
    else:
        st.warning("⚠️ Você precisa estar logado para consultar sessões.")
