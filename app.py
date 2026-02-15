"""
Main FastAPI application for BnB Chatbot.
Run with:
    uvicorn app:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

from models import ChatRequest, ChatResponse
from services.chatbot import ChatService
from database import init_db

app = FastAPI(title="BnB Chatbot API")

# Initialize database
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()


@app.get("/")
async def root():
    return {"message": "BnB Chatbot API is running."}


@app.get("/debug/bookings")
async def debug_bookings():
    """
    Debug endpoint to view all bookings.
    Remove in production.
    """
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    rows = cursor.fetchall()
    conn.close()

    return {"bookings": rows}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = await chat_service.generate_response(
            session_id=request.session_id,
            message=request.message
        )
        return ChatResponse(reply=response)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
