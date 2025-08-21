# Voice-HIL Integration Design

## Overview

Integration of voice recording functionality into the Human-in-the-Loop (HIL) system to solve the non-interactive execution problem in Claude Code.

## Problem Statement

Claude Code executes bash commands in non-interactive mode, making the standalone `claude-helpers voice` command unusable within agent workflows. The command expects interactive input (Enter key presses) which cannot be provided in the `!` execution context.

## Solution Architecture

### 1. Voice as HIL Question Type

Transform voice recording from a standalone CLI command to a question type within the HIL system:

```
Agent → ask-human.sh --voice → Question File → Listener → Voice UI → Transcription → Answer File → Agent
```

### 2. Question Protocol Extension

```json
{
  "type": "voice",              // New type: "text" | "voice"
  "agent_id": "123_456",
  "timestamp": "2025-01-07T12:00:00Z",
  "prompt": "Describe the issue you're experiencing",
  "timeout": 300,
  "metadata": {
    "max_duration": 30,        // Maximum recording duration in seconds
    "language": "en",          // Transcription language
    "require_confirmation": true,  // Show preview before sending
    "fallback_to_text": true  // Use text input if voice fails
  }
}
```

### 3. Component Changes

#### A. scripts/ask-human.sh

```bash
#!/bin/bash
# Extended to support voice questions

usage() {
    echo "Usage: $0 [--voice] [--duration N] \"question\""
    echo "  --voice      Request voice input instead of text"
    echo "  --duration N Max recording duration (default: 30)"
    exit 1
}

# Parse arguments
QUESTION_TYPE="text"
MAX_DURATION=30
while [[ $# -gt 0 ]]; do
    case $1 in
        --voice)
            QUESTION_TYPE="voice"
            shift
            ;;
        --duration)
            MAX_DURATION="$2"
            shift 2
            ;;
        *)
            QUESTION="$1"
            shift
            ;;
    esac
done

# Create question file with appropriate type
if [ "$QUESTION_TYPE" = "voice" ]; then
    create_voice_question "$QUESTION" "$MAX_DURATION"
else
    create_text_question "$QUESTION"
fi

# Wait for answer (same as before)
wait_for_answer
```

#### B. HIL Listener Enhancement

```python
# src/claude_helpers/hil/listener.py

class QuestionHandler:
    """Handles different types of questions from agents."""
    
    def __init__(self, config: GlobalConfig):
        self.config = config
        self.text_handler = TextQuestionHandler()
        self.voice_handler = VoiceQuestionHandler(config)
    
    def process_question(self, question_file: Path) -> str:
        """Route question to appropriate handler based on type."""
        data = json.loads(question_file.read_text())
        
        if data['type'] == 'voice':
            return self.voice_handler.handle(data)
        else:
            return self.text_handler.handle(data)
```

#### C. Voice Question Handler

```python
# src/claude_helpers/hil/voice_handler.py

class VoiceQuestionHandler:
    """Handles voice recording requests from agents."""
    
    def __init__(self, config: GlobalConfig):
        self.config = config
        self.recorder = CrossPlatformRecorder(
            device_id=config.audio.device_id,
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels
        )
        self.whisper = create_whisper_client(config.openai_api_key)
    
    def handle(self, question_data: dict) -> str:
        """Handle a voice question request."""
        try:
            # Show recording UI
            audio_data = self._record_with_ui(
                prompt=question_data['prompt'],
                max_duration=question_data['metadata'].get('max_duration', 30)
            )
            
            # Transcribe
            result = self.whisper.transcribe_audio(audio_data)
            
            # Preview and edit if requested
            if question_data['metadata'].get('require_confirmation', True):
                final_text = self._preview_and_edit(result.text)
                if final_text is None:
                    return "ERROR: Recording cancelled by user"
                return final_text
            
            return result.text
            
        except Exception as e:
            # Fallback to text if configured
            if question_data['metadata'].get('fallback_to_text', True):
                return self._fallback_to_text(question_data['prompt'])
            else:
                return f"ERROR: Voice recording failed: {e}"
    
    def _preview_and_edit(self, transcription: str) -> Optional[str]:
        """Show transcription preview with edit capability."""
        # Use rich prompt with pre-filled text
        from rich.prompt import Prompt
        
        console.print(Panel(
            transcription,
            title="📝 Transcription Preview",
            border_style="blue"
        ))
        
        edited = Prompt.ask(
            "Press Enter to accept, or type new text",
            default=transcription,
            show_default=False
        )
        
        if edited.strip() == "":
            return None  # User cancelled
        
        return edited
```

### 4. User Experience Flow

1. **Agent requests voice input:**
   ```bash
   !./scripts/ask-human.sh --voice "Please describe the bug"
   ```

2. **Listener shows recording interface:**
   - Rich UI with recording instructions
   - Visual feedback during recording
   - Automatic stop after max duration

3. **Transcription and preview:**
   - Shows transcribed text
   - User can accept (Enter) or edit
   - Edited text becomes the response

4. **Fallback handling:**
   - If voice fails (permissions, API, etc.)
   - Automatically falls back to text input
   - Clear error messages guide user

### 5. Error Handling

#### Voice-specific errors:
- **No microphone permission**: Clear instructions for OS settings
- **API key invalid**: Fallback to text with error message
- **Recording failed**: Retry option or text fallback
- **User cancelled**: Return "ERROR: Cancelled" to agent

#### Fallback chain:
1. Try voice recording
2. If fails, show error and offer text input
3. If text also cancelled, return error to agent

### 6. Configuration

#### Global config additions:
```python
class HILConfig(BaseModel):
    """HIL-specific configuration."""
    
    enable_voice: bool = True
    voice_preview: bool = True
    voice_fallback: bool = True
    default_voice_duration: int = 30
```

### 7. Testing Strategy

1. **Unit tests:**
   - Question routing logic
   - Voice handler with mocked recorder
   - Fallback scenarios

2. **Integration tests:**
   - Full voice flow with test audio
   - Error handling paths
   - Multi-agent scenarios

3. **Manual testing:**
   - Real microphone recording
   - API transcription
   - Preview/edit flow

## Implementation Priority

1. **Phase 1**: Basic voice-HIL integration
   - Extend ask-human.sh with --voice flag
   - Create VoiceQuestionHandler
   - Basic recording without preview

2. **Phase 2**: Enhanced UX
   - Add preview/edit capability
   - Implement fallback to text
   - Rich error messages

3. **Phase 3**: Polish
   - Configuration options
   - Performance optimization
   - Extended testing

## Benefits

1. **Solves non-interactive problem**: Voice works in Claude Code
2. **Unified interface**: One listener for all interactions
3. **Better UX**: Preview and edit capability
4. **Robust**: Automatic fallbacks ensure reliability
5. **Extensible**: Easy to add more interaction types

## Migration Path

1. Keep standalone `claude-helpers voice` for direct CLI use
2. Document new `ask-human.sh --voice` for Claude Code
3. Update CLAUDE.md with voice examples
4. Deprecate standalone usage in Claude Code context