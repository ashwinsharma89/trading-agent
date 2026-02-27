"""
Configuration management for Financial Ratio Chart App
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Zerodha Kite Connect (Primary Indian data source)
    ZERODHA_API_KEY: str = ""
    ZERODHA_API_SECRET: str = ""
    ZERODHA_ACCESS_TOKEN: str = ""
    ZERODHA_REQUEST_TOKEN: str = ""

    # Upstox (Fallback Indian data source)
    UPSTOX_CLIENT_ID: str = ""
    UPSTOX_CLIENT_SECRET: str = ""
    UPSTOX_REDIRECT_URI: str = "http://localhost:8000/auth/upstox/callback"
    UPSTOX_ACCESS_TOKEN: str = ""

    # External data APIs
    TWELVE_DATA_API_KEY: str = ""
    FRED_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 900  # 15 minutes

    # Primary Indian data source: "zerodha" or "upstox"
    INDIAN_DATA_SOURCE: str = "zerodha"

    # App settings
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # SQLite database path
    DB_PATH: str = "ratio_chart.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
