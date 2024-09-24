from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    mongodb_token: SecretStr
    gpt_token: SecretStr
    system_content_table: SecretStr
    system_content_analyzer: SecretStr
    prompt: SecretStr
    system_content_bioethic: SecretStr

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()
