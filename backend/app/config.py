from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://dashboard:dashboard@localhost:5432/dashboard"
    api_key: str = "change-me-before-deploy"

    # Meta Ads
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_access_token: str = ""

    # Google Ads
    google_ads_developer_token: str = ""
    google_ads_client_id: str = ""
    google_ads_client_secret: str = ""
    google_ads_refresh_token: str = ""
    google_ads_login_customer_id: str = ""

    # GA4 (fase 7)
    ga4_property_id: str = ""
    google_service_account_file: str = "./credentials/dashboard-491401-c0437eaebae8.json"

    # App
    backend_url: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
