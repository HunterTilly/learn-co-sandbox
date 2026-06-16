"""
Scavenge Module
Sends survivor parties to biomes, collects returning parties, and
manages the energy loop so we never waste energy overflow.

Game flow:
  1. Tap the world-map / scavenge button to open the biome selector.
  2. Select a biome (from priority list in config).
  3. Choose survivors to assign (select the top recommended team).
  4. Confirm / send.
  5. Repeat up to SCAVENGE_MAX_PARTIES parties.
  6. On subsequent cycles, collect any parties that have returned.

Templates required:
  templates/btn_scavenge.png      — main scavenge button on base screen
  templates/tab_world_map.png     — world-map / explore tab icon
  templates/biome_forest.png
  templates/biome_plains.png
  templates/biome_ruins.png
  templates/btn_send_party.png    — "Send" / "Go" confirmation button
  templates/btn_collect_party.png — collect button on a returned party
  templates/party_returned.png    — indicator that a party is back
  templates/btn_close.png
"""

import time
from typing import List, Optional, Tuple

import config as cfg
from core.screen import ScreenCapture
from core.input import click, action_pause, cycle_pause
from core.window import GameWindow
from utils.logger import log


_BIOME_TEMPLATES = {
    "forest": "biome_forest",
    "plains": "biome_plains",
    "ruins":  "biome_ruins",
}


class ScavengeModule:
    def __init__(self, screen: ScreenCapture, window: GameWindow):
        self.screen = screen
        self.window = window
        self._parties_sent = 0

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Full scavenge cycle: collect returned parties, then send new ones."""
        if not cfg.RUN_SCAVENGE:
            return

        log.info("[Scavenge] Starting scavenge cycle")
        self._open_scavenge_screen()
        self._collect_returned_parties()
        self._send_parties()
        self._close_scavenge_screen()

    # ------------------------------------------------------------------
    # Open / close the scavenge / world-map screen
    # ------------------------------------------------------------------

    def _open_scavenge_screen(self) -> bool:
        # Try dedicated scavenge button first
        pos = self.screen.find_template("btn_scavenge")
        if pos:
            click(*pos)
            action_pause()
            return True

        # Fallback: world-map tab
        pos = self.screen.find_template("tab_world_map")
        if pos:
            click(*pos)
            action_pause()
            return True

        log.warning("[Scavenge] Cannot find scavenge entry point — skipping")
        return False

    def _close_scavenge_screen(self) -> None:
        pos = self.screen.find_template("btn_close")
        if pos:
            click(*pos)
            action_pause()
        else:
            ax, ay = self.window.abs_coords(0.05, 0.05)
            click(ax, ay)
            action_pause()

    # ------------------------------------------------------------------
    # Collect returned parties
    # ------------------------------------------------------------------

    def _collect_returned_parties(self) -> int:
        """Tap all returned-party collect buttons visible on screen."""
        collected = 0
        # Keep clicking collect buttons until none remain
        for _ in range(cfg.SCAVENGE_MAX_PARTIES + 2):
            screenshot = self.screen.grab()
            pos = self.screen.find_template("btn_collect_party", screenshot)
            if not pos:
                pos = self.screen.find_template("party_returned", screenshot)
            if not pos:
                break
            log.info("[Scavenge] Collecting returned party at (%d, %d)", *pos)
            click(*pos)
            action_pause()
            # There may be a reward popup — close it
            close = self.screen.find_template("btn_close")
            if close:
                click(*close)
                action_pause()
            collected += 1

        if collected:
            log.info("[Scavenge] Collected %d returned parties", collected)
        return collected

    # ------------------------------------------------------------------
    # Send new parties
    # ------------------------------------------------------------------

    def _send_parties(self) -> int:
        sent = 0
        for biome_name in cfg.SCAVENGE_BIOME_PRIORITY:
            if sent >= cfg.SCAVENGE_MAX_PARTIES:
                break
            if self._send_one_party(biome_name):
                sent += 1

        log.info("[Scavenge] Sent %d new parties", sent)
        self._parties_sent = sent
        return sent

    def _send_one_party(self, biome_name: str) -> bool:
        """Select a biome and send a party to it. Returns True on success."""
        tmpl_name = _BIOME_TEMPLATES.get(biome_name)
        if not tmpl_name:
            log.warning("[Scavenge] Unknown biome: %s", biome_name)
            return False

        pos = self.screen.find_template(tmpl_name)
        if not pos:
            log.debug("[Scavenge] Biome %r not visible", biome_name)
            return False

        log.info("[Scavenge] Selecting biome: %s", biome_name)
        click(*pos)
        action_pause()

        # The game now shows survivor selection — we pick the auto/recommended team
        # by tapping the first available slot or an "Auto" button
        auto_pos = self.screen.find_template("btn_auto_assign")
        if auto_pos:
            click(*auto_pos)
            action_pause()

        # Confirm sending
        send_pos = self.screen.find_template("btn_send_party")
        if not send_pos:
            log.warning("[Scavenge] Send button not found for biome %s", biome_name)
            # Close the biome panel and abort
            close = self.screen.find_template("btn_close")
            if close:
                click(*close)
                action_pause()
            return False

        click(*send_pos)
        action_pause()
        log.info("[Scavenge] Party sent to %s", biome_name)
        return True
