from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_service_role_key: str
    supabase_anon_key: str
    supabase_jwt_secret: str = ""

    # OpenRouter
    openrouter_api_key: str
    llm_realtime_model: str = "google/gemini-2.5-flash-preview"
    llm_analysis_model: str = "anthropic/claude-sonnet-4-20250514"

    # App
    cors_origins: str = "http://localhost:3000"
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
