from logging import config as logging_config
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


class RedisSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "localhost"
    port: int = 6379

    @property
    def url(self):
        return f"redis://{self.host}:{self.port}"


class MongoSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="MONGO_")
    host: str = "localhost"
    port: int = 27017
    database: str = "likes"

    @property
    def url(self):
        return f"mongodb://{self.host}:{self.port}"


class Settings(BaseSettings):

    project: str = "likes"
    cache_expire_in_seconds: int = 60 * 5
    use_cache: bool = True
    enable_tracer: bool = False
    AUTH_API_URL: str = "http://nginx/auth/api/v1/user/verify"
    UGC_API_URL: str = "http://nginx/ugc/api/v1"
    redis: RedisSetting = RedisSetting()
    mongo: MongoSetting = MongoSetting()


settings = Settings()
