# Claude Helpers - Configuration System Design

## Overview

Two-level configuration system:
1. **Global configuration** - API keys, audio settings, stored in user home
2. **Project configuration** - HIL setup, scripts, CLAUDE.md instructions

## Configuration Levels

### Global Configuration
**Location**: Platform-specific user config directory
- **Linux**: `~/.config/claude-helpers/config.json`
- **macOS**: `~/Library/Application Support/claude-helpers/config.json`

**Contents**:
```json
{
  "openai_api_key": "sk-...",
  "audio": {
    "device_id": null,        // null = default device
    "sample_rate": 44100,
    "channels": 1
  },
  "hil": {
    "dialog_tool": "auto",    // auto-detect or specific tool
    "timeout": 300            // seconds
  },
  "version": "0.1.0"          // config format version
}
```

**Security**:
- File permissions: `0o600` (user read/write only)
- Never stored in project directories
- Support for environment variable override: `OPENAI_API_KEY`

### Project Configuration
**Location**: `.helpers/` directory in project root

**Structure**:
```
.helpers/
├── questions/              # HIL questions from agents
├── answers/               # HIL answers to agents  
├── agents/               # Agent registry
├── queue/                # Queue status
└── .listener.pid         # Listener process PID
```

**Associated Files**:
- `scripts/ask-human.sh` - Generated agent script
- `CLAUDE.md` - Updated with HIL instructions
- `.gitignore` - Updated to exclude `.helpers/`

## Platform Detection

```python
# src/claude_helpers/platform.py
import platform
import sys
from pathlib import Path

def get_platform():
    """Detect current platform"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unsupported'

def get_config_dir():
    """Get platform-appropriate config directory"""
    system = get_platform()
    if system == 'macos':
        return Path.home() / "Library" / "Application Support" / "claude-helpers"
    elif system == 'linux':
        return Path.home() / ".config" / "claude-helpers"
    else:
        raise RuntimeError(f"Unsupported platform: {platform.system()}")

def get_dialog_tools():
    """Get available dialog tools for platform"""
    system = get_platform()
    if system == 'macos':
        return ['osascript', 'terminal']
    elif system == 'linux':
        return ['zenity', 'yad', 'dialog', 'terminal']
    else:
        return ['terminal']
```

## Configuration Management

### Configuration Loading
```python
# src/claude_helpers/config.py
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .platform import get_config_dir

class AudioConfig(BaseModel):
    device_id: Optional[int] = None
    sample_rate: int = 44100
    channels: int = 1

class HILConfig(BaseModel):
    dialog_tool: str = "auto"
    timeout: int = 300

class GlobalConfig(BaseModel):
    openai_api_key: str
    audio: AudioConfig = Field(default_factory=AudioConfig)
    hil: HILConfig = Field(default_factory=HILConfig)
    version: str = "0.1.0"

def get_config_file() -> Path:
    """Get global config file path"""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"

def check_config() -> bool:
    """Check if global config exists and is valid"""
    config_file = get_config_file()
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        # Basic validation
        return 'openai_api_key' in data and data['openai_api_key']
    except:
        return False

def load_config() -> GlobalConfig:
    """Load and validate global configuration"""
    config_file = get_config_file()
    
    if not config_file.exists():
        raise RuntimeError(
            "Global configuration not found. Please run: claude-helpers init"
        )
    
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        return GlobalConfig(**data)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid configuration file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")

def save_config(config: GlobalConfig) -> None:
    """Save global configuration"""
    config_file = get_config_file()
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config.model_dump(), f, indent=2)
        
        # Set secure permissions
        config_file.chmod(0o600)
    except Exception as e:
        raise RuntimeError(f"Failed to save configuration: {e}")
```

## Init Command Implementation

