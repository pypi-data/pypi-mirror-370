from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyvoicelib",
    version="0.1.1",
    author="Shay Yazirofi",
    author_email="yazirofi@gmail.com",
    description="A simple Python voice library for Voice Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yazirofi/pyvoicelib",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition>=3.8.1",
        "pyttsx3>=2.90",
        "PyAudio>=0.2.11",
    ],
    package_data={
        'speech_recognition': ['*.wav'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.8",
    keywords="voice assistant speech recognition text-to-speech",
)
