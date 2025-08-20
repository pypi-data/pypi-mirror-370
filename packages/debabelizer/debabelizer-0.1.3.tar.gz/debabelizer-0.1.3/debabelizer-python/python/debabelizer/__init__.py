"""
Debabelizer - Universal Voice Processing Library

Breaking down language barriers, one voice at a time.
"""

from ._internal import (
    AudioFormat,
    WordTiming,
    TranscriptionResult,
    Voice,
    SynthesisResult,
    StreamingResult,
    DebabelizerConfig,
    VoiceProcessor,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ConfigurationError,
    create_processor,
)

# Create aliases to match the original Python API exactly
STTProvider = None  # Base class - not directly exposed in original
TTSProvider = None  # Base class - not directly exposed in original

# Version
__version__ = "0.1.3"

# Main exports - matching the original exactly
__all__ = [
    "VoiceProcessor",
    "DebabelizerConfig", 
    "STTProvider",
    "TTSProvider",
    "TranscriptionResult",
    "SynthesisResult", 
    "StreamingResult",
    "Voice",
    "AudioFormat",
    "ProviderError",
    "WordTiming",
    "AuthenticationError",
    "RateLimitError", 
    "ConfigurationError",
    "create_processor",
]