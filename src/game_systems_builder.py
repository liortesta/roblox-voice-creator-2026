"""
Game Systems Builder - מערכות משחק שלמות בפקודה אחת
=====================================================
"תוסיף מערכת חיים" → מייצר Lua שלם שמוסיף Health, GUI, respawn
"תוסיף חנות" → מייצר חנות עם GUI ומוצרים
"תוסיף מערכת כסף" → מייצר currency system
"""

from typing import Dict, Any, Optional


# ============================================
# GAME SYSTEM TEMPLATES
# ============================================

GAME_SYSTEMS = {
    "health": {
        "hebrew_names": ["חיים", "בריאות", "HP", "מערכת חיים"],
        "description": "מערכת חיים עם leaderboard ו-respawn",
        "lua": """
-- === HEALTH SYSTEM ===
local Players = game:GetService("Players")

-- ServerScriptService equivalent: put in workspace as a system script
local healthScript = Instance.new("Script")
healthScript.Name = "HealthSystem"
healthScript.Source = [====[
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    -- Leaderstats
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
    end

    -- Health display
    local healthVal = leaderstats:FindFirstChild("Health")
    if not healthVal then
        healthVal = Instance.new("IntValue")
        healthVal.Name = "Health"
        healthVal.Value = 100
        healthVal.Parent = leaderstats
    end

    -- Track health changes
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            humanoid.HealthChanged:Connect(function(health)
                healthVal.Value = math.floor(health)
            end)

            humanoid.Died:Connect(function()
                healthVal.Value = 0
                task.wait(3)
                -- Respawn
                player:LoadCharacter()
            end)
        end
    end)
end)

-- Init existing players
for _, player in pairs(Players:GetPlayers()) do
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
    end
    if not leaderstats:FindFirstChild("Health") then
        local hv = Instance.new("IntValue")
        hv.Name = "Health"
        hv.Value = 100
        hv.Parent = leaderstats
    end
end

print("Health System Active!")
]====]
healthScript.Parent = workspace

print("✅ מערכת חיים הותקנה! (Health + Respawn)")
"""
    },

    "currency": {
        "hebrew_names": ["כסף", "מטבעות", "coins", "מערכת כסף", "כלכלה"],
        "description": "מערכת מטבעות/כסף עם leaderboard",
        "lua": """
-- === CURRENCY SYSTEM ===
local currencyScript = Instance.new("Script")
currencyScript.Name = "CurrencySystem"
currencyScript.Source = [====[
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
    end

    if not leaderstats:FindFirstChild("Coins") then
        local coins = Instance.new("IntValue")
        coins.Name = "Coins"
        coins.Value = 0
        coins.Parent = leaderstats
    end

    if not leaderstats:FindFirstChild("Score") then
        local score = Instance.new("IntValue")
        score.Name = "Score"
        score.Value = 0
        score.Parent = leaderstats
    end
end)

-- Init existing players
for _, player in pairs(Players:GetPlayers()) do
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then
        leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player
    end
    if not leaderstats:FindFirstChild("Coins") then
        local c = Instance.new("IntValue")
        c.Name = "Coins"
        c.Value = 0
        c.Parent = leaderstats
    end
    if not leaderstats:FindFirstChild("Score") then
        local s = Instance.new("IntValue")
        s.Name = "Score"
        s.Value = 0
        s.Parent = leaderstats
    end
end

print("Currency System Active!")
]====]
currencyScript.Parent = workspace

print("✅ מערכת מטבעות הותקנה! (Coins + Score)")
"""
    },

    "coin_spawner": {
        "hebrew_names": ["מטבעות לאיסוף", "פזר מטבעות", "מטבעות באוויר"],
        "description": "יוצר מטבעות מפוזרים שאפשר לאסוף",
        "lua": """
-- === COIN SPAWNER ===
local parts = {}
local numCoins = {count}
local areaSize = {area}

for i = 1, numCoins do
    local coin = Instance.new("Part")
    coin.Name = "Coin_" .. i
    coin.Shape = Enum.PartType.Cylinder
    coin.Size = Vector3.new(0.5, 3, 3)
    coin.Position = Vector3.new(
        math.random(-areaSize, areaSize),
        3,
        math.random(-areaSize, areaSize)
    )
    coin.Orientation = Vector3.new(0, 0, 90)
    coin.BrickColor = BrickColor.new("Gold")
    coin.Material = Enum.Material.Neon
    coin.Anchored = true
    coin.CanCollide = false
    coin.Parent = workspace

    -- Collect script
    local script = Instance.new("Script")
    script.Name = "CollectScript"
    script.Source = [====[
local Players = game:GetService("Players")
local coin = script.Parent
local collected = {}

-- Spin animation
task.spawn(function()
    while coin and coin.Parent do
        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)
        task.wait(0.03)
    end
end)

coin.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not collected[player.UserId] then
        collected[player.UserId] = true

        -- Add coins
        local ls = player:FindFirstChild("leaderstats")
        if ls then
            local coins = ls:FindFirstChild("Coins")
            if coins then coins.Value = coins.Value + 1 end
        end

        -- Hide
        coin.Transparency = 1
        task.wait(10)
        if coin and coin.Parent then
            coin.Transparency = 0
            collected[player.UserId] = nil
        end
    end
end)
]====]
    script.Parent = coin

    table.insert(parts, coin)
end

game.Selection:Set(parts)
print("✅ " .. numCoins .. " מטבעות נפוזרו!")
""",
        "params": {"count": 20, "area": 50}
    },

    "race": {
        "hebrew_names": ["מירוץ", "מסלול מירוצים", "race", "תחרות"],
        "description": "מערכת מירוץ עם התחלה וסוף",
        "lua": """
-- === RACE SYSTEM ===
local parts = {}

-- Start line
local startLine = Instance.new("Part")
startLine.Name = "RaceStart"
startLine.Size = Vector3.new(30, 1, 5)
startLine.Position = Vector3.new(0, 0.5, 0)
startLine.BrickColor = BrickColor.new("Bright green")
startLine.Material = Enum.Material.Neon
startLine.Anchored = true
startLine.Parent = workspace
table.insert(parts, startLine)

-- Finish line
local finishLine = Instance.new("Part")
finishLine.Name = "RaceFinish"
finishLine.Size = Vector3.new(30, 1, 5)
finishLine.Position = Vector3.new(0, 0.5, 200)
finishLine.BrickColor = BrickColor.new("Bright red")
finishLine.Material = Enum.Material.Neon
finishLine.Anchored = true
finishLine.Parent = workspace
table.insert(parts, finishLine)

-- Race track
for i = 1, 8 do
    local track = Instance.new("Part")
    track.Name = "Track_" .. i
    track.Size = Vector3.new(30, 0.5, 25)
    track.Position = Vector3.new(0, 0.25, i * 25 - 12.5)
    track.BrickColor = BrickColor.new("Medium stone grey")
    track.Material = Enum.Material.Concrete
    track.Anchored = true
    track.Parent = workspace
    table.insert(parts, track)
end

-- Race script
local raceScript = Instance.new("Script")
raceScript.Name = "RaceManager"
raceScript.Source = [====[
local Players = game:GetService("Players")
local startPart = workspace:FindFirstChild("RaceStart")
local finishPart = workspace:FindFirstChild("RaceFinish")

if not startPart or not finishPart then return end

local racing = {}

startPart.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not racing[player.UserId] then
        racing[player.UserId] = tick()
        print(player.Name .. " started the race!")
    end
end)

finishPart.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and racing[player.UserId] then
        local raceTime = tick() - racing[player.UserId]
        racing[player.UserId] = nil
        local timeStr = string.format("%.2f", raceTime)
        print(player.Name .. " finished in " .. timeStr .. " seconds!")

        -- Update score
        local ls = player:FindFirstChild("leaderstats")
        if ls then
            local score = ls:FindFirstChild("Score")
            if score then
                score.Value = score.Value + math.floor(100 / raceTime)
            end
        end
    end
end)
]====]
raceScript.Parent = workspace

game.Selection:Set(parts)
print("✅ מסלול מירוצים מוכן! (Start → Finish)")
"""
    },

    "respawn": {
        "hebrew_names": ["רספאון", "respawn", "חזרה לחיים", "תחייה"],
        "description": "מערכת respawn - חוזר לחיים אחרי מוות",
        "lua": """
-- === RESPAWN SYSTEM ===
local respawnScript = Instance.new("Script")
respawnScript.Name = "RespawnSystem"
respawnScript.Source = [====[
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        local humanoid = character:WaitForChild("Humanoid", 10)
        if humanoid then
            humanoid.Died:Connect(function()
                task.wait(3)
                player:LoadCharacter()
            end)
        end
    end)
end)

print("Respawn System Active!")
]====]
respawnScript.Parent = workspace

print("✅ מערכת Respawn הותקנה! (חוזר לחיים אחרי 3 שניות)")
"""
    },

    "day_night": {
        "hebrew_names": ["יום לילה", "מחזור יום", "day night", "שעות"],
        "description": "מחזור יום-לילה אוטומטי",
        "lua": """
-- === DAY/NIGHT CYCLE ===
local Lighting = game:GetService("Lighting")

local cycleScript = Instance.new("Script")
cycleScript.Name = "DayNightCycle"
cycleScript.Source = [====[
local Lighting = game:GetService("Lighting")
local speed = {speed}

while true do
    Lighting.ClockTime = (Lighting.ClockTime + 0.01 * speed) % 24
    task.wait(0.1)
end
]====]
cycleScript.Parent = workspace

print("✅ מחזור יום/לילה פעיל!")
""",
        "params": {"speed": 1}
    },
}


