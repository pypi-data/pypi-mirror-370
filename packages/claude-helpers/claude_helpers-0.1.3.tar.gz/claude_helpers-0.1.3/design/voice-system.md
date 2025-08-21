# Claude Helpers - Voice System Design

## Overview

Voice input system that records audio and outputs transcription directly to Claude Code via `!claude-helpers voice` command.

## Usage Pattern

```bash
# In Claude Code
!claude-helpers voice
# User speaks, recording starts
# User presses ESC to stop  
# Transcribed text appears in chat as next prompt
```

## Implementation Flow

1. **Config Check**: Verify global configuration exists (fail with helpful message if not)
2. **Audio Setup**: Initialize recording from default/configured microphone
3. **User Interface**: Show status "Recording... Press ESC to stop" to stderr
4. **Recording**: Capture audio until ESC pressed
5. **Transcription**: Send audio to OpenAI Whisper API
6. **Output**: Print transcription to stdout (becomes Claude prompt)
7. **Cleanup**: Exit cleanly

## Core Components

### Voice Command Entry Point
```python
# src/claude_helpers/voice.py
import sys
from pathlib import Path
import numpy as np
import sounddevice as sd
from .audio.recorder import CrossPlatformRecorder
from .transcription.openai_client import WhisperClient
from .config import load_config, check_config

def voice_command():
    """Record audio and output transcription"""
    # Check config exists
    if not check_config():
        print("ERROR: Global configuration not found.", file=sys.stderr)
        print("Please run: claude-helpers init", file=sys.stderr)
        sys.exit(1)
    
    config = load_config()
    
    # Status to stderr (visible but not in prompt)
    print("Recording... Press ESC to stop", file=sys.stderr)
    
    # Record audio
    recorder = CrossPlatformRecorder(
        sample_rate=config.audio.sample_rate,
        device_id=config.audio.device_id
    )
    audio_data = recorder.record_until_esc()
    
    if len(audio_data) == 0:
        print("No audio recorded", file=sys.stderr)
        return
    
    # Transcribe
    print("Transcribing...", file=sys.stderr)
    client = WhisperClient(api_key=config.openai_api_key)
    text = client.transcribe(audio_data, config.audio.sample_rate)
    
    # Output to stdout (becomes Claude prompt)
    print(text)
```

### Cross-Platform Audio Recording
```python
# src/claude_helpers/audio/recorder.py
import platform
import keyboard
import sounddevice as sd
import numpy as np
import sys

class CrossPlatformRecorder:
    def __init__(self, sample_rate=44100, device_id=None):
        self.sample_rate = sample_rate
        self.device_id = device_id
        self.frames = []
        self.recording = True
        self.platform = platform.system().lower()
        
    def record_until_esc(self) -> np.ndarray:
        """Record until ESC pressed - works on Linux and macOS"""
        def callback(indata, frames, time, status):
            if self.recording:
                self.frames.append(indata.copy())
        
        # Platform-specific setup
        if self.platform == 'darwin':  # macOS
            self._request_macos_permissions()
        
        # Start recording
        with sd.InputStream(
            callback=callback,
            samplerate=self.sample_rate,
            channels=1,
            device=self.device_id,
            dtype='float32'
        ):
            try:
                # Wait for ESC - works on both platforms
                keyboard.wait('esc')
            except Exception as e:
                # Fallback for permission issues
                print(f"Keyboard access issue: {e}", file=sys.stderr)
                input("Press Enter to stop recording...")
            finally:
                self.recording = False
        
        # Return concatenated audio
        if self.frames:
            return np.concatenate(self.frames, axis=0)
        return np.array([])
    
    def _request_macos_permissions(self):
        """Request microphone permissions on macOS"""
        try:
            # Test microphone access
            test_record = sd.rec(int(0.1 * self.sample_rate), 
                               samplerate=self.sample_rate, 
                               channels=1, 
                               device=self.device_id)
            sd.wait()
        except Exception:
            print("Microphone permission required on macOS", file=sys.stderr)
            print("Please grant permission in System Preferences > Security & Privacy > Microphone", file=sys.stderr)
```

