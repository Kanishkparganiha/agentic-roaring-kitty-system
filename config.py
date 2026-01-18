from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
