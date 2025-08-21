"""Cross-platform audio recorder for Claude Helpers."""

import logging
import threading
import time
from typing import Optional, Callable
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RecordingSession:
    """Information about a recording session."""
    
    duration: float
    sample_rate: int
    channels: int
    samples: int
    device_id: Optional[int] = None
    device_name: Optional[str] = None


class RecordingError(Exception):
    """Base recording error."""
    pass


class DeviceError(RecordingError):
    """Device related recording error."""
    pass


class StreamError(RecordingError):
    """Audio stream error."""
    pass


class CrossPlatformRecorder:
    """Cross-platform audio recorder optimized for voice transcription.
    
    Features:
    - 44.1kHz sample rate (OpenAI Whisper optimal)
    - Mono recording for transcription
    - Low latency streaming capture
    - Real-time volume monitoring
    - Memory efficient buffering
    """
    
    def __init__(
        self,
        device_id: Optional[int] = None,
        sample_rate: int = 44100,
        channels: int = 1,
        dtype: str = 'float32'
    ):
        """Initialize recorder with device and quality settings.
        
        Args:
            device_id: Specific device ID, None for default
            sample_rate: Recording sample rate (Hz)
            channels: Number of channels (1 for mono, 2 for stereo)
            dtype: NumPy data type for audio samples
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        
        # Recording state
        self._recording = False
        self._stream = None
        self._audio_data = []
        self._start_time = None
        self._lock = threading.Lock()
        
        # Volume monitoring
        self._current_volume = 0.0
        self._volume_callback: Optional[Callable[[float], None]] = None
        
        # Validate settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate recording settings."""
        if self.sample_rate < 8000 or self.sample_rate > 96000:
            raise RecordingError(f"Invalid sample rate: {self.sample_rate}. Must be between 8000-96000 Hz")
        
        if self.channels < 1 or self.channels > 2:
            raise RecordingError(f"Invalid channels: {self.channels}. Must be 1 (mono) or 2 (stereo)")
        
        if self.dtype not in ['float32', 'int16', 'int32']:
            raise RecordingError(f"Invalid dtype: {self.dtype}. Must be 'float32', 'int16', or 'int32'")
    
    def _get_sounddevice(self):
        """Get sounddevice module with error handling."""
        try:
            import sounddevice as sd
            return sd
        except ImportError as e:
            raise RecordingError(
                "sounddevice library not available. Please install with: uv add sounddevice"
            ) from e
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio stream.
        
        This is called by sounddevice in a separate thread.
        """
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Calculate volume level (RMS)
        if len(indata) > 0:
            volume = float(np.sqrt(np.mean(indata**2)))
            with self._lock:
                self._current_volume = min(volume * 10, 1.0)  # Scale and clamp to [0,1]
            
            # Call volume callback if set
            if self._volume_callback:
                try:
                    self._volume_callback(self._current_volume)
                except Exception as e:
                    logger.warning(f"Volume callback error: {e}")
        
        # Store audio data
        if self._recording:
            with self._lock:
                self._audio_data.append(indata.copy())
    
    def start_recording(self) -> None:
        """Start audio recording session.
        
        Raises:
            RecordingError: If recording cannot be started
            DeviceError: If audio device is not available
        """
        if self._recording:
            raise RecordingError("Recording is already in progress")
        
        try:
            sd = self._get_sounddevice()
            
            # Validate device if specified
            if self.device_id is not None:
                devices = sd.query_devices()
                if self.device_id < 0 or self.device_id >= len(devices):
                    raise DeviceError(f"Device ID {self.device_id} not found")
                
                device = devices[self.device_id]
                if device['max_input_channels'] < self.channels:
                    raise DeviceError(
                        f"Device {self.device_id} supports {device['max_input_channels']} input channels, "
                        f"but {self.channels} requested"
                    )
            
            # Clear previous recording data
            with self._lock:
                self._audio_data = []
                self._current_volume = 0.0
            
            # Calculate optimal blocksize for low latency
            # Aim for ~100ms blocks which is good balance between latency and efficiency
            blocksize = int(self.sample_rate * 0.1)  # 100ms
            
            # Create and start audio stream
            self._stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=self.dtype,
                blocksize=blocksize,
                latency='low',
                callback=self._audio_callback
            )
            
            # Start recording
            self._stream.start()
            self._recording = True
            self._start_time = time.time()
            
            logger.info(f"Started recording: device={self.device_id}, "
                       f"rate={self.sample_rate}Hz, channels={self.channels}")
            
        except Exception as e:
            self._recording = False
            if self._stream:
                try:
                    self._stream.close()
                except:
                    pass
                self._stream = None
            
            if "permission" in str(e).lower() or "authorize" in str(e).lower():
                raise DeviceError(
                    "Microphone access denied. Please grant permission:\n"
                    "macOS: System Preferences → Security & Privacy → Microphone\n"
                    "Linux: Check user permissions for audio group"
                ) from e
            elif "device" in str(e).lower():
                raise DeviceError(f"Audio device error: {e}") from e
            else:
                raise RecordingError(f"Failed to start recording: {e}") from e
    
    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data.
        
        Returns:
            NumPy array with recorded audio data
            
        Raises:
            RecordingError: If no recording is in progress
        """
        if not self._recording:
            raise RecordingError("No recording in progress")
        
        try:
            # Stop recording
            self._recording = False
            
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            
            # Combine all audio chunks
            with self._lock:
                if not self._audio_data:
                    logger.warning("No audio data recorded")
                    return np.array([], dtype=self.dtype)
                
                # Concatenate all chunks
                audio_array = np.concatenate(self._audio_data, axis=0)
                
                # If stereo but we want mono, convert to mono
                if audio_array.ndim == 2 and self.channels == 1 and audio_array.shape[1] > 1:
                    audio_array = np.mean(audio_array, axis=1, keepdims=False)
                
                # Ensure correct shape for mono
                if self.channels == 1 and audio_array.ndim == 2:
                    audio_array = audio_array.flatten()
            
            logger.info(f"Recording stopped. Captured {len(audio_array)} samples "
                       f"({len(audio_array) / self.sample_rate:.2f} seconds)")
            
            return audio_array
            
        except Exception as e:
            self._recording = False
            if self._stream:
                try:
                    self._stream.close()
                except:
                    pass
                self._stream = None
            raise RecordingError(f"Failed to stop recording: {e}") from e
    
    def get_recording_duration(self) -> float:
        """Get current recording duration in seconds.
        
        Returns:
            Duration in seconds, or 0.0 if not recording
        """
        if not self._recording or self._start_time is None:
            return 0.0
        
        return time.time() - self._start_time
    
    def is_recording(self) -> bool:
        """Check if currently recording.
        
        Returns:
            True if recording is in progress
        """
        return self._recording
    
    def get_volume_level(self) -> float:
        """Get current input volume level.
        
        Returns:
            Volume level normalized to 0.0-1.0 range
        """
        with self._lock:
            return self._current_volume
    
    def set_volume_callback(self, callback: Optional[Callable[[float], None]]):
        """Set callback function for real-time volume updates.
        
        Args:
            callback: Function that receives volume level (0.0-1.0), or None to disable
        """
        self._volume_callback = callback
    
    def get_session_info(self) -> Optional[RecordingSession]:
        """Get information about current/last recording session.
        
        Returns:
            RecordingSession with session details, or None if no session
        """
        if not self._start_time:
            return None
        
        duration = self.get_recording_duration()
        samples = len(self._audio_data) * (
            self._audio_data[0].shape[0] if self._audio_data else 0
        )
        
        # Get device name if available
        device_name = None
        if self.device_id is not None:
            try:
                sd = self._get_sounddevice()
                devices = sd.query_devices()
                if self.device_id < len(devices):
                    device_name = devices[self.device_id]['name']
            except:
                pass
        
        return RecordingSession(
            duration=duration,
            sample_rate=self.sample_rate,
            channels=self.channels,
            samples=samples,
            device_id=self.device_id,
            device_name=device_name
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure recording is stopped."""
        if self._recording:
            try:
                self.stop_recording()
            except Exception as e:
                logger.error(f"Error stopping recording in context manager: {e}")
        
        if self._stream:
            try:
                self._stream.close()
            except Exception as e:
                logger.error(f"Error closing stream in context manager: {e}")


def create_recorder_for_transcription(device_id: Optional[int] = None) -> CrossPlatformRecorder:
    """Create recorder optimized for OpenAI Whisper transcription.
    
    Args:
        device_id: Specific device ID, None for default
        
    Returns:
        CrossPlatformRecorder with optimal settings for transcription
    """
    return CrossPlatformRecorder(
        device_id=device_id,
        sample_rate=44100,  # Whisper's preferred sample rate
        channels=1,         # Mono for transcription
        dtype='float32'     # Standard floating point
    )


def get_recording_quality_info(sample_rate: int, channels: int, duration: float) -> dict:
    """Get information about recording quality and suitability for transcription.
    
    Args:
        sample_rate: Recording sample rate
        channels: Number of channels
        duration: Recording duration in seconds
        
    Returns:
        Dictionary with quality assessment
    """
    quality_info = {
        'sample_rate': sample_rate,
        'channels': channels,
        'duration': duration,
        'whisper_optimal': False,
        'transcription_suitable': False,
        'recommendations': []
    }
    
    # Check Whisper optimization
    if sample_rate == 44100 and channels == 1:
        quality_info['whisper_optimal'] = True
    else:
        if sample_rate != 44100:
            quality_info['recommendations'].append(f"Consider 44.1kHz sample rate (current: {sample_rate}Hz)")
        if channels != 1:
            quality_info['recommendations'].append(f"Consider mono recording (current: {channels} channels)")
    
    # Check transcription suitability
    if sample_rate >= 16000 and duration >= 0.1:  # Minimum requirements
        quality_info['transcription_suitable'] = True
    else:
        if sample_rate < 16000:
            quality_info['recommendations'].append("Sample rate too low for good transcription (minimum 16kHz)")
        if duration < 0.1:
            quality_info['recommendations'].append("Recording too short for transcription")
    
    # Duration recommendations
    if duration > 60:
        quality_info['recommendations'].append("Long recordings may take time to transcribe")
    elif duration < 1:
        quality_info['recommendations'].append("Very short recordings may not transcribe well")
    
    return quality_info