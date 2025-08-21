"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Mock configuration object."""
    config = Mock()
    config.openai_api_key = "test-key"
    config.audio = Mock()
    config.audio.device_id = 0
    config.audio.sample_rate = 44100
    config.audio.channels = 1
    return config