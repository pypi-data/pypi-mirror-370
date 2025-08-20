from typing import Optional, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings

class CommonConfigs(BaseSettings):
    service_name: Optional[str] = None
    service_port: Optional[int] = None
    service_id: Optional[str] = None
    service_hostname: Optional[Any] = '127.0.0.1'
    service_host: Optional[str] = None

#     db
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DB_ALEMBIC_URL: Optional[str] = None

    # Broker

    RABBITMQ_URL: Optional[str] = None

    DIGITALOCEAN_STORAGE_BUCKET_NAME: Optional[str] = None
    DIGITALOCEAN_S3_ENDPOINT_URL: Optional[str] = None

    @property
    def database_url(self) -> Optional[str]:
        """Construct the database URL if all required fields are present."""
        required_fields = [
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB
        ]
        if all(required_fields):
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


configs = CommonConfigs()