# Claude Helpers - Architecture Design

## Core Principles

- **Single global tool** - Install once, use in any project
- **Project initialization** - `claude-helpers init` sets up both global config AND project integration
- **No manual configuration** - Everything works after init
- **Native Claude Code integration** - Uses `!` bash commands and CLAUDE.md instructions

## Installation Model

- **Global Python package** via `uv tool install`
- Accessible system-wide as `claude-helpers` command
- Configuration stored in platform-appropriate directories:
  - **Linux**: `~/.config/claude-helpers/`
  - **macOS**: `~/Library/Application Support/claude-helpers/`
- Project-specific data in `./.helpers/` (when needed)

## Component Structure

```
claude-helpers/
├── pyproject.toml              # UV package configuration
├── README.md
├── LICENSE
├── .gitignore
├── scripts/
│   └── ask-human.sh           # Bash script for agent-side HIL
├── src/
│   └── claude_helpers/
│       ├── __init__.py
│       ├── __main__.py        # Entry point
│       ├── cli.py             # Click CLI interface
│       ├── config.py          # Configuration management
│       ├── voice.py           # Voice recording and transcription
│       ├── platform.py        # Cross-platform utilities
│       ├── audio/
│       │   ├── __init__.py
│       │   ├── recorder.py    # Audio recording with sounddevice
│       │   └── devices.py     # Audio device detection
│       ├── transcription/
│       │   ├── __init__.py
│       │   └── openai_client.py  # Whisper API client
│       └── hil/               # Human-in-the-loop
│           ├── __init__.py
│           ├── listener.py   # Background listener process
│           ├── dialog.py      # GUI dialog manager
│           └── protocol.py    # File-based message protocol
└── tests/
    └── ...
```

## Key Insights

- **Claude Code bash-mode**: Commands starting with `!` execute and output goes to chat
- **Multi-agent support**: Single HIL listener handles multiple Claude Code windows
- **File-based communication**: No servers needed, uses `.helpers/` directory
- **CLAUDE.md instructions**: Teaches Claude when and how to use our tools

## Installation Flow

### One-time Global Setup
```bash
uv tool install claude-helpers
claude-helpers init --global-only
# Enter OpenAI API key
# Configure audio device
```

### Per-project Setup
```bash
cd /path/to/project
claude-helpers init
# Creates .helpers/, scripts/ask-human.sh, updates CLAUDE.md
```

### Daily Usage
```bash
# Terminal 1: HIL Listener (handles all agents)
claude-helpers listen

# Terminal 2+: Claude Code sessions
!claude-helpers voice              # Voice input
!./scripts/ask-human.sh "Question" # HIL (automatic via CLAUDE.md)
```

## Multi-Agent Architecture

- **Single listener** serves multiple Claude Code windows
- **Automatic agent identification** via PID/process info
- **Question queue** with sequential processing
- **Agent context** showing which Claude instance is asking
- **File protocol** with agent-specific naming:
  - `q_agent_12345_timestamp_uuid.json` (questions)
  - `a_agent_12345_timestamp_uuid.json` (answers)

## Security & Privacy

- **API keys**: Stored in user home with 600 permissions
- **Audio privacy**: No recordings saved by default
- **File cleanup**: Automatic cleanup of HIL files
- **Validation**: JSON structure validation
- **Environment variables**: Support for `OPENAI_API_KEY` override