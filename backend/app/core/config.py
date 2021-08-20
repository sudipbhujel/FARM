from typing import List

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FARM stack"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        case_sensitive = True


settings = Settings()
