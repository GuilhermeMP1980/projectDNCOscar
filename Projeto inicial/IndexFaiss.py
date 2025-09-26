from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

def index_data(dfs):
    docs = []
    for df in dfs:
        for _, row in df.iterrows():
            content = "\n".join([f"{col}: {val}" for col, val in row.items()])
            docs.append(Document(page_content=content))
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore
