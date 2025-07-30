from pydantic import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./exchange_rates.db"
    ECHO: bool = False
    external_api_key: str = "secret_key"
    api_version: str = "1.0.0"
    api_title: str = "Exchange Rate API"
    api_description: str = "API for currency exchange rates"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
