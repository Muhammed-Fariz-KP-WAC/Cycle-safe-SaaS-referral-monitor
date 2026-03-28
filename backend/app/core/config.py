from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cycle-Safe Referral Engine"
    api_prefix: str = "/api"
    database_url: str = "postgresql+psycopg://referral:referral@localhost:5432/referral_engine"
    cors_origins: list[str] = ["*"]
    reward_max_depth: int = 3
    reward_type: str = "fixed"
    reward_level_1: float = 100.0
    reward_level_2: float = 50.0
    reward_level_3: float = 25.0
    velocity_limit_per_minute: int = 5
    referral_expiry_days: int = 365
    recent_activity_limit: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
