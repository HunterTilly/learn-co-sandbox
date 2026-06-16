"""
Human-like mouse movement and clicking, plus swipe (drag) simulation.

All delays are randomised within the ranges set in config.py to
avoid triggering any client-side bot detection.
"""

import random
import time
from typing import Tuple, Optional

import pyautogui

import config as cfg
from utils.logger import log

# Disable pyautogui's built-in pause so we control timing ourselves
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True   # Move mouse to corner to emergency-stop


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _jitter(base: float) -> float:
    """Add ±15 % random noise to a value."""
    return base * random.uniform(0.85, 1.15)


def _rand_delay(lo: float, hi: float) -> None:
    time.sleep(random.uniform(lo, hi))


def _human_move(x: int, y: int) -> None:
    """Move to (x, y) with a brief eased motion instead of teleporting."""
    cur_x, cur_y = pyautogui.position()
    # Short random arc — roughly 5-15 intermediate steps
    steps = random.randint(5, 15)
    for i in range(1, steps + 1):
        t = i / steps
        ease = t * t * (3 - 2 * t)   # smoothstep
        nx = int(cur_x + (x - cur_x) * ease)
        ny = int(cur_y + (y - cur_y) * ease)
        # Tiny pixel-level noise
        nx += random.randint(-1, 1)
        ny += random.randint(-1, 1)
        pyautogui.moveTo(nx, ny, duration=0)
        time.sleep(0.004)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def click(
    x: int,
    y: int,
    *,
    button: str = "left",
    double: bool = False,
    delay: bool = True,
) -> None:
    """Click at absolute screen coordinates with human-like motion."""
    # Small random offset so we never hit the exact same pixel twice
    ox = x + random.randint(-3, 3)
    oy = y + random.randint(-3, 3)
    _human_move(ox, oy)
    if double:
        pyautogui.doubleClick(ox, oy, button=button)
    else:
        pyautogui.click(ox, oy, button=button)
    if delay:
        _rand_delay(cfg.CLICK_DELAY_MIN, cfg.CLICK_DELAY_MAX)
    log.debug("Click (%d, %d)", ox, oy)


def click_rel(rel_x: float, rel_y: float, window, **kwargs) -> None:
    """Click at relative coords (0-1) resolved through *window*."""
    ax, ay = window.abs_coords(rel_x, rel_y)
    click(ax, ay, **kwargs)


def swipe(
    start: Tuple[int, int],
    end: Tuple[int, int],
    duration: float = 0.3,
) -> None:
    """Drag from *start* to *end* — simulates a swipe gesture in BlueStacks."""
    pyautogui.mouseDown(*start)
    time.sleep(0.05)
    steps = max(10, int(duration / 0.02))
    sx, sy = start
    ex, ey = end
    for i in range(steps):
        t = (i + 1) / steps
        nx = int(sx + (ex - sx) * t)
        ny = int(sy + (ey - sy) * t)
        pyautogui.moveTo(nx, ny)
        time.sleep(duration / steps)
    pyautogui.mouseUp()
    _rand_delay(cfg.ACTION_DELAY_MIN, cfg.ACTION_DELAY_MAX)


def scroll(x: int, y: int, clicks: int = -3) -> None:
    """Scroll at position. Negative = scroll down in BlueStacks."""
    pyautogui.moveTo(x, y)
    pyautogui.scroll(clicks)
    _rand_delay(cfg.ACTION_DELAY_MIN / 2, cfg.ACTION_DELAY_MAX / 2)


def action_pause() -> None:
    """Short pause between logical steps within a module."""
    _rand_delay(cfg.ACTION_DELAY_MIN, cfg.ACTION_DELAY_MAX)


def cycle_pause() -> None:
    """Long pause between full farming cycles."""
    delay = _jitter(random.uniform(cfg.CYCLE_DELAY_MIN, cfg.CYCLE_DELAY_MAX))
    log.info("Cycle complete — waiting %.0f s before next cycle", delay)
    time.sleep(delay)
