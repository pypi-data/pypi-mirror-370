# Claude Helpers - Development Context Journal

## 📋 Project Overview

**Project**: Claude Helpers - Cross-platform voice and HIL tools for Claude Code  
**Goal**: Globally installable Python package providing `!claude-helpers voice` and human-in-the-loop functionality  
**Status**: Design Complete, Ready for Development  
**Started**: 2025-01-07  

## 🎯 Current Development State

### Active Epic: Epic 4 - Dialog System (Voice-HIL Integration Focus)
**Current Epic**: Epic 4 - Dialog System  
**Current Task**: Task 4.1 - Dialog Tool Detection (modified for voice integration)  
**Focus**: Integrating voice into HIL system instead of standalone command  
**Decision Date**: 2025-01-07  

### Epic Completion Status
- [x] **Design Phase**: Complete task breakdown and architecture
- [x] **Epic 1**: Project Foundation (6 tasks, COMPLETED 2025-01-07)
- [x] **Epic 2**: Configuration System (7 tasks, COMPLETED 2025-01-07)  
- [x] **Epic 3**: Voice System (6 tasks, COMPLETED 2025-01-07)
- [ ] **Epic 4**: Dialog System (5 tasks, IN PROGRESS - WITH VOICE INTEGRATION)
- [ ] **Epic 5**: HIL System (5 tasks, 6-7 days)
- [ ] **Epic 6**: Final Integration (4 tasks, 4-5 days)

## 🏗️ Architecture Decisions Made

### Core System Architecture
**Decision**: Multi-agent file-based communication protocol  
**Reasoning**: No servers needed, works with multiple Claude Code sessions  
**Impact**: HIL system can serve multiple projects simultaneously  
**Date**: 2025-01-07

**Decision**: Voice integrated into HIL system instead of standalone  
**Reasoning**: Claude Code can't handle interactive input in ! commands  
**Impact**: Voice becomes a type of HIL question, listener orchestrates all interactions  
**Date**: 2025-01-07  

**Decision**: Cross-platform audio recording with sounddevice  
**Reasoning**: Unified API for Linux/macOS, good OpenAI Whisper compatibility  
**Impact**: Single codebase for audio across platforms  
**Date**: 2025-01-07  

**Decision**: Fallback chain for GUI dialogs (GUI → Terminal)  
**Reasoning**: Ensures HIL works in all environments  
**Impact**: Reliable user interaction regardless of environment  
**Date**: 2025-01-07  

### Package Structure Decisions
**Decision**: UV tool install as global package manager  
**Reasoning**: Modern Python packaging, better than pip for CLI tools  
**Impact**: Users install with `uv tool install claude-helpers`  
**Date**: 2025-01-07  

**Decision**: Two-level configuration (global + project)  
**Reasoning**: API key global, project setup per directory  
**Impact**: Clean separation of concerns, easy multi-project use  
**Date**: 2025-01-07  

## 🔍 Critical Technical Insights

### Multi-Agent Architecture
**Key Insight**: Agent identification via PID + process hierarchy  
**Challenge**: Multiple Claude Code sessions need unique IDs  
**Solution**: Generate agent IDs from process info with collision detection  
**Implication**: Robust support for concurrent Claude sessions  

### Cross-Platform Compatibility  
**Key Insight**: Platform detection must drive all system choices  
**Challenge**: Different audio systems, dialog tools, config directories  
**Solution**: Platform abstraction layer with tool detection  
**Implication**: Single codebase with platform-specific implementations  

### Voice Transcription Flow
**Key Insight**: Audio quality optimization critical for transcription accuracy  
**Challenge**: Raw audio from various microphones needs preprocessing  
**Solution**: 44.1kHz mono recording with volume normalization  
**Implication**: Consistent transcription quality across hardware  

## 🚨 Identified Risks and Mitigations

### Risk: Audio Permission Complexity (macOS)
**Risk Level**: High  
**Description**: macOS requires explicit microphone permissions  
**Mitigation**: Clear error messages guiding users to system preferences  
**Status**: Identified, solution designed  

### Risk: GUI Dialog Tool Availability (Linux)
**Risk Level**: Medium  
**Description**: Various Linux distros have different dialog tools  
**Mitigation**: Detection system with multiple fallbacks to terminal  
**Status**: Identified, solution designed  

