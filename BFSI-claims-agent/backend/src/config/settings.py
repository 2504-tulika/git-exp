from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "claims_processing_agent"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    groq_api_key: str
    
    llm_model_name: str = "opeai/gpt-oss-120b"

    
    embedding_model_name: str = "all-mpnet-base-v2"
    vector_store_dir: str = "./vector_store"
    
    retrieval_top_k: int = 5

    max_chat_history_turns: int = 10

    cors_allowed_origins: str = "http://localhost:8501"

    log_level: str = "INFO"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()

