from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MySQL connection
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "claims_processing_agent"

    # Auth / JWT
    jwt_secret_key: str = "change-this-in-your-.env-file"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # LLM (filled in once we build the agent)
    anthropic_api_key: str = ""

    # RAG
    embedding_model_name: str = "all-mpnet-base-v2"
    vector_store_dir: str = "./vector_store"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Other files just do: `from src.config.settings import settings`
settings = Settings()
