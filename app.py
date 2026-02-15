"""
Main FastAPI application for BnB Chatbot.
Run with:
    uvicorn app:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse
from services.chatbot import ChatService

app = FastAPI(title="BnB Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ChatService()


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