### Audio Device Management
```python
# src/claude_helpers/audio/devices.py
import sounddevice as sd
from typing import List, Dict, Optional

def list_devices() -> List[Dict]:
    """List available audio input devices"""
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append({
                'id': i,
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate'],
                'hostapi': device['hostapi']
            })
    
    return input_devices

def get_default_device() -> Optional[int]:
    """Get default input device ID"""
    try:
        return sd.default.device[0]  # Input device
    except Exception:
        devices = list_devices()
        return devices[0]['id'] if devices else None

def test_device(device_id: Optional[int] = None) -> bool:
    """Test if audio device works"""
    try:
        # Short test recording
        test_duration = 0.1  # 100ms
        test_recording = sd.rec(
            int(test_duration * 44100), 
            samplerate=44100, 
            channels=1, 
            device=device_id,
            dtype='float32'
        )
        sd.wait()
        
        # Check if we got audio data
        return len(test_recording) > 0 and test_recording.max() > 0
    except Exception:
        return False
```

### OpenAI Whisper Integration
```python
# src/claude_helpers/transcription/openai_client.py
import numpy as np
import io
from scipy.io.wavfile import write
from openai import OpenAI
from typing import Optional

class WhisperClient:
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 44100, 
                   language: Optional[str] = None) -> str:
        """Transcribe audio data to text"""
        
        # Convert numpy array to WAV bytes
        wav_bytes = self._numpy_to_wav(audio_data, sample_rate)
        
        # Prepare file-like object
        audio_file = io.BytesIO(wav_bytes)
        audio_file.name = "audio.wav"  # OpenAI requires a name
        
        try:
            # Send to OpenAI Whisper
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="text"
            )
            
            return response.strip()
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def _numpy_to_wav(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array to WAV file bytes"""
        # Ensure audio_data is in the right format
        if audio_data.ndim == 2:
            audio_data = audio_data.flatten()
        
        # Convert to int16 for WAV
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        write(wav_buffer, sample_rate, audio_int16)
        wav_bytes = wav_buffer.getvalue()
        wav_buffer.close()
        
        return wav_bytes
```

## Configuration Integration

### Audio Configuration
```json
{
  "audio": {
    "device_id": null,        // null = default device
    "sample_rate": 44100,
    "channels": 1
  }
}
```

### Device Selection in Init
```python
# During claude-helpers init
from claude_helpers.audio.devices import list_devices, test_device

devices = list_devices()

if len(devices) > 1:
    click.echo("\nAvailable audio input devices:")
    for i, device in enumerate(devices):
        working = "✓" if test_device(device['id']) else "✗"
        click.echo(f"  {i}: {device['name']} {working}")
    
    device_id = click.prompt(
        "Select device number (or Enter for default)",
        type=int,
        default=-1,
        show_default=False
    )
    
    if device_id >= 0 and device_id < len(devices):
        config.setdefault('audio', {})['device_id'] = devices[device_id]['id']
```

## Error Handling

### Configuration Errors
- **No global config**: Clear error message with init instruction
- **Missing API key**: Check format, suggest re-init
- **Invalid config**: Validation with helpful error messages

### Audio Errors  
- **No microphone**: List available devices, prompt to reconfigure
- **Device busy**: Suggest closing other audio applications
- **Permission denied** (macOS): Guide to System Preferences

### Network Errors
- **API failure**: Save audio locally as backup with retry option
- **Rate limit**: Implement exponential backoff
- **Invalid API key**: Clear error message with re-init suggestion

### Transcription Errors
- **Empty result**: Handle gracefully with fallback message
- **API timeout**: Retry mechanism with user notification
- **Audio too short/long**: Validate duration before sending

## Platform-Specific Considerations

### macOS
- **Microphone permissions**: Automatic detection and user guidance
- **Audio device handling**: CoreAudio integration via sounddevice
- **Keyboard access**: Handle permission requirements gracefully

### Linux
- **Audio systems**: Support PulseAudio, ALSA, JACK via sounddevice
- **Keyboard access**: Option to avoid sudo requirement
- **Device enumeration**: Handle different audio subsystems

## Testing Strategy

### Unit Tests
- Audio device enumeration
- Configuration validation
- Numpy-to-WAV conversion
- Mock OpenAI API responses

### Integration Tests
- End-to-end voice flow with test audio files
- Cross-platform device detection
- Error scenarios and recovery

### Manual Testing
- Different microphones and audio devices
- Network interruptions during transcription
- Permission scenarios on macOS