"""
Chat service handling OpenAI interactions and session memory.
Supports DEV_MODE to avoid API billing during development.
"""

import os
from typing import Dict, List

from openai import AsyncOpenAI
from config import settings
from database import is_available, calculate_price


class ChatService:
    def __init__(self) -> None:
        self.dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"
        self.sessions: Dict[str, List[dict]] = {}

        self.system_prompt = {
            "role": "system",
            "content": (
                "You are a professional assistant for a boutique BnB website. "
                "Answer clearly and concisely."
            ),
        }

        if not self.dev_mode:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment.")
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_response(self, session_id: str, message: str) -> str:
        if self.dev_mode:
            return self._mock_response(message)

        if session_id not in self.sessions:
            self.sessions[session_id] = [self.system_prompt]

        self.sessions[session_id].append(
            {"role": "user", "content": message}
        )

        completion = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.sessions[session_id],
            temperature=0.3,
        )

        reply = completion.choices[0].message.content
        self.sessions[session_id].append(
            {"role": "assistant", "content": reply}
        )

        return reply

    def _mock_response(self, message: str) -> str:
        message = message.lower().strip()

        # Booking intent trigger
        if "book" in message or "availability" in message:
            return (
                "I'd be happy to check availability 😊\n"
                "Please provide your dates in this format:\n"
                "YYYY-MM-DD to YYYY-MM-DD"
            )

        # Date parsing logic
        if "to" in message and "-" in message:
            try:
                parts = message.split("to")
                check_in = parts[0].strip()
                check_out = parts[1].strip()

                if is_available(check_in, check_out):
                    price = calculate_price(check_in, check_out)

                    return (
                        f"🎉 Great news! The property is available.\n"
                        f"Total price for your stay: ${price:.2f}\n\n"
                        f"Would you like to proceed with booking?"
                    )
                else:
                    return (
                        "Unfortunately those dates are not available.\n"
                        "Would you like to try different dates?"
                    )

            except Exception:
                return (
                    "Please provide dates in the correct format:\n"
                    "YYYY-MM-DD to YYYY-MM-DD"
                )

        # General FAQ fallback
        faq = {
            "check-in": "Check-in starts at 3 PM.",
            "check out": "Check-out is at 11 AM.",
            "wifi": "Yes, we provide free high-speed WiFi.",
            "parking": "Free parking is available on-site.",
            "pets": "Sorry, pets are not allowed.",
            "location": "We are located in the city center, 5 minutes from downtown.",
        }

        for key, value in faq.items():
            if key in message:
                return value

        return "How can I assist you with your stay today?"
