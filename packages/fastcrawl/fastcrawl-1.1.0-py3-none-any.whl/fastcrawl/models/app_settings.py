from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Settings for FastCrawl application.

    Attributes:
        workers (int): Number of worker threads to use for crawling. Defaults to 15.

    """

    workers: int = 15

    model_config = SettingsConfigDict(env_prefix="fastcrawl_app_", extra="ignore")
