"""
Resource Farm Module
Collects Grain, Timber, Herbs, and Medicine from base buildings,
then restarts production.

Buildings handled:
  - Farm          (grain_collect, grain_produce)
  - Lumberyard    (lumber_collect, lumber_produce)
  - Herb Garden   (herb_collect, herb_produce)
  - Pharmacy      (medicine_collect, medicine_produce)

Each building has:
  1. A floating "collect" bubble that appears when the building is full.
  2. A building tap → "Collect" button flow as fallback.
  3. A "Produce / Start" button to restart the production cycle.

Template images required (capture with calibrate.py):
  templates/grain_bubble.png
  templates/lumber_bubble.png
  templates/herb_bubble.png
  templates/medicine_bubble.png
  templates/btn_collect.png
  templates/btn_produce.png
  templates/btn_close.png
"""

import time
from typing import Optional, Tuple

import config as cfg
from core.screen import ScreenCapture
from core.input import click, action_pause
from core.window import GameWindow
from utils.logger import log


# ---------------------------------------------------------------------------
# Relative-coordinate fallback positions (1080 × 1920 layout)
# These are approximate — use template matching where possible.
# ---------------------------------------------------------------------------
_BUILDINGS: dict = {
    "farm": {
        "tap":     (0.50, 0.62),   # Centre of the Farm building
        "bubble":  "grain_bubble",
        "collect": "btn_collect",
        "produce": "btn_produce",
    },
    "lumberyard": {
        "tap":     (0.68, 0.70),
        "bubble":  "lumber_bubble",
        "collect": "btn_collect",
        "produce": "btn_produce",
    },
    "herb_garden": {
        "tap":     (0.32, 0.68),
        "bubble":  "herb_bubble",
        "collect": "btn_collect",
        "produce": "btn_produce",
    },
    "pharmacy": {
        "tap":     (0.52, 0.45),
        "bubble":  "medicine_bubble",
        "collect": "btn_collect",
        "produce": "btn_produce",
    },
}


class FarmModule:
    def __init__(self, screen: ScreenCapture, window: GameWindow):
        self.screen = screen
        self.window = window

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> int:
        """Collect and restart all configured resource buildings.
        Returns the number of buildings successfully serviced."""
        collected = 0

        buildings_to_run = []
        if cfg.COLLECT_FARM:
            buildings_to_run.append("farm")
        if cfg.COLLECT_LUMBERYARD:
            buildings_to_run.append("lumberyard")
        if cfg.COLLECT_HERB_GARDEN:
            buildings_to_run.append("herb_garden")
        if cfg.COLLECT_PHARMACY:
            buildings_to_run.append("pharmacy")

        screenshot = self.screen.grab()   # single capture for bubble pass

        # --- Pass 1: Tap any visible floating bubbles (quickest method) ---
        for key in buildings_to_run:
            info   = _BUILDINGS[key]
            bubble = info["bubble"]
            pos    = self.screen.find_template(bubble, screenshot)
            if pos:
                log.info("[Farm] Collecting %s via bubble", key)
                click(*pos)
                action_pause()
                collected += 1

        # --- Pass 2: Open buildings and collect / restart via menus ----
        screenshot = self.screen.grab()
        for key in buildings_to_run:
            info = _BUILDINGS[key]
            if self._service_building(key, info):
                collected += 1

        log.info("[Farm] Buildings serviced this cycle: %d", collected)
        return collected

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _service_building(self, name: str, info: dict) -> bool:
        """Tap a building → collect if ready → restart production."""
        rel_tap = info["tap"]
        ax, ay  = self.window.abs_coords(*rel_tap)
        click(ax, ay)
        action_pause()

        # Try to collect
        collect_pos = self.screen.find_template(info["collect"])
        if collect_pos:
            log.info("[Farm] Collecting from %s via menu", name)
            click(*collect_pos)
            action_pause()

        # Try to restart production
        produce_pos = self.screen.find_template(info["produce"])
        if produce_pos:
            log.info("[Farm] Restarting production in %s", name)
            click(*produce_pos)
            action_pause()

        # Close the building menu
        self._close_menu()
        return collect_pos is not None or produce_pos is not None

    def _close_menu(self) -> None:
        """Dismiss any open popup / menu."""
        close_pos = self.screen.find_template("btn_close")
        if close_pos:
            click(*close_pos)
        else:
            # Tap the top-left corner — usually outside any panel
            ax, ay = self.window.abs_coords(0.05, 0.05)
            click(ax, ay)
        action_pause()
