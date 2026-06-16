--[[
  Last Asylum: Plague — iPhone Farming Script
  ============================================
  Device   : iPhone 17 Pro Max
  Screen   : 440 × 956 logical points  (2868 × 1320 px physical, 3× scale, 460 ppi)
  Platform : AutoTouch app (no jailbreak required)

  All coordinates below are in LOGICAL POINTS, not pixels.
  AutoTouch uses logical points so coordinates always match what you see
  on screen regardless of pixel density.

  FINE-TUNING:
    If a tap lands slightly off after a game update or UI change:
    1. Open Last Asylum on your iPhone.
    2. Open AutoTouch → tap Record, tap the element, tap Stop.
    3. The log shows the exact (x, y) for that tap — update the value below.

  RUNNING:
    1. Open the game and navigate to your base / home screen.
    2. Switch to AutoTouch and tap ▶ next to this script.
    3. The script runs in the background while the game is in the foreground.
    4. Press the AutoTouch stop button (■) to halt at any time.
]]

-- =========================================================================
-- CONFIG — iPhone 17 Pro Max (440 × 956 logical points)
-- =========================================================================

local CYCLES           = 0      -- 0 = run forever; set e.g. 10 for 10 cycles
local CYCLE_SLEEP_SEC  = 60     -- seconds between full farming cycles
local TAP_HOLD_MS      = 80     -- milliseconds each tap is held down

-- -------------------------------------------------------------------------
-- Resource building collect bubbles
-- These float above the building when production is full.
-- -------------------------------------------------------------------------

-- Grain Farm bubble  (left-center of base, bubble appears above rooftop)
local FARM_X, FARM_Y           = 232, 600
-- Lumberyard bubble  (right-center of base)
local LUMBER_X, LUMBER_Y       = 325, 673
-- Herb Garden bubble (left side of base)
local HERB_X, HERB_Y           = 146, 685
-- Pharmacy / Apothecary bubble (upper-center of base)
local PHARMACY_X, PHARMACY_Y   = 232, 415

-- -------------------------------------------------------------------------
-- Navigation bar  (row of icons at the very bottom, Y ≈ 915)
-- Five-icon bar — centres from left: 44, 132, 220, 308, 396
-- -------------------------------------------------------------------------

-- World Map / Scavenge button (2nd tab from left)
local SCAVENGE_BTN_X, SCAVENGE_BTN_Y = 87, 915
-- Quests / Missions tab (4th tab from left)
local QUESTS_TAB_X, QUESTS_TAB_Y     = 353, 915

-- -------------------------------------------------------------------------
-- Scavenge screen — biome card centres (three cards across the screen)
-- -------------------------------------------------------------------------
local BIOME_FOREST_X, BIOME_FOREST_Y = 112, 505
local BIOME_PLAINS_X, BIOME_PLAINS_Y = 224, 505
local BIOME_RUINS_X,  BIOME_RUINS_Y  = 336, 505

-- Party dispatch confirm ("Send" / "Go") — center-bottom of the popup
local SEND_X, SEND_Y = 220, 842

-- -------------------------------------------------------------------------
-- Hospital / Sanctuary
-- -------------------------------------------------------------------------

-- Hospital building tap (upper-center of base)
local HOSPITAL_X, HOSPITAL_Y = 220, 415
-- "Collect All" or individual healed-patient collect button
local COLLECT_HEALED_X, COLLECT_HEALED_Y = 220, 617
-- "Admit Patient" button inside the hospital panel
local ADMIT_X, ADMIT_Y = 220, 696

-- -------------------------------------------------------------------------
-- Quest panel
-- -------------------------------------------------------------------------

-- "Claim All" button inside the quest panel (upper-right of list)
local CLAIM_ALL_X, CLAIM_ALL_Y = 381, 224

-- -------------------------------------------------------------------------
-- Common / shared
-- -------------------------------------------------------------------------

-- Generic close / back button — top-left of any popup (below Dynamic Island)
local CLOSE_X, CLOSE_Y = 34, 62

-- Daily login reward popup — tap centre to claim
local LOGIN_CLAIM_X, LOGIN_CLAIM_Y = 220, 561

