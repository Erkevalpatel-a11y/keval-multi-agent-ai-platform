from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Keval Multi-Agent AI Platform"
    ai_base_url: str = ""
    ai_model: str = ""
    ai_api_key: str = ""
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 20
    upload_dir: str = "uploads"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
