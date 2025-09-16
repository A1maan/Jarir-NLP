"""
FastAPI wrapper exposing /chat for the browser extension.
Run with:  uvicorn app:app --reload
"""

# testing time
import time

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent_core import generate_response

class ChatReq(BaseModel):
    message: str
    context: dict | None = None

app = FastAPI(title="Jarir-AI Backend", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten after demo
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(req: ChatReq):
    answer = generate_response(req.message, req.context)
    return {"reply": answer}
