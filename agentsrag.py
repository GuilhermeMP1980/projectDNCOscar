from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from .prompts import get_custom_prompt

def create_rag_agent(vectorstore: FAISS):
    """
    Cria um agente RAG com GPT-4 e base vetorial FAISS.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        max_tokens=512
    )

    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": get_custom_prompt()}
    )

    return qa_chain