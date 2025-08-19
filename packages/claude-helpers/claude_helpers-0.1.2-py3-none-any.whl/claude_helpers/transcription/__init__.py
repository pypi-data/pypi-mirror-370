"""Transcription system for Claude Helpers."""

from .openai_client import (
    WhisperClient, TranscriptionResult, TranscriptionError, NetworkError, APIError, AudioFormatError,
    create_whisper_client, get_supported_languages, estimate_transcription_cost
)

__all__ = [
    'WhisperClient',
    'TranscriptionResult',
    'TranscriptionError',
    'NetworkError', 
    'APIError',
    'AudioFormatError',
    'create_whisper_client',
    'get_supported_languages',
    'estimate_transcription_cost',
]