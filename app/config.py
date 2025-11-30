from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ETHERSCAN_API_KEY: str
    RATE_LIMIT: int = 5
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    def rate_limit_str(self) -> str:
        return f"{self.RATE_LIMIT}/minute"


settings = Settings()

