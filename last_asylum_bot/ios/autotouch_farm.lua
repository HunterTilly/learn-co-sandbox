--[[
  Last Asylum: Plague — iPhone Farming Script
  ============================================
  Platform : iPhone (any model) via AutoTouch app
  App store : AutoTouch is available as a paid app. Install it, then
              load this script from the AutoTouch script browser.

  HOW TO CALIBRATE:
    1. Open Last Asylum: Plague on your iPhone.
    2. Open AutoTouch and start recording.
    3. Tap each building / button once in game order (collect grain,
       collect lumber, collect herbs, collect medicine, open quests,
       claim quests).
    4. Stop recording.  AutoTouch shows the (x, y) coordinates.
    5. Replace the coordinate values below with your recorded ones.
       Coordinates are in logical points (not pixels) — they scale
       automatically across iPhone models.

  DEFAULT COORDS assume iPhone 14 Pro (393 × 852 logical points).
  Scale for other models:
    iPhone SE 3rd gen   : ×0.74 / ×0.82
    iPhone 15 Pro Max   : ×1.04 / ×1.04
    iPhone 13 mini      : ×0.74 / ×0.85

  RUNNING:
    - Open the game, navigate to your base / home screen.
    - Switch to AutoTouch and tap ▶ to run this script.
    - The script loops indefinitely; press the AutoTouch stop button to halt.
]]

-- =========================================================================
-- CONFIG — edit these to match YOUR screen
-- =========================================================================

local CYCLES           = 0      -- 0 = run forever; set e.g. 10 for 10 cycles
local CYCLE_SLEEP_SEC  = 60     -- seconds between full cycles
local TAP_HOLD_MS      = 80     -- milliseconds each tap is held down

-- Grain Farm collect bubble position
local FARM_X, FARM_Y           = 207, 535
-- Lumberyard collect bubble
local LUMBER_X, LUMBER_Y       = 290, 600
-- Herb Garden collect bubble
local HERB_X, HERB_Y           = 130, 610
-- Pharmacy collect bubble
local PHARMACY_X, PHARMACY_Y   = 207, 370

-- Scavenge / World Map button (bottom navigation)
local SCAVENGE_BTN_X, SCAVENGE_BTN_Y = 78, 815

-- Biome selection — these are the centres of the biome cards
local BIOME_FOREST_X, BIOME_FOREST_Y = 100, 450
local BIOME_PLAINS_X, BIOME_PLAINS_Y = 200, 450
local BIOME_RUINS_X,  BIOME_RUINS_Y  = 300, 450

-- "Send Party" confirm button
local SEND_X, SEND_Y = 196, 750

-- Hospital button
local HOSPITAL_X, HOSPITAL_Y = 196, 370

-- "Collect Healed" / "Collect All" button inside hospital
local COLLECT_HEALED_X, COLLECT_HEALED_Y = 196, 550

-- "Admit Patient" button inside hospital
local ADMIT_X, ADMIT_Y = 196, 620

-- Daily quests tab
local QUESTS_TAB_X, QUESTS_TAB_Y = 315, 815

-- "Claim All" quest button
local CLAIM_ALL_X, CLAIM_ALL_Y = 340, 200

-- Generic close / back button (top-left)
local CLOSE_X, CLOSE_Y = 30, 55

-- Login reward — tapping the screen dismisses/claims it
local LOGIN_CLAIM_X, LOGIN_CLAIM_Y = 196, 500

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

    -- Collect any returned parties first
    -- (Tap the area where returned party indicators appear — adjust as needed)
    for i = 1, 3 do
        tap(196, 400 + i * 60)
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
        -- Confirm selection popup if present
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
