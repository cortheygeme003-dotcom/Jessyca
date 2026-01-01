# actions_windows.py
import os
import subprocess
import webbrowser
from pathlib import Path

def open_app(app_path_or_name: str) -> bool:
    """
    Abre una app por:
    - ruta completa a .exe
    - comando del sistema (calc, notepad, etc.)
    - o usando 'start' (Windows)
    """
    target = app_path_or_name.strip().strip('"')

    # Si es una ruta existente
    if Path(target).exists():
        try:
            os.startfile(target)  # Windows
            return True
        except Exception:
            pass

    # Intentar como comando directo (calc, notepad, etc.)
    try:
        subprocess.Popen(target, shell=True)
        return True
    except Exception:
        pass

    # Intentar con "start"
    try:
        subprocess.Popen(f'start "" "{target}"', shell=True)
        return True
    except Exception:
        return False

def open_path(path_str: str) -> bool:
    p = Path(path_str.strip().strip('"'))
    if p.exists():
        try:
            os.startfile(str(p))
            return True
        except Exception:
            return False
    return False

def open_url(url: str) -> bool:
    url = url.strip()
    if not url:
        return False
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False
