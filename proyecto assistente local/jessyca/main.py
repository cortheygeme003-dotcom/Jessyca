# main.py
from tts import init_tts, speak
from stt import listen_google, listen_vosk
from commands import has_wake_word, parse_command, execute

# ===== CONFIG =====
USE_OFFLINE_VOSK = False  # True = offline con Vosk, False = online Google
VOSK_MODEL_PATH = "vosk-model-small-es-0.42"  # carpeta del modelo (si offline)
LANG = "es-ES"
# ==================

def listen_once():
    if USE_OFFLINE_VOSK:
        return listen_vosk(VOSK_MODEL_PATH)
    return listen_google(lang=LANG)

def main():
    init_tts()
    speak("Hola. Soy Jessyca. Dime un comando empezando por Jessyca.")
    print("Jessyca lista. Di: 'Jessyca, abre calculadora'")

    while True:
        text = listen_once()
        if not text:
            continue

        print("Escuché:", text)

        # Requiere wake word para evitar activación accidental
        if not has_wake_word(text):
            continue

        intent, payload = parse_command(text)
        ok, response = execute(intent, payload)

        print("→", response)
        speak(response)

        if intent == "exit":
            break

if __name__ == "__main__":
    main()
