from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    OPENAI_API_KEY: str
    DATABASE_URL_ASYNC: str
    SUPABASE_URL: str
    SUPABASE_API_KEY: str
    SUPABASE_SERVICE_ROLE: str


settings = Settings()