### Risk: OpenAI API Rate Limiting
**Risk Level**: Medium  
**Description**: Heavy usage could hit API limits  
**Mitigation**: Error handling with retry logic and clear user guidance  
**Status**: Identified, solution designed  

### Risk: File System Performance (HIL)
**Risk Level**: Low  
**Description**: File watching might be slow on some systems  
**Mitigation**: Efficient file operations with proper cleanup  
**Status**: Identified, solution designed  

## 📝 Development Standards Established

### Code Quality Requirements
- **Language**: English for all code, comments, documentation
- **Architecture**: Simple, clean, testable components
- **Error Handling**: Explicit error handling with helpful messages
- **Testing**: Critical functionality tests only, no test bloat
- **Dependencies**: Minimal, well-justified dependencies only

### Development Flow Requirements
- **Epic-by-Epic**: Complete each epic fully before next
- **Task-by-Task**: Complete each task's acceptance criteria
- **No Shortcuts**: No placeholder or temporary code
- **Integration Focus**: Each epic must integrate with previous ones

### Communication Standards
- **Code/Docs**: English language for global accessibility
- **Development**: Russian for detailed technical discussions
- **Documentation**: English README, API docs, error messages
- **Comments**: English inline code comments

## 🎯 Next Development Session Plan

### Immediate Goals - HIL System Refactoring
1. **Split init command**: Separate `setup` (global) and `init` (project)
2. **Enhanced project init**: Add gitignore handling, MCP integration, timeouts
3. **Dynamic HIL dialogs**: Add text/voice switching in interactive mode
4. **Claude Code integration**: Slash commands, .claudeignore, CLAUDE.md updates

### Prerequisites Check
- [x] Design documents complete
- [x] Task breakdown detailed  
- [x] Dependencies analyzed
- [x] Architecture decisions made
- [x] Development rules established
- [x] **Epic 1 Foundation complete and tested**

### Environment Setup Complete ✅
- [x] Python 3.10+ with UV package manager
- [x] Git repository initialization  
- [x] Development environment preparation
- [x] Testing framework setup
- [x] CLI framework operational
- [x] Platform detection working

## 🔄 Integration Points Documented

### Epic 1 → Epic 2 Handoff
**What Epic 1 Provides**: Basic project structure, CLI framework, platform detection  
**What Epic 2 Needs**: Stable foundation to build configuration system  
**Integration Point**: Platform detection feeds into config directory selection  

### Epic 2 → Epic 3/4 Handoff  
**What Epic 2 Provides**: Configuration loading, init command, project setup  
**What Epic 3 Needs**: Audio configuration settings  
**What Epic 4 Needs**: HIL configuration settings  
**Integration Point**: Both systems use global config for their settings  

### Epic 3/4 → Epic 5 Handoff
**What Epic 3 Provides**: Voice transcription functionality (independent)  
**What Epic 4 Provides**: Dialog system for user interaction (required by HIL)  
**What Epic 5 Needs**: Dialog system for asking questions  
**Integration Point**: HIL uses dialog system, voice system remains independent  

### Epic 5 → Epic 6 Handoff
**What Epic 5 Provides**: Complete HIL functionality  
**What Epic 6 Needs**: All systems working together  
**Integration Point**: Final testing of voice + HIL workflows  

## 📊 Success Metrics Defined

### Development Velocity Targets
- **Task Completion**: 1-2 tasks per day
- **Epic Duration**: Stay within estimated time bounds
- **Integration Time**: < 1 day between epic transitions
- **Issue Resolution**: Problems solved within current epic

### Quality Targets  
- **Test Coverage**: All critical functionality covered
- **Documentation**: All user-facing features documented
- **Cross-Platform**: 100% functionality on Linux and macOS
- **Error Handling**: All failure modes handled gracefully

### User Experience Targets
- **Installation**: One-command global install with UV
- **Setup**: Clear init process for both global and project setup
- **Voice Command**: < 30 second total time for transcription
- **HIL Response**: < 2 second response time for dialog appearance

## 🎯 Critical Success Factors

### Technical Excellence
- Clean, maintainable code architecture
- Comprehensive error handling and user guidance  
- Cross-platform compatibility without compromises
- Performance that meets user expectations

