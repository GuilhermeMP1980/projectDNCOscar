from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================
# 1. Conexão com PostgreSQL
# ============================
CONNECTION_STRING = "postgresql+psycopg2://usuario:senha@localhost:5432/meubanco"

# ============================
# 2. Embeddings e Vetorstore
# ============================
embedding = OllamaEmbeddings(model="mistral")

vectorstore = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embedding,
    collection_name="skus_collection"
)

# ============================
# 3. Armazenar documentos
# ============================
docs = [
    Document(page_content="SKU_1 está em Estoque_2 e Estoque_3."),
    Document(page_content="SKU_2 aparece apenas em Estoque_1."),
    Document(page_content="SKU_3 tem baixa similaridade com outros SKUs."),
]

splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_documents(docs)

vectorstore.add_documents(chunks)

# ============================
# 4. Recuperação via RAG
# ============================
retriever = vectorstore.as_retriever()
llm = Ollama(model="mistral")

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

query = "Quais SKUs estão em Estoque_2?"
result = rag_chain.invoke({"query": query})

print("Resposta:")
print(result["result"])

print("\n Fontes:")
for doc in result["source_documents"]:
    print("-", doc.page_content)

# ============================
# 5. Persistência de Estado
# ============================
Base = declarative_base()

class EstadoAgente(Base):
    __tablename__ = "estado_agente"
    id = Column(String, primary_key=True)
    estado = Column(JSON)

engine = create_engine(CONNECTION_STRING)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Exemplo de estado
state = {
    "llm": query,
    "resposta": result["result"],
    "modelo_usado": "mistral"
}

# Salvar estado
novo_estado = EstadoAgente(id="sessao_001", estado=state)
session.merge(novo_estado)
session.commit()
