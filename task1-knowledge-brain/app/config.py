
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://consultant:"
        "local_dev_password@localhost:5433/consultant"
    )
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
