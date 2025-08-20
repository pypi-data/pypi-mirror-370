from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-2024-11-20"
    MESSAGE_HISTORY_DEPTH: int = 20
    SEND_TYPING: bool = True


config = Config()
