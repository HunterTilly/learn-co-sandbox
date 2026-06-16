"""
Hospital Module
Handles the core healing loop:
  1. Admit new patients from the waiting queue.
  2. Collect rewards from patients who have been fully healed.
  3. Re-queue any pending patients.

Templates required:
  templates/btn_hospital.png      — hospital building or tab
  templates/btn_admit_patient.png — "Admit" button in the patient queue
  templates/patient_healed.png    — indicator that a patient is ready to collect
  templates/btn_collect_healed.png
  templates/btn_collect_all.png   — "Collect All" batch button (if game has it)
  templates/btn_close.png
"""

import config as cfg
from core.screen import ScreenCapture
from core.input import click, action_pause
from core.window import GameWindow
from utils.logger import log


class HospitalModule:
    def __init__(self, screen: ScreenCapture, window: GameWindow):
        self.screen = screen
        self.window = window

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        if not cfg.RUN_HOSPITAL:
            return

        log.info("[Hospital] Starting hospital cycle")
        if not self._open_hospital():
            return

        self._collect_healed()
        self._admit_patients()
        self._close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _open_hospital(self) -> bool:
        pos = self.screen.find_template("btn_hospital")
        if not pos:
            # Try tapping the relative position of the Sanctuary / hospital
            ax, ay = self.window.abs_coords(0.50, 0.38)
            click(ax, ay)
        else:
            click(*pos)
        action_pause()

        # Verify we are in the hospital screen
        check = self.screen.find_template("btn_admit_patient") or \
                self.screen.find_template("patient_healed")
        if not check:
            log.debug("[Hospital] Hospital screen not confirmed — proceeding anyway")
        return True

    def _collect_healed(self) -> int:
        count = 0

        # Try "Collect All" first
        all_pos = self.screen.find_template("btn_collect_all")
        if all_pos:
            log.info("[Hospital] Collecting all healed patients")
            click(*all_pos)
            action_pause()
            self._dismiss_reward_popup()
            return 1   # We don't know the exact count

        # Individual collect
        for _ in range(cfg.HOSPITAL_MAX_QUEUE + 5):
            screenshot = self.screen.grab()
            pos = self.screen.find_template("btn_collect_healed", screenshot) or \
                  self.screen.find_template("patient_healed", screenshot)
            if not pos:
                break
            click(*pos)
            action_pause()
            self._dismiss_reward_popup()
            count += 1

        if count:
            log.info("[Hospital] Collected %d healed patients", count)
        return count

    def _admit_patients(self) -> int:
        count = 0
        for _ in range(cfg.HOSPITAL_MAX_QUEUE):
            screenshot = self.screen.grab()
            pos = self.screen.find_template("btn_admit_patient", screenshot)
            if not pos:
                break
            log.info("[Hospital] Admitting patient")
            click(*pos)
            action_pause()
            # Confirm the patient selection popup if it appears
            confirm = self.screen.find_template("btn_collect")  # re-use generic confirm
            if confirm:
                click(*confirm)
                action_pause()
            count += 1

        if count:
            log.info("[Hospital] Admitted %d patients", count)
        return count

    def _dismiss_reward_popup(self) -> None:
        close = self.screen.find_template("btn_close")
        if close:
            click(*close)
            action_pause()

    def _close(self) -> None:
        close = self.screen.find_template("btn_close")
        if close:
            click(*close)
        else:
            ax, ay = self.window.abs_coords(0.05, 0.05)
            click(ax, ay)
        action_pause()
