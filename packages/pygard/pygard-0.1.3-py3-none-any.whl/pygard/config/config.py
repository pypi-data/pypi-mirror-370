# !/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @Project ：data-service-sdk-python
# @Author ：qm
# @Date ：2025/5/9 9:47
# @Description:


"""
Configuration management for PyGard client.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GardConfig(BaseSettings):
    """Configuration for PyGard client."""

    # API Configuration
    base_url: str = Field(
        default="http://localhost:8083",
        description="Base URL for the Gard service API"
    )
    api_version: str = Field(
        default="v1",
        description="API version to use"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests"
    )

    # Authentication
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )

    # Connection
    connection_pool_size: int = Field(
        default=10,
        description="Connection pool size"
    )
    keepalive_timeout: int = Field(
        default=30,
        description="Keep-alive timeout in seconds"
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        if v is None:
            return "INFO"

        v_upper = v.upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("log_format", mode="before")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        if v is None:
            return "json"

        v_lower = v.lower()
        valid_formats = {"json", "text"}
        if v_lower not in valid_formats:
            raise ValueError(f"Log format must be one of {valid_formats}")
        return v_lower

    @property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        return f"{self.base_url}/api/{self.api_version}/data-service"

    model_config = SettingsConfigDict(
        env_prefix="PYGARD_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
