import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import field_validator

# Load .env locally (in production it will simply do nothing if .env isn't there)
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "cschool Backend"
    API_V1_STR: str = "/api/v1"

    # Database (required)
    DATABASE_URL: str = os.environ["DATABASE_URL"]

    # Security (required)
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Optional
    PORT: int = int(os.getenv("PORT", "8001"))

    # CORS (optional; set in env for production)
    BACKEND_CORS_ORIGINS: list[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def sqlalchemy_database_uri(self) -> str:
        # Railway/Heroku compatibility
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

settings = Settings()
