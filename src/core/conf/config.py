from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
