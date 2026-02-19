"""Chat endpoint — proxies user messages to the Claude-powered chatbot."""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import DB_PATH
from backend.services.chatbot import chat

router = APIRouter()


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]


class ChatResponse(BaseModel):
    reply: str
    messages: List[Dict[str, Any]]


@router.post("/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest):
    """Accept a conversation and return the assistant's reply."""
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages array cannot be empty")

    conn = sqlite3.connect(DB_PATH)
    try:
        result = chat(req.messages, conn)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat error: {e}")
    finally:
        conn.close()

    return result
