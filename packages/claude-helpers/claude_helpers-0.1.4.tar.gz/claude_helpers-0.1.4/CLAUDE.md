# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude Helpers** - Cross-platform Python utility for seamless Claude Code integration providing voice input and human-in-the-loop capabilities for enhanced AI agent workflows.

**Key Features**:
- Voice Input: `!claude-helpers voice` records audio and outputs transcription via OpenAI Whisper
- Multi-Agent HIL: File-based message exchange supporting multiple Claude Code sessions simultaneously
- Cross-Platform: Native support for Linux and macOS with platform-specific optimizations

## Critical Development Rules

### Epic-Based Development Flow
**MANDATORY**: Work strictly by epics in sequential order. Each epic must be 100% functional before moving to next.

**Epic Order**:
1. **Foundation** (6 tasks, 3-4 days) - Project structure, UV packaging, CLI framework
2. **Configuration** (7 tasks, 4-5 days) - Platform detection, config management, init command  
3. **Voice System** (6 tasks, 5-6 days) - Audio recording, device management, Whisper integration
4. **Dialog System** (5 tasks, 4-5 days) - Cross-platform GUI dialogs with terminal fallback
5. **HIL System** (5 tasks, 6-7 days) - Multi-agent file protocol, background listener
6. **Integration** (4 tasks, 4-5 days) - Testing, packaging, documentation, release

**Task Progression**: Complete each task's acceptance criteria before moving to next task within epic.

### Forbidden Actions
- **NO EPIC JUMPING**: Cannot work on Epic 3 while Epic 2 incomplete
- **NO BULLSHIT CODE**: No placeholder, dummy, or temporary implementations  
- **NO OVER-ENGINEERING**: Only implement features defined in requirements
- **NO PLATFORM ASSUMPTIONS**: Code must work on both Linux AND macOS
- **NO SILENT FAILURES**: All errors must be handled explicitly with clear messages

### Required Standards
- **Code Language**: English for all code, comments, variable names, function names
- **Documentation**: English for README, docstrings, error messages, API interfaces
- **Architecture**: Single responsibility, dependency injection, loose coupling
- **Testing**: Critical functionality tests only, no test bloat
- **Cross-Platform**: Platform-aware implementations with proper abstractions

## Architecture Overview

### System Architecture
Multi-layered architecture with clear component boundaries:

1. **CLI Interface** (`cli.py`) - Thin layer over core functionality
2. **Configuration System** (`config.py`) - Foundation for all other systems
3. **Audio System** (`audio/`) - Independent audio recording and device management
4. **Dialog System** (`hil/dialog.py`) - Platform-agnostic user interaction
5. **HIL System** (`hil/`) - Orchestrates components for human-in-the-loop workflows

### Key Technical Decisions
- **Multi-Agent Architecture**: File-based communication protocol supporting multiple Claude Code sessions
- **Cross-Platform Audio**: Unified sounddevice API with 44.1kHz mono recording optimized for OpenAI Whisper
- **Dialog Fallback Chain**: GUI → Terminal fallback ensures HIL works in all environments
- **Two-Level Configuration**: Global config (~/.config/) for API keys, project config (.helpers/) for HIL
- **Agent Identification**: Process hierarchy (PID + PPID) generates unique agent IDs

### Integration Points
- **With Claude Code**: Uses native `!` bash-mode, output to stdout becomes next prompt input
- **Cross-Component**: Configuration system feeds platform-specific settings to all components
- **HIL Dependencies**: HIL System requires Dialog System, but Voice System remains independent

## Common Development Tasks

### Project Setup
```bash
# Initial project structure (Epic 1, Task 1.1)
uv init --name claude-helpers --package
uv add click pydantic rich sounddevice numpy scipy openai keyboard watchdog

# Build and test
uv build
uv run pytest
uv tool install --editable .
```

### Development Workflow
```bash
# Run tests for current epic components
uv run pytest tests/ -v

# Test CLI commands
claude-helpers --version
claude-helpers --help

# Cross-platform testing
uv run pytest tests/test_platform.py

# Integration testing (Epic 6)
uv run pytest tests/integration/ -v
```

### Epic Validation Commands
Each epic includes specific test commands in task acceptance criteria. Always run these before considering epic complete.

## Key Implementation Patterns

### Cross-Platform Implementation Pattern
```python
def get_config_dir() -> Path:
    if platform.system() == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'claude-helpers'
    else:  # Linux
        return Path.home() / '.config' / 'claude-helpers'
```

### Error Handling Pattern
```python
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}")
    raise UserFriendlyError(
        "Unable to connect to transcription service. "
        "Please check your internet connection and API key."
    ) from e
```

### Component Interface Pattern
```python
class AudioDevice:
    """Clear data model with validation"""
    id: int
    name: str
    channels: int
    is_default: bool

def list_devices() -> List[AudioDevice]:
    """Simple, testable interface"""
    # Implementation with platform-specific logic
```

## Critical Context Files

### Development Context Tracking
- **`design/current-context.md`**: Must be updated every development session with current epic/task, decisions made, issues discovered
- **`design/agent-flow-rules.md`**: Contains complete development rules and quality gates

### Task Documentation  
- **`design/tasks/README.md`**: Epic overview and dependencies
- **`design/tasks/0X-*.md`**: Detailed task breakdowns with acceptance criteria

### System Design
- **`design/general.md`**: High-level system overview and feature specifications
- **`design/architecture.md`**: Core architectural principles and component relationships

## Human-in-the-Loop Usage

This project implements HIL functionality for Claude agents. When complete:

1. **Project Setup**: `claude-helpers init` creates .helpers/, scripts/ask-human.sh, CLAUDE.md
2. **Background Listener**: `claude-helpers listen` monitors for questions from agents  
3. **Agent Questions**: `!./scripts/ask-human.sh "question"` creates dialog for human response
4. **Multi-Project**: Single listener can serve multiple Claude Code sessions simultaneously

## Quality Gates

### Before Task Completion
- [ ] All acceptance criteria met
- [ ] Test commands execute successfully  
- [ ] Code follows project standards
- [ ] Integration with existing components tested

### Before Epic Completion
- [ ] All epic tasks completed
- [ ] Epic-level integration tests passing
- [ ] Performance benchmarks met
- [ ] Cross-platform compatibility verified
- [ ] Epic fully functional end-to-end

### Development Session Protocol
1. **Start**: Read `design/current-context.md` for current state
2. **Work**: Follow epic → task progression strictly
3. **End**: Update `design/current-context.md` with progress, decisions, issues

**Remember**: The goal is production-ready, maintainable, user-friendly software that real people can install and use successfully.

<!-- CLAUDE HELPERS HIL START -->

# Claude Code Integration

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


<!-- CLAUDE HELPERS HIL END -->