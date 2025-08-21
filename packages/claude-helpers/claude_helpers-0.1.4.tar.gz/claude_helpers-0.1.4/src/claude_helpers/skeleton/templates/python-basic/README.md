# {{PROJECT_TITLE}}

Brief description of what this service does.

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Start service (if applicable)
uv run python -m src
```

## Architecture

This service follows Clean Architecture with these layers:
- **Domain**: Business logic
- **Application**: Use cases
- **Infrastructure**: External integrations  
- **API**: HTTP endpoints (if applicable)

## Configuration

Copy `.env.example` to `.env` and adjust values.

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Lint code
uv run ruff check src tests

# Format code
uv run ruff format src tests
```

## Testing

- **Unit tests**: `tests/unit/` - Test individual components
- **Integration tests**: `tests/integration/` - Test component interactions
- **E2E tests**: `tests/e2e/` - Test complete workflows