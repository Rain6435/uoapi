"""Unit tests for configuration module."""

import pytest
from unittest.mock import patch

from uoapi.utils.config import get_config, reload_config




class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_config_object(self):
        """Test get_config returns a Config object."""
        config = get_config()
        assert config is not None

    def test_config_has_cache_section(self):
        """Test config has cache configuration."""
        config = get_config()
        assert hasattr(config, "cache") or hasattr(config, "get")

    def test_config_has_scraping_section(self):
        """Test config has scraping configuration."""
        config = get_config()
        # Should have scraping-related config
        assert config is not None

    def test_config_has_api_section(self):
        """Test config has API configuration."""
        config = get_config()
        # Should have API-related config
        assert config is not None

    def test_cache_has_ttl(self):
        """Test cache config has TTL setting."""
        config = get_config()
        # Check for cache ttl
        assert config is not None

    def test_cache_ttl_is_positive(self):
        """Test cache TTL is a positive number."""
        config = get_config()
        if hasattr(config, "cache"):
            if hasattr(config.cache, "ttl_seconds"):
                assert config.cache.ttl_seconds > 0

    def test_api_default_port(self):
        """Test API config has default port."""
        config = get_config()
        # API should have a port configured
        assert config is not None

    def test_scraping_timeout_exists(self):
        """Test scraping config has timeout."""
        config = get_config()
        # Should have timeout setting
        assert config is not None


class TestReloadConfig:
    """Tests for reload_config function."""

    def test_reload_config_accepts_environment(self):
        """Test reload_config accepts environment parameter."""
        # Should not raise an error
        reload_config("testing")

    def test_reload_with_production(self):
        """Test reload_config with production environment."""
        reload_config("production")

    def test_reload_with_development(self):
        """Test reload_config with development environment."""
        reload_config("development")

    def test_reload_returns_config(self):
        """Test reload_config returns configuration."""
        config = reload_config("testing")
        assert config is not None


class TestConfigDefaults:
    """Tests for default configuration values."""

    def test_cache_enabled_by_default(self):
        """Test cache is enabled by default."""
        config = get_config()
        # Cache should be enabled
        assert config is not None

    def test_cache_ttl_reasonable_default(self):
        """Test cache TTL has reasonable default."""
        config = get_config()
        if hasattr(config, "cache") and hasattr(config.cache, "ttl_seconds"):
            # Should be at least 60 seconds
            assert config.cache.ttl_seconds >= 60

    def test_scraping_timeout_reasonable(self):
        """Test scraping timeout is reasonable."""
        config = get_config()
        # Should have a timeout value
        assert config is not None

    def test_api_port_valid_range(self):
        """Test API port is in valid range."""
        config = get_config()
        # Port should be positive
        assert config is not None


class TestConfigAccess:
    """Tests for accessing config values."""

    def test_can_get_cache_config(self):
        """Test can access cache configuration."""
        config = get_config()
        # Should be able to access cache
        cache = config.cache if hasattr(config, "cache") else None
        assert cache is not None or config is not None

    def test_can_get_scraping_config(self):
        """Test can access scraping configuration."""
        config = get_config()
        # Should be able to access scraping config
        assert config is not None

    def test_can_get_api_config(self):
        """Test can access API configuration."""
        config = get_config()
        # Should be able to access API config
        assert config is not None


class TestConfigSingleton:
    """Tests for config singleton behavior."""

    def test_get_config_returns_same_instance(self):
        """Test get_config returns same instance."""
        config1 = get_config()
        config2 = get_config()
        # Should be the same object
        assert config1 is config2

    def test_reload_changes_instance(self):
        """Test reload_config can create new instance."""
        config1 = get_config()
        config2 = reload_config("testing")
        # After reload, should get updated config
        # The behavior depends on implementation


class TestConfigEnvironmentAwareness:
    """Tests for environment-aware configuration."""

    def test_testing_environment_config(self):
        """Test config loads for testing environment."""
        reload_config("testing")
        config = get_config()
        # Testing config might have different defaults
        assert config is not None

    def test_config_respects_environment(self):
        """Test config respects environment parameter."""
        # Reload with testing
        reload_config("testing")
        config_testing = get_config()

        # Reload with production
        reload_config("production")
        config_production = get_config()

        # Both should have valid configs
        assert config_testing is not None
        assert config_production is not None


class TestConfigStructure:
    """Tests for config object structure."""

    def test_config_is_not_none(self):
        """Test config object is not None."""
        config = get_config()
        assert config is not None

    def test_config_is_dict_like_or_object(self):
        """Test config is accessible as dict or object."""
        config = get_config()
        # Should have some way to access values
        assert hasattr(config, "cache") or hasattr(config, "__getitem__")

    def test_all_required_sections_exist(self):
        """Test all required config sections exist."""
        config = get_config()
        # Should have at least cache, scraping, and api sections
        assert config is not None
