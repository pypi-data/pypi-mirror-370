# Claude Helpers - Design Documentation

## Overview

Cross-platform Python utility for seamless Claude Code integration via native bash-mode (`!` commands). Provides voice input and human-in-the-loop capabilities for enhanced AI agent workflows.

### Key Features
1. **Voice Input** - `!claude-helpers voice` - records audio and outputs transcription
2. **Multi-Agent HIL** - File-based message exchange supporting multiple Claude Code sessions
3. **Cross-Platform** - Works natively on Linux and macOS
4. **Zero Configuration** - Works out of the box after simple init

## Design Documents

### Core System Design

#### [🏗️ Architecture](./architecture.md)
- Core principles and installation model
- Component structure and relationships
- Multi-agent architecture overview
- Security and privacy considerations

#### [📦 Package Structure](./package-structure.md)
- Project layout and organization
- Dependencies and build configuration
- Module structure and public APIs
- Testing and development setup

### Feature Systems

#### [🎤 Voice System](./voice-system.md)
- Audio recording and device management
- OpenAI Whisper integration
- Cross-platform recording implementation
- Error handling and fallbacks

#### [💬 Human-in-the-Loop System](./hil-system.md)  
- Multi-agent file-based communication
- Background listener architecture
- Agent identification and registration
- Question queue and processing

#### [🖥️ Dialog System](./dialog-system.md)
- Cross-platform GUI dialog implementation
- macOS AppleScript integration
- Linux Zenity/Yad/Dialog support
- Terminal fallback system

#### [⚙️ Configuration System](./configuration.md)
- Two-level configuration (global + project)
- Platform-specific config directories
- Init command implementation
- Template generation and project setup

## Quick Start for Developers

### Understanding the Flow

1. **Installation**: Global UV package install (`uv tool install claude-helpers`)
2. **Global Setup**: `claude-helpers init --global-only` (API key, audio device)
3. **Project Setup**: `claude-helpers init` (creates .helpers/, scripts/, CLAUDE.md)
4. **Usage**: Voice (`!claude-helpers voice`) + HIL (automatic via CLAUDE.md instructions)

### Development Priority

For agentaí development, implement in this order:

1. **[Configuration System](./configuration.md)** - Core foundation
   - Platform detection and config directories
   - Init command with global/project setup
   - Template generation

2. **[Voice System](./voice-system.md)** - Independent feature
   - Audio recording and device management
   - OpenAI Whisper integration
   - CLI command implementation

3. **[Dialog System](./dialog-system.md)** - HIL dependency  
   - Cross-platform dialog detection
   - GUI tool implementations
   - Terminal fallback

4. **[HIL System](./hil-system.md)** - Complex multi-agent system
   - File-based protocol
   - Multi-agent listener
   - Agent identification and queue management

5. **[Package Structure](./package-structure.md)** - Final assembly
   - Build configuration
   - Testing setup
   - Distribution preparation

## Key Implementation Notes

### Multi-Agent Architecture
- **Single listener** serves multiple Claude Code windows
- **Automatic agent ID** generation via PID/process info  
- **Sequential processing** of questions with user context
- **File-based communication** no servers needed

### Cross-Platform Compatibility
- **Config directories**: Linux (`~/.config/`) vs macOS (`~/Library/Application Support/`)
- **Audio systems**: PulseAudio/ALSA vs CoreAudio
- **Dialog tools**: Zenity/Yad vs AppleScript
- **Bash compatibility**: UUID generation, JSON parsing fallbacks

### Error Handling Philosophy
- **Graceful degradation**: GUI → Terminal fallbacks
- **Clear error messages**: Guide user to solutions
- **Config validation**: Fail fast with helpful instructions
- **Recovery mechanisms**: Auto-fix common issues

## File Structure Overview

```
design/
├── general.md              # This navigation file
├── architecture.md         # Overall system design  
├── voice-system.md         # Voice recording & transcription
├── hil-system.md           # Human-in-the-loop messaging
├── dialog-system.md        # Cross-platform GUI dialogs
├── configuration.md        # Config management & init
└── package-structure.md    # Project layout & build
```

## Development Guidelines

### Code Organization
- **Modular design**: Each system is independent where possible
- **Platform abstraction**: Unified interfaces with platform-specific implementations  
- **Error handling**: Consistent error types and messages
- **Testing**: Unit tests for components, integration tests for flows

### Agent Development Strategy
- **Start small**: Implement configuration system first
- **Test early**: Each component should work independently
- **Cross-platform**: Test on both Linux and macOS throughout development
- **User experience**: Focus on clear error messages and helpful guidance

## Integration Points

### With Claude Code
- Uses native `!` bash-mode for command execution
- Output to stdout becomes Claude's next prompt input
- Error messages to stderr for user visibility
- CLAUDE.md instructions guide agent behavior

### With System
- Respects platform conventions for config storage
- Integrates with native dialog systems
- Uses system audio APIs via sounddevice
- Handles platform-specific permissions (macOS microphone)

## Future Considerations

### Extensibility
- Plugin system for additional dialog tools
- Configurable transcription providers  
- Custom agent identification methods
- Additional file-based communication protocols

### Performance
- Lazy loading of heavy dependencies
- Efficient file watching and processing
- Memory management for audio data
- Network request optimization and retries