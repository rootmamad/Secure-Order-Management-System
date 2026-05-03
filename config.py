from pydantic_settings import SettingsConfigDict, BaseSettings


class Setting(BaseSettings):
    secret_key: str
    algorithm: str
    URl_Database: str
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    CELERY_BROKER: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Setting()
