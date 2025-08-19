"""Configuration management for Claude Helpers."""

import json
import os
import shutil
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from .platform_utils import get_config_dir


# Custom Exceptions

class ConfigError(Exception):
    """Base configuration error."""
    pass


class ConfigNotFoundError(ConfigError):
    """Configuration file not found."""
    pass


class ConfigValidationError(ConfigError):
    """Configuration validation failed."""
    pass


class PlatformNotSupportedError(ConfigError):
    """Platform not supported."""
    pass


class AudioConfig(BaseModel):
    """Audio recording configuration."""
    
    device_id: Optional[int] = None
    sample_rate: int = 44100
    channels: int = 1
    
    @field_validator('sample_rate')
    @classmethod
    def validate_sample_rate(cls, v):
        """Validate sample rate is reasonable."""
        if v < 8000 or v > 96000:
            raise ValueError('Sample rate must be between 8000 and 96000 Hz')
        return v
    
    @field_validator('channels')
    @classmethod
    def validate_channels(cls, v):
        """Validate channel count."""
        if v < 1 or v > 2:
            raise ValueError('Channels must be 1 (mono) or 2 (stereo)')
        return v


class HILConfig(BaseModel):
    """Human-in-the-loop configuration."""
    
    dialog_tool: str = "auto"
    timeout: int = 300
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        """Validate timeout is reasonable."""
        if v < 10 or v > 3600:
            raise ValueError('Timeout must be between 10 and 3600 seconds')
        return v
    
    @field_validator('dialog_tool')
    @classmethod
    def validate_dialog_tool(cls, v):
        """Validate dialog tool."""
        allowed_tools = ["auto", "zenity", "kdialog", "dialog", "whiptail", "osascript", "terminal"]
        if v not in allowed_tools:
            raise ValueError(f'Dialog tool must be one of: {", ".join(allowed_tools)}')
        return v


class LLMConfig(BaseModel):
    """LLM post-processing configuration."""
    
    enabled: bool = False
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # If None, uses standard OpenAI API
    temperature: float = 0.3
    max_tokens: int = 1000
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if v < 0.0 or v > 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        """Validate max_tokens range."""
        if v < 1 or v > 10000:
            raise ValueError('Max tokens must be between 1 and 10000')
        return v


class MemoryBankProject(BaseModel):
    """Memory-Bank project mapping."""
    
    name: str
    path: Path
    created_at: datetime


class MemoryBankConfig(BaseModel):
    """Memory-Bank configuration."""
    
    projects: Dict[str, MemoryBankProject] = Field(default_factory=dict)
    active_project: Optional[str] = None


