"""
Daily Quests & Login Reward Module
Claims all completed daily quest rewards and the daily login chest.

Templates required:
  templates/tab_quests.png        — quests / missions tab icon
  templates/quest_completed.png   — green checkmark or "Claim" on a quest row
  templates/btn_claim_quest.png   — "Claim" button in a quest row
  templates/btn_claim_all.png     — "Claim All" batch button (if present)
  templates/login_reward.png      — daily login reward popup / button
  templates/btn_claim_login.png
  templates/btn_close.png
"""

import config as cfg
from core.screen import ScreenCapture
from core.input import click, action_pause, scroll
from core.window import GameWindow
from utils.logger import log


class QuestModule:
    def __init__(self, screen: ScreenCapture, window: GameWindow):
        self.screen = screen
        self.window = window

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        if cfg.RUN_LOGIN_REWARD:
            self._claim_login_reward()
        if cfg.RUN_DAILY_QUESTS:
            self._claim_daily_quests()

    # ------------------------------------------------------------------
    # Login reward
    # ------------------------------------------------------------------

    def _claim_login_reward(self) -> None:
        log.info("[Quests] Checking login reward")
        pos = self.screen.find_template("login_reward")
        if not pos:
            log.debug("[Quests] No login reward popup visible")
            return

        click(*pos)
        action_pause()

        claim = self.screen.find_template("btn_claim_login") or \
                self.screen.find_template("btn_collect")
        if claim:
            click(*claim)
            action_pause()

        self._close()
        log.info("[Quests] Login reward claimed")

    # ------------------------------------------------------------------
    # Daily quests
    # ------------------------------------------------------------------

    def _claim_daily_quests(self) -> None:
        log.info("[Quests] Opening quest panel")
        tab = self.screen.find_template("tab_quests")
        if not tab:
            log.warning("[Quests] Quest tab not found — skipping")
            return

        click(*tab)
        action_pause()

        # Try "Claim All" first
        claim_all = self.screen.find_template("btn_claim_all")
        if claim_all:
            click(*claim_all)
            action_pause()
            self._close()
            log.info("[Quests] All quest rewards claimed via Claim All")
            return

        # Scroll through the list and claim individually
        claimed = 0
        for _ in range(20):   # max 20 quests
            screenshot = self.screen.grab()
            pos = self.screen.find_template("btn_claim_quest", screenshot) or \
                  self.screen.find_template("quest_completed", screenshot)
            if not pos:
                break
            click(*pos)
            action_pause()
            # Dismiss any reward popup
            close = self.screen.find_template("btn_close")
            if close:
                click(*close)
                action_pause()
            claimed += 1

        if claimed == 0:
            log.info("[Quests] No completed quests to claim")
        else:
            log.info("[Quests] Claimed %d quest rewards", claimed)

        self._close()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _close(self) -> None:
        pos = self.screen.find_template("btn_close")
        if pos:
            click(*pos)
        else:
            ax, ay = self.window.abs_coords(0.05, 0.05)
            click(ax, ay)
        action_pause()
