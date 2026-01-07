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
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="Scoutly AI API")

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_ai(data: Question):
    try:
        # TEMPORARY SAFE RESPONSE (no OpenAI)
        return {
            "answer": (
                "I’m currently running in offline mode. "
                "Here’s a general Scout-related answer:\n\n"
                "The Scout Law is a set of principles that guide a Scout’s behavior, "
                "including being trustworthy, loyal, helpful, friendly, courteous, "
                "kind, obedient, cheerful, thrifty, brave, clean, and reverent."
            )
        }

    except Exception as e:
        return {
            "answer": "Sorry — something went wrong, but the server is still running."
        }
