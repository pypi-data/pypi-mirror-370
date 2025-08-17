import speech_recognition as sr
from typing import Optional
from .constants import *
from .exceptions import *
from .utils import initialize_components

# Global components initialized on first use
_recognizer = None
_engine = None


def _get_components():
    """Lazy initialization of global components"""
    global _recognizer, _engine
    if _recognizer is None or _engine is None:
        _recognizer, _engine = initialize_components()
    return _recognizer, _engine


def speak(text: str, wait: bool = True, rate: int = None, volume: float = None):
    """
    Convert text to speech and speak it out loud (standalone function).

    Args:
        text: Text to speak
        wait: Whether to wait for speech to complete
        rate: Optional speech rate (words per minute)
        volume: Optional volume level (0.0 to 1.0)
    """
    try:
        recognizer, engine = _get_components()

        if rate is not None:
            engine.setProperty('rate', rate)
        if volume is not None:
            if 0 <= volume <= 1:
                engine.setProperty('volume', volume)
            else:
                raise ValueError("Volume must be between 0.0 and 1.0")

        engine.say(text)
        if wait:
            engine.runAndWait()
    except Exception as e:
        raise SpeechError(f"Text-to-speech error: {str(e)}")

def listen(
        timeout: int = DEFAULT_TIMEOUT,
        phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT
) -> Optional[str]:
    """
    Listen for user speech and return recognized text (standalone function).

    Args:
        timeout: Timeout in seconds for listening
        phrase_time_limit: Maximum time for a phrase

    Returns:
        Recognized text or None if no speech detected
    """
    try:
        recognizer, engine = _get_components()

        with sr.Microphone() as source:
            print("Listening...")  # Can be made configurable later
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        raise ListenTimeoutError("No speech detected within timeout period")
    except sr.UnknownValueError:
        return None
    except Exception as e:
        raise AudioCaptureError(f"Error capturing audio: {str(e)}")


class VoiceAssistant:
    def __init__(self,
                 voice_rate: int = DEFAULT_VOICE_RATE,
                 voice_volume: float = DEFAULT_VOICE_VOLUME):
        """
        Initialize the voice assistant.

        Args:
            voice_rate: Words per minute
            voice_volume: Volume level (0.0 to 1.0)
        """
        try:
            self.recognizer, self.engine = initialize_components()
            self.set_voice_rate(voice_rate)
            self.set_voice_volume(voice_volume)
        except Exception as e:
            raise InitializationError(str(e))

    def set_voice_rate(self, rate: int):
        """Set the speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)

    def set_voice_volume(self, volume: float):
        """Set the speech volume (0.0 to 1.0)"""
        if 0 <= volume <= 1:
            self.engine.setProperty('volume', volume)
        else:
            raise ValueError("Volume must be between 0.0 and 1.0")

    def speak(self, text: str, wait: bool = True):
        """Convert text to speech and speak it out loud."""
        try:
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
        except Exception as e:
            raise SpeechError(f"Text-to-speech error: {str(e)}")

    def listen(self,
               timeout: int = DEFAULT_TIMEOUT,
               phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT) -> Optional[str]:
        """Listen for user speech and return the recognized text."""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                return self.recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            raise ListenTimeoutError("No speech detected within timeout period")
        except sr.UnknownValueError:
            return None
        except Exception as e:
            raise AudioCaptureError(f"Error capturing audio: {str(e)}")

    def simple_conversation(self, prompt: str):
        """A simple conversation helper that speaks and then listens."""
        self.speak(prompt)
        return self.listen()