from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union, Literal, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",              # local dev convenience
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "cschool Backend"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str

    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    PORT: int = 8001

    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]):
        if not v:
            return []
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def DEBUG(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def docs_url(self) -> Optional[str]:
        return "/docs" if self.ENVIRONMENT != "production" else None

    @property
    def redoc_url(self) -> Optional[str]:
        return "/redoc" if self.ENVIRONMENT != "production" else None

    @property
    def openapi_url(self) -> Optional[str]:
        return f"{self.API_V1_STR}/openapi.json" if self.ENVIRONMENT != "production" else None

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

settings = Settings()
