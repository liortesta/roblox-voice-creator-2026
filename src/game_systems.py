# -*- coding: utf-8 -*-
"""
Game Systems Module - מערכות משחק מלאות
=========================================

מודול ליצירת מערכות משחק שלמות:
- מערכת חיים (Lives)
- מערכת בריאות (Health)
- מערכת ניקוד (Score)
- מערכת שלבים (Levels)
- מערכת משימות (Quests)
- מערכת אויבים (Enemies)
- מערכת פאוור-אפים (Power-ups)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto


class GameSystemType(Enum):
    """סוגי מערכות משחק"""
    LIVES = auto()          # חיים
    HEALTH = auto()         # בריאות
    SCORE = auto()          # ניקוד
    LEVELS = auto()         # שלבים
    QUESTS = auto()         # משימות
    ENEMIES = auto()        # אויבים
    COLLECTIBLES = auto()   # פריטים לאיסוף
    TIMER = auto()          # טיימר
    CHECKPOINT = auto()     # נקודות שמירה


@dataclass
class GameConfig:
    """הגדרות משחק"""
    name: str = "MyGame"
    max_lives: int = 3
    max_health: int = 100
    starting_level: int = 1
    total_levels: int = 5
    time_limit: int = 0  # 0 = ללא הגבלה
    collectibles_to_win: int = 10
    enemies_count: int = 5


class GameSystemsGenerator:
    """
    מחולל מערכות משחק.
    יוצר קוד Lua מלא עבור מערכות משחק שלמות.
    """

    def __init__(self, on_status=None):
        self.on_status = on_status or print

    # ========================================
    # מערכת ליבה - GameManager
    # ========================================

    def create_game_manager(self, config: GameConfig) -> str:
        """יצירת GameManager - הלב של המשחק"""
        return f'''
-- ==========================================
-- GameManager - מנהל המשחק הראשי
-- ==========================================

local GameManager = {{}}
GameManager.__index = GameManager

-- הגדרות משחק
GameManager.Config = {{
    GameName = "{config.name}",
    MaxLives = {config.max_lives},
    MaxHealth = {config.max_health},
    StartingLevel = {config.starting_level},
    TotalLevels = {config.total_levels},
    TimeLimit = {config.time_limit},
    CollectiblesToWin = {config.collectibles_to_win}
}}

-- מצב משחק
GameManager.State = {{
    Lives = GameManager.Config.MaxLives,
    Health = GameManager.Config.MaxHealth,
    Score = 0,
    CurrentLevel = GameManager.Config.StartingLevel,
    Collectibles = 0,
    IsPlaying = false,
    IsPaused = false,
    GameOver = false,
    Victory = false
}}

-- אירועים
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Events = Instance.new("Folder")
Events.Name = "GameEvents"
Events.Parent = ReplicatedStorage

local function createEvent(name)
    local event = Instance.new("BindableEvent")
    event.Name = name
    event.Parent = Events
    return event
end

GameManager.Events = {{
    OnLivesChanged = createEvent("OnLivesChanged"),
    OnHealthChanged = createEvent("OnHealthChanged"),
    OnScoreChanged = createEvent("OnScoreChanged"),
    OnLevelChanged = createEvent("OnLevelChanged"),
    OnGameOver = createEvent("OnGameOver"),
    OnVictory = createEvent("OnVictory"),
    OnCollectiblePickup = createEvent("OnCollectiblePickup")
}}

-- פונקציות ליבה
function GameManager:StartGame()
    self.State.IsPlaying = true
    self.State.GameOver = false
    self.State.Victory = false
    self.State.Lives = self.Config.MaxLives
    self.State.Health = self.Config.MaxHealth
    self.State.Score = 0
    self.State.CurrentLevel = self.Config.StartingLevel
    self.State.Collectibles = 0
    print("🎮 משחק התחיל!")
end

function GameManager:TakeDamage(amount)
    if self.State.GameOver then return end

    self.State.Health = math.max(0, self.State.Health - amount)
    self.Events.OnHealthChanged:Fire(self.State.Health)

    if self.State.Health <= 0 then
        self:LoseLife()
    end
end

function GameManager:Heal(amount)
    self.State.Health = math.min(self.Config.MaxHealth, self.State.Health + amount)
    self.Events.OnHealthChanged:Fire(self.State.Health)
end

function GameManager:LoseLife()
    self.State.Lives = self.State.Lives - 1
    self.Events.OnLivesChanged:Fire(self.State.Lives)

    if self.State.Lives <= 0 then
        self:GameOver()
    else
        self.State.Health = self.Config.MaxHealth
        print("💔 נשארו " .. self.State.Lives .. " חיים")
    end
end

function GameManager:AddLife()
    self.State.Lives = self.State.Lives + 1
    self.Events.OnLivesChanged:Fire(self.State.Lives)
    print("❤️ קיבלת חיים! סה״כ: " .. self.State.Lives)
end

function GameManager:AddScore(points)
    self.State.Score = self.State.Score + points
    self.Events.OnScoreChanged:Fire(self.State.Score)
end

function GameManager:CollectItem()
    self.State.Collectibles = self.State.Collectibles + 1
    self.Events.OnCollectiblePickup:Fire(self.State.Collectibles)
    self:AddScore(100)

    if self.State.Collectibles >= self.Config.CollectiblesToWin then
        self:NextLevel()
    end
end

function GameManager:NextLevel()
    self.State.CurrentLevel = self.State.CurrentLevel + 1
    self.Events.OnLevelChanged:Fire(self.State.CurrentLevel)

    if self.State.CurrentLevel > self.Config.TotalLevels then
        self:Victory()
    else
        self.State.Collectibles = 0
        self.State.Health = self.Config.MaxHealth
        print("🎉 שלב " .. self.State.CurrentLevel .. "!")
    end
end

function GameManager:GameOver()
    self.State.GameOver = true
    self.State.IsPlaying = false
    self.Events.OnGameOver:Fire()
    print("💀 Game Over! ניקוד סופי: " .. self.State.Score)
end

function GameManager:Victory()
    self.State.Victory = true
    self.State.IsPlaying = false
    self.Events.OnVictory:Fire()
    print("🏆 ניצחת! ניקוד סופי: " .. self.State.Score)
end

-- שמירה גלובלית
_G.GameManager = GameManager
print("✅ GameManager נטען!")
'''

    # ========================================
    # מערכת UI
    # ========================================

    def create_game_ui(self, config: GameConfig) -> str:
        """יצירת UI למשחק"""
        return f'''
-- ==========================================
-- Game UI - ממשק משתמש
-- ==========================================

local Players = game:GetService("Players")
local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

-- יצירת ScreenGui
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "GameUI"
screenGui.Parent = playerGui

-- פריים ראשי
local mainFrame = Instance.new("Frame")
mainFrame.Name = "HUD"
mainFrame.Size = UDim2.new(1, 0, 0, 60)
mainFrame.Position = UDim2.new(0, 0, 0, 0)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
mainFrame.BackgroundTransparency = 0.3
mainFrame.Parent = screenGui

-- תצוגת חיים
local livesLabel = Instance.new("TextLabel")
livesLabel.Name = "Lives"
livesLabel.Size = UDim2.new(0, 150, 1, 0)
livesLabel.Position = UDim2.new(0, 10, 0, 0)
livesLabel.BackgroundTransparency = 1
livesLabel.Text = "❤️ x {config.max_lives}"
livesLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
livesLabel.TextSize = 24
livesLabel.Font = Enum.Font.GothamBold
livesLabel.Parent = mainFrame

-- תצוגת בריאות
local healthFrame = Instance.new("Frame")
healthFrame.Name = "HealthBar"
healthFrame.Size = UDim2.new(0, 200, 0, 20)
healthFrame.Position = UDim2.new(0, 170, 0.5, -10)
healthFrame.BackgroundColor3 = Color3.fromRGB(50, 50, 50)
healthFrame.Parent = mainFrame

local healthFill = Instance.new("Frame")
healthFill.Name = "Fill"
healthFill.Size = UDim2.new(1, 0, 1, 0)
healthFill.BackgroundColor3 = Color3.fromRGB(0, 255, 100)
healthFill.Parent = healthFrame

-- תצוגת ניקוד
local scoreLabel = Instance.new("TextLabel")
scoreLabel.Name = "Score"
scoreLabel.Size = UDim2.new(0, 200, 1, 0)
scoreLabel.Position = UDim2.new(0.5, -100, 0, 0)
scoreLabel.BackgroundTransparency = 1
scoreLabel.Text = "⭐ 0"
scoreLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
scoreLabel.TextSize = 28
scoreLabel.Font = Enum.Font.GothamBold
scoreLabel.Parent = mainFrame

-- תצוגת שלב
local levelLabel = Instance.new("TextLabel")
levelLabel.Name = "Level"
levelLabel.Size = UDim2.new(0, 150, 1, 0)
levelLabel.Position = UDim2.new(1, -160, 0, 0)
levelLabel.BackgroundTransparency = 1
levelLabel.Text = "שלב 1"
levelLabel.TextColor3 = Color3.fromRGB(100, 200, 255)
levelLabel.TextSize = 24
levelLabel.Font = Enum.Font.GothamBold
levelLabel.Parent = mainFrame

-- עדכון UI
local function updateUI()
    local gm = _G.GameManager
    if not gm then return end

    livesLabel.Text = "❤️ x " .. gm.State.Lives
    healthFill.Size = UDim2.new(gm.State.Health / gm.Config.MaxHealth, 0, 1, 0)
    scoreLabel.Text = "⭐ " .. gm.State.Score
    levelLabel.Text = "שלב " .. gm.State.CurrentLevel
end

-- חיבור לאירועים
local events = game.ReplicatedStorage:WaitForChild("GameEvents")
events.OnLivesChanged.Event:Connect(updateUI)
events.OnHealthChanged.Event:Connect(updateUI)
events.OnScoreChanged.Event:Connect(updateUI)
events.OnLevelChanged.Event:Connect(updateUI)

print("✅ Game UI נטען!")
'''

    # ========================================
    # מערכת פריטים לאיסוף
    # ========================================

    def create_collectibles(self, count: int = 10, value: int = 100) -> str:
        """יצירת פריטים לאיסוף"""
        return f'''
-- ==========================================
-- Collectibles - פריטים לאיסוף
-- ==========================================

local collectibles = {{}}

local function createCollectible(position)
    local coin = Instance.new("Part")
    coin.Name = "Collectible"
    coin.Shape = Enum.PartType.Cylinder
    coin.Size = Vector3.new(0.3, 2, 2)
    coin.Position = position
    coin.Anchored = true
    coin.CanCollide = false
    coin.BrickColor = BrickColor.new("Bright yellow")
    coin.Material = Enum.Material.Neon
    coin.CFrame = coin.CFrame * CFrame.Angles(0, 0, math.rad(90))
    coin.Parent = workspace

    -- סיבוב
    spawn(function()
        while coin.Parent do
            coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(2), 0)
            wait(0.03)
        end
    end)

    -- נגיעה
    coin.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid and coin.Parent then
            coin:Destroy()
            if _G.GameManager then
                _G.GameManager:CollectItem()
            end
        end
    end)

    table.insert(collectibles, coin)
    return coin
end

-- יצירת {count} פריטים במיקומים רנדומליים
for i = 1, {count} do
    local x = math.random(-50, 50)
    local z = math.random(-50, 50)
    createCollectible(Vector3.new(x, 3, z))
end

print("✅ נוצרו " .. {count} .. " פריטים לאיסוף!")
'''

    # ========================================
    # מערכת אויבים
    # ========================================

    def create_enemies(self, count: int = 5, damage: int = 20) -> str:
        """יצירת אויבים"""
        return f'''
-- ==========================================
-- Enemies - אויבים
-- ==========================================

local enemies = {{}}

local function createEnemy(position)
    -- גוף האויב
    local enemy = Instance.new("Part")
    enemy.Name = "Enemy"
    enemy.Size = Vector3.new(4, 6, 4)
    enemy.Position = position
    enemy.Anchored = false
    enemy.BrickColor = BrickColor.new("Bright red")
    enemy.Material = Enum.Material.SmoothPlastic
    enemy.Parent = workspace

    -- עיניים
    local eye1 = Instance.new("Part")
    eye1.Size = Vector3.new(0.5, 0.5, 0.5)
    eye1.Position = position + Vector3.new(0.8, 1.5, -1.8)
    eye1.BrickColor = BrickColor.new("Black")
    eye1.Parent = enemy
    local weld1 = Instance.new("WeldConstraint")
    weld1.Part0 = enemy
    weld1.Part1 = eye1
    weld1.Parent = enemy

    -- AI פשוט - רדיפה
    local lastHit = 0
    spawn(function()
        while enemy.Parent do
            wait(0.5)
            local players = game.Players:GetPlayers()
            local closest = nil
            local closestDist = 50

            for _, player in ipairs(players) do
                local char = player.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    local dist = (char.HumanoidRootPart.Position - enemy.Position).Magnitude
                    if dist < closestDist then
                        closest = char
                        closestDist = dist
                    end
                end
            end

            if closest then
                local direction = (closest.HumanoidRootPart.Position - enemy.Position).Unit
                enemy.CFrame = enemy.CFrame + direction * 0.5
            end
        end
    end)

    -- פגיעה בשחקן
    enemy.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid and tick() - lastHit > 1 then
            lastHit = tick()
            if _G.GameManager then
                _G.GameManager:TakeDamage({damage})
            end
        end
    end)

    table.insert(enemies, enemy)
    return enemy
end

-- יצירת {count} אויבים
for i = 1, {count} do
    local x = math.random(-40, 40)
    local z = math.random(-40, 40)
    createEnemy(Vector3.new(x, 5, z))
end

print("✅ נוצרו " .. {count} .. " אויבים!")
'''

    # ========================================
    # מערכת פאוור-אפים
    # ========================================

    def create_powerups(self) -> str:
        """יצירת פאוור-אפים"""
        return '''
-- ==========================================
-- Power-ups - כוחות מיוחדים
-- ==========================================

local PowerUps = {}

-- חיים נוספים
function PowerUps.createExtraLife(position)
    local heart = Instance.new("Part")
    heart.Name = "ExtraLife"
    heart.Size = Vector3.new(2, 2, 1)
    heart.Position = position
    heart.Anchored = true
    heart.CanCollide = false
    heart.BrickColor = BrickColor.new("Bright red")
    heart.Material = Enum.Material.Neon
    heart.Parent = workspace

    -- אנימציה
    spawn(function()
        local startY = position.Y
        local t = 0
        while heart.Parent do
            t = t + 0.05
            heart.Position = Vector3.new(position.X, startY + math.sin(t) * 0.5, position.Z)
            wait(0.03)
        end
    end)

    heart.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid and heart.Parent then
            heart:Destroy()
            if _G.GameManager then
                _G.GameManager:AddLife()
            end
        end
    end)

    return heart
end

-- ריפוי
function PowerUps.createHealthPack(position)
    local pack = Instance.new("Part")
    pack.Name = "HealthPack"
    pack.Size = Vector3.new(2, 2, 2)
    pack.Position = position
    pack.Anchored = true
    pack.CanCollide = false
    pack.BrickColor = BrickColor.new("Bright green")
    pack.Material = Enum.Material.Neon
    pack.Parent = workspace

    -- סימן +
    local decal = Instance.new("Decal")
    decal.Texture = "rbxassetid://139478873"  -- סימן +
    decal.Face = Enum.NormalId.Front
    decal.Parent = pack

    pack.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid and pack.Parent then
            pack:Destroy()
            if _G.GameManager then
                _G.GameManager:Heal(50)
            end
        end
    end)

    return pack
end

-- בונוס ניקוד
function PowerUps.createScoreBonus(position, points)
    points = points or 500
    local star = Instance.new("Part")
    star.Name = "ScoreBonus"
    star.Size = Vector3.new(2, 2, 0.5)
    star.Position = position
    star.Anchored = true
    star.CanCollide = false
    star.BrickColor = BrickColor.new("New Yeller")
    star.Material = Enum.Material.Neon
    star.Parent = workspace

    -- סיבוב
    spawn(function()
        while star.Parent do
            star.CFrame = star.CFrame * CFrame.Angles(0, math.rad(3), 0)
            wait(0.03)
        end
    end)

    star.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid and star.Parent then
            star:Destroy()
            if _G.GameManager then
                _G.GameManager:AddScore(points)
            end
        end
    end)

    return star
end

_G.PowerUps = PowerUps
print("✅ PowerUps מוכן!")
'''

    # ========================================
    # מערכת Checkpoint
    # ========================================

    def create_checkpoints(self) -> str:
        """יצירת נקודות שמירה"""
        return '''
-- ==========================================
-- Checkpoints - נקודות שמירה
-- ==========================================

local Checkpoints = {}
local currentCheckpoint = nil

function Checkpoints.create(position, number)
    local checkpoint = Instance.new("Part")
    checkpoint.Name = "Checkpoint_" .. number
    checkpoint.Size = Vector3.new(10, 0.5, 10)
    checkpoint.Position = position
    checkpoint.Anchored = true
    checkpoint.CanCollide = false
    checkpoint.BrickColor = BrickColor.new("Lime green")
    checkpoint.Material = Enum.Material.Neon
    checkpoint.Transparency = 0.5
    checkpoint.Parent = workspace

    -- מספר
    local billboard = Instance.new("BillboardGui")
    billboard.Size = UDim2.new(0, 100, 0, 50)
    billboard.StudsOffset = Vector3.new(0, 5, 0)
    billboard.Parent = checkpoint

    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.BackgroundTransparency = 1
    label.Text = "📍 " .. number
    label.TextColor3 = Color3.new(1, 1, 1)
    label.TextSize = 24
    label.Font = Enum.Font.GothamBold
    label.Parent = billboard

    checkpoint.Touched:Connect(function(hit)
        local humanoid = hit.Parent:FindFirstChild("Humanoid")
        if humanoid then
            currentCheckpoint = checkpoint.Position + Vector3.new(0, 3, 0)
            checkpoint.BrickColor = BrickColor.new("Bright blue")
            print("✅ Checkpoint " .. number .. " נשמר!")
        end
    end)

    return checkpoint
end

function Checkpoints.respawn(player)
    if currentCheckpoint and player.Character then
        local root = player.Character:FindFirstChild("HumanoidRootPart")
        if root then
            root.CFrame = CFrame.new(currentCheckpoint)
        end
    end
end

_G.Checkpoints = Checkpoints
print("✅ Checkpoints מוכן!")
'''

    # ========================================
    # יצירת משחק שלם
    # ========================================

    def create_complete_game(self, config: GameConfig) -> str:
        """יצירת משחק שלם עם כל המערכות"""
        parts = [
            "local parts = {}",
            "",
            self.create_game_manager(config),
            self.create_powerups(),
            self.create_checkpoints(),
            "",
            f"-- יצירת {config.collectibles_to_win} פריטים לאיסוף",
            self.create_collectibles(config.collectibles_to_win),
            "",
            f"-- יצירת {config.enemies_count} אויבים",
            self.create_enemies(config.enemies_count),
            "",
            "-- התחלת המשחק",
            "_G.GameManager:StartGame()",
            "",
            "-- יצירת כמה Power-ups",
            "PowerUps.createExtraLife(Vector3.new(20, 3, 0))",
            "PowerUps.createHealthPack(Vector3.new(-20, 3, 0))",
            "PowerUps.createScoreBonus(Vector3.new(0, 3, 20), 500)",
            "",
            "-- יצירת Checkpoints",
            "Checkpoints.create(Vector3.new(0, 1, 0), 1)",
            "Checkpoints.create(Vector3.new(30, 1, 0), 2)",
            "Checkpoints.create(Vector3.new(60, 1, 0), 3)",
            "",
            f'print("🎮 {config.name} מוכן!")',
            "game.Selection:Set(parts)"
        ]

        return "\n".join(parts)


# ========================================
# בדיקה
# ========================================

if __name__ == "__main__":
    generator = GameSystemsGenerator()

    config = GameConfig(
        name="Super Adventure",
        max_lives=3,
        max_health=100,
        total_levels=5,
        collectibles_to_win=10,
        enemies_count=5
    )

    code = generator.create_complete_game(config)
    print("Generated code length:", len(code))
    print(code[:1000])
