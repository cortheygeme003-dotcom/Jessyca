# tts.py
import pyttsx3

_engine = None

def init_tts(rate: int = 175, volume: float = 1.0):
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", rate)
        _engine.setProperty("volume", volume)

def speak(text: str):
    global _engine
    if _engine is None:
        init_tts()
    _engine.say(text)
    _engine.runAndWait()
