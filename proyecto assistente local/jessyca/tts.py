# tts.py
import os
import wave
import tempfile
import pyttsx3

try:
    from TTS.api import TTS
    HAS_COQUI = True
except ImportError:
    HAS_COQUI = False

# Fallback for playing audio if not using pyttsx3
try:
    import pyaudio
except ImportError:
    pyaudio = None

_engine = None
_coqui_tts = None
USE_COQUI = True

def init_tts(rate: int = 175, volume: float = 1.0):
    global _engine, _coqui_tts

    # Initialize Coqui TTS if requested and available
    if USE_COQUI and HAS_COQUI:
        if _coqui_tts is None:
            # Using a Spanish model as default
            # This will download the model on first run if not present
            print("Inicializando Coqui TTS (puede tardar la primera vez)...")
            try:
                _coqui_tts = TTS(model_name="tts_models/es/css10/vits", progress_bar=False, gpu=False)
                print("Coqui TTS inicializado.")
            except Exception as e:
                print(f"No se pudo inicializar Coqui TTS: {e}")
                # _coqui_tts remains None, fallback to pyttsx3 logic below might happen if implemented logic allows

    # Initialize pyttsx3 (always good to have as fallback)
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate", rate)
        _engine.setProperty("volume", volume)

def _play_audio_file(path):
    """Plays a wav file using PyAudio."""
    if pyaudio is None:
        raise ImportError("PyAudio no está instalado, no se puede reproducir el audio de Coqui.")

    wf = wave.open(path, 'rb')
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        chunk = 1024
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
    except Exception as e:
        # Re-raise logic error or playback error so speak can fallback
        raise e
    finally:
        p.terminate()
        wf.close()

def speak(text: str):
    global _engine, _coqui_tts

    # Try Coqui first
    if USE_COQUI and HAS_COQUI and _coqui_tts is not None:
        try:
            # Generate to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
                temp_path = fp.name

            # Use Coqui to generate speech
            _coqui_tts.tts_to_file(text=text, file_path=temp_path)

            # Play the generated file
            _play_audio_file(temp_path)

            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return
        except Exception as e:
            print(f"Error con Coqui TTS: {e}. Usando fallback.")
            # Fallthrough to pyttsx3

    # Fallback to pyttsx3
    if _engine is None:
        init_tts()
    _engine.say(text)
    _engine.runAndWait()