### Two-Phase Initialization
```python
# src/claude_helpers/cli.py
import click
from pathlib import Path
import json
import os

@click.command()
@click.option('--global-only', is_flag=True, 
              help='Only configure global settings')
@click.option('--project-only', is_flag=True,
              help='Only configure current project (requires existing global config)')
def init(global_only, project_only):
    """Initialize global config and optionally set up current project"""
    
    if project_only:
        if not check_config():
            click.echo("ERROR: Global configuration required first.")
            click.echo("Run: claude-helpers init --global-only")
            return
        setup_project()
        return
    
    # Phase 1: Global Configuration
    setup_global_config()
    
    if not global_only:
        # Phase 2: Project Setup
        if click.confirm("\nSet up current directory as Claude-enabled project?", default=True):
            setup_project()

def setup_global_config():
    """Set up global configuration"""
    config_file = get_config_file()
    
    if config_file.exists():
        click.echo("✓ Global configuration already exists")
        if not click.confirm("Update global configuration?", default=False):
            return
        
        # Load existing config
        with open(config_file, 'r') as f:
            config_data = json.load(f)
    else:
        click.echo("=== Global Configuration Setup ===")
        click.echo("This is required for claude-helpers to work.\n")
        config_data = {}
    
    # API Key
    current_key = config_data.get('openai_api_key', '')
    api_key = click.prompt(
        "OpenAI API key",
        default=current_key if current_key else '',
        hide_input=True,
        show_default=False
    )
    if api_key:
        config_data['openai_api_key'] = api_key
    
    # Audio device configuration
    if click.confirm("Configure audio device?", default=True):
        setup_audio_config(config_data)
    
    # Save configuration
    config = GlobalConfig(**config_data)
    save_config(config)
    
    click.echo(f"\n✓ Global config saved to: {config_file}")

def setup_audio_config(config_data: dict):
    """Set up audio device configuration"""
    from claude_helpers.audio.devices import list_devices, test_device
    
    devices = list_devices()
    
    if len(devices) <= 1:
        click.echo("Using default audio device")
        return
    
    click.echo("\nAvailable audio input devices:")
    current_device = config_data.get('audio', {}).get('device_id')
    
    for i, device in enumerate(devices):
        status_indicators = []
        
        # Show if currently selected
        if device['id'] == current_device:
            status_indicators.append("current")
        
        # Test device functionality
        if test_device(device['id']):
            status_indicators.append("✓")
        else:
            status_indicators.append("✗")
        
        status = f" ({', '.join(status_indicators)})" if status_indicators else ""
        click.echo(f"  {i}: {device['name']}{status}")
    
    device_choice = click.prompt(
        f"Select device number (0-{len(devices)-1}, or Enter for default)",
        type=int,
        default=-1,
        show_default=False
    )
    
    if 0 <= device_choice < len(devices):
        config_data.setdefault('audio', {})['device_id'] = devices[device_choice]['id']
        
        # Test selected device
        if test_device(devices[device_choice]['id']):
            click.echo("✓ Device test successful")
        else:
            click.echo("⚠ Device test failed - you may need to check permissions")

def setup_project():
    """Set up current project for Claude Helpers"""
    project_dir = Path.cwd()
    click.echo(f"\n=== Project Setup ===")
    click.echo(f"Setting up: {project_dir}")
    
    # Create .helpers directory structure
    helpers_dir = project_dir / ".helpers"
    helpers_dir.mkdir(exist_ok=True)
    
    for subdir in ["questions", "answers", "agents", "queue"]:
        (helpers_dir / subdir).mkdir(exist_ok=True)
    
    click.echo("✓ Created .helpers directory structure")
    
    # Update .gitignore
    setup_gitignore(project_dir)
    
    # Create ask-human.sh script
    setup_ask_script(project_dir)
    
    # Create/update CLAUDE.md
    setup_claude_md(project_dir)
    
    click.echo("\n=== Setup Complete ===")
    click.echo("\nTo use Human-in-the-Loop:")
    click.echo("1. Start listener in separate terminal: claude-helpers listen")
    click.echo("2. Claude will use ask-human.sh when it needs clarification")
    click.echo("\nTo use voice input in Claude Code:")
    click.echo("Type: !claude-helpers voice")

def setup_gitignore(project_dir: Path):
    """Add .helpers to .gitignore"""
    gitignore = project_dir / ".gitignore"
    
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            content = f.read()
        
        if '.helpers' not in content:
            with open(gitignore, 'a') as f:
                f.write('\n# Claude Helpers\n.helpers/\n')
            click.echo("✓ Added .helpers to .gitignore")
        else:
            click.echo("✓ .helpers already in .gitignore")
    else:
        with open(gitignore, 'w') as f:
            f.write('# Claude Helpers\n.helpers/\n')
        click.echo("✓ Created .gitignore with .helpers")

def setup_ask_script(project_dir: Path):
    """Create ask-human.sh script"""
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    ask_script = scripts_dir / "ask-human.sh"
    
    # Use template from hil-system.md
    script_content = get_ask_human_script_template()
    
    with open(ask_script, 'w') as f:
        f.write(script_content)
    
    ask_script.chmod(0o755)  # Make executable
    click.echo(f"✓ Created executable script: {ask_script}")

def setup_claude_md(project_dir: Path):
    """Create or update CLAUDE.md with HIL instructions"""
    claude_md = project_dir / "CLAUDE.md"
    
    if claude_md.exists():
        with open(claude_md, 'r') as f:
            existing_content = f.read()
        
        if "HUMAN-IN-THE-LOOP INSTRUCTIONS" not in existing_content:
            # Prepend our instructions
            with open(claude_md, 'w') as f:
                f.write(get_claude_md_template())
                f.write("\n\n")
                f.write(existing_content)
            click.echo("✓ Updated CLAUDE.md with HIL instructions")
        else:
            click.echo("✓ CLAUDE.md already has HIL instructions")
    else:
        with open(claude_md, 'w') as f:
            f.write(get_claude_md_template())
        click.echo("✓ Created CLAUDE.md with HIL instructions")
```

