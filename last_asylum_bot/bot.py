"""
Last Asylum: Plague — Farming Bot
==================================
Entry point.  Run from the terminal with:

    python bot.py            # Run all enabled modules in a loop
    python bot.py --once     # Run a single farming cycle then exit
    python bot.py --modules farm scavenge   # Run only specific modules

Hotkeys while running:
    F12  — stop safely after the current cycle
    F11  — pause / resume

Requirements: see requirements.txt
Platform:     Windows 10/11 + BlueStacks (Android emulator)
iOS note:     See ios/autotouch_farm.lua for iPhone automation.
"""

import argparse
import sys
import threading
import time

import keyboard   # pip install keyboard

import config as cfg
from core.screen import ScreenCapture
from core.window import GameWindow
from core.input import cycle_pause
from modules.farm     import FarmModule
from modules.scavenge import ScavengeModule
from modules.hospital import HospitalModule
from modules.quests   import QuestModule
from utils.logger import log


# ---------------------------------------------------------------------------
# State flags controlled by hotkeys
# ---------------------------------------------------------------------------
_stop_requested  = threading.Event()
_pause_requested = threading.Event()


def _on_stop():
    log.info("Stop hotkey pressed — will stop after this cycle")
    _stop_requested.set()


def _on_pause():
    if _pause_requested.is_set():
        _pause_requested.clear()
        log.info("Bot resumed")
    else:
        _pause_requested.set()
        log.info("Bot paused — press %s again to resume", cfg.HOTKEY_PAUSE)


# ---------------------------------------------------------------------------
# Bot class
# ---------------------------------------------------------------------------

class LastAsylumBot:
    def __init__(self, modules_to_run: list[str]):
        self.modules_to_run = set(modules_to_run)
        self.window  = GameWindow()
        self.screen  = ScreenCapture(self.window)

        self.farm     = FarmModule(self.screen, self.window)
        self.scavenge = ScavengeModule(self.screen, self.window)
        self.hospital = HospitalModule(self.screen, self.window)
        self.quests   = QuestModule(self.screen, self.window)

        self.cycle_count = 0

    # ------------------------------------------------------------------

    def start(self, once: bool = False) -> None:
        log.info("=" * 60)
        log.info("Last Asylum: Plague — Farming Bot starting")
        log.info("Modules: %s", ", ".join(sorted(self.modules_to_run)))
        log.info("Press %s to stop  |  %s to pause", cfg.HOTKEY_STOP, cfg.HOTKEY_PAUSE)
        log.info("=" * 60)

        keyboard.add_hotkey(cfg.HOTKEY_STOP,  _on_stop)
        keyboard.add_hotkey(cfg.HOTKEY_PAUSE, _on_pause)

        if not self.window.find_and_focus():
            log.error("Emulator window not found.  Is BlueStacks running?")
            sys.exit(1)

        try:
            while not _stop_requested.is_set():
                self._wait_if_paused()
                self._run_cycle()
                if once:
                    break
                cycle_pause()
        finally:
            keyboard.unhook_all()
            log.info("Bot stopped after %d cycles", self.cycle_count)

    # ------------------------------------------------------------------

    def _run_cycle(self) -> None:
        self.cycle_count += 1
        log.info("--- Cycle %d start ---", self.cycle_count)

        if "quests" in self.modules_to_run:
            self.quests.run()

        if "farm" in self.modules_to_run:
            self.farm.run()

        if "hospital" in self.modules_to_run:
            self.hospital.run()

        if "scavenge" in self.modules_to_run:
            self.scavenge.run()

        log.info("--- Cycle %d complete ---", self.cycle_count)

    def _wait_if_paused(self) -> None:
        if _pause_requested.is_set():
            log.info("Paused — waiting...")
        while _pause_requested.is_set() and not _stop_requested.is_set():
            time.sleep(0.5)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Last Asylum: Plague farming bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single farming cycle then exit",
    )
    parser.add_argument(
        "--modules",
        nargs="+",
        choices=["farm", "scavenge", "hospital", "quests", "all"],
        default=["all"],
        metavar="MODULE",
        help="Which modules to run (farm | scavenge | hospital | quests | all)",
    )
    return parser.parse_args()


def _resolve_modules(raw: list[str]) -> list[str]:
    all_modules = ["farm", "scavenge", "hospital", "quests"]
    if "all" in raw:
        return all_modules
    return [m for m in raw if m in all_modules]


if __name__ == "__main__":
    args = _parse_args()
    active_modules = _resolve_modules(args.modules)
    bot = LastAsylumBot(active_modules)
    bot.start(once=args.once)
