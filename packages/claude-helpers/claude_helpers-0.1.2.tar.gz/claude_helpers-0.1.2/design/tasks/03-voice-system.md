# Epic 3: 🎤 Voice System

**Priority**: HIGH - Core feature (can develop parallel with Dialog)
**Estimated Time**: 5-6 days
**Dependencies**: Epic 1 (Foundation), Epic 2 (Configuration)

## Overview

Реализация системы записи аудио, device management, и OpenAI Whisper интеграции. Это независимая feature система которая может разрабатываться параллельно с Dialog System.

## Definition of Done

- [ ] Audio recording работает на обеих платформах
- [ ] Device enumeration и selection функциональны
- [ ] OpenAI Whisper интеграция стабильна
- [ ] Voice command выводит transcription в stdout
- [ ] Error handling для audio и network issues
- [ ] Cross-platform audio permissions обрабатываются
- [ ] Audio quality optimization реализована

---

## Task 3.1: Audio Device Management
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать систему для enumeration, selection и testing audio devices

### Deliverables
- `src/claude_helpers/audio/devices.py` с device management
- Cross-platform device detection
- Default device selection logic
- Device testing functionality

### Core Functions
```python
def list_devices() -> List[AudioDevice]:
    """List all available input devices"""

def get_default_device() -> Optional[AudioDevice]:
    """Get system default input device"""

def test_device(device_id: int) -> bool:
    """Test if device is working and accessible"""

def get_device_info(device_id: int) -> AudioDeviceInfo:
    """Get detailed device information"""

@dataclass
class AudioDevice:
    id: int
    name: str
    channels: int
    sample_rate: int
    is_default: bool
    platform_info: dict
```

### Platform Considerations
- **macOS**: Микрофон permissions требуют user approval
- **Linux**: PulseAudio vs ALSA detection
- **Both**: USB device hotplug detection

### Acceptance Criteria
- Все input devices корректно перечислены
- Default device detection работает на обеих платформах
- Device testing не вызывает system hangs
- Permission errors handled gracefully
- USB device changes обнаруживаются

### Test Commands
```python
from claude_helpers.audio.devices import list_devices, get_default_device, test_device

devices = list_devices()
assert len(devices) > 0, "Should find at least one input device"

default = get_default_device()
if default:
    assert test_device(default.id), "Default device should be testable"

# Test with invalid device ID
assert not test_device(99999), "Invalid device should fail test"
```

---

## Task 3.2: Cross-Platform Audio Recorder
**Time**: 2 days | **Complexity**: 🔴 High

### Описание
Реализовать CrossPlatformRecorder для stable audio recording

### Deliverables
- `src/claude_helpers/audio/recorder.py` с unified recording interface
- Platform-specific optimizations
- Recording quality management
- Memory efficient audio buffering

### Core Implementation
```python
class CrossPlatformRecorder:
    def __init__(self, device_id: Optional[int] = None, 
                 sample_rate: int = 44100, channels: int = 1):
        """Initialize recorder with device and quality settings"""
    
    def start_recording(self) -> None:
        """Start audio recording session"""
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data"""
    
    def get_recording_duration(self) -> float:
        """Get current recording duration in seconds"""
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
    
    def get_volume_level(self) -> float:
        """Get current input volume level (0-1)"""
```

### Technical Requirements
- **Sample Rate**: 44100 Hz (OpenAI Whisper optimal)
- **Channels**: Mono (1 channel) for transcription
- **Format**: 16-bit PCM for compatibility
- **Buffering**: Streaming capture for memory efficiency
- **Latency**: < 100ms recording start time

### Platform-Specific Features
- **macOS**: CoreAudio integration, permission handling
- **Linux**: PulseAudio/ALSA fallback, different audio servers
- **Both**: USB device reconnection, sample rate conversion

### Acceptance Criteria
- Recording starts within 100ms
- Audio качество подходит для transcription
- Memory usage остается stable during long recordings
- Device disconnection handled gracefully
- No audio dropouts или corruption
- Volume level monitoring функциональный

### Test Commands
```python
from claude_helpers.audio.recorder import CrossPlatformRecorder

recorder = CrossPlatformRecorder()
recorder.start_recording()
# Record for 2 seconds
import time
time.sleep(2)
audio_data = recorder.stop_recording()

assert len(audio_data) > 0, "Should capture audio data"
assert recorder.get_recording_duration() >= 1.9, "Should record for ~2 seconds"
assert 0 <= recorder.get_volume_level() <= 1, "Volume level should be normalized"
```

---

## Task 3.3: OpenAI Whisper Client
**Time**: 1.5 days | **Complexity**: 🟡 Medium

### Описание
Создать WhisperClient для audio transcription via OpenAI API

### Deliverables
- `src/claude_helpers/transcription/openai_client.py`
- Audio format conversion для API compatibility
- Error handling и retry logic
- Rate limiting и optimization

