from aqt import mw
from .main import init_addon

# 1. Zuerst die Config prüfen/erstellen
def ensure_config_exists():
    conf = mw.addonManager.getConfig(__name__)
    # Falls gar keine Config da ist oder unser neuer Key fehlt
    if not conf or "selected_tags" not in conf:
        # Bestehende Config nehmen oder leeres Dict starten
        new_conf = conf if conf else {}
        new_conf["selected_tags"] = ["Anki_Erlangen"]
        mw.addonManager.writeConfig(__name__, new_conf)

ensure_config_exists()

# 2. Dann das Addon (Menü-Einträge etc.) initialisieren
init_addon()

# 3. Zum Schluss die Config-GUI Verknüpfung laden
from . import config_gui
