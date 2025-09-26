import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

# ============================
# 1. Autenticação
# ============================
def login(email, senha):
    resp = requests.post(f"{API_URL}/login", json={"email": email, "senha": senha})
    return resp.json() if resp.status_code == 200 else None

def cadastro(email, senha):
    return requests.post(f"{API_URL}/cadastro", json={"email": email, "senha": senha})

# ============================
# 2. Execução do agente
# ============================
def executar_agente(token, id_sessao):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/executar", json={"id_sessao": id_sessao}, headers=headers)
    return resp.json()

def recuperar_sessao(token, id_sessao):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_URL}/sessao/" + id_sessao, headers=headers)
    return resp.json()

# ============================
# 3. Interface Streamlit
# ============================
st.set_page_config(page_title="Agente Inteligente", layout="wide")
st.title("Interface do Agente Inteligente")

if "token" not in st.session_state:
    st.session_state.token = None

tab1, tab2, tab3 = st.tabs(["Login/Cadastro", "Executar Agente", "Sessão & Dados"])

with tab1:
    st.subheader("Autenticação")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            result = login(email, senha)
            if result:
                st.session_state.token = result["access_token"]
                st.success("Login realizado com sucesso!")
            else:
                st.error("Credenciais inválidas")
    with col2:
        if st.button("Cadastrar"):
            r = cadastro(email, senha)
            if r.status_code == 200:
                st.success("Cadastro realizado!")
            else:
                st.error("Erro no cadastro")

with tab2:
    st.subheader("Executar agente")
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão", value="sessao_001")
        if st.button("Executar"):
            resultado = executar_agente(st.session_state.token, id_sessao)
            st.json(resultado)
    else:
        st.warning("Faça login para executar o agente")

with tab3:
    st.subheader("Sessão e Dados Consolidados")
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão para consulta", value="sessao_001", key="consulta")
        if st.button("Consultar sessão"):
            sessao = recuperar_sessao(st.session_state.token, id_sessao)
            if "estado" in sessao:
                st.write("Histórico:", sessao["estado"].get("historico", []))
                if "consolidado" in sessao["estado"]:
                    df = pd.DataFrame(sessao["estado"]["consolidado"])
                    st.dataframe(df)
            else:
                st.error("Sessão não encontrada")
    else:
        st.warning("Faça login para consultar sessões")
