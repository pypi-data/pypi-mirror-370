"""Configuration management for {{PROJECT_NAME}} service."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Service configuration with environment variable prefix."""
    
    model_config = SettingsConfigDict(
        env_prefix="{{PACKAGE_NAME|upper}}_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Service settings
    service_name: str = Field(default="{{PROJECT_NAME}}", description="Service name")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    log_level: str = Field(default="INFO", description="Log level")
    
    # API settings (uncomment if building API)
    # api_host: str = Field(default="0.0.0.0", description="API host")
    # api_port: int = Field(default=8000, description="API port")
    
    # Database settings (uncomment if using database)
    # database_url: str | None = Field(default=None, description="Database connection URL")


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get cached configuration instance."""
    return Config()