"""Audio device management for Claude Helpers."""

import logging
import platform
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Audio device information."""
    
    id: int
    name: str
    channels: int
    sample_rate: int
    is_default: bool
    platform_info: Dict[str, Any]


@dataclass
class AudioDeviceInfo:
    """Detailed audio device information."""
    
    id: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_sample_rate: float
    default_low_input_latency: float
    default_high_input_latency: float
    default_low_output_latency: float
    default_high_output_latency: float
    host_api: str
    is_default_input: bool
    is_default_output: bool
    platform_specific: Dict[str, Any]


class AudioSystemError(Exception):
    """Base audio system error."""
    pass


class AudioDeviceNotFoundError(AudioSystemError):
    """Audio device not found."""
    pass


class AudioPermissionError(AudioSystemError):
    """Audio permission denied."""
    pass


def _get_sounddevice():
    """Get sounddevice module with error handling."""
    try:
        import sounddevice as sd
        return sd
    except ImportError as e:
        raise AudioSystemError(
            "sounddevice library not available. Please install with:\n"
            "uv add sounddevice"
        ) from e
    except OSError as e:
        # Common on Linux when audio system is not configured
        if "ALSA" in str(e) or "PulseAudio" in str(e):
            raise AudioSystemError(
                "Audio system not properly configured. Please check your audio setup:\n"
                "Linux: Ensure PulseAudio or ALSA is running\n"
                "macOS: Check audio permissions in System Preferences"
            ) from e
        raise AudioSystemError(f"Audio system error: {e}") from e


def list_devices() -> List[AudioDevice]:
    """List all available audio input devices.
    
    Returns:
        List of AudioDevice objects for input devices
        
    Raises:
        AudioSystemError: If audio system is not available
        AudioPermissionError: If microphone access is denied
    """
    try:
        sd = _get_sounddevice()
        
        # Query all devices
        devices = sd.query_devices()
        default_input = sd.default.device[0] if sd.default.device[0] is not None else -1
        
        input_devices = []
        
        for i, device in enumerate(devices):
            # Only include devices with input channels
            if device['max_input_channels'] > 0:
                # Determine if this is the default device
                is_default = (i == default_input)
                
                # Extract platform-specific information
                platform_info = {
                    'host_api': sd.query_hostapis(device['hostapi'])['name'],
                    'max_input_channels': device['max_input_channels'],
                    'max_output_channels': device['max_output_channels'],
                    'default_samplerate': device['default_samplerate'],
                    'default_low_input_latency': device['default_low_input_latency'],
                    'default_high_input_latency': device['default_high_input_latency'],
                }
                
                # Add platform-specific details
                if platform.system() == 'Darwin':
                    # macOS specific info
                    platform_info.update({
                        'coreaudio_device': True,
                        'requires_permission': True
                    })
                elif platform.system() == 'Linux':
                    # Linux specific info  
                    platform_info.update({
                        'audio_system': platform_info['host_api'],
                        'requires_permission': False
                    })
                
                audio_device = AudioDevice(
                    id=i,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=int(device['default_samplerate']),
                    is_default=is_default,
                    platform_info=platform_info
                )
                
                input_devices.append(audio_device)
        
        if not input_devices:
            logger.warning("No input devices found")
            
        return input_devices
        
    except Exception as e:
        if "permission" in str(e).lower() or "authorize" in str(e).lower():
            raise AudioPermissionError(
                "Microphone access denied. Please grant permission:\n"
                "macOS: System Preferences → Security & Privacy → Microphone\n" 
                "Linux: Check user permissions for audio group"
            ) from e
        elif isinstance(e, AudioSystemError):
            raise
        else:
            raise AudioSystemError(f"Failed to list audio devices: {e}") from e


def get_default_device() -> Optional[AudioDevice]:
    """Get the system default input device.
    
    Returns:
        AudioDevice for default input device, or None if not available
        
    Raises:
        AudioSystemError: If audio system is not available
    """
    try:
        devices = list_devices()
        
        # Find device marked as default
        for device in devices:
            if device.is_default:
                return device
        
        # If no explicit default, return first available device
        if devices:
            logger.info("No explicit default device, using first available")
            return devices[0]
            
        return None
        
    except Exception as e:
        if isinstance(e, (AudioSystemError, AudioPermissionError)):
            raise
        else:
            raise AudioSystemError(f"Failed to get default device: {e}") from e


def validate_device(device_id: int) -> bool:
    """Test if an audio device is working and accessible.
    
    Args:
        device_id: Device ID to test
        
    Returns:
        True if device is working, False otherwise
    """
    try:
        sd = _get_sounddevice()
        
        # Check if device exists
        devices = sd.query_devices()
        if device_id < 0 or device_id >= len(devices):
            logger.debug(f"Device ID {device_id} out of range")
            return False
            
        device = devices[device_id]
        
        # Check if device has input channels
        if device['max_input_channels'] <= 0:
            logger.debug(f"Device {device_id} has no input channels")
            return False
        
        # Try to create a test stream
        try:
            # Very short test recording (100ms)
            with sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=44100,
                blocksize=4410,  # 100ms at 44.1kHz
                latency='low'
            ):
                # If we can create the stream, device is working
                pass
            
            logger.debug(f"Device {device_id} test successful")
            return True
            
        except Exception as stream_error:
            logger.debug(f"Device {device_id} stream test failed: {stream_error}")
            return False
            
    except Exception as e:
        logger.debug(f"Device {device_id} test error: {e}")
        return False


def get_device_info(device_id: int) -> AudioDeviceInfo:
    """Get detailed information about a specific audio device.
    
    Args:
        device_id: Device ID to query
        
    Returns:
        AudioDeviceInfo with detailed device information
        
    Raises:
        AudioDeviceNotFoundError: If device ID is invalid
        AudioSystemError: If audio system is not available
    """
    try:
        sd = _get_sounddevice()
        
        # Check if device exists
        devices = sd.query_devices()
        if device_id < 0 or device_id >= len(devices):
            raise AudioDeviceNotFoundError(f"Device ID {device_id} not found")
            
        device = devices[device_id]
        host_api = sd.query_hostapis(device['hostapi'])
        
        # Check for default devices
        default_input = sd.default.device[0] if sd.default.device[0] is not None else -1
        default_output = sd.default.device[1] if sd.default.device[1] is not None else -1
        
        # Platform-specific information
        platform_specific = {
            'host_api_name': host_api['name'],
            'system': platform.system(),
        }
        
        if platform.system() == 'Darwin':
            platform_specific.update({
                'coreaudio_device': True,
                'permission_required': True,
                'audio_unit_available': True
            })
        elif platform.system() == 'Linux':
            platform_specific.update({
                'audio_backend': host_api['name'],
                'permission_required': False,
                'pulse_available': 'pulse' in host_api['name'].lower(),
                'alsa_available': 'alsa' in host_api['name'].lower()
            })
        
        return AudioDeviceInfo(
            id=device_id,
            name=device['name'],
            max_input_channels=device['max_input_channels'],
            max_output_channels=device['max_output_channels'],
            default_sample_rate=device['default_samplerate'],
            default_low_input_latency=device['default_low_input_latency'],
            default_high_input_latency=device['default_high_input_latency'],
            default_low_output_latency=device['default_low_output_latency'],
            default_high_output_latency=device['default_high_output_latency'],
            host_api=host_api['name'],
            is_default_input=(device_id == default_input),
            is_default_output=(device_id == default_output),
            platform_specific=platform_specific
        )
        
    except AudioDeviceNotFoundError:
        raise
    except Exception as e:
        if isinstance(e, AudioSystemError):
            raise
        else:
            raise AudioSystemError(f"Failed to get device info: {e}") from e


def get_recommended_settings(device_id: Optional[int] = None) -> Dict[str, Any]:
    """Get recommended audio settings for voice recording.
    
    Args:
        device_id: Specific device ID, or None for default device
        
    Returns:
        Dictionary with recommended settings
    """
    try:
        # Default settings optimized for OpenAI Whisper
        settings = {
            'sample_rate': 44100,  # Whisper's preferred sample rate
            'channels': 1,         # Mono for transcription
            'dtype': 'float32',    # Standard floating point format
            'blocksize': 4410,     # 100ms blocks for low latency
            'latency': 'low'       # Minimize recording latency
        }
        
        # If specific device requested, get its optimal settings
        if device_id is not None:
            try:
                device_info = get_device_info(device_id)
                
                # Adjust sample rate if device doesn't support 44.1kHz well
                if device_info.default_sample_rate != 44100:
                    logger.info(f"Device prefers {device_info.default_sample_rate}Hz, but using 44100Hz for Whisper compatibility")
                
                # Adjust latency based on device capabilities
                if device_info.default_low_input_latency > 0.1:  # > 100ms
                    settings['latency'] = 'high'
                    logger.info("Using high latency mode for device compatibility")
                
            except Exception as e:
                logger.warning(f"Could not get device-specific settings: {e}")
        
        return settings
        
    except Exception as e:
        logger.warning(f"Error getting recommended settings: {e}")
        # Return safe defaults
        return {
            'sample_rate': 44100,
            'channels': 1,
            'dtype': 'float32',
            'blocksize': 4410,
            'latency': 'low'
        }