### Core Implementation
```python
class WhisperClient:
    def __init__(self, api_key: str):
        """Initialize OpenAI client with API key"""
    
    def transcribe_audio(self, audio_data: np.ndarray, 
                        sample_rate: int = 44100,
                        language: Optional[str] = None) -> TranscriptionResult:
        """Transcribe audio data and return result"""
    
    def transcribe_file(self, file_path: Path) -> TranscriptionResult:
        """Transcribe audio file directly"""
    
    def test_api_key(self) -> bool:
        """Test if API key is valid"""

@dataclass
class TranscriptionResult:
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[float] = None
    word_timestamps: Optional[List[dict]] = None
```

### Audio Processing Features
- Convert numpy array to WAV format for API
- Audio compression для faster uploads
- Silence detection и trimming
- Audio quality validation

### Error Handling
- **Network Issues**: Retry with exponential backoff
- **API Limits**: Rate limiting with proper delays
- **Invalid Audio**: Clear error messages
- **Authentication**: API key validation

### Optimization Features
- Audio preprocessing для better accuracy
- Language detection hints
- Timeout management для long files
- Response caching (optional)

### Acceptance Criteria
- Transcription accuracy suitable для Claude interaction
- API errors handled gracefully с helpful messages
- Network issues не crash приложение
- Audio processing optimized для speed
- Rate limiting respected для API terms

### Test Commands
```python
from claude_helpers.transcription.openai_client import WhisperClient
from claude_helpers.config import load_config

config = load_config()
client = WhisperClient(config.openai_api_key)

# Test API key
assert client.test_api_key(), "API key should be valid"

# Test transcription with sample audio
# Note: In real tests, use mock responses
import numpy as np
sample_audio = np.random.randn(44100)  # 1 second of noise
result = client.transcribe_audio(sample_audio)
assert isinstance(result.text, str), "Should return transcription text"
```

---

## Task 3.4: Voice Recording UI/UX
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Создать user-friendly interface для voice recording process

### Deliverables
- Interactive recording prompts с visual feedback
- Keyboard controls для start/stop recording
- Real-time volume level indicators
- Recording duration display
- Rich CLI output с progress indicators

### UI Features
```python
class VoiceRecordingUI:
    def __init__(self, console: Console):
        """Initialize with Rich console for output"""
    
    def show_recording_prompt(self) -> None:
        """Display recording instructions"""
    
    def start_recording_display(self) -> None:
        """Show recording in progress interface"""
    
    def update_recording_status(self, duration: float, volume: float) -> None:
        """Update real-time recording status"""
    
    def show_transcription_progress(self) -> None:
        """Display transcription API call progress"""
    
    def display_result(self, transcription: str) -> None:
        """Show final transcription result"""
```

### Interactive Elements
- **Start Recording**: Space bar или Enter
- **Stop Recording**: Space bar или Enter again
- **Cancel**: Ctrl+C graceful cancel
- **Volume Meter**: Real-time audio level bar
- **Timer**: Recording duration display
- **Status**: Clear status messages

### Visual Design (Rich CLI)
```
┌─ Voice Recording ─────────────────────────────┐
│                                               │
│  🎤 Recording in progress...                  │
│                                               │
│  Duration: 00:05                             │
│  Volume:   ████████░░ 80%                    │
│                                               │
│  Press SPACE to stop recording               │
│                                               │
└───────────────────────────────────────────────┘
```

### Acceptance Criteria
- Recording controls интуитивные и responsive
- Volume meter updates в real-time
- Duration display accurate
- Error states показаны clearly
- Transcription progress visible
- Final result formatted properly

### Test Commands
```bash
# Manual testing required
claude-helpers voice
# Should show interactive recording interface
# Test all keyboard controls
# Verify visual feedback works
```

---

## Task 3.5: Voice Command Integration
**Time**: 1 day | **Complexity**: 🟡 Medium

### Описание
Интегрировать все voice components в unified voice command

### Deliverables
- `src/claude_helpers/voice.py` main entry point
- Configuration integration
- Error handling workflow
- Output formatting для Claude Code

### Main Voice Function
```python
def voice_command() -> None:
    """Main voice command entry point"""
    config = load_config_with_env_override()
    
    try:
        # Initialize components
        ui = VoiceRecordingUI(console)
        recorder = CrossPlatformRecorder(
            device_id=config.audio.device_id,
            sample_rate=config.audio.sample_rate,
            channels=config.audio.channels
        )
        whisper = WhisperClient(config.openai_api_key)
        
        # Execute recording workflow
        ui.show_recording_prompt()
        audio_data = record_with_ui_feedback(recorder, ui)
        
        ui.show_transcription_progress()
        result = whisper.transcribe_audio(audio_data, config.audio.sample_rate)
        
        # Output to stdout for Claude Code
        print(result.text)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Recording cancelled by user[/yellow]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]", file=sys.stderr)
        sys.exit(1)

def record_with_ui_feedback(recorder: CrossPlatformRecorder, 
                           ui: VoiceRecordingUI) -> np.ndarray:
    """Record audio with real-time UI updates"""
```

