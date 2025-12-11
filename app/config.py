from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ETHERSCAN_API_KEY: str = ""
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/fp_basdat"
    MYSQLHOST: str | None = None
    MYSQLPORT: int | None = None
    MYSQLUSER: str | None = None
    MYSQLPASSWORD: str | None = None
    MYSQLDATABASE: str | None = None
    RAILWAY_DATABASE_URL: str | None = None
    RAILWAY_TCP_PROXY_DOMAIN: str | None = None
    RAILWAY_TCP_PROXY_PORT: int | None = None
    RATE_LIMIT: int = 5
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "your-super-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    def rate_limit_str(self) -> str:
        return f"{self.RATE_LIMIT}/minute"

    def model_post_init(self, __context) -> None:
        # Prefer explicit Railway MySQL env vars when available
        if (
            self.MYSQLHOST
            and self.MYSQLPORT
            and self.MYSQLUSER
            and self.MYSQLPASSWORD
            and self.MYSQLDATABASE
        ):
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQLUSER}:{self.MYSQLPASSWORD}"
                f"@{self.MYSQLHOST}:{self.MYSQLPORT}/{self.MYSQLDATABASE}"
            )
            return

        # Fallback to Railway TCP proxy domain/port if provided
        if (
            self.RAILWAY_TCP_PROXY_DOMAIN
            and self.RAILWAY_TCP_PROXY_PORT
            and self.MYSQLUSER
            and self.MYSQLPASSWORD
            and self.MYSQLDATABASE
        ):
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQLUSER}:{self.MYSQLPASSWORD}"
                f"@{self.RAILWAY_TCP_PROXY_DOMAIN}:{self.RAILWAY_TCP_PROXY_PORT}/{self.MYSQLDATABASE}"
            )
            return

        # If Railway provides a full database URL, normalize driver to pymysql
        if self.RAILWAY_DATABASE_URL:
            url = self.RAILWAY_DATABASE_URL
            if url.startswith("mysql://"):
                url = "mysql+pymysql://" + url[len("mysql://") :]
            self.DATABASE_URL = url
            return

        # Normalize driver for plain mysql scheme in DATABASE_URL
        if self.DATABASE_URL.startswith("mysql://"):
            self.DATABASE_URL = "mysql+pymysql://" + self.DATABASE_URL[len("mysql://") :]


settings = Settings()
