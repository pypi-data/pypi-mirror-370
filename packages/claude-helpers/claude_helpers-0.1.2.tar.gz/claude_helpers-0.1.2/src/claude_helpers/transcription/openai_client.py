"""OpenAI Whisper client for audio transcription."""

import io
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    
    text: str
    language: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[float] = None
    word_timestamps: Optional[List[Dict[str, Any]]] = None
    processing_time: Optional[float] = None


class TranscriptionError(Exception):
    """Base transcription error."""
    pass


class NetworkError(TranscriptionError):
    """Network-related transcription error."""
    pass


class APIError(TranscriptionError):
    """OpenAI API error."""
    pass


class AudioFormatError(TranscriptionError):
    """Audio format error."""
    pass


class WhisperClient:
    """OpenAI Whisper API client for audio transcription.
    
    Features:
    - Audio format conversion for API compatibility
    - Automatic retry with exponential backoff
    - Rate limiting and timeout handling
    - Error handling with user-friendly messages
    - Language auto-detection for multi-language support
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "whisper-1"):
        """Initialize Whisper client with API key.
        
        Args:
            api_key: OpenAI API key
            base_url: Custom API base URL (for testing or proxies)
            model: Whisper model to use (default: whisper-1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client = None
        
        # Rate limiting settings
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 30.0
        self.timeout = 30.0
        
        # Audio processing settings
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit from OpenAI
        self.supported_formats = {'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg', 'webm'}
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            
            if self.base_url:
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self._client = OpenAI(api_key=self.api_key)
                
        except ImportError as e:
            raise TranscriptionError(
                "OpenAI library not available. Please install with: uv add openai"
            ) from e
        except Exception as e:
            raise APIError(f"Failed to initialize OpenAI client: {e}") from e
    
    def test_api_key(self) -> bool:
        """Test if API key is valid by making a minimal request.
        
        Returns:
            True if API key is valid and accessible
        """
        try:
            # Create minimal test audio (1 second of silence)
            sample_rate = 16000
            duration = 1.0
            silence = np.zeros(int(sample_rate * duration), dtype=np.float32)
            
            # Convert to WAV format
            wav_data = self._numpy_to_wav(silence, sample_rate)
            
            # Try to transcribe (this will use credits but minimal)
            result = self._make_api_request(wav_data, "test.wav")
            
            # If we get here without exception, API key works
            return True
            
        except Exception as e:
            # Check for authentication errors first  
            error_str = str(e).lower()
            if "401" in error_str or "unauthorized" in error_str:
                return False
            # Check if this was converted to our APIError
            elif isinstance(e, APIError) and ("401" in error_str or "unauthorized" in error_str):
                return False
            # Other API errors might indicate the key works but there's another issue
            elif isinstance(e, APIError):
                logger.warning(f"API key test got non-auth API error: {e}")
                return True
            else:
                logger.warning(f"API key test failed with unexpected error: {e}")
                return False
    
    def transcribe_audio(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int = 44100,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> TranscriptionResult:
        """Transcribe audio data from numpy array.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio data
            language: Target language (ISO 639-1 code), None for auto-detect
            prompt: Optional context to guide transcription
            temperature: Sampling temperature (0.0 for deterministic, default: 0.0)
            
        Returns:
            TranscriptionResult with transcribed text and metadata
            
        Raises:
            TranscriptionError: If transcription fails
            NetworkError: If network request fails
            APIError: If API returns an error
        """
        start_time = time.time()
        
        try:
            # Validate and process audio data
            processed_audio = self._preprocess_audio(audio_data, sample_rate)
            
            # Convert to WAV format for API
            wav_data = self._numpy_to_wav(processed_audio, sample_rate)
            
            # Check file size
            if len(wav_data) > self.max_file_size:
                raise AudioFormatError(
                    f"Audio file too large ({len(wav_data) / 1024 / 1024:.1f}MB). "
                    f"Maximum size is {self.max_file_size / 1024 / 1024}MB"
                )
            
            # Make API request
            response = self._make_api_request(
                wav_data, 
                "audio.wav",
                language=language,
                prompt=prompt,
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            return self._parse_response(response, processing_time)
            
        except (TranscriptionError, NetworkError, APIError):
            raise
        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {e}") from e
    
    def transcribe_file(
        self, 
        file_path: Path, 
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> TranscriptionResult:
        """Transcribe audio file directly.
        
        Args:
            file_path: Path to audio file
            language: Target language (ISO 639-1 code), None for auto-detect  
            prompt: Optional context to guide transcription
            temperature: Sampling temperature (0.0 for deterministic, default: 0.0)
            
        Returns:
            TranscriptionResult with transcribed text and metadata
            
        Raises:
            TranscriptionError: If file cannot be read or transcription fails
        """
        start_time = time.time()
        
        try:
            # Validate file
            if not file_path.exists():
                raise TranscriptionError(f"Audio file not found: {file_path}")
            
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise AudioFormatError(
                    f"Audio file too large ({file_size / 1024 / 1024:.1f}MB). "
                    f"Maximum size is {self.max_file_size / 1024 / 1024}MB"
                )
            
            # Check format
            suffix = file_path.suffix.lower().lstrip('.')
            if suffix not in self.supported_formats:
                raise AudioFormatError(
                    f"Unsupported audio format: {suffix}. "
                    f"Supported formats: {', '.join(self.supported_formats)}"
                )
            
            # Read file
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            # Make API request
            response = self._make_api_request(
                audio_data,
                file_path.name,
                language=language,
                prompt=prompt,
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            
            # Parse response
            return self._parse_response(response, processing_time)
            
        except (TranscriptionError, NetworkError, APIError):
            raise
        except Exception as e:
            raise TranscriptionError(f"File transcription failed: {e}") from e
    
    def _preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Preprocess audio data for optimal transcription.
        
        Args:
            audio_data: Raw audio data
            sample_rate: Sample rate
            
        Returns:
            Processed audio data
        """
        # Ensure audio is 1D (mono)
        if audio_data.ndim > 1:
            # Convert stereo to mono by averaging channels
            audio_data = np.mean(audio_data, axis=1)
        
        # Normalize audio to prevent clipping
        if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
            # For floating point, ensure range is [-1, 1]
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
        
        # Remove leading/trailing silence (basic implementation)
        audio_data = self._trim_silence(audio_data)
        
        # Ensure minimum length (Whisper works better with at least 100ms)
        min_samples = int(sample_rate * 0.1)  # 100ms
        if len(audio_data) < min_samples:
            # Pad with zeros if too short
            padding = min_samples - len(audio_data)
            audio_data = np.pad(audio_data, (0, padding), mode='constant')
        
        return audio_data
    
    def _trim_silence(self, audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Remove leading and trailing silence from audio.
        
        Args:
            audio_data: Audio data
            threshold: Silence threshold (relative to max amplitude)
            
        Returns:
            Trimmed audio data
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Calculate absolute values for silence detection
        abs_audio = np.abs(audio_data)
        max_val = np.max(abs_audio)
        
        if max_val == 0:
            return audio_data  # All silence
        
        silence_threshold = max_val * threshold
        
        # Find first and last non-silent samples
        non_silent = abs_audio > silence_threshold
        if not np.any(non_silent):
            return audio_data  # All below threshold, keep as-is
        
        first_sound = np.argmax(non_silent)
        last_sound = len(audio_data) - np.argmax(non_silent[::-1]) - 1
        
        return audio_data[first_sound:last_sound + 1]
    
    def _numpy_to_wav(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array to WAV format bytes.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate
            
        Returns:
            WAV file as bytes
        """
        try:
            import wave
            import struct
            
            # Convert to 16-bit integers
            if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
                # Convert float [-1, 1] to int16 [-32768, 32767]
                audio_int16 = (audio_data * 32767).astype(np.int16)
            else:
                audio_int16 = audio_data.astype(np.int16)
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_int16.tobytes())
            
            return wav_buffer.getvalue()
            
        except Exception as e:
            raise AudioFormatError(f"Failed to convert audio to WAV format: {e}") from e
    
    def _make_api_request(
        self, 
        audio_data: bytes, 
        filename: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """Make API request with retry logic.
        
        Args:
            audio_data: Audio data as bytes
            filename: Filename for the request
            language: Target language code
            prompt: Optional context prompt
            temperature: Sampling temperature for deterministic results
            
        Returns:
            API response as dictionary
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Calculate delay for exponential backoff
                if attempt > 0:
                    delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                    logger.info(f"Retrying transcription request after {delay}s delay (attempt {attempt + 1})")
                    time.sleep(delay)
                
                # Create file-like object for API
                audio_file = io.BytesIO(audio_data)
                audio_file.name = filename
                
                # Prepare request parameters
                request_params = {
                    'file': audio_file,
                    'model': self.model,
                    'response_format': 'verbose_json',  # Get detailed response with language info
                    'temperature': temperature,
                    'timeout': self.timeout,
                }
                
                # Add timestamp granularities if supported (may not be available in all versions)
                try:
                    request_params['timestamp_granularities'] = ['segment']
                except Exception:
                    # Ignore if not supported
                    pass
                
                if language:
                    request_params['language'] = language
                
                if prompt:
                    request_params['prompt'] = prompt
                
                # Make API request
                logger.info(f"Making transcription request (attempt {attempt + 1})")
                response = self._client.audio.transcriptions.create(**request_params)
                
                # Convert response to dict for easier handling
                if hasattr(response, 'model_dump'):
                    return response.model_dump()
                else:
                    return response.__dict__
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Handle different types of errors
                if "401" in error_str or "unauthorized" in error_str:
                    raise APIError(
                        "Invalid API key. Please check your OpenAI API key.\n"
                        "You can update it by running: claude-helpers init --global-only"
                    ) from e
                elif "429" in error_str or "rate limit" in error_str:
                    # Rate limit - will retry
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries:
                        raise APIError(
                            "Rate limit exceeded. Please wait a few minutes and try again."
                        ) from e
                elif "timeout" in error_str or "connection" in error_str:
                    # Network issue - will retry
                    logger.warning(f"Network error on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries:
                        raise NetworkError(
                            "Network connection failed. Please check your internet connection."
                        ) from e
                elif "413" in error_str or "too large" in error_str:
                    # File too large - don't retry
                    raise AudioFormatError(
                        "Audio file too large for API. Please use a shorter recording."
                    ) from e
                else:
                    # Unknown error
                    logger.warning(f"API error on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries:
                        raise APIError(f"Transcription API error: {e}") from e
        
        # Should never reach here, but just in case
        raise APIError(f"Transcription failed after {self.max_retries + 1} attempts: {last_exception}")
    
    def _parse_response(self, response: Dict[str, Any], processing_time: float) -> TranscriptionResult:
        """Parse API response into TranscriptionResult.
        
        Args:
            response: API response dictionary
            processing_time: Time taken for processing
            
        Returns:
            Parsed TranscriptionResult
        """
        try:
            # Extract text (required field)
            text = response.get('text', '').strip()
            
            # Extract optional fields
            language = response.get('language')
            duration = response.get('duration')
            
            # Word-level timestamps (if available)
            word_timestamps = None
            if 'words' in response:
                word_timestamps = response['words']
            
            # Calculate confidence (if available)
            confidence = None
            if word_timestamps:
                # Average confidence from word timestamps
                word_confidences = [w.get('confidence', 0) for w in word_timestamps if 'confidence' in w]
                if word_confidences:
                    confidence = sum(word_confidences) / len(word_confidences)
            
            return TranscriptionResult(
                text=text,
                language=language,
                confidence=confidence,
                duration=duration,
                word_timestamps=word_timestamps,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise TranscriptionError(f"Failed to parse API response: {e}") from e


def create_whisper_client(api_key: str) -> WhisperClient:
    """Create WhisperClient with standard settings.
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Configured WhisperClient instance
    """
    return WhisperClient(api_key=api_key)


def get_supported_languages() -> List[str]:
    """Get list of languages supported by Whisper.
    
    Returns:
        List of ISO 639-1 language codes supported by Whisper
    """
    # Based on OpenAI Whisper documentation
    return [
        'af', 'ar', 'hy', 'az', 'be', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en',
        'et', 'fi', 'fr', 'gl', 'de', 'el', 'he', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'kn',
        'kk', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'mi', 'ne', 'no', 'fa', 'pl', 'pt', 'ro',
        'ru', 'sr', 'sk', 'sl', 'es', 'sw', 'sv', 'tl', 'ta', 'th', 'tr', 'uk', 'ur', 'vi',
        'cy'
    ]


def estimate_transcription_cost(audio_duration: float) -> float:
    """Estimate transcription cost based on audio duration.
    
    Args:
        audio_duration: Duration in seconds
        
    Returns:
        Estimated cost in USD (based on OpenAI pricing as of 2024)
    """
    # OpenAI Whisper pricing: $0.006 per minute
    cost_per_minute = 0.006
    duration_minutes = audio_duration / 60
    return duration_minutes * cost_per_minute