"""
Last Asylum: Plague — Bot Configuration
Edit these values to match your setup before running.
"""

import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Window / emulator
# ---------------------------------------------------------------------------
BLUESTACKS_WINDOW_TITLE = "BlueStacks"   # Change if you use LDPlayer: "LDPlayer"
GAME_RESOLUTION = (1080, 1920)           # Width x Height of the emulator game area
BLUESTACKS_SCALE = 1.0                   # Scale factor if you run BlueStacks at a non-default size

# ---------------------------------------------------------------------------
# Timing (seconds) — slightly randomised at runtime for human-like behaviour
# ---------------------------------------------------------------------------
CLICK_DELAY_MIN    = 0.08   # Minimum pause after each click
CLICK_DELAY_MAX    = 0.25   # Maximum pause after each click
ACTION_DELAY_MIN   = 0.4    # Pause between logical actions (e.g. open menu → tap button)
ACTION_DELAY_MAX   = 1.1
CYCLE_DELAY_MIN    = 45     # Seconds to wait between full farming cycles
CYCLE_DELAY_MAX    = 90

# ---------------------------------------------------------------------------
# Features — toggle what the bot does each cycle
# ---------------------------------------------------------------------------
COLLECT_FARM        = True   # Collect grain from the Farm
COLLECT_LUMBERYARD  = True   # Collect timber from the Lumberyard
COLLECT_HERB_GARDEN = True   # Collect herbs from the Herb Garden
COLLECT_PHARMACY    = True   # Collect medicine from the Pharmacy / Apothecary
RUN_HOSPITAL        = True   # Admit patients and collect healed patient rewards
RUN_SCAVENGE        = True   # Send survivors out to scavenge biomes
RUN_DAILY_QUESTS    = True   # Claim daily quest / mission rewards
RUN_LOGIN_REWARD    = True   # Claim daily login chest

# ---------------------------------------------------------------------------
# Scavenge settings
# ---------------------------------------------------------------------------
SCAVENGE_BIOME_PRIORITY = [
    "forest",      # Best timber + herbs
    "plains",      # Best grain
    "ruins",       # Best lumber + drops
]
SCAVENGE_MAX_PARTIES = 3        # How many scavenge parties to send simultaneously
SCAVENGE_ENERGY_THRESHOLD = 20  # Wait until energy >= this before scavenging

# ---------------------------------------------------------------------------
# Hospital settings
# ---------------------------------------------------------------------------
HOSPITAL_MAX_QUEUE    = 10   # Max patients to queue per cycle
HOSPITAL_COLLECT_ALL  = True  # Automatically collect all finished healings

# ---------------------------------------------------------------------------
# Template matching
# ---------------------------------------------------------------------------
TEMPLATE_DIR          = Path(__file__).parent / "templates"
TEMPLATE_MATCH_THRESH = 0.82   # Confidence threshold (0-1). Lower = more lenient.

# ---------------------------------------------------------------------------
# Hotkeys (keyboard shortcuts while the bot is running)
# ---------------------------------------------------------------------------
HOTKEY_STOP   = "f12"        # Press F12 to stop the bot safely
HOTKEY_PAUSE  = "f11"        # Press F11 to pause / resume

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR        = Path(__file__).parent / "logs"
LOG_LEVEL      = "INFO"       # DEBUG | INFO | WARNING | ERROR
LOG_TO_FILE    = True
LOG_TO_CONSOLE = True

# ---------------------------------------------------------------------------
# Override with a JSON config file if it exists (user-local settings)
# ---------------------------------------------------------------------------
_LOCAL_CONFIG = Path(__file__).parent / "config_local.json"

def _load_local():
    if _LOCAL_CONFIG.exists():
        data = json.loads(_LOCAL_CONFIG.read_text())
        g = globals()
        for k, v in data.items():
            if k in g:
                g[k] = v

_load_local()
