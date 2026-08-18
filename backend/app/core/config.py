import os
import json
from typing import List, Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path=env_path)


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "UC05 - Healthcare Provider Access & Decision Intelligence")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Supabase Credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    def __init__(self, **data):
        super().__init__(**data)
        # Parse CORS_ORIGINS from env if provided
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                if cors_env.startswith("["):
                    self.CORS_ORIGINS = json.loads(cors_env)
                else:
                    self.CORS_ORIGINS = [i.strip() for i in cors_env.split(",") if i.strip()]
            except Exception:
                pass


settings = Settings()
