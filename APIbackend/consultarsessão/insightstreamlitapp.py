import streamlit as st
import pandas as pd
import requests
import plotly.express as px

API_URL = "http://localhost:8000"

# ... [autenticação e execução do agente como antes] ...

elif menu == "📊 Consultar Sessão":
    st.subheader("📊 Visualizar sessão consolidada")
    if st.session_state.token:
        id_sessao = st.text_input("ID da sessão para consulta", value="sessao_001")
        if st.button("Consultar"):
            sessao = consultar_sessao(id_sessao)
            if "consolidado" in sessao:
                df = pd.DataFrame(sessao["consolidado"])
                st.dataframe(df)

                st.markdown("### 📌 Insights")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de produtos", df["produto_id"].nunique())
                with col2:
                    if "quantidade" in df.columns:
                        st.metric("Quantidade total", int(df["quantidade"].sum()))
                with col3:
                    if "valor" in df.columns:
                        st.metric("Valor médio", round(df["valor"].mean(), 2))

                st.markdown("### 📊 Gráfico de Quantidade por Produto")
                if "quantidade" in df.columns:
                    fig = px.bar(df, x="produto_id", y="quantidade", title="Distribuição de Quantidade")
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📈 Gráfico de Valor por Produto")
                if "valor" in df.columns:
                    fig2 = px.scatter(df, x="produto_id", y="valor", color="valor", title="Valor por Produto")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum dado consolidado encontrado.")
    else:
        st.warning("⚠️ Você precisa estar logado para consultar sessões.")
