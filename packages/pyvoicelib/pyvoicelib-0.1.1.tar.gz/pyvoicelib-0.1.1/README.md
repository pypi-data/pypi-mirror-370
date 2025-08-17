# 🎙️ pyvoicelib

> A **simple, cross-platform Python voice assistant library** for beginners, hobbyists, and developers.  
Easily add **speech recognition** 🗣️ and **text-to-speech** 🔊 to your Python projects.

---

## ✨ Features

✅ Text-to-speech conversion (TTS)  
✅ Speech recognition (STT)  
✅ Simple API – both **functions** and **VoiceAssistant class**  
✅ Set **voice rate, volume, and gender** (male/female/neutral)  
✅ Cross-platform: Windows, macOS, Linux  
✅ Python **3.6+** supported  

---

## 📦 Installation

```bash
pip install pyvoicelib
````

For development (with testing):

```bash
git clone https://github.com/Yazirofi/pyvoicelib.git
cd pyvoicelib
pip install -r requirements-dev.txt
```

---

## 🚀 Quick Start

### 1. Standalone Functions

```python
from pyvoicelib import speak, listen

# Text-to-speech
speak("Hello, I am your Python voice assistant!")

# Speech recognition
try:
    text = listen()
    print("You said:", text)
except Exception as e:
    print("Error:", e)
```

---

### 2. Using the VoiceAssistant Class

```python
from pyvoicelib import VoiceAssistant

# Initialize assistant
assistant = VoiceAssistant(voice_rate=160, voice_volume=0.8, voice_gender="female")

# Speak
assistant.speak("Hi there, how can I help you?")

# Listen
try:
    command = assistant.listen()
    print("You said:", command)
except Exception as e:
    print("Error:", e)
```

---

## 🎛️ Voice Customization

```python
assistant.set_voice_rate(180)   # Words per minute
assistant.set_voice_volume(0.7) # Volume (0.0 – 1.0)
assistant.set_voice_gender("male") # 'male', 'female', 'neutral'
```

Check available voices on your system:

```python
print(assistant.get_available_voices())
```

---

## 🧪 Running Tests

We use **pytest** for testing.

```bash
pytest -v
```

All tests are located in the `tests/` directory.

---

## 🛠️ Troubleshooting

### ❌ `No 'male' voice found. Using default system voice.`

* Your system may not provide explicitly labeled voices.
* Try `assistant.get_available_voices()` to list supported voices.

### ❌ `speech_recognition` or `pyaudio` ImportError

* Install missing dependencies:

  ```bash
  pip install SpeechRecognition pyttsx3 pyaudio
  ```

### ❌ Microphone not working

* Ensure your microphone is enabled and selected as the input device.
* On Linux, install portaudio:

  ```bash
  sudo apt-get install portaudio19-dev
  ```

### ❌ Python version error

* `pyvoicelib` requires **Python 3.6+**.
* Check with:

  ```bash
  python --version
  ```

---

## 💡 Example Project – Simple Conversation Bot

```python
from pyvoicelib import VoiceAssistant

assistant = VoiceAssistant(voice_gender="female")

while True:
    try:
        command = assistant.listen()
        if command:
            print("You:", command)
            if "exit" in command.lower():
                assistant.speak("Goodbye!")
                break
            else:
                assistant.speak(f"You said: {command}")
    except Exception as e:
        print("Error:", e)
```

---

## 🤝 Contributing

Pull requests are welcome! 🎉
Please run tests before submitting:

```bash
pytest -v
```

---

## 📖 Resources

* [SpeechRecognition Docs](https://pypi.org/project/SpeechRecognition/)
* [pyttsx3 Docs](https://pyttsx3.readthedocs.io/)

---

## 📜 License

MIT License © 2025 [Yazirofi](https://github.com/Yazirofi)

---

👉 This README is **clean, stylish, and beginner-friendly**. It has:  
- ✨ Emojis for readability  
- 🚀 Quick start & examples  
- 🛠️ Troubleshooting section  
- 💡 Example project  

Would you like me to also add **badges** (PyPI, Build, License, Python versions) at the top for extra style?

