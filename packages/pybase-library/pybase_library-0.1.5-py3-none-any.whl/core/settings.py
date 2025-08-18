from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    public_key_url: str = "https://staging-iam.gt.vng.vn"
    algorithm: str = "RS256"
    token_header: str = "Authorization"
    token_prefix: str = "Bearer "
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    excluded_paths: List[str] = ["/", "/docs", "/redoc", "/openapi.json", "/health", "/favicon.ico", "/mock-token"]
    unauthorized_message: str = "Token không hợp lệ"