## Template Generation

### Ask-Human Script Template
```python
def get_ask_human_script_template() -> str:
    """Get the ask-human.sh script template"""
    return '''#!/bin/bash
# Multi-agent human-in-the-loop question script for Claude Code
# Auto-generated by claude-helpers

QUESTION="$1"
TYPE="${2:-text}"  # text, yesno, select
OPTIONS="${3:-}"   # comma-separated options for select

HELPERS_DIR=".helpers"
QUESTIONS_DIR="$HELPERS_DIR/questions"
ANSWERS_DIR="$HELPERS_DIR/answers"

# Check if listener is running
if [ ! -f "$HELPERS_DIR/.listener.pid" ]; then
    echo "ERROR: HIL listener not running. Start it with: claude-helpers listen" >&2
    exit 1
fi

# Generate agent identification
AGENT_PID=$$
PARENT_PID=$PPID
TERMINAL_ID=$(ps -p $PARENT_PID -o comm= 2>/dev/null || echo "unknown")
WORKING_DIR=$(pwd)

# Create readable agent name
if [ "$TERMINAL_ID" = "claude" ] || [[ "$TERMINAL_ID" == *"claude"* ]]; then
    AGENT_NAME="Claude-${AGENT_PID}"
else
    AGENT_NAME="Agent-${TERMINAL_ID}-${AGENT_PID}"
fi

AGENT_ID="agent_${AGENT_PID}"

# Generate unique question ID
TIMESTAMP=$(date +%s%N 2>/dev/null || date +%s)
UUID="${TIMESTAMP}_${AGENT_PID}_$$"
QUESTION_ID="$UUID"

# Create question file with agent identification
QUESTION_FILE="$QUESTIONS_DIR/q_${AGENT_ID}_${TIMESTAMP}_${UUID}.json"

# Build JSON with agent information
if [ "$TYPE" = "select" ] && [ -n "$OPTIONS" ]; then
    IFS=',' read -ra OPTS <<< "$OPTIONS"
    OPTIONS_JSON=$(printf '"%s",' "${OPTS[@]}" | sed 's/,$//')
    cat > "$QUESTION_FILE" << EOF
{
  "id": "$QUESTION_ID",
  "agent_id": "$AGENT_ID",
  "agent_name": "$AGENT_NAME",
  "working_dir": "$WORKING_DIR",
  "timestamp": $TIMESTAMP,
  "type": "$TYPE",
  "content": "$QUESTION",
  "options": [$OPTIONS_JSON],
  "priority": "normal",
  "answered": false,
  "timeout": 300
}
EOF
else
    cat > "$QUESTION_FILE" << EOF
{
  "id": "$QUESTION_ID",
  "agent_id": "$AGENT_ID",
  "agent_name": "$AGENT_NAME",
  "working_dir": "$WORKING_DIR",
  "timestamp": $TIMESTAMP,
  "type": "$TYPE",
  "content": "$QUESTION",
  "priority": "normal",
  "answered": false,
  "timeout": 300
}
EOF
fi

echo "[HIL:$AGENT_NAME] Question sent, waiting for response..." >&2

# Wait for answer (with agent-specific filename)
ANSWER_FILE="$ANSWERS_DIR/a_${AGENT_ID}_${QUESTION_ID}.json"
TIMEOUT=300
ELAPSED=0

while [ ! -f "$ANSWER_FILE" ] && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 0.5
    ELAPSED=$((ELAPSED + 1))
    
    # Show progress every 60 seconds
    if [ $((ELAPSED % 120)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        echo "[HIL:$AGENT_NAME] Still waiting... (${ELAPSED}s elapsed)" >&2
    fi
done

if [ ! -f "$ANSWER_FILE" ]; then
    echo "ERROR: Timeout waiting for response (${TIMEOUT}s)" >&2
    rm -f "$QUESTION_FILE" 2>/dev/null
    exit 1
fi

# Read answer (cross-platform JSON parsing)
if command -v jq >/dev/null 2>&1; then
    ANSWER=$(jq -r '.content' "$ANSWER_FILE" 2>/dev/null)
elif command -v python3 >/dev/null 2>&1; then
    ANSWER=$(python3 -c "
import json
try:
    with open('$ANSWER_FILE') as f:
        print(json.load(f).get('content', ''))
except:
    print('')
" 2>/dev/null)
else
    # Fallback grep method
    ANSWER=$(grep '"content"' "$ANSWER_FILE" 2>/dev/null | sed 's/.*"content".*:.*"\\([^"]*\\)".*/\\1/')
fi

# Cleanup files
rm -f "$QUESTION_FILE" "$ANSWER_FILE" 2>/dev/null

# Output answer for Claude
echo "$ANSWER"
'''
```