### Error Handling Scenarios
1. **No microphone available**
2. **Permission denied**
3. **API key invalid/expired**
4. **Network connectivity issues**
5. **Audio recording failures**
6. **Transcription service errors**

### Output Requirements
- **Success**: Transcribed text to stdout (для Claude Code prompt)
- **Errors**: Helpful error messages to stderr
- **User Feedback**: Rich UI to stderr (не влияет на Claude output)

### Integration Points
- Configuration system для device settings
- Platform detection для audio system selection
- Error handling с proper exit codes
- Logging для debugging issues

### Acceptance Criteria
- Voice command завершается с proper exit codes
- Transcription выводится clean в stdout
- Error messages helpful и actionable
- Configuration settings respected
- All error scenarios handled gracefully

### Test Commands
```bash
# Test successful voice transcription
claude-helpers voice
# Should record, transcribe, and output text

# Test with invalid API key
export OPENAI_API_KEY="invalid"
claude-helpers voice
# Should show clear error message

# Test with no microphone (mock test)
# Should handle gracefully with helpful error
```

---

## Task 3.6: Voice System Error Handling
**Time**: 0.5 day | **Complexity**: 🟢 Low

### Описание
Comprehensive error handling для всех voice system components

### Deliverables
- Custom exception classes для voice-specific errors
- Error recovery mechanisms
- User guidance для common issues
- Debug logging для troubleshooting

### Custom Exceptions
```python
class VoiceError(Exception):
    """Base voice system error"""

class AudioDeviceError(VoiceError):
    """Audio device related errors"""

class RecordingError(VoiceError):
    """Recording process errors"""

class TranscriptionError(VoiceError):
    """API transcription errors"""

class AudioPermissionError(VoiceError):
    """Permission denied for microphone access"""
```

### Error Recovery Strategies
1. **Device Issues**: Try alternative devices
2. **Permission Issues**: Guide user через permission setup
3. **Network Issues**: Retry with backoff
4. **API Issues**: Clear troubleshooting steps
5. **Audio Quality**: Recording tips и suggestions

### User Guidance Messages
```python
ERROR_MESSAGES = {
    'no_microphone': """
No microphone devices found.
Please ensure a microphone is connected and try again.
On macOS: Check System Preferences → Security & Privacy → Microphone
On Linux: Check audio settings and permissions
""",
    'api_key_invalid': """
OpenAI API key appears to be invalid.
Please run: claude-helpers init --global-only
Or set environment variable: export OPENAI_API_KEY="your-key"
""",
    'network_error': """
Network connection failed. Please check your internet connection.
If you're behind a proxy, configure it in your system settings.
""",
}
```

### Acceptance Criteria
- All error scenarios имеют appropriate exceptions
- Error messages include actionable solutions
- Debug logging available для troubleshooting
- Recovery mechanisms work где possible
- Error handling не crash CLI unexpectedly

### Test Commands
```python
# Test various error conditions
from claude_helpers.voice import voice_command
import pytest

# Mock various error scenarios and verify proper handling
def test_no_microphone_error():
    # Mock no devices available
    with pytest.raises(AudioDeviceError):
        # Test error handling
        pass

def test_invalid_api_key():
    # Mock invalid API key
    with pytest.raises(TranscriptionError):
        # Test API error handling
        pass
```

---

## Epic 3 Completion Criteria

### Must Have
- [x] Audio recording stable на обеих платформах
- [x] OpenAI Whisper integration functional
- [x] Voice command outputs clean transcription
- [x] All error scenarios handled appropriately
- [x] User experience intuitive и responsive
- [x] Configuration integration working
- [x] Cross-platform audio permissions handled

### Success Metrics
- Recording latency: < 100ms to start
- Transcription accuracy: > 90% for clear speech
- API response time: < 10 seconds for 30-second clips
- Error recovery rate: > 80% of common issues
- User satisfaction: Clear feedback and guidance

### Integration Points
- **Configuration System**: Uses audio settings from global config
- **Dialog System**: Independent - но can show error dialogs
- **HIL System**: Voice transcription может be used в HIL workflows

### Handoff to Next Epics
После Epic 3, Voice System ready для integration:

1. **Independent Usage**: `!claude-helpers voice` works standalone
2. **Dialog Integration**: Can use dialogs для error handling (Epic 4)
3. **HIL Integration**: Voice может be used для responses (Epic 5)

**Parallel Development**: Epic 4 (Dialog System) может develop одновременно с Epic 3.

**Next Steps**: Epic 5 (HIL System) может start после completion Epic 3 и Epic 4.