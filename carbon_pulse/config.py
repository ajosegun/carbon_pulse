"""Configuration settings for Carbon Pulse."""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")

    # Database Configuration
    database_url: str = Field(
        default="duckdb:///data/carbon_pulse.duckdb", env="DATABASE_URL"
    )

    # Electricity Maps API
    electricity_maps_api_key: Optional[str] = Field(
        default=None, env="ELECTRICITY_MAPS_API_KEY"
    )
    electricity_maps_base_url: str = Field(
        default="https://api.electricitymap.org/v3", env="ELECTRICITY_MAPS_BASE_URL"
    )

    # Monitoring
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    grafana_cloud_url: Optional[str] = Field(default=None, env="GRAFANA_CLOUD_URL")
    grafana_cloud_token: Optional[str] = Field(default=None, env="GRAFANA_CLOUD_TOKEN")

    # Airflow
    airflow_dags_folder: str = Field(default="dags", env="AIRFLOW_DAGS_FOLDER")

    # Data Validation
    great_expectations_data_dir: str = Field(
        default="great_expectations", env="GE_DATA_DIR"
    )

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        env="LOG_FORMAT",
    )
    log_file: Optional[str] = Field(default="logs/carbon_pulse.log", env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
