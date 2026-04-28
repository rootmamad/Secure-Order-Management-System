from pydantic_settings import SettingsConfigDict,BaseSettings


class Setting(BaseSettings):
    secret_key : str
    algorithm : str
    URl_Database:str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Setting()