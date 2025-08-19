# Claude Helpers

Cross-platform Python utility for seamless Claude Code integration providing voice input and human-in-the-loop (HIL) capabilities for enhanced AI agent workflows.

## Features

### 🎤 Voice Input
- Record voice prompts and get instant OpenAI Whisper transcription
- Configurable audio devices and recording settings
- Auto-language detection for transcription

### 🤝 Human-in-the-Loop (HIL)
- MCP (Model Context Protocol) integration for Claude Code
- Multi-agent support with unique agent identification
- File-based message exchange for reliable communication
- Background listener with text/voice response options

### 🖥️ Cross-Platform
- Native support for Linux and macOS
- Platform-specific optimizations
- Terminal and GUI dialog support

## Installation

### Using UV (recommended)
```bash
uv tool install claude-helpers
```

### Using pip
```bash
pip install claude-helpers
```

## Quick Start

### 1. Initial Setup
```bash
# Configure global settings (API keys, audio devices)
claude-helpers setup

# Initialize project for Claude Code integration
claude-helpers init
```

### 2. Voice Transcription
```bash
# Record voice and output transcription
claude-helpers voice
```

### 3. Human-in-the-Loop

Start the HIL listener in your project:
```bash
claude-helpers listen
```

In Claude Code, the agent can ask questions using the MCP tool:
- `ask-question` - Ask human for input (they can respond via text or voice)

## Configuration

Global configuration is stored in:
- Linux: `~/.config/claude-helpers/`
- macOS: `~/Library/Application Support/claude-helpers/`

Project-specific HIL configuration in `.helpers/` directory.

## Requirements

- Python 3.10+
- OpenAI API key (for Whisper transcription)
- Audio input device (for voice features)

## MCP Integration

Claude Helpers provides MCP server for seamless Claude Code integration:

```json
{
  "type": "stdio",
  "command": "claude-helpers",
  "args": ["mcp-server"]
}
```

The MCP server exposes the `ask-question` tool that allows Claude to request human input with automatic voice/text switching in the UI.

## Development Status

This project is actively maintained and welcomes contributions. Current version focuses on core HIL and voice functionality.

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/claude-helpers/claude-helpers/issues)
- Documentation: [Full documentation](https://github.com/claude-helpers/claude-helpers)

## Author

Vladimir Loskutov (claude-helpers@modus.dev)