# ============================================
# HEBREW DETECTION
# ============================================

def find_game_system(text: str) -> Optional[Dict[str, Any]]:
    """
    Find matching game system for Hebrew command.

    Args:
        text: Hebrew text like "תוסיף מערכת חיים"

    Returns:
        System dict with lua code, or None
    """
    text_lower = text.lower().strip()

    for system_name, system in GAME_SYSTEMS.items():
        for hebrew_name in system["hebrew_names"]:
            if hebrew_name in text_lower:
                return {
                    "name": system_name,
                    "hebrew": hebrew_name,
                    "description": system["description"],
                    "lua": system["lua"],
                    "params": system.get("params", {}),
                }

    return None


def generate_game_system_lua(system_name: str, custom_params: Dict[str, Any] = None) -> Optional[str]:
    """
    Generate Lua code for a game system.

    Args:
        system_name: e.g. "health", "currency", "race"
        custom_params: override default parameters

    Returns:
        Lua code string
    """
    system = GAME_SYSTEMS.get(system_name)
    if not system:
        return None

    lua = system["lua"]
    params = system.get("params", {})

    if custom_params:
        params.update(custom_params)

    for key, value in params.items():
        lua = lua.replace(f"{{{key}}}", str(value))

    return lua


def list_game_systems() -> Dict[str, str]:
    """List all available game systems."""
    return {
        name: system["description"]
        for name, system in GAME_SYSTEMS.items()
    }


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Game Systems Builder")
    print("=" * 60)

    tests = [
        "תוסיף מערכת חיים",
        "תוסיף מטבעות",
        "תעשה מירוץ",
        "תוסיף respawn",
        "תעשה מחזור יום לילה",
    ]

    for test in tests:
        result = find_game_system(test)
        if result:
            print(f"\n✅ '{test}' → {result['name']} ({result['description']})")
            lua = generate_game_system_lua(result['name'])
            print(f"   Generated {len(lua)} chars of Lua")
        else:
            print(f"\n❌ '{test}' → No match")