-- Returned-party base Y position in scavenge screen (spaced by 75 pts)
local PARTY_LIST_X   = 220
local PARTY_LIST_Y0  = 449   -- first returned-party slot
local PARTY_LIST_DY  = 75    -- vertical gap between slots

-- =========================================================================
-- HELPERS
-- =========================================================================

local function tap(x, y)
    touchDown(0, x, y)
    msleep(TAP_HOLD_MS)
    touchUp(0, x, y)
    msleep(300 + math.random(0, 200))
end

local function short_sleep()
    msleep(600 + math.random(0, 400))
end

local function long_sleep()
    msleep(1200 + math.random(0, 600))
end

local function close_panel()
    tap(CLOSE_X, CLOSE_Y)
    short_sleep()
end

-- =========================================================================
-- MODULE: Collect resources from base buildings
-- =========================================================================

local function collect_resources()
    log("[Farm] Collecting base resources")

    -- Tap each resource bubble (if the building is full the bubble is present)
    tap(FARM_X,     FARM_Y)
    tap(LUMBER_X,   LUMBER_Y)
    tap(HERB_X,     HERB_Y)
    tap(PHARMACY_X, PHARMACY_Y)

    long_sleep()
end

-- =========================================================================
-- MODULE: Scavenge
-- =========================================================================

local function run_scavenge()
    log("[Scavenge] Opening scavenge screen")
    tap(SCAVENGE_BTN_X, SCAVENGE_BTN_Y)
    long_sleep()

    -- Collect any returned parties (up to 3 slots visible at once)
    for i = 0, 2 do
        tap(PARTY_LIST_X, PARTY_LIST_Y0 + i * PARTY_LIST_DY)
        short_sleep()
        close_panel()
    end

    -- Send a new party to the forest biome
    tap(BIOME_FOREST_X, BIOME_FOREST_Y)
    long_sleep()
    tap(SEND_X, SEND_Y)
    long_sleep()

    close_panel()
    log("[Scavenge] Done")
end

-- =========================================================================
-- MODULE: Hospital
-- =========================================================================

local function run_hospital()
    log("[Hospital] Opening hospital")
    tap(HOSPITAL_X, HOSPITAL_Y)
    long_sleep()

    -- Collect all healed patients
    tap(COLLECT_HEALED_X, COLLECT_HEALED_Y)
    short_sleep()
    close_panel()

    -- Admit new patients
    for i = 1, 5 do
        tap(ADMIT_X, ADMIT_Y)
        short_sleep()
        -- Confirm any patient-selection popup that appears
        tap(SEND_X, SEND_Y)
        short_sleep()
    end

    close_panel()
    log("[Hospital] Done")
end

-- =========================================================================
-- MODULE: Daily quests
-- =========================================================================

local function run_quests()
    log("[Quests] Opening quest panel")
    tap(QUESTS_TAB_X, QUESTS_TAB_Y)
    long_sleep()

    -- Claim all completed quests
    tap(CLAIM_ALL_X, CLAIM_ALL_Y)
    long_sleep()
    close_panel()

    log("[Quests] Done")
end

-- =========================================================================
-- MODULE: Login reward (only relevant on first run of the day)
-- =========================================================================

local function claim_login_reward()
    -- The login reward popup usually appears on launch.
    -- We tap the claim position and dismiss it.
    tap(LOGIN_CLAIM_X, LOGIN_CLAIM_Y)
    short_sleep()
    close_panel()
end

-- =========================================================================
-- MAIN LOOP
-- =========================================================================

log("=== Last Asylum Farming Bot started ===")
log("Cycles: " .. (CYCLES == 0 and "infinite" or tostring(CYCLES)))

local cycle = 0
while CYCLES == 0 or cycle < CYCLES do
    cycle = cycle + 1
    log("--- Cycle " .. cycle .. " start ---")

    claim_login_reward()
    collect_resources()
    run_hospital()
    run_scavenge()
    run_quests()

    log("--- Cycle " .. cycle .. " complete — sleeping " .. CYCLE_SLEEP_SEC .. "s ---")
    msleep(CYCLE_SLEEP_SEC * 1000)
end

log("=== Bot finished after " .. cycle .. " cycles ===")
