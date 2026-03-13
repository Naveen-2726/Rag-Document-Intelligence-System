from fastapi import FastAPI
from backend.rag_pipeline import load_rag

app = FastAPI()

qa = load_rag()

@app.get("/")
def home():
    return {"message": "RAG Document Intelligence System Running"}

@app.get("/ask")
def ask_question(query: str):

    result = qa.run(query)

    return {"answer": result}