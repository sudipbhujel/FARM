import os
from typing import List

from pydantic import AnyHttpUrl, BaseSettings
from databases import DatabaseURL
from dotenv import load_dotenv

load_dotenv(".env")


class Settings(BaseSettings):
    PROJECT_NAME: str = "FARM stack"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
    MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))
    MONGODB_URL = os.getenv("MONGOURI", "")
    if not MONGODB_URL:
        MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
        MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
        MONGO_USER = os.getenv("MONGO_USER", "admin")
        MONGO_PASS = os.getenv("MONGO_PASSWORD", "markqiu")
        MONGO_DB = os.getenv("MONGO_DB", "fastapi")

        MONGODB_URL = DatabaseURL(
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
        )
    else:
        MONGODB_URL = DatabaseURL(MONGODB_URL)

    # Authentication and Authorization
    SECRET_KEY = os.getenv("SECRET_KEY", "Your secret key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Model Register
    MODELS = ["student", "user", "permission", "role"]


class Config:
    case_sensitive = True


database_name = os.getenv("MONGO_DB", "fastapi")
student_collection_name = "students"
users_collection_name = "users"
role_collection_name = "roles"

settings = Settings()
