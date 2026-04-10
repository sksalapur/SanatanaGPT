from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    FIREBASE_CREDENTIALS: str = "serviceAccountKey.json"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    ADMIN_UID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
