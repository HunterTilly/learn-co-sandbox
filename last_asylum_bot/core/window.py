"""
Finds and focuses the BlueStacks (or LDPlayer) emulator window on Windows.
Returns the bounding rect used by all other core modules.
"""

import sys
import time
from typing import Optional, Tuple

_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    import pygetwindow as gw

import config as cfg
from utils.logger import log


class GameWindow:
    """Represents the emulator window region on screen."""

    def __init__(self):
        self.left   = 0
        self.top    = 0
        self.width  = cfg.GAME_RESOLUTION[0]
        self.height = cfg.GAME_RESOLUTION[1]
        self._win   = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_and_focus(self) -> bool:
        """Locate the emulator window, bring it to the foreground, and
        store its bounding rect.  Returns True on success."""
        if not _IS_WINDOWS:
            log.warning("Window management is Windows-only; using defaults.")
            return True

        wins = gw.getWindowsWithTitle(cfg.BLUESTACKS_WINDOW_TITLE)
        if not wins:
            log.error(
                "Cannot find window with title %r.  "
                "Make sure BlueStacks is open and the game is running.",
                cfg.BLUESTACKS_WINDOW_TITLE,
            )
            return False

        self._win = wins[0]
        try:
            self._win.activate()
            time.sleep(0.4)
        except Exception as exc:
            log.warning("Could not activate window: %s", exc)

        self.left   = self._win.left
        self.top    = self._win.top
        self.width  = self._win.width
        self.height = self._win.height

        log.info(
            "Emulator window found at (%d, %d) size %dx%d",
            self.left, self.top, self.width, self.height,
        )
        return True

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def abs_coords(self, rel_x: float, rel_y: float) -> Tuple[int, int]:
        """Convert (0-1) relative coords → absolute screen coords."""
        x = int(self.left + rel_x * self.width)
        y = int(self.top  + rel_y * self.height)
        return x, y

    def region(self) -> Tuple[int, int, int, int]:
        """Return (left, top, width, height) for pyautogui/screenshot calls."""
        return self.left, self.top, self.width, self.height

    def is_active(self) -> bool:
        if not _IS_WINDOWS or self._win is None:
            return True
        try:
            active = gw.getActiveWindow()
            return active is not None and active._hWnd == self._win._hWnd
        except Exception:
            return False
