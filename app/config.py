from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "factory-knowledge-agent"
    app_env: str = "development"
    api_prefix: str = "/api/v1"

    openai_api_key: str | None = None
    database_url: str = "sqlite:///./factory_agent.db"
    chroma_persist_dir: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()