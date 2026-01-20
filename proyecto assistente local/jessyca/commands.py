# commands.py
import re
from typing import Tuple, Optional
from actions_windows import open_app, open_url, open_path

# Mapea nombres "humanos" -> rutas/comandos
APP_ALIASES = {
    # básicos Windows
    "calculadora": "calc",
    "calc": "calc",
    "bloc de notas": "notepad",
    "notas": "notepad",
    "cmd": "cmd",
    "terminal": "cmd",
    "explorador": "explorer",
    "archivos": "explorer",

    # agrega los tuyos (ejemplos típicos):
    # "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # "spotify": r"C:\Users\TU_USUARIO\AppData\Roaming\Spotify\Spotify.exe",
    # "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
}

WAKE_WORDS = ("jessyca", "jessica")  # por si STT confunde

# Compiled Regexes
RE_EXIT = re.compile(r"\b(salir|terminar|apagar|cierra jessyca|adios)\b")
RE_OPEN_GENERIC = re.compile(r"\b(abr(e|ir)|abre)\b\s+(.*)$")
RE_PATH_CHECK = re.compile(r"([a-zA-Z]:\\|^\\\\|^/)")
RE_OPEN_URL_EXPLICIT = re.compile(r"\b(abr(e|ir)|abre)\b\s+(https?://\S+)")
RE_WAKE_WORDS = [re.compile(rf"\b{re.escape(w)}\b[:,]?\s*") for w in WAKE_WORDS]

def strip_wake_word(text: str) -> str:
    t = text.lower().strip()
    for pattern in RE_WAKE_WORDS:
        t = pattern.sub("", t).strip()
    return t

def has_wake_word(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in WAKE_WORDS)

def parse_command(text: str) -> Tuple[str, Optional[str]]:
    """
    Devuelve: (intent, payload)
    intent:
      - open_app
      - open_url
      - open_path
      - exit
      - unknown
    """
    t = strip_wake_word(text)

    # salir
    if RE_EXIT.search(t):
        return ("exit", None)

    # abre "algo"
    m = RE_OPEN_GENERIC.search(t)
    if m:
        target = m.group(3).strip().strip('"')
        # si parece url
        if "." in target and " " not in target and not target.endswith((".exe", ".lnk")):
            return ("open_url", target)
        # si parece ruta (tiene :\ o empieza con \ o /)
        if RE_PATH_CHECK.search(target):
            return ("open_path", target)
        return ("open_app", target)

    # abrir url explícita
    m = RE_OPEN_URL_EXPLICIT.search(t)
    if m:
        return ("open_url", m.group(3))

    return ("unknown", t)

def execute(intent: str, payload: Optional[str]) -> Tuple[bool, str]:
    if intent == "exit":
        return (True, "Saliendo. Hasta luego.")

    if intent == "open_app" and payload:
        key = payload.lower()
        target = APP_ALIASES.get(key, payload)
        ok = open_app(target)
        return (ok, f"Abriendo {payload}." if ok else f"No pude abrir {payload}. ¿Puedes decirme la ruta?")

    if intent == "open_path" and payload:
        ok = open_path(payload)
        return (ok, "Listo." if ok else "No encontré esa ruta o no pude abrirla.")

    if intent == "open_url" and payload:
        ok = open_url(payload)
        return (ok, f"Abriendo {payload}." if ok else "No pude abrir esa página.")

    return (False, "No entendí el comando. Prueba: 'Jessyca, abre calculadora' o 'Jessyca, abre google.com'.")
