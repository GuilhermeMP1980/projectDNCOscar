from fastapi import FastAPI, UploadFile, Form
from fastapi import APIRouter

app = FastAPI(title="Retail RAG Agent")
app.include_router(APIRouter)
