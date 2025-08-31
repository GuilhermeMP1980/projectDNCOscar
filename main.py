from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ingestion"))
from loader import load_files
sys.path.append(os.path.join(os.path.dirname(__file__), "vectorstore_index"))
from langchain.vectorstores import index_data
sys.path.append(os.path.join(os.path.dirname(__file__), "agent"))
from langchain.embeddings import create_agent_rag
from prompts import format_query

# Inicialização do FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logger = logging.getLogger(__name__)

# Modelo de entrada
class QueryRequest(BaseModel):
    query: str
  
# Inicialização dos componentes
dfs = load_files("data/")
vectorstore = index_data(dfs)
agent = create_agent_rag(vectorstore)

# Endpoint principal
@app.post("/ask")
def ask_question(request: QueryRequest):
    try:
        formatted = format_query(request.query)
        response = agent({"question": formatted})

        if "answer" not in response or "source_documents" not in response:
            raise ValueError("Resposta incompleta do agente.")

        return JSONResponse(content={
            "answer": response["answer"],
            "sources": [doc.metadata.get("source", "desconhecido") for doc in response["source_documents"]]
        })

    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro interno no servidor."})