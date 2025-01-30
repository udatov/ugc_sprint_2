from logging import config as logging_config
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


class KafksSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="KAFKA_")
    host: str = "ugc-kafka-0"
    port: int = 9094

    @property
    def bootstrap_servers(self):
        return f"{self.host}:{self.port}"


class Settings(BaseSettings):

    project: str = "likes"
    cache_expire_in_seconds: int = 60 * 5
    use_cache: bool = True
    enable_tracer: bool = False
    errors_max: int = 10


settings = Settings()
