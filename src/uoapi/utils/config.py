"""
Configuration management for the uoapi package.

This module provides centralized configuration management
and settings for the application.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""

    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    database: str = "uoapi"

    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour default
    max_size: int = 1000

    # Provider-specific cache settings
    uottawa_ttl: int = 7200  # 2 hours for UOttawa (slower-changing data)
    carleton_ttl: int = 1800  # 30 minutes for Carleton (live data)


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""

    # Request settings
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    # Rate limiting
    requests_per_minute: int = 60
    concurrent_workers: int = 4

    # User agent
    user_agent: str = "uoapi/3.0 (Educational Course Data API)"

    # UOttawa specific
    uottawa_base_url: str = "https://catalogue.uottawa.ca/en/courses/"

    # Carleton specific
    carleton_base_url: str = "https://central.carleton.ca/prod"
    carleton_max_courses_per_subject: int = 50


@dataclass
class APIConfig:
    """Configuration for the API server."""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False

    # CORS settings
    cors_origins: list = None
    cors_credentials: bool = True
    cors_methods: list = None
    cors_headers: list = None

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"] if self.debug else []
        if self.cors_methods is None:
            self.cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        if self.cors_headers is None:
            self.cors_headers = ["*"]


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # File logging
    file_enabled: bool = False
    file_path: str = "logs/uoapi.log"
    file_max_bytes: int = 10 * 1024 * 1024  # 10MB
    file_backup_count: int = 5

    # Console logging
    console_enabled: bool = True

    # Logger levels for specific modules
    logger_levels: Dict[str, str] = None

    def __post_init__(self):
        if self.logger_levels is None:
            self.logger_levels = {
                "httpx": "WARNING",
                "urllib3": "WARNING",
                "requests": "WARNING",
            }


@dataclass
class RMPConfig:
    """Configuration for Rate My Professor integration."""

    enabled: bool = True
    base_url: str = "https://www.ratemyprofessors.com"
    cache_ttl: int = 86400  # 24 hours

    # Rate limiting for RMP requests
    requests_per_minute: int = 30
    timeout_seconds: int = 15


class Config:
    """Main configuration class."""

    def __init__(self, env: str = None):
        self.env = env or os.getenv("UOAPI_ENV", "development")

        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.scraping = ScrapingConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()
        self.rmp = RMPConfig()

        # Load environment-specific overrides
        self._load_from_environment()
        self._apply_environment_overrides()

    def _load_from_environment(self):
        """Load configuration from environment variables."""

        # Database config
        if os.getenv("DATABASE_URL"):
            # Parse DATABASE_URL if provided
            db_url = os.getenv("DATABASE_URL")
            # Simple parsing - in production you might want to use a URL parsing library
            if "://" in db_url:
                parts = db_url.split("://")[1].split("@")
                if len(parts) == 2:
                    user_pass, host_port_db = parts
                    if ":" in user_pass:
                        self.database.username, self.database.password = (
                            user_pass.split(":", 1)
                        )

        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port))
        self.database.username = os.getenv("DB_USERNAME", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        self.database.database = os.getenv("DB_DATABASE", self.database.database)

        # Cache config
        self.cache.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache.ttl_seconds = int(os.getenv("CACHE_TTL", self.cache.ttl_seconds))

        # API config
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", self.api.port))
        self.api.debug = os.getenv("API_DEBUG", "false").lower() == "true"

        # Logging config
        self.logging.level = os.getenv("LOG_LEVEL", self.logging.level)
        self.logging.file_enabled = (
            os.getenv("LOG_FILE_ENABLED", "false").lower() == "true"
        )
        self.logging.file_path = os.getenv("LOG_FILE_PATH", self.logging.file_path)

        # RMP config
        self.rmp.enabled = os.getenv("RMP_ENABLED", "true").lower() == "true"

    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""

        if self.env == "production":
            # Production overrides
            self.api.debug = False
            self.api.reload = False
            self.logging.level = "WARNING"
            self.cache.ttl_seconds = 7200  # Longer cache in production

        elif self.env == "testing":
            # Testing overrides
            self.cache.enabled = False  # Disable cache in tests
            self.database.database = "uoapi_test"
            self.logging.level = "ERROR"  # Reduce noise in tests

        elif self.env == "development":
            # Development overrides
            self.api.debug = True
            self.api.reload = True
            self.logging.level = "DEBUG"
            self.cache.ttl_seconds = 300  # Shorter cache in development

    def get_assets_path(self) -> Path:
        """Get the path to data assets."""
        # This replicates the logic from discovery_service
        import sys
        import site

        # Check if we're in a virtual environment
        in_venv = hasattr(sys, "prefix") and sys.prefix != sys.base_prefix

        # PRIORITY 1: Development assets (current working directory)
        cwd_assets = Path.cwd() / "assets"
        if cwd_assets.exists() and (cwd_assets / "carleton" / "courses.json").exists():
            return cwd_assets

        # PRIORITY 2: Project root assets (for development)
        current_file = Path(__file__)
        src_dir = current_file.parent.parent.parent.parent  # Go up to project root
        dev_assets = src_dir / "assets"

        if dev_assets.exists() and (dev_assets / "carleton" / "courses.json").exists():
            return dev_assets

        if in_venv:
            # Virtual environment paths
            venv_assets = Path(sys.prefix) / "assets"
            if (
                venv_assets.exists()
                and (venv_assets / "carleton" / "courses.json").exists()
            ):
                return venv_assets

            for site_dir in site.getsitepackages():
                if site_dir.startswith(sys.prefix):
                    site_assets = Path(site_dir).parent / "assets"
                    if (
                        site_assets.exists()
                        and (site_assets / "carleton" / "courses.json").exists()
                    ):
                        return site_assets
        else:
            # System-wide paths
            if hasattr(sys, "prefix"):
                installed_assets = Path(sys.prefix) / "assets"
                if (
                    installed_assets.exists()
                    and (installed_assets / "carleton" / "courses.json").exists()
                ):
                    return installed_assets

        # Fallback to development assets even if they don't exist
        return dev_assets

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "env": self.env,
            "database": self.database.__dict__,
            "cache": self.cache.__dict__,
            "scraping": self.scraping.__dict__,
            "api": self.api.__dict__,
            "logging": self.logging.__dict__,
            "rmp": self.rmp.__dict__,
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def reload_config(env: Optional[str] = None):
    """Reload configuration with optional environment override."""
    global config
    config = Config(env)
    return config
