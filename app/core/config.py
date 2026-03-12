import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = "TrackUp"
    VERSION: str = "0.1.0"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://models.inference.ai.azure.com") # Defaulting to GitHub Models endpoint as hint
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

settings = Settings()