### User Experience Excellence
- Installation "just works" on supported platforms
- Clear, helpful error messages guide users to solutions
- Voice and HIL features integrate seamlessly with Claude Code
- Documentation enables independent user success

### Development Process Excellence
- Iterative progress with working software at each stage
- Thorough testing prevents regression issues
- Clear architecture enables future maintenance and enhancement
- Complete documentation facilitates community contribution

---

## 📅 Session Log Template

```markdown
### Session: YYYY-MM-DD HH:MM

**Epic**: [Current Epic]
**Task**: [Current Task] 
**Duration**: [Time spent]

**Goals**:
- [ ] Goal 1
- [ ] Goal 2

**Achievements**:
- [x] Achievement 1
- [x] Achievement 2

**Decisions Made**:
- Decision 1 and reasoning
- Decision 2 and reasoning

**Issues Discovered**:
- Issue 1 and resolution
- Issue 2 and status

**Next Steps**:
- Next immediate task
- Any blockers to address

**Integration Notes**:
- How current work affects other components
- Any architectural implications
```

**Note**: Each development session should start with reading this context file and end with updating it.

---

## 🔄 Session Log: Voice-HIL Integration - IN PROGRESS

### Session: 2025-08-08 - Init Command Refactoring ✅ COMPLETED

**Epic**: System Refactoring & Simplification
**Duration**: 2+ hours  
**Status**: ✅ COMPLETED - Init command fully refactored per user requirements

**Major Changes Made**:
1. ✅ **Fixed IntPrompt.ask() TypeError**: Replaced all IntPrompt.ask() calls with manual validation loops
2. ✅ **Removed Preset System**: Eliminated confusing preset choices (Basic/Skip)
3. ✅ **Individual Setup Choices**: Now asks separately for voice, HIL rules, and MCP setup
4. ✅ **Removed Auto-editing**: No longer automatically edits CLAUDE.md or .claudeignore
5. ✅ **Updated Command Content**: /voice now describes MCP tools for agent understanding
6. ✅ **Updated MCP Tool Names**: record-voice-prompt instead of voice_input
7. ✅ **Simplified CLI**: ask command hidden, only available internally for MCP

**Technical Implementation**:
- **IntPrompt fixes**: All timeout/device/rate validations use while loops with proper error messages
- **setup_project_interactive()**: Completely rewritten with clean individual choices
- **MCP integration**: Proper tool descriptions explaining when/how to use ask-human and record-voice-prompt
- **Voice command**: Now explains MCP tool usage rather than CLI command usage
- **Error handling**: Improved user feedback for all setup steps

**User Requirements Met**:
- ✅ Only /voice needed as slash command (not /ask)
- ✅ ask command only as MCP tool, not regular CLI
- ✅ Removed presets, replaced with individual choices
- ✅ Command content describes MCP tools for agent comprehension
- ✅ No automatic CLAUDE.md/.claudeignore editing

**Files Modified**:
- `src/claude_helpers/config.py` - Complete setup_project_interactive rewrite, IntPrompt fixes
- `src/claude_helpers/cli.py` - Hidden ask command for internal use only
- `src/claude_helpers/mcp/server.py` - Updated tool name to record-voice-prompt

**Current System State**:
- Init command asks 3 individual questions: voice setup, HIL rules, MCP setup  
- Creates only .helpers/ directory and optionally updates .gitignore
- MCP tools: ask-human, record-voice-prompt with clear agent-focused descriptions
- Voice command explains when/how agent should use MCP tools

---

### Session: 2025-01-08 - MCP Server Implementation 🚧 ARCHIVED
**Epic**: MCP Integration & System Refactoring
**Duration**: 4+ hours
**Status**: 🚧 IN PROGRESS - CRITICAL BUG: Watchdog Latency in HIL Listener
**Blocker**: MCP integration works but has massive delays (minutes) due to watchdog Observer issues

**MCP Implementation Progress**:
1. ✅ **MCP Server Architecture**:
   - Added FastMCP dependency to pyproject.toml
   - Created HIL core functions (`src/claude_helpers/hil/core.py`)
   - Implemented MCP server (`src/claude_helpers/mcp/server.py`) with ask_human/voice_input tools
   - Added `claude-helpers mcp-server` CLI command
   - Proper MCP registration: `claude mcp add-json ask-human '{"type":"stdio","command":"claude-helpers","args":["mcp-server"]}'`