### CLAUDE.md Template
```python
def get_claude_md_template() -> str:
    """Get the CLAUDE.md instructions template"""
    return '''# HUMAN-IN-THE-LOOP INSTRUCTIONS

IMPORTANT: This project has Human-in-the-Loop (HIL) support enabled.

## When to use HIL

You MUST use the ask-human script when you need clarification on:
- Ambiguous requirements or design decisions
- Choice between multiple valid approaches
- Missing information that affects implementation
- Confirmation before making significant changes
- Any situation where you're unsure about user intent

## How to use HIL

Execute the ask-human script using bash mode:

```bash
# For text questions
!./scripts/ask-human.sh "Your question here"

# For yes/no questions
!./scripts/ask-human.sh "Should I proceed with X?" "yesno"

# For multiple choice
!./scripts/ask-human.sh "Which option?" "select" "option1,option2,option3"
```

The script will wait for a human response and return the answer, allowing you to continue without interruption.

## Example usage

```bash
# When unsure about implementation approach
!./scripts/ask-human.sh "Should I use PostgreSQL or MySQL for the database?"

# When needing confirmation
!./scripts/ask-human.sh "I found 3 test files. Should I update all of them?" "yesno"

# When choosing between options
!./scripts/ask-human.sh "Which framework should I use?" "select" "Express,Fastify,Koa"
```

## Voice Input Support

Users can provide input via voice using:
```bash
!claude-helpers voice
```

---
<!-- Additional project-specific instructions below -->
'''
```

## Environment Variable Support

```python
def load_config_with_env_override() -> GlobalConfig:
    """Load configuration with environment variable override"""
    config = load_config()
    
    # Override API key from environment if available
    env_api_key = os.getenv('OPENAI_API_KEY')
    if env_api_key:
        config.openai_api_key = env_api_key
    
    return config
```

## Error Handling

### Configuration Validation
- **Missing API key**: Clear error with init instruction
- **Invalid JSON**: Helpful parsing error messages
- **Permission errors**: Guide user to fix file permissions
- **Platform detection**: Graceful fallback for unknown platforms

### Recovery Mechanisms
- **Corrupt config**: Backup and recreate with user confirmation
- **Missing directories**: Auto-create with appropriate permissions
- **Version mismatch**: Migration path for config format changes

## Testing Strategy

### Unit Tests
- Configuration loading and validation
- Platform detection across different systems
- Template generation and variable substitution
- Error handling and recovery scenarios

### Integration Tests
- Full init command flow
- Cross-platform configuration paths
- Environment variable override behavior
- Project setup with existing files