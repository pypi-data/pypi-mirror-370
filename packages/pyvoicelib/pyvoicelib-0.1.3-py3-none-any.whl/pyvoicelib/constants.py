# -----------------------------
# Default configuration values
# -----------------------------
DEFAULT_VOICE_RATE: int = 150            # Words per minute
DEFAULT_VOICE_VOLUME: float = 0.9        # Volume (0.0 to 1.0)
DEFAULT_TIMEOUT: int = 5                 # Max seconds to wait for speech
DEFAULT_PHRASE_TIME_LIMIT: int = 5       # Max seconds per phrase
DEFAULT_ENGINE: str = "pyttsx3"          # Default TTS/STT engine

# Default voice configuration
DEFAULT_VOICE_GENDER: str = "female"     # Default voice preference
SUPPORTED_GENDERS: list[str] = ["male", "female", "neutral"]

# -----------------------------
# Error messages
# -----------------------------
ERROR_MESSAGE: str = """
⚠️ An error occurred in pyvoicelib. Please check:

- Microphone is connected and working
- Internet connection (for speech recognition, Google API)
- Required dependencies are installed
- Try running list_voices() to confirm available voices on your system

For more information and troubleshooting, visit:
🔗 https://github.com/Yazirofi/pyvoicelib
"""
