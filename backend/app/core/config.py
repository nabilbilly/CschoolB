from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    PROJECT_NAME: str = "cschool Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: Optional[str] = None
    PORT: int = 8001
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "https://saas-production-aaeb.up.railway.app",
        "https://confident-celebration-production.up.railway.app",
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL:
            # Handle Railway/Heroku old postgres:// schema
            if self.DATABASE_URL.startswith("postgres://"):
                return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
            return self.DATABASE_URL
        # Fallback for local development if DATABASE_URL is missing
        return "postgresql://postgres:123@localhost:5432/cschool_db"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
