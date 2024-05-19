from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    yandex_gpt_api: SecretStr
    yandex_gpt_catalogue: SecretStr
    tessdata_prefix: SecretStr
    prompt_system: SecretStr
    prompt_user: SecretStr
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


config = Settings()