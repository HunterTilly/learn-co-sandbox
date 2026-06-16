"""
Screenshot capture + template matching + basic colour detection.

Provides the primary way the bot "sees" the game state.
"""

import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pyautogui

import config as cfg
from core.window import GameWindow
from utils.logger import log


class ScreenCapture:
    """Grabs screenshots and searches them for known templates or colours."""

    def __init__(self, window: GameWindow):
        self.window = window
        self._template_cache: dict = {}

    # ------------------------------------------------------------------
    # Screenshot
    # ------------------------------------------------------------------

    def grab(self) -> np.ndarray:
        """Capture the emulator region and return as a BGR numpy array."""
        region = self.window.region()
        shot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    def grab_region(
        self,
        rel_left: float,
        rel_top: float,
        rel_right: float,
        rel_bottom: float,
    ) -> np.ndarray:
        """Capture a sub-region using relative coordinates (0-1)."""
        w, h = self.window.width, self.window.height
        x = self.window.left + int(rel_left * w)
        y = self.window.top  + int(rel_top  * h)
        rw = int((rel_right  - rel_left) * w)
        rh = int((rel_bottom - rel_top)  * h)
        shot = pyautogui.screenshot(region=(x, y, rw, rh))
        return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

    # ------------------------------------------------------------------
    # Template matching
    # ------------------------------------------------------------------

    def _load_template(self, name: str) -> Optional[np.ndarray]:
        if name in self._template_cache:
            return self._template_cache[name]

        for ext in (".png", ".jpg"):
            path = cfg.TEMPLATE_DIR / f"{name}{ext}"
            if path.exists():
                img = cv2.imread(str(path), cv2.IMREAD_COLOR)
                self._template_cache[name] = img
                return img

        log.warning("Template not found: %s (add it to templates/)", name)
        return None

    def find_template(
        self,
        template_name: str,
        screenshot: Optional[np.ndarray] = None,
        threshold: float = cfg.TEMPLATE_MATCH_THRESH,
    ) -> Optional[Tuple[int, int]]:
        """
        Search for a named template in the current (or provided) screenshot.
        Returns the (x, y) screen coordinate of the centre if found, else None.
        """
        tmpl = self._load_template(template_name)
        if tmpl is None:
            return None

        screen = screenshot if screenshot is not None else self.grab()
        result = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold:
            log.debug("Template %r not found (best=%.3f < %.3f)", template_name, max_val, threshold)
            return None

        th, tw = tmpl.shape[:2]
        cx = self.window.left + max_loc[0] + tw // 2
        cy = self.window.top  + max_loc[1] + th // 2
        log.debug("Template %r found at (%d, %d) conf=%.3f", template_name, cx, cy, max_val)
        return cx, cy

    def find_all_templates(
        self,
        template_name: str,
        screenshot: Optional[np.ndarray] = None,
        threshold: float = cfg.TEMPLATE_MATCH_THRESH,
        min_distance: int = 20,
    ) -> List[Tuple[int, int]]:
        """Find ALL instances of a template (e.g. multiple resource bubbles)."""
        tmpl = self._load_template(template_name)
        if tmpl is None:
            return []

        screen = screenshot if screenshot is not None else self.grab()
        result = cv2.matchTemplate(screen, tmpl, cv2.TM_CCOEFF_NORMED)
        th, tw = tmpl.shape[:2]

        locs = np.where(result >= threshold)
        points = list(zip(locs[1], locs[0]))  # (x, y)

        # Deduplicate nearby matches
        unique: List[Tuple[int, int]] = []
        for pt in points:
            if all(abs(pt[0] - u[0]) > min_distance or abs(pt[1] - u[1]) > min_distance for u in unique):
                sx = self.window.left + pt[0] + tw // 2
                sy = self.window.top  + pt[1] + th // 2
                unique.append((sx, sy))

        log.debug("Template %r found %d instances", template_name, len(unique))
        return unique

    # ------------------------------------------------------------------
    # Colour detection
    # ------------------------------------------------------------------

    def pixel_color(self, rel_x: float, rel_y: float) -> Tuple[int, int, int]:
        """Return the (R, G, B) colour of a single relative-coordinate pixel."""
        ax, ay = self.window.abs_coords(rel_x, rel_y)
        shot = pyautogui.screenshot(region=(ax, ay, 1, 1))
        return shot.getpixel((0, 0))[:3]

    def color_matches(
        self,
        rel_x: float,
        rel_y: float,
        target_rgb: Tuple[int, int, int],
        tolerance: int = 20,
    ) -> bool:
        r, g, b = self.pixel_color(rel_x, rel_y)
        tr, tg, tb = target_rgb
        return abs(r - tr) <= tolerance and abs(g - tg) <= tolerance and abs(b - tb) <= tolerance

    # ------------------------------------------------------------------
    # Convenience wait
    # ------------------------------------------------------------------

    def wait_for_template(
        self,
        template_name: str,
        timeout: float = 10.0,
        poll: float = 0.5,
    ) -> Optional[Tuple[int, int]]:
        """Block until a template appears on screen or timeout elapses."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            pos = self.find_template(template_name)
            if pos:
                return pos
            time.sleep(poll)
        log.warning("Timed out waiting for template: %r", template_name)
        return None
