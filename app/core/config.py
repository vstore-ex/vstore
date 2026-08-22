import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "vstore"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vstore.db")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@ex.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "givemeapasssword")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-duper-very-secret-key-lol")
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")

settings = Settings()
