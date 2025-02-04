from logging import config as logging_config
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


class PGSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")
    host: str = "localhost"
    port: int = 5432
    name: str = "auth_database"
    user: str = "postgres"
    password: str = ""

    @property
    def dsn_asyncpg(self, db_name: str = None):
        db_name = db_name or self.name
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{db_name}"


class RedisSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "localhost"
    port: int = 6379

    @property
    def url(self):
        return f"redis://{self.host}:{self.port}"


class YandexOauthSetting(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="YANDEX_")
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str = "http://127.0.0.1/auth/api/v1/oauth/yandex/callback"
    OAUTH_URI: str = "https://oauth.yandex.com/authorize?"
    token_url: str = "https://oauth.yandex.com/token"
    login_url: str = "https://login.yandex.ru/info"

    @property
    def auth_url(self):
        return (
            f"{self.OAUTH_URI}response_type=code&"
            f"client_id={self.CLIENT_ID}&"
            f"redirect_uri={self.REDIRECT_URI}&"
            "scope=login:info"
        )


class Setting(BaseSettings):

    pg: PGSetting = PGSetting()
    redis: RedisSetting = RedisSetting()
    yandex_oauth: YandexOauthSetting = YandexOauthSetting()
    project: str = Field("auth", env="PROJECT_NAME")
    cache_expire_in_seconds: int = 60 * 5
    use_cache: bool = True
    default_role: str = "user"
    default_role_uuid: UUID = "fdcc42ea-d824-455c-9385-64acbf9a778b"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_in_minutes: int = 30
    refresh_token_expire_in_days: int = 7
    enable_tracer: bool = False
    errors_max: int = 10


settings = Setting()