2. 🚧 **CRITICAL BUG - HIL Watchdog Delay**:
   - MCP server creates question files in `.helpers/questions/` ✅
   - HIL listener running but **massive watchdog delay** 🐛
   - **Symptom**: MCP request hangs for long time, then suddenly processes after user cancellation
   - **Root cause**: watchdog.observers.Observer has significant latency
   - Files accumulate: agent_119498_436116.json, agent_121587_387734.json, etc.
   - Manual test file creation also delayed
   - **Impact**: MCP integration appears broken due to timeout

3. ✅ **Architecture Changes**:
   - MCP server runs per-request (not daemon)
   - HIL listener runs continuously in background
   - Communication via file system (.helpers/questions → .helpers/answers)
   - Each MCP request gets unique agent_id with mcp_ prefix

**Files Created/Modified**:
- `pyproject.toml` - Added fastmcp>=0.2.0 dependency
- `src/claude_helpers/hil/core.py` - NEW: HIL core functions for MCP integration
- `src/claude_helpers/mcp/__init__.py` - NEW: MCP module
- `src/claude_helpers/mcp/server.py` - NEW: FastMCP server with ask_human/voice_input tools
- `src/claude_helpers/cli.py` - Replaced old mcp-server with FastMCP implementation

**Current Architecture**:
```
Claude Code → claude mcp add-json ask-human → claude-helpers mcp-server
     ↓
MCP Server (per request) → creates .helpers/questions/mcp_*.json
     ↓
HIL Listener (daemon) → should process files → .helpers/answers/
     ↓
MCP Server reads answer → returns to Claude Code
```

**Critical Bug**: Watchdog in HIL listener not triggering on file creation

**Design Changes Made**:
1. **MCP Integration**: Now primary interaction method for agents (not slash commands)
2. **Simplified Init**: Removed CLAUDE.md and .claudeignore auto-editing
3. **HIL Core**: Extracted reusable functions from CLI for MCP server
4. **FastMCP**: Using industry standard MCP implementation

**Immediate Next Steps**:
1. **Fix watchdog latency** - investigate Observer configuration
2. **Add polling fallback** - hybrid watchdog + periodic scan
3. **Improve logging** - debug why events are delayed
4. **Test file flush** - ensure files are fully written before processing
5. **Optimize file handling** - reduce I/O latency

**Debugging Evidence**:
- HIL listener process running (PID visible in ps aux)
- Question files created correctly in `.helpers/questions/`
- Answer files eventually appear in `.helpers/answers/` but with major delay
- User reports: "message came through much later after canceling command"

**Possible Solutions**:
- Replace watchdog with inotify (Linux) / FSEvents (macOS)
- Add polling mechanism as backup
- Optimize file I/O operations
- Implement immediate file processing check

**Critical Issue Discovered**:
- Claude Code runs bash commands in non-interactive mode
- Voice command requires interactive input (Enter key presses)
- Solution: Integrate voice into HIL system as a question type

**Architectural Pivot**:
- FROM: Standalone `!claude-helpers voice` command
- TO: `!./scripts/ask-human.sh --voice "prompt"` integration
- BENEFIT: Listener handles all UI interaction, agent gets clean text output

**Implementation Completed**:
1. ✅ Extended ask-human.sh with --voice flag and JSON format
2. ✅ Created VoiceQuestionHandler in listener.py
3. ✅ Integrated existing voice recording infrastructure
4. ✅ Added preview/edit capability for transcriptions
5. ✅ Implemented text fallback on voice failure
6. ✅ Created QuestionRouter for type-based handling

**Files Created/Modified**:
- `scripts/ask-human.sh` - Added voice support with JSON protocol
- `src/claude_helpers/hil/listener.py` - Complete HIL listener implementation
- `src/claude_helpers/cli.py` - Updated listen command
- `src/claude_helpers/hil/__init__.py` - Fixed import issues

**Technical Decisions**:
- JSON format for questions (backward compatible with text)
- Question routing based on type field
- Watchdog for file system monitoring
- Rich UI for all interactions

