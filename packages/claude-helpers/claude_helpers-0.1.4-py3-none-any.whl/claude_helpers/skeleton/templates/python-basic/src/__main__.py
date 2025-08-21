"""Entry point for {{PROJECT_NAME}} service."""

from .config import get_config


def main():
    """Main entry point."""
    config = get_config()
    print(f"Starting {{PROJECT_NAME}} service...")
    print(f"Environment: {config.environment}")
    print(f"Log level: {config.log_level}")
    
    # TODO: Add your application logic here


if __name__ == "__main__":
    main()