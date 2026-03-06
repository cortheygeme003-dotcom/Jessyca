import sys
import os
from unittest.mock import MagicMock

# 1. Mock external deps that might be missing or broken
# We do this BEFORE importing the project modules so they don't fail on import
sys.modules["pyaudio"] = MagicMock()
sys.modules["pyttsx3"] = MagicMock()
sys.modules["speech_recognition"] = MagicMock()
sys.modules["vosk"] = MagicMock()

# 2. Import project modules
# Assuming we run this from inside 'proyecto assistente local/jessyca'
try:
    import main
    import commands
    import tts
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# 3. Patch functions used by main and commands

# Patch TTS
def mock_speak(text):
    print(f"[JESSYCA]: {text}")

# Patch both the module function and the imported reference in main
main.speak = mock_speak
tts.speak = mock_speak
main.init_tts = MagicMock()

# Patch STT in main (since main imports them directly: from stt import ...)
# We simulate a user conversation
command_sequence = [
    "Jessyca, abre calculadora",     # Should trigger open_app
    "Jessyca, abre google.com",      # Should trigger open_url
    "Jessyca, salir"                 # Should trigger exit
]

def mock_listen_func(*args, **kwargs):
    if command_sequence:
        cmd = command_sequence.pop(0)
        print(f"[USER]: {cmd}")
        return cmd
    return "Jessyca, salir"

main.listen_google = mock_listen_func
main.listen_vosk = mock_listen_func

# Patch Actions in commands (since commands imports them directly: from actions_windows import ...)
def mock_open_app(target):
    print(f"[SYSTEM]: Opening App -> {target}")
    return True

def mock_open_url(url):
    print(f"[SYSTEM]: Opening URL -> {url}")
    return True

def mock_open_path(path):
    print(f"[SYSTEM]: Opening Path -> {path}")
    return True

commands.open_app = mock_open_app
commands.open_url = mock_open_url
commands.open_path = mock_open_path

if __name__ == "__main__":
    print(">>> INICIANDO PRUEBA DE LA VERSION VETA (BETA) <<<")
    try:
        main.main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    print(">>> PRUEBA FINALIZADA <<<")
