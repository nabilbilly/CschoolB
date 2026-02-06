# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import field_validator
# from typing import Optional, List, Union


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#         extra="ignore"
#     )

#     PROJECT_NAME: str
#     API_V1_STR: str
    
#     # Database
#     DATABASE_URL: str

#     # Security
#     SECRET_KEY: str
#     ALGORITHM: str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int

#     # Environment
#     ENVIRONMENT: str

#     # Optional
#     PORT: int

#     # CORS
#     BACKEND_CORS_ORIGINS: List[str] = []

#     @field_validator("BACKEND_CORS_ORIGINS", mode="before")
#     @classmethod
#     def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
#         if v is None or v == "":
#             return []
#         if isinstance(v, str):
#             if v.startswith("["):
#                 import json
#                 return json.loads(v)
#             return [i.strip() for i in v.split(",")]
#         return v

#     @property
#     def sqlalchemy_database_uri(self) -> str:
#         # Railway/Heroku compatibility: replace postgres:// with postgresql://
#         if self.DATABASE_URL.startswith("postgres://"):
#             return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
#         return self.DATABASE_URL


# settings = Settings()




from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union, Literal

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
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self.DATABASE_URL

settings = Settings()
