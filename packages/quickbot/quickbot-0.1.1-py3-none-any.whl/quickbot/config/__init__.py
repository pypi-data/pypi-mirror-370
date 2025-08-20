from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Self
import warnings


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    STACK_NAME: str = "quickbot"

    SECRET_KEY: str = "changethis"

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    DB_NAME: str = "app"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "app"
    DB_PASSWORD: str = "changethis"

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    API_PORT: int = 8000

    TELEGRAM_WEBHOOK_DOMAIN: str = "localhost"
    TELEGRAM_WEBHOOK_SCHEME: str = "https"
    TELEGRAM_WEBHOOK_PORT: int = 443

    @property
    def TELEGRAM_WEBHOOK_URL(self) -> str:
        return f"{self.TELEGRAM_WEBHOOK_SCHEME}://{self.TELEGRAM_WEBHOOK_DOMAIN}{
            f':{self.TELEGRAM_WEBHOOK_PORT}'
            if (
                (
                    self.TELEGRAM_WEBHOOK_PORT != 80
                    and self.TELEGRAM_WEBHOOK_SCHEME == 'http'
                )
                or (
                    self.TELEGRAM_WEBHOOK_PORT != 443
                    and self.TELEGRAM_WEBHOOK_SCHEME == 'https'
                )
            )
            else ''
        }"

    TELEGRAM_WEBHOOK_AUTH_KEY: str = "changethis"

    TELEGRAM_BOT_USERNAME: str = "quickbot"
    TELEGRAM_BOT_SERVER: str = "https://api.telegram.org"
    TELEGRAM_BOT_SERVER_IS_LOCAL: bool = False
    TELEGRAM_BOT_TOKEN: str = "changethis"

    ADMIN_TELEGRAM_ID: int

    LOG_LEVEL: str = "DEBUG"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("DB_PASSWORD", self.DB_PASSWORD)
        self._check_default_secret("TELEGRAM_BOT_TOKEN", self.TELEGRAM_BOT_TOKEN)

        return self


config = Config()
