import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the absolute path to the directory two levels up (the project root where .env lives)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str = "" # Provide empty default just in case
    DB_NAME: str
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str 
    
    @property
    def database_url(self) -> str:
        # This stitches together the PyMySQL connection string
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Force Pydantic to look for the .env file in the exact ROOT_DIR, and ignore extra variables
    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"), 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# We create a single instance to import throughout the app
settings = Settings()