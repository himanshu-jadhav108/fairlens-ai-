from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any
import json

class Settings(BaseSettings):
    """
    Application Settings.
    This class loads environment variables and validates them.
    If a required variable is missing, the app will fail to start.
    """
    GEMINI_API_KEY: str
    FRONTEND_URL: str = "http://localhost:5173"
    FIREBASE_CREDENTIALS_JSON: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    
    # Database and Cache
    DATABASE_URL: str = "sqlite:///./fairlens.db" # Default for local dev if not provided
    REDIS_URL: str = "redis://localhost:6379/0"

    @property
    def firebase_credentials_dict(self) -> Dict[str, Any]:
        """Parses the JSON string into a dictionary for Firebase Admin."""
        if not self.FIREBASE_CREDENTIALS_JSON:
            return {}
        try:
            return json.loads(self.FIREBASE_CREDENTIALS_JSON)
        except json.JSONDecodeError:
            raise ValueError("FIREBASE_CREDENTIALS_JSON is not a valid JSON string.")

    # This tells pydantic to load from the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
