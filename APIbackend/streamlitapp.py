import streamlit as st, pandas as pd, requests
API = "http://localhost:8000"
st.set_page_config("Agente Inteligente", layout="wide")
st.title("🧠 Interface do Agente")

if "token" not in st.session_state: st.session_state.token = None

def login(email, senha):
    r = requests.post(f"{API}/login", json={"email": email, "senha": senha})
    return r.json() if r.status_code == 200 else None

def cadastro(email, senha):
    return requests.post(f"{API}/cadastro", json={"email": email, "senha": senha})

def executar(token, id_sessao):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API}/executar", json={"id_sessao": id_sessao}, headers=h)
    return r.json()

def sessao(token, id_sessao):
    h = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API}/sessao/{id_sessao}", headers=h)
    return r.json()

tab1, tab2, tab3 = st.tabs(["🔐 Login", "🚀 Executar", "📊 Sessão"])

with tab1:
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Login"):
        r = login(email, senha)
        if r: st.session_state.token = r["access_token"]; st.success("Login OK")
        else: st.error("Erro")
    if st.button("Cadastrar"): cadastro(email, senha)

with tab2:
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão", value="sessao_001")
        if st.button("Executar agente"):
            r = executar(st.session_state.token, id_sessao)
            st.json(r)
    else: st.warning("Faça login")

with tab3:
    if st.session_state.token:
        id_sessao = st.text_input("Consultar sessão", value="sessao_001", key="consulta")
        if st.button("Consultar"):
            r = sessao(st.session_state.token, id_sessao)
            st.write("📜 Histórico:", r.get("historico", []))
            if "consolidado" in r:
                df = pd.DataFrame(r["consolidado"])
                st.dataframe(df)
    else: st.warning("Faça login")
