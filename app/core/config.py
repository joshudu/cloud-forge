import os
from pydantic_settings import BaseSettings
from functools import cached_property

class Settings(BaseSettings):
    environment: str = "local"
    aws_region: str = "eu-west-1"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Local development only — ignored in production
    database_url: str = ""
    jwt_secret_key: str = ""

    @cached_property
    def get_database_url(self) -> str:
        if self.environment == "local":
            return self.database_url
        from app.core.secrets import get_db_secret
        secret = get_db_secret()
        return (
            f"postgresql+asyncpg://{secret['username']}:{secret['password']}"
            f"@{secret['host']}/{secret['dbname']}"
        )

    @cached_property
    def get_jwt_secret(self) -> str:
        if self.environment == "local":
            return self.jwt_secret_key
        from app.core.secrets import get_jwt_secret
        return get_jwt_secret()["secret_key"]

    class Config:
        env_file = ".env"

settings = Settings()