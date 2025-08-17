import pytest
from unittest.mock import MagicMock, patch
from pyvoicelib import (
    speak,
    listen,
    VoiceAssistant,
    VoiceLibError,
    ListenTimeoutError,
    AudioCaptureError,
    SpeechError,
    InitializationError  # Added missing import
)

# Constants for testing
TEST_TEXT = "Hello world"
TEST_AUDIO = b"fake_audio_data"
TEST_TRANSCRIPT = "test transcript"


### Fixtures ###

@pytest.fixture
def mock_engine():
    with patch('pyttsx3.init') as mock:
        engine = MagicMock()
        mock.return_value = engine
        yield engine


@pytest.fixture
def mock_recognizer():
    with patch('speech_recognition.Recognizer') as mock:
        recognizer = MagicMock()
        mock.return_value = recognizer
        yield recognizer


@pytest.fixture
def mock_microphone():
    with patch('speech_recognition.Microphone') as mock:
        mic = MagicMock()
        mock.return_value = mic
        yield mic


@pytest.fixture
def assistant(mock_engine, mock_recognizer):
    return VoiceAssistant()


### Helper Functions ###

def setup_recognizer_mock(recognizer, text=TEST_TRANSCRIPT, timeout=False):
    """Configure the recognizer mock for different scenarios"""
    if timeout:
        recognizer.listen.side_effect = WaitTimeoutError("Test timeout")
    else:
        recognizer.listen.return_value = TEST_AUDIO

    if text is None:
        recognizer.recognize_google.side_effect = UnknownValueError()
    else:
        recognizer.recognize_google.return_value = text


### Tests for Standalone Functions ###

@patch('pyvoicelib.core._get_components')
def test_speak_success(mock_get, mock_engine):
    mock_get.return_value = (MagicMock(), mock_engine)
    speak(TEST_TEXT)
    mock_engine.say.assert_called_once_with(TEST_TEXT)
    mock_engine.runAndWait.assert_called_once()


@patch('pyvoicelib.core._get_components')
def test_speak_error(mock_get):
    mock_engine = MagicMock()
    mock_engine.say.side_effect = Exception("Test error")
    mock_get.return_value = (MagicMock(), mock_engine)

    with pytest.raises(SpeechError):
        speak(TEST_TEXT)


@patch('pyvoicelib.core._get_components')
def test_listen_success(mock_get, mock_recognizer, mock_microphone):
    setup_recognizer_mock(mock_recognizer)
    mock_get.return_value = (mock_recognizer, MagicMock())

    result = listen()
    assert result == TEST_TRANSCRIPT
    mock_recognizer.listen.assert_called_once()


@patch('pyvoicelib.core._get_components')
def test_listen_timeout(mock_get, mock_recognizer):
    setup_recognizer_mock(mock_recognizer, timeout=True)
    mock_get.return_value = (mock_recognizer, MagicMock())

    with pytest.raises(ListenTimeoutError):
        listen()


@patch('pyvoicelib.core._get_components')
def test_listen_no_speech(mock_get, mock_recognizer):
    setup_recognizer_mock(mock_recognizer, text=None)
    mock_get.return_value = (mock_recognizer, MagicMock())

    assert listen() is None


### Tests for VoiceAssistant Class ###

def test_voice_assistant_init(assistant, mock_engine):
    assert assistant.engine == mock_engine
    mock_engine.setProperty.assert_any_call('rate', 150)
    mock_engine.setProperty.assert_any_call('volume', 0.9)


def test_voice_assistant_speak(assistant, mock_engine):
    assistant.speak(TEST_TEXT)
    mock_engine.say.assert_called_once_with(TEST_TEXT)
    mock_engine.runAndWait.assert_called_once()


def test_voice_assistant_listen(assistant, mock_recognizer):
    setup_recognizer_mock(mock_recognizer)
    result = assistant.listen()
    assert result == TEST_TRANSCRIPT


def test_voice_assistant_set_voice_rate(assistant, mock_engine):
    assistant.set_voice_rate(200)
    mock_engine.setProperty.assert_called_with('rate', 200)


def test_voice_assistant_set_voice_volume(assistant, mock_engine):
    assistant.set_voice_volume(0.5)
    mock_engine.setProperty.assert_called_with('volume', 0.5)


def test_voice_assistant_set_voice_volume_invalid(assistant):
    with pytest.raises(ValueError):
        assistant.set_voice_volume(1.5)


def test_simple_conversation(assistant, mock_engine, mock_recognizer):
    setup_recognizer_mock(mock_recognizer)
    response = assistant.simple_conversation(TEST_TEXT)

    mock_engine.say.assert_called_once_with(TEST_TEXT)
    assert response == TEST_TRANSCRIPT


def test_set_voice_gender_supported(mocker):
    mock_engine = mocker.Mock()

    male_voice = mocker.Mock()
    male_voice.name = "MaleVoice"
    male_voice.id = "0"

    female_voice = mocker.Mock()
    female_voice.name = "FemaleVoice"
    female_voice.id = "1"

    mock_engine.getProperty.return_value = [male_voice, female_voice]
    mocker.patch("pyvoicelib.core.initialize_components", return_value=(mocker.Mock(), mock_engine))

    assistant = VoiceAssistant()
    assistant.set_voice_gender("female")

    mock_engine.setProperty.assert_called_with("voice", "1")


def test_set_voice_gender_fallback(mocker):
    mock_engine = mocker.Mock()

    random_voice = mocker.Mock()
    random_voice.name = "SomeRandomVoice"
    random_voice.id = "0"

    mock_engine.getProperty.return_value = [random_voice]
    mocker.patch("pyvoicelib.core.initialize_components", return_value=(mocker.Mock(), mock_engine))

    assistant = VoiceAssistant()
    assistant.set_voice_gender("male")

    mock_engine.setProperty.assert_called_with("voice", "0")  # falls back to default


def test_set_voice_gender_invalid():
    assistant = VoiceAssistant()
    with pytest.raises(ValueError):
        assistant.set_voice_gender("robot")

### Error Handling Tests ###

def test_initialization_error():
    with patch('pyttsx3.init') as mock_init:
        mock_init.side_effect = Exception("Init failed")
        with pytest.raises(InitializationError):
            VoiceAssistant()


@patch('pyvoicelib.core._get_components')
def test_error_message_includes_github(mock_get):
    mock_engine = MagicMock()
    mock_engine.say.side_effect = Exception("Test error")
    mock_get.return_value = (MagicMock(), mock_engine)

    with pytest.raises(SpeechError) as exc_info:
        speak(TEST_TEXT)
    assert "github.com/Yazirofi/pyvoicelib" in str(exc_info.value)

### Mock Classes for SpeechRecognition Exceptions ###

class WaitTimeoutError(Exception):
    pass


class UnknownValueError(Exception):
    pass


# Patch these into the speech_recognition module for testing
@pytest.fixture(autouse=True)
def patch_sr_exceptions():
    with patch('speech_recognition.WaitTimeoutError', WaitTimeoutError), \
            patch('speech_recognition.UnknownValueError', UnknownValueError):
        yield