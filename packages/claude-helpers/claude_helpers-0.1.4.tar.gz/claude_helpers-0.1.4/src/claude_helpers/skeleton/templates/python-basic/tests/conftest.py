"""Root pytest configuration and fixtures."""

import pytest
from src.config import Config


@pytest.fixture
def test_config():
    """Test configuration with safe defaults."""
    return Config(
        environment="test",
        log_level="DEBUG",
        service_name="{{PROJECT_NAME}}-test"
    )