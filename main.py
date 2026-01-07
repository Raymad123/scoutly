from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Scoutly API")

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "Scoutly backend running"}

@app.post("/ask")
def ask(data: Question):
    return {
        "answer": (
            "The Scout Law is a set of principles that guide how Scouts behave. "
            "A Scout is trustworthy, loyal, helpful, friendly, courteous, kind, "
            "obedient, cheerful, thrifty, brave, clean, and reverent."
        )
    }
