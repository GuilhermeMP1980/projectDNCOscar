import streamlit as st
import requests

st.title("Retail RAG Agent")
user_id = st.text_input("Seu ID de usuário")

uploaded_file = st.file_uploader("Envie seu arquivo CSV/XLSX")
if uploaded_file:
    res = requests.post("http://localhost:8000/upload/", files={"file": uploaded_file}, data={"user_id": user_id})
    st.success("Arquivo enviado e processado!")

query = st.text_input("Digite sua pergunta")
if st.button("Enviar"):
    res = requests.post("http://localhost:8000/query/", data={"user_id": user_id, "question": query})
    st.write(res.json()["response"])
