# Claude Helpers - Package Structure Design

## Project Layout

```
claude-helpers/
├── pyproject.toml              # UV package configuration
├── README.md                   # Installation and usage guide
├── LICENSE                     # MIT license
├── .gitignore                  # Python/UV gitignore
├── CHANGELOG.md                # Version history
├── scripts/                    # Utility scripts
│   └── install-deps.py         # Platform dependency installer
├── src/
│   └── claude_helpers/
│       ├── __init__.py         # Package version and exports
│       ├── __main__.py         # Entry point for python -m claude_helpers
│       ├── cli.py              # Click CLI interface
│       ├── config.py           # Configuration management
│       ├── voice.py            # Voice command entry point
│       ├── platform.py         # Cross-platform utilities
│       ├── audio/
│       │   ├── __init__.py
│       │   ├── recorder.py     # Cross-platform audio recording
│       │   └── devices.py      # Audio device management
│       ├── transcription/
│       │   ├── __init__.py
│       │   └── openai_client.py # OpenAI Whisper integration
│       └── hil/                # Human-in-the-loop system
│           ├── __init__.py
│           ├── listener.py     # Multi-agent file watcher
│           ├── dialog.py       # Cross-platform GUI dialogs
│           └── protocol.py     # File-based message protocol
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── test_config.py          # Configuration tests
│   ├── test_voice.py           # Voice system tests
│   ├── test_audio.py           # Audio recording tests
│   ├── test_hil.py             # HIL system tests
│   ├── test_dialog.py          # Dialog system tests
│   ├── test_cli.py             # CLI interface tests
│   ├── fixtures/               # Test fixtures
│   │   ├── audio/              # Test audio files
│   │   └── configs/            # Test configurations
│   └── integration/            # Integration tests
│       ├── test_full_voice.py
│       └── test_full_hil.py
└── docs/                       # Additional documentation
    ├── development.md
    ├── troubleshooting.md
    └── examples/
        └── project-templates/
```

## Package Configuration (pyproject.toml)

```toml
[project]
name = "claude-helpers"
version = "0.1.0"
description = "Cross-platform voice and HIL tools for Claude Code"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your@email.com"}
]
keywords = ["claude", "voice", "ai", "transcription", "human-in-the-loop"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Tools",
    "Topic :: Multimedia :: Sound/Audio :: Speech",
]

dependencies = [
    # Core dependencies
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",                # Better CLI output
    
    # Audio processing
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    
    # API integration  
    "openai>=1.0.0",
    
    # System integration
    "keyboard>=0.13.5",
    "watchdog>=3.0.0",             # File system watching
]

# Platform-specific extras
[project.optional-dependencies]
linux = [
    "python-xlib>=0.33",           # Keyboard access without sudo
]
macos = [
    "pyobjc-framework-Cocoa>=9.0", # Better macOS integration
]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "ruff>=0.1.0",                 # Linting and formatting
    "mypy>=1.5.0",                 # Type checking
    "pre-commit>=3.0.0",           # Git hooks
]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
]

[project.urls]
Homepage = "https://github.com/username/claude-helpers"
Repository = "https://github.com/username/claude-helpers.git"
Issues = "https://github.com/username/claude-helpers/issues"
Documentation = "https://github.com/username/claude-helpers/blob/main/README.md"

[project.scripts]
claude-helpers = "claude_helpers.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/claude_helpers"]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0", 
    "pytest-mock>=3.10.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
]

# Ruff configuration
[tool.ruff]
target-version = "py310"
line-length = 88
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"tests/**/*" = ["B011", "S101"]  # Allow assert in tests

# MyPy configuration
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "sounddevice.*",
    "keyboard.*",
    "watchdog.*",
]
ignore_missing_imports = true

# Pytest configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=claude_helpers",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-branch",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "audio: marks tests that require audio hardware",
    "gui: marks tests that require GUI environment",
]

# Coverage configuration  
[tool.coverage.run]
source = ["claude_helpers"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

## Module Structure

### Core Package (`src/claude_helpers/`)

#### `__init__.py`
```python
"""Claude Helpers - Voice and HIL tools for Claude Code."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your@email.com"

# Public API exports
from .voice import voice_command
from .config import load_config, check_config
from .hil.dialog import show_dialog

__all__ = [
    "voice_command",
    "load_config", 
    "check_config",
    "show_dialog",
]
```

#### `__main__.py`
```python
"""Entry point for python -m claude_helpers."""

from .cli import cli

if __name__ == "__main__":
    cli()
```

#### `cli.py`
```python
"""Click CLI interface."""

import click
from rich.console import Console
from rich.panel import Panel

from .config import check_config
from .voice import voice_command  
from .hil.listener import listen_command

console = Console()

@click.group()
@click.version_option()
def cli():
    """Claude Helpers - Voice and HIL tools for Claude Code."""
    pass

@cli.command()
@click.option('--global-only', is_flag=True, help='Only configure global settings')
@click.option('--project-only', is_flag=True, help='Only configure current project')
def init(global_only, project_only):
    """Initialize configuration and project setup."""
    from .config import setup_global_config, setup_project
    
    if project_only:
        if not check_config():
            console.print(Panel.fit(
                "Global configuration required first.\nRun: claude-helpers init --global-only",
                style="red"
            ))
            return
        setup_project()
        return
    
    setup_global_config()
    
    if not global_only:
        if click.confirm("\nSet up current directory as Claude-enabled project?", default=True):
            setup_project()

@cli.command()
def voice():
    """Record voice and output transcription."""
    if not check_config():
        console.print(Panel.fit(
            "Global configuration not found.\nPlease run: claude-helpers init",
            style="red"
        ))
        return
    
    voice_command()

@cli.command()
@click.option('--dir', '-d', type=click.Path(exists=True), 
              help='Project directory to watch')
def listen(dir):
    """Start human-in-the-loop listener."""
    from pathlib import Path
    
    if not check_config():
        console.print(Panel.fit(
            "Global configuration not found.\nPlease run: claude-helpers init",
            style="red"
        ))
        return
    
    listen_command(Path(dir) if dir else None)

if __name__ == '__main__':
    cli()
```

### Audio Package (`src/claude_helpers/audio/`)

#### `__init__.py`
```python
"""Audio recording and device management."""

from .recorder import CrossPlatformRecorder
from .devices import list_devices, get_default_device, test_device

__all__ = [
    "CrossPlatformRecorder",
    "list_devices",
    "get_default_device", 
    "test_device",
]
```

### Transcription Package (`src/claude_helpers/transcription/`)

#### `__init__.py`
```python
"""Audio transcription services."""

from .openai_client import WhisperClient

__all__ = ["WhisperClient"]
```

### HIL Package (`src/claude_helpers/hil/`)

#### `__init__.py` 
```python
"""Human-in-the-loop communication system."""

from .dialog import show_dialog
from .listener import listen_command
from .protocol import create_question, read_answer

__all__ = [
    "show_dialog",
    "listen_command", 
    "create_question",
    "read_answer",
]
```

## Testing Structure

### Test Configuration (`tests/conftest.py`)
```python
"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

from claude_helpers.config import GlobalConfig, AudioConfig

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def test_config():
    """Test configuration object."""
    return GlobalConfig(
        openai_api_key="test-key",
        audio=AudioConfig(device_id=0, sample_rate=44100, channels=1)
    )

@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice module."""
    with pytest.mock.patch('claude_helpers.audio.recorder.sd') as mock_sd:
        mock_sd.query_devices.return_value = [
            {'name': 'Test Device', 'max_input_channels': 1, 'default_samplerate': 44100}
        ]
        mock_sd.default.device = [0, 0]  # input, output
        yield mock_sd

