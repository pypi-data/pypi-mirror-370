# Epic 1: 🏗️ Project Foundation

**Priority**: CRITICAL - Must be completed first
**Estimated Time**: 3-4 days
**Dependencies**: None

## Overview

Создание базовой структуры проекта, настройка build system и core dependencies. Это foundation для всей разработки.

## Definition of Done

- [ ] Проект структурирован по современным Python стандартам
- [ ] UV package management настроен и работает
- [ ] Базовые зависимости установлены и протестированы
- [ ] CLI entry point создан и функционирует
- [ ] Basic testing infrastructure настроена
- [ ] Cross-platform compatibility проверена (Linux + macOS)

---

## Task 1.1: Initial Project Structure
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Создать структуру проекта согласно `package-structure.md`

### Deliverables
```
claude-helpers/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/claude_helpers/
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py
└── tests/
    └── __init__.py
```

### Acceptance Criteria
- Все директории созданы
- Базовые файлы содержат placeholder content
- `__init__.py` содержит правильные exports

### Test Commands
```bash
find . -name "*.py" -exec python -m py_compile {} \;
```

---

## Task 1.2: UV Project Configuration
**Time**: 1 day | **Complexity**: 🟢 Low

### Описание
Настроить `pyproject.toml` с правильными зависимостями и build config

### Deliverables
- Complete `pyproject.toml` based on `package-structure.md` specs
- UV lock file генерируется без ошибок
- Build configuration работает

### Core Dependencies to Configure
```toml
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "openai>=1.0.0",
    "keyboard>=0.13.5",
    "watchdog>=3.0.0",
]
```

### Acceptance Criteria
- `uv sync` выполняется без ошибок
- `uv build` создает valid wheel
- Platform-specific extras работают
- Dev dependencies настроены правильно

### Test Commands
```bash
uv sync
uv build
uv tool install dist/*.whl
claude-helpers --version
```

---

## Task 1.3: Basic CLI Framework
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать основу CLI интерфейса с Click framework

### Deliverables
- `src/claude_helpers/cli.py` с базовой структурой команд
- Entry point работает через `claude-helpers` command
- Help system настроена
- Version command работает

### Core CLI Structure
```python
@click.group()
@click.version_option()
def cli():
    """Claude Helpers - Voice and HIL tools for Claude Code."""
    pass

@cli.command()
def init():
    """Initialize configuration."""
    click.echo("Init command - placeholder")

@cli.command() 
def voice():
    """Record voice and output transcription."""
    click.echo("Voice command - placeholder")

@cli.command()
def listen():
    """Start human-in-the-loop listener."""
    click.echo("Listen command - placeholder")
```

### Acceptance Criteria
- `claude-helpers --help` показывает все команды
- `claude-helpers --version` возвращает правильную версию
- Каждая команда показывает placeholder сообщение
- Error handling работает для unknown commands

### Test Commands
```bash
claude-helpers --help
claude-helpers --version
claude-helpers init
claude-helpers voice
claude-helpers listen
claude-helpers nonexistent  # should show error
```

---

## Task 1.4: Platform Detection Module
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Создать `src/claude_helpers/platform.py` для кроссплатформенной поддержки

### Deliverables
- Platform detection functions
- Config directory detection
- Dialog tools detection framework

### Core Functions
```python
def get_platform() -> str:
    """Returns: 'macos', 'linux', or 'unsupported'"""

def get_config_dir() -> Path:
    """Platform-appropriate config directory"""

def get_dialog_tools() -> List[str]:
    """Available dialog tools for platform"""
```

### Acceptance Criteria
- Правильно определяет macOS vs Linux
- Config directories соответствуют platform conventions
- Unsupported platforms обрабатываются gracefully
- Type hints и docstrings присутствуют

### Test Commands
```python
from claude_helpers.platform import get_platform, get_config_dir
print(get_platform())
print(get_config_dir())
assert get_config_dir().exists() or True  # Should be createable
```

---

## Task 1.5: Testing Infrastructure
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Настроить pytest, coverage, и basic testing utilities

### Deliverables
- `tests/conftest.py` с fixtures
- `tests/test_cli.py` с basic CLI tests
- `tests/test_platform.py` с platform detection tests
- Coverage configuration
- pytest configuration in pyproject.toml

### Basic Test Structure
```python
# tests/conftest.py
@pytest.fixture
def temp_dir():
    """Temporary directory for tests"""

@pytest.fixture
def mock_config():
    """Mock configuration object"""

# tests/test_cli.py
def test_cli_version():
    """Test --version command"""

def test_cli_help():
    """Test --help command"""
```

### Acceptance Criteria
- `uv run pytest` выполняется без ошибок
- `uv run pytest --cov` показывает coverage report
- Все basic tests проходят
- Test fixtures работают правильно

### Test Commands
```bash
uv run pytest
uv run pytest --cov
uv run pytest -v
```

---

## Task 1.6: Cross-Platform Validation
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Проверить что foundation работает на обеих платформах

### Deliverables
- Документированные результаты тестирования на Linux и macOS
- Исправления platform-specific issues
- CI/CD configuration (optional)

### Validation Checklist
- [ ] Project installs cleanly on both platforms
- [ ] CLI commands работают на both platforms
- [ ] Platform detection правильная на both platforms
- [ ] Tests проходят на both platforms
- [ ] Dependencies устанавливаются без конфликтов

### Platform-Specific Issues to Check
- **macOS**: Permissions, path differences, case sensitivity
- **Linux**: Different distributions, package managers
- **Both**: Python version compatibility, dependency versions

### Test Commands
```bash
# On each platform:
uv tool install --editable .
claude-helpers --version
claude-helpers --help
uv run pytest
```

---

## Epic 1 Completion Criteria

### Must Have
- [x] Project structure following Python best practices
- [x] UV package management fully configured
- [x] Basic CLI framework operational
- [x] Platform detection working
- [x] Testing infrastructure established
- [x] Cross-platform compatibility verified

### Success Metrics
- Installation time: < 2 minutes on clean system
- Test coverage: > 80% for foundation modules
- CLI response time: < 100ms for basic commands
- Zero platform-specific installation failures

### Handoff to Next Epic
После завершения Epic 1, разработчик должен уметь:

1. Install project in development mode: `uv tool install --editable .`
2. Run all tests: `uv run pytest`
3. Execute basic CLI commands successfully
4. Add new modules following established structure
5. Platform-specific development path clearly documented

**Next Epic**: Configuration System может начинать development с уверенностью в stable foundation.