from langchain.llms import Ollama, OpenAI, ChatAnthropic, ChatGoogleGenerativeAI

# Modelo local via Ollama
ollama_llm = Ollama(model="mistral")

# Fallbacks proprietários
openai_llm = OpenAI(model="gpt-4")
claude_llm = ChatAnthropic(model="claude-3-opus-20240229")
gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro")
def interpretar_com_ollama(state):
    try:
        resposta = ollama_llm.invoke(state["llm"])
        state["interpretacao"] = resposta
        state["modelo_usado"] = "ollama"
        return "decidir_acao"
    except Exception:
        return "interpretar_com_modelo_proprietario"

def interpretar_com_modelo_proprietario(state):
    try:
        # Prioridade: OpenAI → Claude → Gemini
        for modelo, nome in [(openai_llm, "openai"), (claude_llm, "claude"), (gemini_llm, "gemini")]:
            try:
                resposta = modelo.invoke(state["llm"])
                state["interpretacao"] = resposta
                state["modelo_usado"] = nome
                return "decidir_acao"
            except Exception:
                continue
        state["interpretacao"] = "Não foi possível interpretar com nenhum modelo."
        state["modelo_usado"] = "falha"
        return "responder_erro"
    except Exception:
        state["interpretacao"] = "Erro inesperado."
        return "responder_erro"
graph = StateGraph(AgentState)

graph.add_node("interpretar_com_ollama", interpretar_com_ollama)
graph.add_node("interpretar_com_modelo_proprietario", interpretar_com_modelo_proprietario)
graph.add_node("decidir_acao", decidir_acao_node)
graph.add_node("responder_erro", responder_erro)

graph.set_entry_point("interpretar_com_ollama")
graph.add_conditional_edges("interpretar_com_ollama", {
    "decidir_acao": "decidir_acao",
    "interpretar_com_modelo_proprietario": "interpretar_com_modelo_proprietario"
})
graph.add_edge("interpretar_com_modelo_proprietario", "decidir_acao")
