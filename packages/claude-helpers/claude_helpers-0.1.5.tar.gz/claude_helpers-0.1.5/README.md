# Claude Helpers

**CLI Agentic-SWE toolkit for Claude Code: Voice input, Human-in-the-Loop, and structured project management.**

## Install

PYPI install:
```bash
uv tool install claude-helpers
```

or PYPI update:

```bash
uv tool upgrade claude-helpers
```

or loocal install:

```bash
git clone {repo} claude-helpers
cd claude-helpers
uv tool install --force --editable .
```

## Setup

```bash
claude-helpers setup
```
Configures OpenAI API keys, audio device, and Claude Code integration.

## Commands

### Basic Usage
```bash
claude-helpers voice          # Record voice, get text transcription
claude-helpers init           # Setup HIL in current project  
claude-helpers listen         # Start HIL background listener
claude-helpers status         # Check configuration and features
claude-helpers skeleton       # List available project templates
```

### Project Templates
```bash
# List all available templates (built-in + Memory-Bank)
claude-helpers skeleton

# Create new project from template
claude-helpers skeleton python-basic --name my-service
claude-helpers skeleton fastapi-service --name my-api

# Create template files in current directory
mkdir my-service && cd my-service
claude-helpers skeleton python-basic --here
```

Custom templates can be added to Memory-Bank at `templates/skeletons/template-name/`.

### Memory-Bank (Advanced)
```bash
# Create Memory-Bank repository
claude-helpers memory-bank spawn-structure
claude-helpers memory-bank spawn-templates  
claude-helpers memory-bank spawn-prompts

# Link Memory-Bank to work project (repo SHALL contain .helpers, by `claude-helpers init`)
claude-helpers memory-bank init
```

### MCP Servers
```bash
# (For Agent mcp STDIO use, server is not required)
claude-helpers mcp-server         # HIL MCP server
claude-helpers memory-bank-mcp    # Memory-Bank MCP server
```

#### HIL MCP Server
Enables agents to interact with humans during development:
- `ask_human(question)` - Ask human a question, wait for response
- `voice_input(prompt)` - Record voice input from human
- File-based async communication between agents and background listener

#### Memory-Bank MCP Server  
Project management and documentation for structured development:
- `get-focus(release, component)` - Get current work context and standards
- `get-progress(release, component)` - View implementation progress
- `current-task/epic/component` - Navigate project structure
- `validate-project-structure(path, purpose)` - Check file placement
- `update-task-status(task, status)` - Mark tasks complete
- `note-journal(content, role)` - Add development notes

## Integration

Add to Claude Code MCP configuration:

**HIL Integration:**
```json
{
  "type": "stdio",
  "command": "claude-helpers", 
  "args": ["mcp-server"]
}
```

**Memory-Bank Integration:**
```json
{
  "type": "stdio",
  "command": "claude-helpers",
  "args": ["memory-bank-mcp"]
}
```

## What it does

- **Voice**: Record voice prompts, get Whisper transcription
- **HIL**: Agents can ask questions, humans respond via GUI/terminal
- **Memory-Bank**: Structured project docs and workflow templates
- **MCP**: Seamless Claude Code integration for all features

## Requirements

- Python 3.10+
- OpenAI API key
- Audio device (for voice)

## License

MIT