**Implementation Completed**:
1. ✅ Extended ask-human.sh with --voice flag and JSON format
2. ✅ Created VoiceQuestionHandler in listener.py
3. ✅ Integrated existing voice recording infrastructure
4. ✅ Added preview/edit capability for transcriptions
5. ✅ Implemented text fallback on voice failure
6. ✅ Created QuestionRouter for type-based handling
7. ✅ **NEW**: Redesigned for Claude Code integration
8. ✅ **NEW**: Global claude-helpers ask command
9. ✅ **NEW**: .claude/commands.md integration
10. ✅ **NEW**: .claudeignore support
11. ✅ **NEW**: Status command for environment checking

**Files Created/Modified**:
- `scripts/ask-human.sh` - Added voice support with JSON protocol
- `src/claude_helpers/hil/listener.py` - Complete HIL listener implementation
- `src/claude_helpers/cli.py` - Updated listen command + ask command + status command
- `src/claude_helpers/hil/__init__.py` - Fixed import issues
- `src/claude_helpers/scripts/ask-human.sh` - Global version of ask script
- `src/claude_helpers/config.py` - Claude Code integration setup functions

**Architecture Changes**:
- FROM: Project-local scripts/ask-human.sh
- TO: Global claude-helpers ask command
- BENEFIT: No local script copying, consistent global interface

**Claude Code Integration Features**:
- ✅ .claude/commands.md automatic setup with usage examples
- ✅ .claudeignore automatic setup to hide .helpers/
- ✅ Global claude-helpers ask command accessible from anywhere
- ✅ Status command for environment verification
- ✅ Voice integration: `!claude-helpers ask --voice "prompt"`
- ✅ Text questions: `!claude-helpers ask "question"`

**Testing Results**:
- ✅ claude-helpers ask command functional
- ✅ Automated question/answer flow working
- ✅ Status command shows all green checks
- ✅ Claude Code integration properly configured
- ✅ File cleanup working correctly

**Voice-HIL Integration: COMPLETED** 🎉

---

## 🎉 Session Log: Epic 1 Foundation - COMPLETED

### Session: 2025-01-07 14:00-16:00
**Epic**: Epic 1 - Project Foundation  
**Duration**: 2 hours  
**Status**: ✅ COMPLETED

**Goals Achieved**:
- [x] Task 1.1: Initial Project Structure
- [x] Task 1.2: UV Project Configuration  
- [x] Task 1.3: Basic CLI Framework
- [x] Task 1.4: Platform Detection Module
- [x] Task 1.5: Testing Infrastructure
- [x] Task 1.6: Cross-Platform Validation

**Key Achievements**:
- ✅ Complete project structure with proper Python packaging
- ✅ UV package management fully configured and working
- ✅ CLI framework operational with all placeholder commands
- ✅ Cross-platform detection working (Linux tested, macOS ready)
- ✅ Testing infrastructure with 97% code coverage
- ✅ All 15 tests passing, zero installation failures

**Success Metrics Met**:
- Installation time: < 1 minute (UV is fast!)
- Test coverage: 97% (exceeds 80% target)
- CLI response time: < 100ms for basic commands
- Zero platform-specific installation failures

**Technical Decisions Made**:
- Used Click for CLI framework - clean and extensible
- Platform detection supports macOS/Linux with graceful fallback
- Testing covers both unit and integration patterns
- Build system uses modern hatchling backend

**Files Created**:
- `src/claude_helpers/`: Complete package structure
- `tests/`: Comprehensive test suite with fixtures
- `pyproject.toml`: Full UV package configuration
- `README.md`, `LICENSE`, `.gitignore`: Project metadata

**Quality Validation**:
- All Python files compile without errors
- UV sync/build/install cycle works perfectly
- CLI commands functional and error handling working
- Platform detection accurately identifies Linux environment
- All test commands from acceptance criteria pass

**Next Steps**:
Epic 2 (Configuration System) is ready to start with a stable foundation:
1. Global configuration loading and validation
2. Platform-aware config directories (already detected)
3. Project initialization commands (CLI structure ready)
4. API key management and security

**Integration Notes**:
- Platform detection feeds directly into Epic 2 config directories
- CLI structure ready for real command implementations
- Testing framework ready for configuration system tests