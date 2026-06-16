"""
Calibration Helper
==================
Run this script FIRST to capture template images from the live game.

Usage:
    python calibrate.py

What it does:
  1. Shows a live preview window of the emulator screen.
  2. You drag a rectangle around a UI element.
  3. Type a name for it and press Enter — the image is saved to templates/.
  4. Repeat for every template the bot needs.
  5. Press Q to quit.

Required templates checklist:
  [ ] grain_bubble        — yellow grain icon floating above the Farm
  [ ] lumber_bubble       — brown lumber icon above the Lumberyard
  [ ] herb_bubble         — green herb icon above the Herb Garden
  [ ] medicine_bubble     — blue vial icon above the Pharmacy
  [ ] btn_collect         — "Collect" button text/icon inside a building menu
  [ ] btn_produce         — "Produce" / "Start" button
  [ ] btn_close           — X / close button on any panel
  [ ] btn_scavenge        — Scavenge button on the base screen
  [ ] tab_world_map       — World Map / Explore tab icon
  [ ] biome_forest        — Forest biome card image
  [ ] biome_plains        — Plains biome card image
  [ ] biome_ruins         — Ruins biome card image
  [ ] btn_send_party      — "Send" / "Go" button on the party dispatch screen
  [ ] btn_collect_party   — "Collect" on a returned scavenge party
  [ ] party_returned      — the "!" or green indicator when a party is back
  [ ] btn_hospital        — Hospital building or tab button
  [ ] btn_admit_patient   — "Admit" button in patient queue
  [ ] patient_healed      — Healed patient ready-to-collect indicator
  [ ] btn_collect_healed  — "Collect" on a fully healed patient
  [ ] btn_collect_all     — "Collect All" batch button
  [ ] tab_quests          — Quests / Missions tab icon
  [ ] quest_completed     — Green tick on a completed quest row
  [ ] btn_claim_quest     — "Claim" button on a completed quest
  [ ] btn_claim_all       — "Claim All" in the quest panel
  [ ] login_reward        — Daily login reward popup or button
  [ ] btn_claim_login     — "Claim" button on the login reward
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import pyautogui

TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)

_drawing   = False
_ix, _iy   = -1, -1
_rect      = None
_frame_copy = None


def _mouse_callback(event, x, y, flags, param):
    global _drawing, _ix, _iy, _rect, _frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        _drawing  = True
        _ix, _iy  = x, y
        _rect     = None

    elif event == cv2.EVENT_MOUSEMOVE and _drawing:
        img = _frame_copy.copy()
        cv2.rectangle(img, (_ix, _iy), (x, y), (0, 255, 0), 2)
        cv2.imshow("Calibrate — drag rect, then type name + Enter | Q to quit", img)

    elif event == cv2.EVENT_LBUTTONUP:
        _drawing = False
        x1, y1   = min(_ix, x), min(_iy, y)
        x2, y2   = max(_ix, x), max(_iy, y)
        _rect    = (x1, y1, x2, y2)


def run():
    win_name = "Calibrate — drag rect, then type name + Enter | Q to quit"
    cv2.namedWindow(win_name)
    cv2.setMouseCallback(win_name, _mouse_callback)

    print("\nCalibration tool started.")
    print("Make sure BlueStacks (or another emulator) is visible behind this window.\n")

    global _frame_copy, _rect

    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        _frame_copy = frame.copy()

        display = frame.copy()
        if _rect:
            x1, y1, x2, y2 = _rect
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow(win_name, display)

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            break

        if key == 13 and _rect:   # Enter pressed with a rect selected
            x1, y1, x2, y2 = _rect
            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                print("Empty selection — try again")
                _rect = None
                continue

            name = input("Template name (no extension): ").strip()
            if not name:
                print("Cancelled.")
                _rect = None
                continue

            out_path = TEMPLATE_DIR / f"{name}.png"
            cv2.imwrite(str(out_path), crop)
            print(f"Saved  →  {out_path}  ({crop.shape[1]}×{crop.shape[0]} px)")
            _rect = None

    cv2.destroyAllWindows()
    print("\nCalibration complete.  Templates saved to:", TEMPLATE_DIR)


if __name__ == "__main__":
    run()
