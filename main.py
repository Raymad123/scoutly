from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from openai import OpenAI

# Initialize app
app = FastAPI(title="Scout AI API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----- Data Model -----
class QuestionRequest(BaseModel):
    question: str

# ----- Web Search (DuckDuckGo Instant Answer API) -----
def web_search(query: str) -> str:
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        related = data.get("RelatedTopics", [])
        if related:
            if isinstance(related[0], dict):
                return related[0].get("Text", "")

        return ""
    except Exception:
        return ""

# ----- GPT Fallback / Reasoning -----
def ai_answer(question: str, web_info: str) -> str:
    prompt = f"""
You are an expert assistant on Scouts BSA, Boy Scouts, and scouting topics.
Answer clearly, accurately, and age-appropriate.

Web information (may be empty):
{web_info}

Question:
{question}

If web info is weak, rely on general scouting knowledge.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Scout handbook expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400
    )

    return response.choices[0].message.content.strip()

# ----- API Endpoint -----
@app.post("/ask")
def ask_scout_ai(req: QuestionRequest):
    web_info = web_search(req.question)
    answer = ai_answer(req.question, web_info)

    return {
        "question": req.question,
        "answer": answer
    }
