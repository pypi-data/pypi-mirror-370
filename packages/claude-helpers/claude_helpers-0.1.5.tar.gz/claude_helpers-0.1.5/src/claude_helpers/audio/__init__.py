"""Audio system for Claude Helpers."""

from .devices import AudioDevice, AudioDeviceInfo, list_devices, get_default_device, validate_device, get_device_info
from .recorder import CrossPlatformRecorder, RecordingSession, RecordingError, DeviceError, StreamError, create_recorder_for_transcription, get_recording_quality_info

__all__ = [
    # Device management
    'AudioDevice',
    'AudioDeviceInfo', 
    'list_devices',
    'get_default_device',
    'validate_device',
    'get_device_info',
    
    # Recording
    'CrossPlatformRecorder',
    'RecordingSession',
    'RecordingError',
    'DeviceError', 
    'StreamError',
    'create_recorder_for_transcription',
    'get_recording_quality_info',
]