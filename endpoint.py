from fastapi import APIRouter, UploadFile, Form
from ingestion.loader import load_files
from api.session_manager import SessionManager
from utils.prompts import format_query
import shutil, os

router = APIRouter()
session_manager = SessionManager()

@router.post("/upload/")
async def upload_file(user_id: str = Form(...), file: UploadFile = Form(...)):
    path = f"data/{user_id}/"
    os.makedirs(path, exist_ok=True)
    with open(f"{path}/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    dfs = load_files(path)
    session_manager.create_session(user_id, dfs)
    return {"status": "Arquivo processado"}

@router.post("/query/")
async def query(user_id: str = Form(...), question: str = Form(...)):
    agent = session_manager.get_agent(user_id)
    if not agent:
        return {"error": "Sessão não encontrada"}
    response = agent.run(format_query(question))
    return {"response": response}