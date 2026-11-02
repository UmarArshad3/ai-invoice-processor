from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Invoice Processor"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str

    bedrock_model_id: str
    aws_region: str = "eu-north-1"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