class GlobalConfig(BaseModel):
    """Global configuration for Claude Helpers."""
    
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    use_plan_mode: bool = False
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hil: HILConfig = Field(default_factory=HILConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory_bank: MemoryBankConfig = Field(default_factory=MemoryBankConfig)
    version: str = "0.1.0"
    debug: bool = False
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_api_key(cls, v):
        """Validate OpenAI API key format."""
        if not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format. Key must start with "sk-"')
        if len(v) < 10:
            raise ValueError('OpenAI API key appears to be too short')
        return v
    
    @field_validator('anthropic_api_key')
    @classmethod
    def validate_anthropic_api_key(cls, v):
        """Validate Anthropic API key format."""
        if v is None:
            return v
        if not v.startswith('sk-ant-'):
            raise ValueError('Invalid Anthropic API key format. Key must start with "sk-ant-"')
        if len(v) < 20:
            raise ValueError('Anthropic API key appears to be too short')
        return v


# Configuration file management functions

def get_config_file() -> Path:
    """Get platform-appropriate config file path."""
    return get_config_dir() / "config.json"


def check_config() -> bool:
    """Check if valid global config exists."""
    config_file = get_config_file()
    if not config_file.exists():
        return False
    
    try:
        load_config()
        return True
    except Exception:
        return False


def load_config() -> GlobalConfig:
    """Load and validate global configuration."""
    config_file = get_config_file()
    
    if not config_file.exists():
        raise ConfigNotFoundError(
            f"Configuration file not found: {config_file}\n"
            "Run 'claude-helpers init' to create initial configuration."
        )
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return GlobalConfig(**data)
    except json.JSONDecodeError as e:
        raise ConfigValidationError(
            f"Invalid JSON in configuration file: {config_file}\n"
            f"JSON error: {e}\n"
            "To fix this issue:\n"
            "1. Delete the corrupted file: rm '{config_file}'\n"
            "2. Run 'claude-helpers init' to recreate configuration"
        )
    except Exception as e:
        raise ConfigValidationError(
            f"Configuration validation failed: {e}\n"
            "The configuration file exists but contains invalid data.\n"
            "To fix this issue:\n"
            "1. Check the configuration format\n"
            "2. Or delete and recreate: rm '{config_file}' && claude-helpers init"
        )


def get_global_config() -> GlobalConfig:
    """Get global configuration (alias for load_config)."""
    return load_config()


def save_global_config(config: GlobalConfig) -> None:
    """Save global configuration (alias for save_config)."""
    save_config(config)


def save_config(config: GlobalConfig) -> None:
    """Save configuration with secure permissions."""
    config_file = get_config_file()
    config_dir = config_file.parent
    
    # Ensure config directory exists
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise ConfigError(
            f"Permission denied creating config directory: {config_dir}\n"
            "Please check directory permissions or run with appropriate privileges."
        )
    except OSError as e:
        raise ConfigError(
            f"Failed to create config directory: {config_dir}\n"
            f"System error: {e}\n"
            "Please check available disk space and directory permissions."
        )
    
    # Write config file with secure permissions
    config_data = config.model_dump(mode='json')
    
    # Write to temporary file first, then move (atomic operation)
    temp_file = config_file.with_suffix('.tmp')
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        # Set secure permissions (600 - owner read/write only)
        temp_file.chmod(0o600)
        
        # Atomic move
        temp_file.replace(config_file)
        
    except PermissionError as e:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
        raise ConfigError(
            f"Permission denied writing configuration file: {config_file}\n"
            f"Error: {e}\n"
            "Please check file permissions or run with appropriate privileges."
        )
    except OSError as e:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()
        raise ConfigError(
            f"Failed to write configuration file: {config_file}\n"
            f"System error: {e}\n"
            "Please check available disk space and directory permissions."
        )
    except Exception as e:
        # Clean up temp file for any other error
        if temp_file.exists():
            temp_file.unlink()
        raise ConfigError(
            f"Unexpected error saving configuration: {e}\n"
            "Please check system permissions and try again."
        )


def backup_config() -> Optional[Path]:
    """Create backup of current config."""
    config_file = get_config_file()
    
    if not config_file.exists():
        return None
    
    backup_file = config_file.with_suffix('.backup')
    try:
        shutil.copy2(config_file, backup_file)
        return backup_file
    except Exception:
        return None


# Environment variable support

def load_config_with_env_override() -> GlobalConfig:
    """Load configuration with environment variable override."""
    # First, try to load from file (may not exist yet)
    try:
        config = load_config()
        config_data = config.model_dump()
    except FileNotFoundError:
        # Create default config data if no file exists
        config_data = {
            'openai_api_key': '',  # Will be overridden by env var
            'audio': {'device_id': None, 'sample_rate': 44100, 'channels': 1},
            'hil': {'dialog_tool': 'auto', 'timeout': 300},
            'version': '0.1.0'
        }
    
    # Override with environment variables (priority: env > file > defaults)
    env_api_key = os.getenv('OPENAI_API_KEY')
    if env_api_key:
        config_data['openai_api_key'] = env_api_key
    
    # Custom config directory support
    custom_config_dir = os.getenv('CLAUDE_HELPERS_CONFIG_DIR')
    if custom_config_dir:
        # This affects where we look for config, but we already loaded it
        # This is mainly for future save operations
        pass
    
    # Debug mode support
    debug_mode = os.getenv('CLAUDE_HELPERS_DEBUG')
    if debug_mode and debug_mode.lower() in ('1', 'true', 'yes'):
        # Add debug info to config (could be used by other components)
        config_data['debug'] = True
    
    # Validate and return the config
    if not config_data.get('openai_api_key'):
        raise ConfigNotFoundError(
            "OpenAI API key is required but not found.\n"
            "To fix this issue:\n"
            "1. Set OPENAI_API_KEY environment variable:\n"
            "   export OPENAI_API_KEY='your-api-key-here'\n"
            "2. Or run interactive setup:\n"
            "   claude-helpers init --global-only\n"
            "3. Or create a project config:\n"
            "   claude-helpers init"
        )
    
    try:
        return GlobalConfig(**config_data)
    except Exception as e:
        raise ConfigValidationError(
            f"Configuration validation failed: {e}\n"
            "Please check your configuration values and try again.\n"
            "You can reset the configuration with:\n"
            "  claude-helpers init --global-only"
        )


def get_effective_config_dir() -> Path:
    """Get effective config directory considering environment variables."""
    custom_dir = os.getenv('CLAUDE_HELPERS_CONFIG_DIR')
    if custom_dir:
        return Path(custom_dir).expanduser()
    return get_config_dir()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    debug_env = os.getenv('CLAUDE_HELPERS_DEBUG', '').lower()
    return debug_env in ('1', 'true', 'yes', 'on')


# Interactive setup functions

def setup_global_config():
    """Interactive global configuration setup."""
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    
    console = Console()
    
    console.print(Panel.fit(
        "🚀 Claude Helpers Global Configuration Setup",
        style="bold blue"
    ))
    
    # Check if config already exists
    config_exists = check_config()
    if config_exists:
        console.print("\n📋 Existing configuration found.")
        if not Confirm.ask("Do you want to update the existing configuration?", default=False):
            console.print("Configuration setup cancelled.")
            return
        
        # Load existing config for defaults
        try:
            existing_config = load_config()
            console.print("✅ Loaded existing configuration for updating.")
        except Exception:
            existing_config = None
            console.print("⚠️  Could not load existing config, starting fresh.")
    else:
        existing_config = None
        console.print("\n📋 Setting up Claude Helpers for the first time.")
    
    # API Key setup
    console.print("\n🔑 OpenAI API Key Configuration")
    
    # Check environment variable first
    env_api_key = os.getenv('OPENAI_API_KEY')
    if env_api_key:
        console.print(f"✅ Found API key in environment variable")
        api_key = env_api_key
    else:
        # Get from existing config or prompt
        default_key = existing_config.openai_api_key if existing_config else ""
        if default_key:
            console.print(f"Current API key: {default_key[:8]}{'*' * (len(default_key) - 8)}")
        
        while True:
            api_key = Prompt.ask(
                "Enter your OpenAI API key",
                default=default_key if default_key else None,
                password=True
            )
            
            if validate_api_key(api_key):
                break
            else:
                console.print("❌ Invalid API key format. Must start with 'sk-'")
    
    # Claude API Configuration (API key or plan mode)
    console.print("\n🔑 Claude API Configuration (for Memory-Bank features)")
    
    # Check environment variable first
    env_anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if env_anthropic_key:
        console.print(f"✅ Found Claude API key in environment variable")
        anthropic_api_key = env_anthropic_key
        use_plan_mode = False
    else:
        # Get from existing config
        default_anthropic_key = existing_config.anthropic_api_key if existing_config else ""
        default_plan_mode = existing_config.use_plan_mode if existing_config else False
        
        if default_anthropic_key:
            console.print(f"Current Claude API key: {default_anthropic_key[:8]}{'*' * (len(default_anthropic_key) - 8)}")
        
        # Ask user preference
        console.print("\n📋 Choose Claude authentication method:")
        console.print("1. Plan Mode - Use existing Claude Code Pro/Max login")  
        console.print("2. API Key - Use separate Anthropic API key")
        
        use_plan_mode = Confirm.ask("Use Claude Code plan mode instead of API key?", default=default_plan_mode)
        
        if use_plan_mode:
            anthropic_api_key = None
            console.print("✅ Will use Claude Code plan mode (no API key needed)")
        else:
            if Confirm.ask("Configure Claude API key for Memory-Bank features?", default=bool(default_anthropic_key)):
                while True:
                    anthropic_api_key = Prompt.ask(
                        "Enter your Claude API key (starts with sk-ant-)",
                        default=default_anthropic_key if default_anthropic_key else None,
                        password=True
                    )
                    
                    if not anthropic_api_key:
                        anthropic_api_key = None
                        console.print("⚠️  Skipping Claude API key (Memory-Bank features will be limited)")
                        break
                    
                    try:
                        # Use the validator from GlobalConfig
                        GlobalConfig.validate_anthropic_api_key(anthropic_api_key)
                        break
                    except ValueError as e:
                        console.print(f"❌ {e}")
            else:
                anthropic_api_key = None
                console.print("⚠️  Skipping Claude API key (Memory-Bank features will be limited)")
    
    # Audio configuration
    console.print("\n🎤 Audio Configuration")
    setup_audio = Confirm.ask("Configure audio device settings?", default=False)
    
    if setup_audio:
        audio_config = setup_audio_config(existing_config.audio if existing_config else None)
    else:
        audio_config = existing_config.audio if existing_config else AudioConfig()
        console.print("✅ Using default audio settings (44.1kHz mono)")
    
    # HIL configuration  
    console.print("\n💬 Human-in-the-Loop Configuration")
    setup_hil = Confirm.ask("Configure dialog settings?", default=False)
    
    if setup_hil:
        hil_config = setup_hil_config(existing_config.hil if existing_config else None)
    else:
        hil_config = existing_config.hil if existing_config else HILConfig()
        console.print("✅ Using default HIL settings (auto dialog tool)")
    
    # LLM post-processing configuration
    console.print("\n🤖 LLM Post-Processing Configuration")
    setup_llm = Confirm.ask("Configure LLM post-processing for HIL responses?", default=False)
    
    if setup_llm:
        llm_config = setup_llm_postprocessing(existing_config.llm if existing_config else None)
    else:
        llm_config = existing_config.llm if existing_config else LLMConfig()
        console.print("✅ LLM post-processing disabled")
    
    # Create and save configuration
    config = GlobalConfig(
        openai_api_key=api_key,
        anthropic_api_key=anthropic_api_key,
        use_plan_mode=use_plan_mode,
        audio=audio_config,
        hil=hil_config,
        llm=llm_config,
        debug=is_debug_mode()
    )
    
    try:
        backup_config()  # Backup existing config if any
        save_config(config)
        console.print(Panel.fit(
            f"✅ Configuration saved successfully!\nLocation: {get_config_file()}",
            style="green"
        ))
    except Exception as e:
        console.print(Panel.fit(
            f"❌ Failed to save configuration: {e}",
            style="red"
        ))
        return
    
    # Test API key if requested
    if Confirm.ask("\nTest API key connection?", default=False):
        test_api_key(api_key)


def setup_audio_config(existing_audio=None):
    """Interactive audio device configuration."""
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    
    console = Console()
    
    # Try to list audio devices
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        # Show available input devices
        input_devices = []
        table = Table(title="Available Audio Input Devices")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Channels", style="green")
        table.add_column("Sample Rate", style="yellow")
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
                table.add_row(
                    str(i),
                    device['name'][:40],
                    str(device['max_input_channels']),
                    f"{device['default_samplerate']:.0f} Hz"
                )
        
        if input_devices:
            console.print(table)
            
            default_device_id = existing_audio.device_id if existing_audio else None
            while True:
                device_input = Prompt.ask(
                    "Select audio device ID (or press Enter for default)",
                    default=str(default_device_id) if default_device_id is not None else ""
                )
                if not device_input:
                    device_id = None
                    break
                try:
                    device_id = int(device_input)
                    break
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
        else:
            console.print("⚠️  No input devices found, using default")
            device_id = None
            
    except ImportError:
        console.print("⚠️  Audio device detection not available")
        device_id = None
    except Exception as e:
        console.print(f"⚠️  Could not query audio devices: {e}")
        device_id = None
    
    # Sample rate configuration
    default_rate = existing_audio.sample_rate if existing_audio else 44100
    while True:
        rate_input = Prompt.ask("Sample rate (Hz)", default=str(default_rate))
        try:
            sample_rate = int(rate_input)
            if 8000 <= sample_rate <= 96000:
                break
            else:
                console.print("[red]Sample rate must be between 8000 and 96000 Hz[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    # Channels configuration  
    default_channels = existing_audio.channels if existing_audio else 1
    while True:
        channels_input = Prompt.ask("Number of channels (1=mono, 2=stereo)", default=str(default_channels))
        try:
            channels = int(channels_input)
            if 1 <= channels <= 2:
                break
            else:
                console.print("[red]Channels must be 1 (mono) or 2 (stereo)[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    return AudioConfig(
        device_id=device_id,
        sample_rate=sample_rate,
        channels=channels
    )


def setup_hil_config(existing_hil=None):
    """Interactive HIL configuration."""
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt
    from .platform_utils import get_dialog_tools
    
    console = Console()
    
    # Dialog tool selection
    available_tools = get_dialog_tools()
    if available_tools:
        console.print(f"Available dialog tools: {', '.join(available_tools)}")
        default_tool = existing_hil.dialog_tool if existing_hil else "auto"
        dialog_tool = Prompt.ask(
            "Dialog tool (auto for automatic selection)",
            default=default_tool,
            choices=["auto"] + available_tools
        )
    else:
        console.print("⚠️  No GUI dialog tools found, will use terminal fallback")
        dialog_tool = "terminal"
    
    # Timeout configuration
    default_timeout = existing_hil.timeout if existing_hil else 300
    while True:
        timeout_input = Prompt.ask("Dialog timeout (seconds)", default=str(default_timeout))
        try:
            timeout = int(timeout_input)
            if 10 <= timeout <= 3600:
                break
            else:
                console.print("[red]Timeout must be between 10 and 3600 seconds[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    return HILConfig(dialog_tool=dialog_tool, timeout=timeout)


def validate_api_key(key: str) -> bool:
    """Validate API key format."""
    try:
        GlobalConfig(openai_api_key=key)
        return True
    except Exception:
        return False


def test_api_key(api_key: str):
    """Test API key with OpenAI (optional)."""
    from rich.console import Console
    
    console = Console()
    console.print("🧪 Testing API key connection...")
    
    try:
        # Simple test - just validate the key format for now
        # In a real implementation, you might make a minimal API call
        if validate_api_key(api_key):
            console.print("✅ API key format is valid")
        else:
            console.print("❌ API key format is invalid")
    except Exception as e:
        console.print(f"⚠️  Could not test API key: {e}")


# Template system

def get_ask_human_script_template() -> str:
    """Generate ask-human.sh bash script content."""
    return '''#!/bin/bash

# Claude Helpers - Human-in-the-loop script
# Generated by claude-helpers init
# 
# This script allows Claude Code agents to ask questions to humans
# and receive responses through file-based communication

set -euo pipefail

# Configuration
HELPERS_DIR="${PWD}/.helpers"
QUESTIONS_DIR="${HELPERS_DIR}/questions"
ANSWERS_DIR="${HELPERS_DIR}/answers"
AGENTS_DIR="${HELPERS_DIR}/agents"
QUEUE_DIR="${HELPERS_DIR}/queue"

# Generate unique agent ID based on process hierarchy
AGENT_ID="agent_$$_$(date +%s%N | cut -b1-13)"

# Create necessary directories
mkdir -p "$QUESTIONS_DIR" "$ANSWERS_DIR" "$AGENTS_DIR" "$QUEUE_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Function to create question file
create_question() {
    local question="$1"
    local question_file="${QUESTIONS_DIR}/${AGENT_ID}.txt"
    local queue_file="${QUEUE_DIR}/${AGENT_ID}.queue"
    
    # Write question
    echo "$question" > "$question_file"
    
    # Add to queue
    echo "$(date +%s):${AGENT_ID}" >> "$queue_file"
    
    # Register agent
    echo "$(date '+%Y-%m-%d %H:%M:%S'):${AGENT_ID}:waiting" > "${AGENTS_DIR}/${AGENT_ID}.status"
    
    log_message "Question created: $question_file"
    echo "$question_file"
}

# Function to wait for answer
wait_for_answer() {
    local agent_id="$1"
    local timeout="${2:-300}"  # 5 minutes default
    local answer_file="${ANSWERS_DIR}/${agent_id}.txt"
    local start_time=$(date +%s)
    
    log_message "Waiting for answer (timeout: ${timeout}s)..."
    
    while [ ! -f "$answer_file" ]; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log_message "Timeout waiting for answer"
            echo "TIMEOUT: No response received within ${timeout} seconds"
            cleanup_agent "$agent_id"
            exit 1
        fi
        
        sleep 1
    done
    
    # Read and return answer
    cat "$answer_file"
    
    # Cleanup
    cleanup_agent "$agent_id"
}

# Function to cleanup agent files
cleanup_agent() {
    local agent_id="$1"
    
    rm -f "${QUESTIONS_DIR}/${agent_id}.txt"
    rm -f "${ANSWERS_DIR}/${agent_id}.txt" 
    rm -f "${AGENTS_DIR}/${agent_id}.status"
    rm -f "${QUEUE_DIR}/${agent_id}.queue"
    
    log_message "Cleaned up agent files: $agent_id"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 '<question>'"
        echo "Example: $0 'Should I use TypeScript or JavaScript for this component?'"
        exit 1
    fi
    
    local question="$*"
    
    # Create question and wait for answer
    local question_file=$(create_question "$question")
    local answer=$(wait_for_answer "$AGENT_ID")
    
    # Output answer to stdout (becomes next Claude prompt)
    echo "$answer"
}

# Handle interruption
trap 'cleanup_agent "$AGENT_ID"; exit 130' INT TERM

# Execute main function
main "$@"
'''


# Old ask/voice command templates removed - now using individual setup functions


def get_claude_commands_template() -> str:
    """Generate Claude Code commands.md content."""
    return '''# Claude Helpers Integration

This project includes Claude Helpers for voice input and human-in-the-loop interactions.

## Human-in-the-Loop Commands

Use these commands to interact with humans during development:

### Text Questions
```bash
!claude-helpers ask "Should I use approach A or B?"
!claude-helpers ask "What's your preferred naming convention?"
```

### Voice Input
```bash
!claude-helpers ask --voice "Describe the bug you're experiencing"
!claude-helpers ask --voice --duration 60 "Explain the architecture in detail"
```

### Environment Status
```bash
!claude-helpers status
```

## Setup Requirements

1. **Start HIL Listener**: Run `claude-helpers listen` in background
2. **Check Status**: Use `claude-helpers status` to verify setup
3. **Global Install**: Ensure `claude-helpers` is installed globally

## Voice Features

- **Recording**: High-quality audio recording optimized for OpenAI Whisper
- **Transcription**: Automatic speech-to-text using OpenAI API
- **Preview/Edit**: Review and edit transcriptions before sending
- **Fallback**: Automatic fallback to text input if voice fails
- **Error Handling**: Clear error messages and recovery guidance

## Multi-Agent Support

The HIL system supports multiple Claude Code sessions simultaneously through file-based communication.

---

**Note**: This integration requires Claude Helpers to be installed and configured. See project documentation for setup instructions.'''


def get_claude_md_template() -> str:
    """Generate CLAUDE.md HIL instructions."""
    return '''# Claude Code Integration

This project is set up to work with Claude Code and includes human-in-the-loop (HIL) capabilities.

## Human-in-the-Loop Usage

Claude Code agents can ask you questions during development using slash commands:

```bash
/ask "Should I implement this feature using A or B approach?"
/voice "Describe the bug you found"
```

Alternative bash commands (if needed):
```bash
!claude-helpers ask "question"
!claude-helpers ask --voice "prompt"
```

### How It Works

1. **Agent asks question**: Claude runs `/ask "question"` or `/voice "prompt"` (slash commands)
2. **Question queued**: Command creates question file in `.helpers/questions/`  
3. **Human responds**: Background listener shows UI and saves answer
4. **Agent gets answer**: Command outputs response, which becomes next Claude prompt

### Setup

To enable HIL functionality:

```bash
# Global configuration (one time)
claude-helpers init --global-only

# Project setup (per project)  
claude-helpers init --project-only

# Start background listener (when working)
claude-helpers listen

# Check environment status
claude-helpers status
```

### Directory Structure

```
.helpers/
├── questions/    # Agent questions waiting for answers
├── answers/      # Human responses  
├── agents/       # Agent status tracking
└── queue/        # Question queue management
```

### Multi-Agent Support

The HIL system supports multiple Claude Code sessions simultaneously. Each agent gets a unique ID based on process information, allowing concurrent development workflows.

### Timeouts and Error Handling

- Default timeout: 5 minutes per question
- Questions that timeout return "TIMEOUT" message
- Failed questions don't crash the agent workflow
- All temporary files are cleaned up automatically

## Development Guidelines

When working with Claude Code in this project:

1. **Ask strategic questions**: Use HIL for architectural decisions, not trivial choices
2. **Provide context**: Include relevant background in your questions
3. **Keep listener running**: The `claude-helpers listen` command should run in background
4. **Check .helpers/**: Monitor question/answer flow if needed

## Configuration

HIL behavior can be customized in global configuration:

```bash
claude-helpers init --global-only  # Reconfigure settings
```

- Dialog tool selection (GUI vs terminal)
- Timeout duration  
- Debug mode for troubleshooting

---

**Note**: This HIL system is part of Claude Helpers. For more information, see the [project documentation](https://github.com/claude-helpers/claude-helpers).
'''


def get_gitignore_entries() -> str:
    """Get gitignore entries for Claude Helpers."""
    return '''
# Claude Helpers - Human-in-the-loop files
.helpers/
*.wav
*.tmp
'''


def render_template(template: str, variables: dict) -> str:
    """Render template with variable substitution."""
    import string
    
    try:
        # Use Python's string.Template for safe substitution
        template_obj = string.Template(template)
        return template_obj.safe_substitute(variables)
    except Exception as e:
        # If template substitution fails, return original
        return template


def setup_project():
    """Legacy wrapper for backward compatibility."""
    setup_project_interactive(update_mode=False)


def setup_project_interactive(update_mode=False):
    """Interactive project setup for Claude Code integration."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    from pathlib import Path
    
    console = Console()
    
    console.print(Panel.fit(
        "🚀 Claude Helpers Project Setup" if not update_mode else "🔄 Update Project Configuration",
        style="bold blue"
    ))
    
    project_dir = Path.cwd()
    console.print(f"\n📁 Project directory: {project_dir}")
    
    # Individual setup choices
    console.print("\n🎯 Configuration Setup:")
    
    # Voice command setup
    setup_voice = Confirm.ask("Setup /voice slash command?", default=True)
    
    # HIL rules setup  
    setup_hil_rules = Confirm.ask("Add init-hil-rules command for CLAUDE.md updates?", default=False)
    
    # MCP setup
    setup_mcp = Confirm.ask("Setup HIL MCP integration (ask-human tool)?", default=True)
    
    # Create .helpers directory for HIL
    helpers_dir = project_dir / ".helpers"
    if (setup_voice or setup_mcp) and not helpers_dir.exists():
        try:
            setup_helpers_directory(project_dir)
            console.print("✅ Created .helpers directory for HIL")
        except Exception as e:
            console.print(f"⚠️  Failed to create .helpers directory: {e}")
    
    # Apply selections
    if setup_voice:
        try:
            setup_voice_command_only(project_dir)
            console.print("✅ Setup /voice command")
        except Exception as e:
            console.print(f"⚠️  Failed to setup voice command: {e}")
    
    if setup_hil_rules:
        try:
            setup_init_hil_rules_command(project_dir)
            console.print("✅ Added init-hil-rules command")
        except Exception as e:
            console.print(f"⚠️  Failed to add init-hil-rules: {e}")
    
    # MCP registration
    mcp_registered = False
    if setup_mcp:
        try:
            register_mcp_integration()
            console.print("✅ Registered MCP ask-human tool")
            mcp_registered = True
        except Exception as e:
            console.print(f"⚠️  Failed to register MCP: {e}")
            console.print("    You can register manually with:")
            console.print("    [cyan]claude mcp add-json ask-human '{\"type\":\"stdio\",\"command\":\"claude-helpers\",\"args\":[\"mcp-server\"]}' [/cyan]")
    
    # MCP timeout configuration (critical for HIL!)
    if mcp_registered or setup_mcp:
        console.print("\n⏰ MCP Timeout Configuration")
        setup_mcp_timeout = Confirm.ask(
            "Increase MCP tool timeout for HIL interactions?", 
            default=True
        )
        if setup_mcp_timeout:
            try:
                configure_mcp_timeout()
                console.print("✅ Configured MCP timeout for HIL")
            except Exception as e:
                console.print(f"⚠️  Failed to configure MCP timeout: {e}")
                console.print("    You can configure manually with:")
                console.print("    [cyan]claude config set MCP_TOOL_TIMEOUT 600000[/cyan]")
    
    # Handle .gitignore
    if Confirm.ask("\nUpdate .gitignore?", default=True):
        gitignore_path = project_dir / ".gitignore"
        if not gitignore_path.exists():
            if Confirm.ask("No .gitignore found. Create one?", default=True):
                try:
                    create_default_gitignore(project_dir)
                    console.print("✅ Created .gitignore with standard entries")
                except Exception as e:
                    console.print(f"⚠️  Failed to create .gitignore: {e}")
        else:
            try:
                setup_gitignore(project_dir)
                console.print("✅ Updated .gitignore")
            except Exception as e:
                console.print(f"⚠️  Failed to update .gitignore: {e}")
    
    # Final summary
    next_steps = ["🎉 Project setup complete!\n"]
    
    if setup_mcp and not mcp_registered:
        next_steps.append("1. Register MCP manually:")
        next_steps.append("   claude mcp add-json claude-helpers-hil '{\"type\":\"stdio\",\"command\":\"claude-helpers\",\"args\":[\"mcp-server\"]}'")
    
    step_num = 2 if (setup_mcp and not mcp_registered) else 1
    
    if setup_voice or setup_mcp:
        next_steps.append(f"{step_num}. Start HIL listener: claude-helpers listen")
        step_num += 1
        
    if setup_voice:
        next_steps.append(f"{step_num}. Use /voice in Claude Code for voice instructions")
        step_num += 1
        
    if setup_mcp:
        next_steps.append(f"{step_num}. Claude Code has ask-question MCP tool available")
        step_num += 1
        
    next_steps.append(f"{step_num}. Check status: claude-helpers status")
    
    console.print(Panel.fit(
        "\n".join(next_steps),
        style="green"
    ))


def create_default_gitignore(project_dir: Path):
    """Create a default .gitignore file."""
    default_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Claude Helpers
.helpers/
*.wav
*.tmp

# OS
.DS_Store
Thumbs.db
"""
    gitignore_path = project_dir / ".gitignore"
    gitignore_path.write_text(default_content)


def setup_voice_command_only(project_dir: Path):
    """Setup only /voice slash command."""
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    
    # Create commands directory
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(exist_ok=True)
    
    # Create voice command only
    voice_cmd = commands_dir / "voice.md"
    voice_content = '''---
description: User wants to provide instructions via voice through HIL interface
---

# Voice Instructions

When the user runs `/voice`, it means they want to provide their instructions or prompts using the Human-in-the-Loop voice interface instead of typing.

Use the `ask-question` MCP tool to request their instructions:

```
Use ask-question with:
- question_author_role: "assistant"  
- question: "Please provide your instructions (you can use voice input in the HIL interface)"
```

The human will see this in the HIL interface and can choose to respond via voice recording or text input. You'll receive their instructions as transcribed text.

This uses the same ask-question tool you use for other clarifying questions during your work.
'''
    voice_cmd.write_text(voice_content)


def register_mcp_integration():
    """Automatically register MCP integration."""
    import subprocess
    
    mcp_config = {
        "type": "stdio",
        "command": "claude-helpers", 
        "args": ["mcp-server"]
    }
    
    import json
    mcp_json = json.dumps(mcp_config)
    
    # Try to register MCP with new tool name
    result = subprocess.run([
        "claude", "mcp", "add-json", "claude-helpers-hil", mcp_json
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"claude mcp command failed: {result.stderr.strip()}")
    
    return True


def show_mcp_setup_instructions():
    """Show MCP registration instructions."""
    from rich.console import Console
    console = Console()
    
    console.print("\n🔧 MCP Server Setup")
    console.print("To register ask-human MCP tool, run:")
    console.print("[cyan]claude mcp add-json ask-human '{\"type\":\"stdio\",\"command\":\"claude-helpers\",\"args\":[\"mcp-server\"]}' [/cyan]")
    console.print("\nThis allows Claude Code to use ask-human tool directly in conversations.")


def setup_init_hil_rules_command(project_dir: Path):
    """Create init-hil-rules command for CLAUDE.md updates."""
    commands_dir = project_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    cmd_file = commands_dir / "init-hil-rules.md"
    content = '''---
description: Update CLAUDE.md with HIL workflow rules
allowed-tools:
  - Read(CLAUDE.md)
  - Edit(CLAUDE.md:*)
---

# Initialize HIL Rules

Update CLAUDE.md to include Human-in-the-Loop workflow guidelines.

Please:
1. Read the current CLAUDE.md file
2. Add a section about working in Human-in-the-Loop mode
3. Specify that unclear or ambiguous requirements should be clarified using the ask-human tool
4. Maintain the original language and style of the document
5. Be concise and integrate naturally with existing content

Key points to add:
- Work in HIL mode for this project
- Use `ask-human` tool when requirements are unclear
- Don't make assumptions - ask for clarification
- Maintain project's coding standards and conventions
'''
    cmd_file.write_text(content)


def setup_helpers_directory(project_dir: Path):
    """Create .helpers directory structure."""
    helpers_dir = project_dir / ".helpers"
    
    # Create main directory
    helpers_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    for subdir in ["questions", "answers", "agents", "queue"]:
        (helpers_dir / subdir).mkdir(exist_ok=True)
    
    # Set proper permissions (700 - owner only)
    helpers_dir.chmod(0o700)


def setup_gitignore(project_dir: Path):
    """Add .helpers to .gitignore."""
    gitignore_file = project_dir / ".gitignore"
    gitignore_entries = get_gitignore_entries().strip()
    
    # Read existing .gitignore if it exists
    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Check if our entries are already there
    if ".helpers/" in existing_content:
        return  # Already added
    
    # Add our entries
    with open(gitignore_file, 'a', encoding='utf-8') as f:
        if existing_content and not existing_content.endswith('\n'):
            f.write('\n')
        f.write(gitignore_entries)
        f.write('\n')


# setup_claude_integration function removed - now using individual setup functions


# setup_claudeignore function removed - .claudeignore doesn't exist in Claude Code API


def setup_claude_md(project_dir: Path):
    """Create or update CLAUDE.md with HIL instructions."""
    claude_md_file = project_dir / "CLAUDE.md"
    hil_template = get_claude_md_template()
    
    # Markers to identify our content
    start_marker = "<!-- CLAUDE HELPERS HIL START -->"
    end_marker = "<!-- CLAUDE HELPERS HIL END -->"
    
    if claude_md_file.exists():
        # Read existing content
        with open(claude_md_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Check if our section already exists
        if start_marker in existing_content and end_marker in existing_content:
            # Replace existing section
            parts = existing_content.split(start_marker, 1)
            if len(parts) == 2:
                before = parts[0]
                after_parts = parts[1].split(end_marker, 1)
                if len(after_parts) == 2:
                    after = after_parts[1]
                    
                    new_content = (
                        before + 
                        start_marker + "\n\n" +
                        hil_template + "\n\n" +
                        end_marker +
                        after
                    )
                else:
                    # Malformed, append at end
                    new_content = existing_content + "\n\n" + start_marker + "\n\n" + hil_template + "\n\n" + end_marker
            else:
                # Should not happen, append at end
                new_content = existing_content + "\n\n" + start_marker + "\n\n" + hil_template + "\n\n" + end_marker
        else:
            # Add our section at the end
            new_content = existing_content + "\n\n" + start_marker + "\n\n" + hil_template + "\n\n" + end_marker
    else:
        # Create new file
        new_content = start_marker + "\n\n" + hil_template + "\n\n" + end_marker
    
    # Write the file
    with open(claude_md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)


def setup_llm_postprocessing(existing_llm=None):
    """Configure LLM post-processing settings."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    
    console = Console()
    console.print("\n🤖 LLM Post-Processing Configuration")
    console.print("This feature allows LLM enhancement of HIL responses for better clarity and structure.")
    console.print("[dim]Uses OpenAI-compatible API endpoints.[/dim]")
    
    # Ask if user wants to enable it
    enable_llm = Confirm.ask("Enable LLM post-processing for HIL responses?", default=False)
    if not enable_llm:
        return LLMConfig(enabled=False)
    
    # Get API key
    console.print("\n🔑 API Key Configuration")
    api_key = Prompt.ask(
        "Enter LLM API key (OpenAI or compatible)",
        password=True,
        default=existing_llm.api_key if existing_llm else ""
    )
    
    # Get base URL (optional)
    console.print("\n🌐 Endpoint Configuration")
    use_custom_url = Confirm.ask("Use custom API endpoint (instead of OpenAI)?", default=False)
    
    base_url = None
    if use_custom_url:
        base_url = Prompt.ask(
            "Enter custom base URL (OpenAI-compatible endpoint)",
            default=existing_llm.base_url if existing_llm else ""
        )
        if not base_url.strip():
            base_url = None
        else:
            console.print(f"[green]✓[/green] Will use custom endpoint: {base_url}")
    else:
        console.print("[green]✓[/green] Will use standard OpenAI API")
    
    # Get model name
    console.print("\n🎛️ Model Configuration")
    default_model = existing_llm.model if existing_llm else "gpt-4o-mini"
    model = Prompt.ask("Model name", default=default_model)
    
    # Advanced settings
    console.print("\n⚙️ Advanced Settings")
    advanced = Confirm.ask("Configure advanced settings (temperature, max_tokens)?", default=False)
    
    if advanced:
        while True:
            temp_input = Prompt.ask(
                "Temperature (0.0-2.0)",
                default=str(existing_llm.temperature if existing_llm else 0.3)
            )
            try:
                temperature = float(temp_input)
                if 0.0 <= temperature <= 2.0:
                    break
                else:
                    console.print("[red]Temperature must be between 0.0 and 2.0[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        
        while True:
            tokens_input = Prompt.ask(
                "Max tokens (1-10000)",
                default=str(existing_llm.max_tokens if existing_llm else 1000)
            )
            try:
                max_tokens = int(tokens_input)
                if 1 <= max_tokens <= 10000:
                    break
                else:
                    console.print("[red]Max tokens must be between 1 and 10000[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
    else:
        temperature = existing_llm.temperature if existing_llm else 0.3
        max_tokens = existing_llm.max_tokens if existing_llm else 1000
    
    # Create config
    llm_config = LLMConfig(
        enabled=True,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    console.print("\n✅ LLM post-processing configured successfully!")
    console.print(f"   Model: {model}")
    if base_url:
        console.print(f"   Custom endpoint: {base_url}")
    else:
        console.print("   Provider: OpenAI API")
    console.print(f"   Temperature: {temperature}")
    console.print(f"   Max tokens: {max_tokens}")
    
    return llm_config


def configure_mcp_timeout():
    """Configure MCP tool timeout for HIL interactions."""
    import subprocess
    from rich.console import Console
    from rich.prompt import IntPrompt, Confirm
    
    console = Console()
    
    console.print("\n⏰ MCP Tool Timeout Configuration")
    console.print("[dim]HIL interactions can take time for voice recording and user thinking.[/dim]")
    console.print("[dim]Default MCP timeout may be too short and cause agent interruptions.[/dim]")
    
    # Recommend 10 minutes (600000ms) for HIL
    recommended_timeout = 600000  # 10 minutes in milliseconds
    
    console.print(f"\n💡 Recommended: {recommended_timeout}ms (10 minutes)")
    console.print("   This allows time for:")
    console.print("   • Voice recording and transcription")
    console.print("   • User thinking and editing")
    console.print("   • LLM post-processing (if enabled)")
    
    use_recommended = Confirm.ask("Use recommended 10-minute timeout?", default=True)
    
    if use_recommended:
        timeout_ms = recommended_timeout
    else:
        while True:
            timeout_input = IntPrompt.ask("Enter timeout in milliseconds (minimum 60000)")
            if timeout_input >= 60000:  # At least 1 minute
                timeout_ms = timeout_input
                break
            else:
                console.print("[red]Timeout must be at least 60000ms (1 minute)[/red]")
    
    # Configure using claude CLI
    try:
        result = subprocess.run([
            "claude", "config", "set", "MCP_TOOL_TIMEOUT", str(timeout_ms)
        ], capture_output=True, text=True, check=True)
        
        console.print(f"[green]✓[/green] Set MCP_TOOL_TIMEOUT to {timeout_ms}ms ({timeout_ms//1000//60} minutes)")
        logger.info(f"Configured MCP_TOOL_TIMEOUT to {timeout_ms}ms")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to configure MCP timeout via claude CLI: {e}[/red]")
        raise Exception(f"Failed to set MCP timeout: {e}")
    except FileNotFoundError:
        console.print("[red]Claude CLI not found. Please ensure Claude Code is installed.[/red]")
        raise Exception("Claude CLI not available")