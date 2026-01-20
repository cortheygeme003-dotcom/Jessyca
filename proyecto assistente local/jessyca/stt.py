# stt.py
import json
from typing import Optional

# Global caches for performance optimization
_VOSK_MODELS = {}
_SR_RECOGNIZER = None
_NOISE_ADJUSTED = False

def listen_google(lang: str = "es-ES", timeout: int = 5, phrase_time_limit: int = 6) -> Optional[str]:
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.6)
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
    import speech_recognition as sr
    from vosk import Model, KaldiRecognizer

    global _SR_RECOGNIZER, _NOISE_ADJUSTED

    # Initialize Recognizer once
    if _SR_RECOGNIZER is None:
        _SR_RECOGNIZER = sr.Recognizer()

    r = _SR_RECOGNIZER

    with sr.Microphone() as source:
        # Perform ambient noise adjustment only once
        if not _NOISE_ADJUSTED:
            r.adjust_for_ambient_noise(source, duration=0.6)
            _NOISE_ADJUSTED = True

        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=timeout)
            data = audio.get_raw_data(convert_rate=16000, convert_width=2)

            # Initialize/Get cached Vosk Model
            if model_path not in _VOSK_MODELS:
                _VOSK_MODELS[model_path] = Model(model_path)

            model = _VOSK_MODELS[model_path]
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
