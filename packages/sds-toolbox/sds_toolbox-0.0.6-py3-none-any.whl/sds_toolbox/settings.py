from pydantic_settings import BaseSettings
from pydantic import validator, FilePath, computed_field, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # DATABASE_URL: str = "sqlite:////tmp/sql_app.db"
    # Ajoutez d'autres paramètres de configuration ici

    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_NAME: str | None = None
    GCP_PROJECT: str | None = None
    GCP_DB_ZONE: str | None = None
    GCP_DB_INSTANCE: str | None = None
    GCP_APP_NAME: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    GAE_RUNTIME: str | None = None
    FORCE_CLOUD: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GCP_SERVICE_ACCOUNT: str | None = None

    @computed_field()
    def ENVIRONMENT(self) -> str:
        if None in [self.DB_USER, self.DB_PASS, self.DB_NAME]:
            return "LOCAL+SQLITE"
        elif any([self.GAE_RUNTIME, self.FORCE_CLOUD]):
            return "GCP"
        else:
            return "LOCAL+PROXY"

    @computed_field()
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == "LOCAL+SQLITE":
            return "sqlite:////tmp/test.db"
        elif self.ENVIRONMENT == "GCP":
            INSTANCE_CONNECTION_NAME = (
                f"{self.GCP_PROJECT}:{self.GCP_DB_ZONE}:{self.GCP_DB_INSTANCE}"
            )
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@/{self.DB_NAME}?host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
        else:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # ?charset=utf8mb4"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
