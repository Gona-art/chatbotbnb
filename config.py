"""
Configuration loader.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY")


settings = Settings()