@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with pytest.mock.patch('claude_helpers.transcription.openai_client.OpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.audio.transcriptions.create.return_value = Mock(text="test transcription")
        mock_client.return_value = mock_instance
        yield mock_client

@pytest.fixture
def helpers_project(temp_dir):
    """Create test project with .helpers directory."""
    project_dir = temp_dir / "test-project"
    project_dir.mkdir()
    
    helpers_dir = project_dir / ".helpers"
    helpers_dir.mkdir()
    
    for subdir in ["questions", "answers", "agents", "queue"]:
        (helpers_dir / subdir).mkdir()
    
    return project_dir
```

### Test Categories

#### Unit Tests (`tests/test_*.py`)
- Individual component functionality
- Mock external dependencies
- Test error conditions and edge cases

#### Integration Tests (`tests/integration/`)
- End-to-end workflows
- Cross-component interaction
- Real (but limited) external service usage

#### Platform Tests
- Platform-specific functionality
- Cross-platform compatibility
- Hardware-dependent features

## Development Scripts

### Platform Dependency Installer (`scripts/install-deps.py`)
```python
"""Install platform-specific dependencies."""

import subprocess
import platform
import sys

def install_audio_deps():
    """Install audio system dependencies."""
    system = platform.system().lower()
    
    if system == 'linux':
        # Detect Linux distribution
        try:
            with open('/etc/os-release') as f:
                os_release = f.read().lower()
            
            if 'ubuntu' in os_release or 'debian' in os_release:
                subprocess.run([
                    'sudo', 'apt-get', 'update', '&&',
                    'sudo', 'apt-get', 'install', '-y', 
                    'portaudio19-dev', 'libasound2-dev'
                ], shell=True, check=True)
            
            elif 'fedora' in os_release or 'rhel' in os_release:
                subprocess.run([
                    'sudo', 'dnf', 'install', '-y',
                    'portaudio-devel', 'alsa-lib-devel'
                ], check=True)
                
            elif 'arch' in os_release:
                subprocess.run([
                    'sudo', 'pacman', '-S', '--noconfirm',
                    'portaudio', 'alsa-lib'
                ], check=True)
                
        except Exception as e:
            print(f"Could not auto-install: {e}")
            print("Please install portaudio development packages manually")
            
    elif system == 'darwin':
        try:
            subprocess.run(['brew', 'install', 'portaudio'], check=True)
        except subprocess.CalledProcessError:
            print("Please install portaudio via Homebrew: brew install portaudio")
            
    print("✓ Audio dependencies installation complete")

if __name__ == "__main__":
    install_audio_deps()
```

## Build and Distribution

### Build Commands
```bash
# Development setup
uv sync --dev

# Run tests
uv run pytest

# Type checking
uv run mypy src/claude_helpers

# Linting and formatting
uv run ruff check src tests
uv run ruff format src tests

# Build package
uv build

# Install locally for testing
uv tool install --editable .

# Install from built package
uv tool install dist/claude_helpers-0.1.0-py3-none-any.whl
```

### Pre-commit Hooks (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## Documentation Structure

### README.md
- Quick start guide
- Installation instructions
- Basic usage examples
- Troubleshooting

### CHANGELOG.md
- Version history
- Breaking changes
- New features and bug fixes

### docs/development.md
- Development setup
- Contributing guidelines
- Code style and conventions
- Testing strategy

### docs/troubleshooting.md
- Common issues and solutions
- Platform-specific problems
- Debug modes and logging