from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://libuser:libpass@localhost:5432/libraryhub"
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    AWS_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"

    LLM_PROVIDER: str = "mock"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    RECOMMENDATION_ENGINE: str = "hybrid"

    class Config:
        env_file = ".env"


settings = Settings()
