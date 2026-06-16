# Last Asylum: Plague — Farming Bot Setup Guide

---

## Platform overview

| Platform | Method | Script |
|---|---|---|
| **Windows PC** | BlueStacks emulator + Python | `bot.py` |
| **iPhone** | AutoTouch app | `ios/autotouch_farm.lua` |

---

## Windows Setup (BlueStacks + Python)

### Step 1 — Install BlueStacks

1. Download BlueStacks 5 from the official site.
2. Install and open it.
3. Sign in with a Google account.
4. Search for **Last Asylum: Plague** in the Play Store and install it.
5. Open the game and reach the base / home screen before running the bot.

### Step 2 — Install Python

1. Download Python 3.11 or newer from python.org.
2. During install, tick **"Add Python to PATH"**.
3. Open a Command Prompt and confirm: `python --version`

### Step 3 — Install bot dependencies

```cmd
cd path\to\last_asylum_bot
pip install -r requirements.txt
```

### Step 4 — Calibrate (capture template images)

This is the most important step.  The bot uses image recognition to
find buttons, so you need to give it reference images from YOUR screen.

1. Start BlueStacks and open the game at your base screen.
2. Run the calibration tool:
   ```cmd
   python calibrate.py
   ```
3. A window opens showing your whole screen.
4. **Drag a rectangle** around each UI element listed below.
5. After each selection, press **Enter** and type the template name exactly.
6. When all templates are captured, press **Q** to quit.

#### Required templates (capture in this order)

| Name to type | What to select |
|---|---|
| `grain_bubble` | The grain icon / bubble above the Farm when it's full |
| `lumber_bubble` | The lumber bubble above the Lumberyard |
| `herb_bubble` | The herb bubble above the Herb Garden |
| `medicine_bubble` | The medicine bubble above the Pharmacy |
| `btn_collect` | The "Collect" button inside any building menu |
| `btn_produce` | The "Produce" or "Start" button inside a building |
| `btn_close` | The X / close button on any open panel |
| `btn_scavenge` | The Scavenge button on the base screen |
| `tab_world_map` | World Map / Explore icon in the bottom navigation |
| `biome_forest` | The Forest biome card in the scavenge screen |
| `biome_plains` | The Plains biome card |
| `biome_ruins` | The Ruins biome card |
| `btn_send_party` | "Send" / "Go" confirm button on party dispatch |
| `btn_collect_party` | "Collect" on a returned scavenge party |
| `party_returned` | The indicator (!) when a party has returned |
| `btn_hospital` | Hospital building or the hospital tab icon |
| `btn_admit_patient` | "Admit" button in the patient queue |
| `patient_healed` | Healed patient ready-to-collect icon |
| `btn_collect_healed` | "Collect" next to a healed patient |
| `btn_collect_all` | "Collect All" batch button (if present) |
| `tab_quests` | Quests / Missions tab in bottom nav |
| `quest_completed` | Green checkmark on a completed quest row |
| `btn_claim_quest` | "Claim" button on a completed quest |
| `btn_claim_all` | "Claim All" in the quest panel |
| `login_reward` | The daily login reward popup or button |
| `btn_claim_login` | "Claim" button inside the login reward popup |

### Step 5 — Configure the bot

Open `config.py` and review the settings at the top:

- `BLUESTACKS_WINDOW_TITLE` — change to `"LDPlayer"` if you use LDPlayer.
- `COLLECT_FARM`, `RUN_SCAVENGE`, etc. — toggle features on/off.
- `CYCLE_DELAY_MIN / MAX` — how long to wait between farming cycles.
- `SCAVENGE_BIOME_PRIORITY` — which biomes to scavenge first.

To save settings without editing `config.py`, create a file called
`config_local.json` in the same folder:

```json
{
  "CYCLE_DELAY_MIN": 60,
  "CYCLE_DELAY_MAX": 120,
  "RUN_SCAVENGE": false
}
```

### Step 6 — Run the bot

```cmd
# Full loop (runs forever, F12 to stop)
python bot.py

# One cycle only
python bot.py --once

# Only farm and hospital
python bot.py --modules farm hospital

# Only scavenge
python bot.py --modules scavenge
```

**Hotkeys while running:**

| Key | Action |
|---|---|
| `F12` | Stop the bot after the current cycle |
| `F11` | Pause / resume |

---

## iPhone Setup (AutoTouch)

### Step 1 — Install AutoTouch

AutoTouch is available for purchase from the AutoTouch website or the
Cydia-style store.  It does NOT require a jailbreak on recent iOS versions.

### Step 2 — Load the script

1. Connect your iPhone to your PC via USB (or use AutoTouch's file
   browser over Wi-Fi).
2. Copy `ios/autotouch_farm.lua` to the AutoTouch scripts directory.
3. Rename it to something short like `last_asylum.lua`.

### Step 3 — Calibrate coordinates

1. Open Last Asylum: Plague on your iPhone.
2. In AutoTouch, tap **Record** and tap:
   - Each resource building bubble
   - The scavenge button
   - The hospital button
   - The quest tab
3. Stop recording and note the (x, y) printed for each tap.
4. Open `ios/autotouch_farm.lua` in a text editor.
5. Replace the coordinate values near the top of the file with your
   recorded coordinates.

### Step 4 — Run the script

1. Open Last Asylum: Plague, navigate to your base.
2. Switch to AutoTouch and tap the play (▶) button next to your script.
3. The script runs in the background while the game is in the foreground.
4. Tap the stop button in AutoTouch to halt it.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Emulator window not found" | Make sure BlueStacks is open and showing the game |
| Bot clicks in wrong spots | Recalibrate — window may have moved or been resized |
| Template not found errors | Recapture that template; make sure no popup is covering it |
| Bot stops immediately | Check `logs/bot.log` for the error message |
| iPhone script taps wrong area | Recalibrate coordinates for your specific iPhone model |

---

## What the bot farms each cycle

1. **Login reward** — claims the daily login chest on first cycle of the day
2. **Grain / Timber / Herbs / Medicine** — collects all full buildings and restarts production
3. **Hospital** — collects healed patients, admits new ones from the queue
4. **Scavenge** — collects returning parties, sends new parties to priority biomes
5. **Daily quests** — claims all completed quest rewards
