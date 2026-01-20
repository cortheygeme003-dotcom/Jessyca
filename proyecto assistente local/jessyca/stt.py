# stt.py
import json
from typing import Optional
import speech_recognition as sr

_recognizer = None

def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.6)
    return _recognizer

def listen_google(lang: str = "es-ES", timeout: int = 5, phrase_time_limit: int = 6) -> Optional[str]:
    r = _get_recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return r.recognize_google(audio, language=lang)
        except sr.WaitTimeoutError:
            # Es normal que esto ocurra si no se habla, no es un error fatal.
            return None
        except Exception:
            return None

def listen_vosk(model_path: str, timeout: int = 6) -> Optional[str]:
    """
    Offline. Requiere modelo Vosk descargado.
    """
    from vosk import Model, KaldiRecognizer

    r = _get_recognizer()
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=timeout)
            data = audio.get_raw_data(convert_rate=16000, convert_width=2)

            # Cargar modelo y reconocer
            model = Model(model_path)
            rec = KaldiRecognizer(model, 16000)
            rec.AcceptWaveform(data)
            result = json.loads(rec.Result())
            text = (result.get("text") or "").strip()
            return text if text else None
        except sr.WaitTimeoutError:
            # Es normal que esto ocurra si no se habla, no es un error fatal.
            return None
        except Exception:
            return None
