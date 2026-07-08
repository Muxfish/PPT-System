"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Generation
    max_slides: int = 30
    temperature: float = 0.7
    max_tokens: int = 4096

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
