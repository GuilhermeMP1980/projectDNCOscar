from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import SessionLocal, criar_tabelas
from models.historico import HistoricoIA
import requests
import logging
import os
import traceback

from dotenv import load_dotenv
from loader import conectar_postgres, carregar_e_normalizar
from indexvectorstore import register_vector
from duckdbrunnerAnalytics import cruzar_dados
from agentsrag import Tool, initialize_agent
from prompts import format_query
from router import router  # Rotas adicionais

# Carrega variáveis do .env
load_dotenv()

# Configurações iniciais
DATA_PATH = os.getenv("DATA_PATH", "data")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/perguntar")

# Inicializa FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de entrada
class QueryRequest(BaseModel):
    query: str

# Inicialização dos componentes de IA
try:
    logger.info("Conectando ao PostgreSQL...")
    engine = conectar_postgres()

    logger.info("Carregando e normalizando dados...")
    dados_normalizados = carregar_e_normalizar(DATA_PATH)

    logger.info("Registrando vetor...")
    vectorstore = register_vector(engine, dados_normalizados)

    logger.info("Inicializando ferramenta e agente...")
    tool = Tool(vectorstore)
    agent = initialize_agent(tool)

    logger.info("Agente de IA inicializado com sucesso.")
except Exception as e:
    logger.error(f"Erro ao inicializar componentes de IA: {e}")
    raise

# Rotas adicionais
app.include_router(router, prefix="/api")

# Endpoint principal de IA
@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        formatted_query = format_query(request.query)
        response = agent({"question": formatted_query})

        if not response or "answer" not in response:
            raise ValueError("Resposta incompleta do agente.")

        dados_cruzados = cruzar_dados()
        tabela_md = dados_cruzados.to_markdown()

        resultado = {
            "answer": response["answer"],
            "sources": [doc.metadata.get("source", "desconhecido") for doc in response.get("source_documents", [])]
        }

        # Salva histórico
        salvar_historico(request.query, resultado["answer"])

        # Aciona fluxo n8n
        acionar_fluxo_n8n({
            "pergunta": request.query,
            "resposta": resultado["answer"],
            "fontes": resultado["sources"]
        })

        return JSONResponse(content=resultado)

    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "trace": traceback.format_exc()
        })

# Chame isso uma vez na inicialização
criar_tabelas()

# Para salvar uma interação
def salvar_historico(pergunta, resposta, sku=None, loja=None, cliente=None, nota_fiscal=None):
    db = SessionLocal()
    try:
        registro = HistoricoIA(
            pergunta=pergunta,
            resposta=resposta,
            sku=sku,
            loja=loja,
            cliente=cliente,
            nota_fiscal=nota_fiscal
        )
        db.add(registro)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar histórico: {e}")
    finally:
        db.close()

# Função para acionar webhook do n8n
def acionar_fluxo_n8n(payload: dict):
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        logger.info("Fluxo n8n acionado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao acionar fluxo n8n: {e}")
