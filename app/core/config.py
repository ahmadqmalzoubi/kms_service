# Future use: environment variables, constants, secret configs

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Application settings
    project_name: str = "KMS Service"
    version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    workers: int = Field(default=1, description="Number of worker processes")
    
    # Backend KMS settings
    kms_backend_url: str = Field(default="http://localhost:9000", description="KMS backend URL")
    kms_backend_timeout: int = Field(default=30, description="KMS backend timeout in seconds")
    kms_backend_retries: int = Field(default=3, description="KMS backend retry attempts")
    
    # Security settings
    api_key: str = Field(..., description="API key for authentication")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    rate_limit_per_minute: int = Field(default=100, description="Rate limit per minute")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Database settings (for future use)
    database_url: Optional[str] = Field(default=None, description="Database URL")
    
    # Redis settings (for caching and rate limiting)
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")
    
    # Health check settings
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
