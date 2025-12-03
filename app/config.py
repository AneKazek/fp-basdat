from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ETHERSCAN_API_KEY: str
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/fp_basdat"
    RATE_LIMIT: int = 5
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "your-super-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    def rate_limit_str(self) -> str:
        return f"{self.RATE_LIMIT}/minute"


settings = Settings()
