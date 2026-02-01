"""
Game Templates - תבניות משחק מוכנות
=====================================
תבניות מוכנות ליצירת משחקים שלמים בפקודה אחת:
- משחק מירוץ
- משחק איסוף מטבעות
- מבוך
- פארק שעשועים
- זירת קרב
"""

from typing import Optional, Dict, List, Tuple
from enum import Enum
import random
import math


class GameType(Enum):
    """סוגי משחקים."""
    RACING = "racing"              # משחק מירוץ
    COLLECTION = "collection"      # משחק איסוף
    MAZE = "maze"                  # מבוך
    OBBY = "obby"                  # פארקור/אובי
    TYCOON = "tycoon"              # טייקון
    BATTLE = "battle"              # קרב
    PARKOUR = "parkour"            # פארקור
    TOWER_DEFENSE = "tower_defense"  # הגנה על מגדל
    PLAYGROUND = "playground"      # פארק שעשועים


class GameTemplates:
    """
    מחולל תבניות משחק מוכנות.
    """

    def __init__(self, on_status=None):
        """אתחול."""
        self.on_status = on_status or (lambda x: print(f"[GameTemplate] {x}"))

    # ========================================
    # משחק מירוץ
    # ========================================

    def create_racing_game(self, track_length: int = 200, track_width: int = 20,
                          num_turns: int = 4, has_obstacles: bool = True) -> str:
        """
        יצירת משחק מירוץ שלם עם:
        - מסלול עם פניות
        - קו התחלה וסיום
        - מכשולים (אופציונלי)
        - טיימר
        - מכוניות
        """
        self.on_status("בונה משחק מירוץ...")

        obstacles_code = ""
        if has_obstacles:
            obstacles_code = """
-- מכשולים
local obstaclePositions = {
    {100, 1.5, -3},
    {120, 1.5, 3},
    {140, 1.5, -2},
    {160, 1.5, 2},
    {180, 3, 0},
}

for i, pos in ipairs(obstaclePositions) do
    local obstacle = Instance.new("Part")
    obstacle.Name = "Obstacle_" .. i
    obstacle.Size = Vector3.new(3, 3, 3)
    obstacle.Position = Vector3.new(pos[1], pos[2], pos[3])
    obstacle.Anchored = true
    obstacle.BrickColor = BrickColor.new("Bright red")
    obstacle.Material = Enum.Material.Neon
    obstacle.Parent = workspace
    table.insert(parts, obstacle)
end
"""

        return f"""
local parts = {{}}
local TweenService = game:GetService("TweenService")

print("🏎️ בונה משחק מירוץ...")

-- === מסלול ===
-- כביש ראשי
local track = Instance.new("Part")
track.Name = "RaceTrack"
track.Size = Vector3.new({track_length}, 1, {track_width})
track.Position = Vector3.new({track_length/2}, 0.5, 0)
track.Anchored = true
track.BrickColor = BrickColor.new("Dark stone grey")
track.Material = Enum.Material.Concrete
track.Parent = workspace
table.insert(parts, track)

-- סימון קווים לבנים
for i = 1, {track_length // 20} do
    local line = Instance.new("Part")
    line.Name = "TrackLine_" .. i
    line.Size = Vector3.new(5, 0.1, 1)
    line.Position = Vector3.new(i * 20, 1.05, 0)
    line.Anchored = true
    line.BrickColor = BrickColor.new("White")
    line.Material = Enum.Material.Neon
    line.Parent = workspace
    table.insert(parts, line)
end

-- קו התחלה
local startLine = Instance.new("Part")
startLine.Name = "StartLine"
startLine.Size = Vector3.new(2, 0.2, {track_width})
startLine.Position = Vector3.new(5, 1.1, 0)
startLine.Anchored = true
startLine.BrickColor = BrickColor.new("Lime green")
startLine.Material = Enum.Material.Neon
startLine.Parent = workspace
table.insert(parts, startLine)

-- קו סיום
local finishLine = Instance.new("Part")
finishLine.Name = "FinishLine"
finishLine.Size = Vector3.new(2, 0.2, {track_width})
finishLine.Position = Vector3.new({track_length - 5}, 1.1, 0)
finishLine.Anchored = true
finishLine.BrickColor = BrickColor.new("Really red")
finishLine.Material = Enum.Material.Neon
finishLine.Parent = workspace
table.insert(parts, finishLine)

-- שער התחלה
local startGate = Instance.new("Part")
startGate.Name = "StartGate"
startGate.Size = Vector3.new(2, 10, {track_width + 4})
startGate.Position = Vector3.new(5, 6, 0)
startGate.Anchored = true
startGate.BrickColor = BrickColor.new("White")
startGate.Material = Enum.Material.Metal
startGate.Transparency = 0.5
startGate.Parent = workspace
table.insert(parts, startGate)

-- שער סיום
local finishGate = Instance.new("Part")
finishGate.Name = "FinishGate"
finishGate.Size = Vector3.new(2, 10, {track_width + 4})
finishGate.Position = Vector3.new({track_length - 5}, 6, 0)
finishGate.Anchored = true
finishGate.BrickColor = BrickColor.new("Really red")
finishGate.Material = Enum.Material.Metal
finishGate.Transparency = 0.5
finishGate.Parent = workspace
table.insert(parts, finishGate)

-- מעקות
for side = -1, 1, 2 do
    local rail = Instance.new("Part")
    rail.Name = "Rail_" .. (side == -1 and "Left" or "Right")
    rail.Size = Vector3.new({track_length}, 3, 1)
    rail.Position = Vector3.new({track_length/2}, 2, side * ({track_width/2} + 0.5))
    rail.Anchored = true
    rail.BrickColor = BrickColor.new("Bright red")
    rail.Material = Enum.Material.Metal
    rail.Parent = workspace
    table.insert(parts, rail)
end

{obstacles_code}

-- === מכוניות ===
local carColors = {{"Bright red", "Bright blue", "Bright green", "Bright yellow"}}

for i, color in ipairs(carColors) do
    -- גוף המכונית
    local car = Instance.new("Part")
    car.Name = "Car_" .. i
    car.Size = Vector3.new(6, 2, 3)
    car.Position = Vector3.new(10, 2, (i - 2.5) * 4)
    car.Anchored = false
    car.BrickColor = BrickColor.new(color)
    car.Material = Enum.Material.SmoothPlastic
    car.Parent = workspace
    table.insert(parts, car)

    -- כיסא נהג
    local seat = Instance.new("VehicleSeat")
    seat.Name = "DriverSeat"
    seat.Size = Vector3.new(2, 1, 2)
    seat.Position = car.Position + Vector3.new(0, 1.5, 0)
    seat.Anchored = false
    seat.MaxSpeed = 80
    seat.Torque = 4
    seat.TurnSpeed = 2
    seat.Parent = car

    -- חיבור
    local weld = Instance.new("WeldConstraint")
    weld.Part0 = car
    weld.Part1 = seat
    weld.Parent = car

    -- גלגלים
    for wx = -1, 1, 2 do
        for wz = -1, 1, 2 do
            local wheel = Instance.new("Part")
            wheel.Name = "Wheel"
            wheel.Shape = Enum.PartType.Cylinder
            wheel.Size = Vector3.new(1, 1.5, 1.5)
            wheel.CFrame = CFrame.new(car.Position.X + wx * 2.5, 1, car.Position.Z + wz * 1.2) * CFrame.Angles(0, 0, math.rad(90))
            wheel.BrickColor = BrickColor.new("Black")
            wheel.Material = Enum.Material.Rubber
            wheel.Parent = workspace
            table.insert(parts, wheel)
        end
    end
end

-- === GUI טיימר ===
local timerGui = [[
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "RaceTimer"
screenGui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")

local timerLabel = Instance.new("TextLabel")
timerLabel.Size = UDim2.new(0, 200, 0, 50)
timerLabel.Position = UDim2.new(0.5, -100, 0, 10)
timerLabel.BackgroundColor3 = Color3.new(0, 0, 0)
timerLabel.BackgroundTransparency = 0.5
timerLabel.TextColor3 = Color3.new(1, 1, 1)
timerLabel.TextScaled = true
timerLabel.Font = Enum.Font.GothamBold
timerLabel.Text = "00:00.00"
timerLabel.Parent = screenGui

local startTime = 0
local running = false

workspace.StartLine.Touched:Connect(function(hit)
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player and not running then
        running = true
        startTime = tick()
    end
end)

workspace.FinishLine.Touched:Connect(function(hit)
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player and running then
        running = false
        local finalTime = tick() - startTime
        timerLabel.Text = "סיימת! " .. string.format("%.2f", finalTime) .. " שניות!"
        timerLabel.TextColor3 = Color3.new(0, 1, 0)
    end
end)

game:GetService("RunService").Heartbeat:Connect(function()
    if running then
        local elapsed = tick() - startTime
        local minutes = math.floor(elapsed / 60)
        local seconds = elapsed % 60
        timerLabel.Text = string.format("%02d:%05.2f", minutes, seconds)
    end
end)
]]

-- יצירת LocalScript לטיימר
local localScript = Instance.new("LocalScript")
localScript.Name = "RaceTimerScript"
localScript.Source = timerGui
localScript.Parent = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")

print("✅ משחק מירוץ מוכן!")
print("🏎️ שב במכונית ונגע בקו הירוק להתחיל!")
game.Selection:Set(parts)
"""

    # ========================================
    # משחק איסוף מטבעות
    # ========================================

    def create_collection_game(self, num_coins: int = 20, area_size: int = 100,
                              has_timer: bool = True, time_limit: int = 60) -> str:
        """
        יצירת משחק איסוף מטבעות עם:
        - מטבעות פזורים
        - מונה נקודות
        - טיימר (אופציונלי)
        - צלילים
        """
        self.on_status("בונה משחק איסוף...")

        timer_code = ""
        if has_timer:
            timer_code = f"""
-- טיימר
local timeLeft = {time_limit}
local timerLabel = Instance.new("TextLabel")
timerLabel.Name = "Timer"
timerLabel.Size = UDim2.new(0, 150, 0, 40)
timerLabel.Position = UDim2.new(0.5, -75, 0, 60)
timerLabel.BackgroundColor3 = Color3.new(0.2, 0.2, 0.2)
timerLabel.BackgroundTransparency = 0.3
timerLabel.TextColor3 = Color3.new(1, 1, 1)
timerLabel.TextScaled = true
timerLabel.Font = Enum.Font.GothamBold
timerLabel.Text = "⏱️ " .. timeLeft
timerLabel.Parent = screenGui

spawn(function()
    while timeLeft > 0 and gameRunning do
        wait(1)
        timeLeft = timeLeft - 1
        timerLabel.Text = "⏱️ " .. timeLeft
        if timeLeft <= 10 then
            timerLabel.TextColor3 = Color3.new(1, 0, 0)
        end
    end
    if gameRunning then
        gameRunning = false
        timerLabel.Text = "⏱️ נגמר הזמן!"
    end
end)
"""

        return f"""
local parts = {{}}

print("🪙 בונה משחק איסוף מטבעות...")

-- === רצפה ===
local floor = Instance.new("Part")
floor.Name = "GameFloor"
floor.Size = Vector3.new({area_size}, 1, {area_size})
floor.Position = Vector3.new(0, 0.5, 0)
floor.Anchored = true
floor.BrickColor = BrickColor.new("Bright green")
floor.Material = Enum.Material.Grass
floor.Parent = workspace
table.insert(parts, floor)

-- === מטבעות ===
local coinCount = {num_coins}
local collectedCoins = 0
local coins = {{}}

for i = 1, coinCount do
    local coin = Instance.new("Part")
    coin.Name = "Coin_" .. i
    coin.Shape = Enum.PartType.Cylinder
    coin.Size = Vector3.new(0.5, 2, 2)

    local x = math.random(-{area_size//2 - 5}, {area_size//2 - 5})
    local z = math.random(-{area_size//2 - 5}, {area_size//2 - 5})
    coin.CFrame = CFrame.new(x, 3, z) * CFrame.Angles(0, 0, math.rad(90))

    coin.Anchored = true
    coin.CanCollide = false
    coin.BrickColor = BrickColor.new("Gold")
    coin.Material = Enum.Material.Neon
    coin.Parent = workspace
    table.insert(parts, coin)
    table.insert(coins, coin)
end

-- === GUI ===
local guiCode = [[
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "CollectionGame"
screenGui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")

local scoreLabel = Instance.new("TextLabel")
scoreLabel.Name = "Score"
scoreLabel.Size = UDim2.new(0, 200, 0, 50)
scoreLabel.Position = UDim2.new(0.5, -100, 0, 10)
scoreLabel.BackgroundColor3 = Color3.new(0.1, 0.1, 0.1)
scoreLabel.BackgroundTransparency = 0.3
scoreLabel.TextColor3 = Color3.new(1, 0.8, 0)
scoreLabel.TextScaled = true
scoreLabel.Font = Enum.Font.GothamBold
scoreLabel.Text = "🪙 0 / ]] .. tostring(coinCount) .. [["
scoreLabel.Parent = screenGui

local gameRunning = true

{timer_code}
]]

local localScript = Instance.new("LocalScript")
localScript.Name = "CollectionGameScript"
localScript.Source = guiCode
localScript.Parent = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")

-- === לוגיקת איסוף ===
local RunService = game:GetService("RunService")

-- סיבוב מטבעות
local angle = 0
RunService.Heartbeat:Connect(function(dt)
    angle = angle + dt * 3
    for _, coin in ipairs(coins) do
        if coin and coin.Parent then
            local pos = coin.Position
            coin.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90)) * CFrame.Angles(angle, 0, 0)
        end
    end
end)

-- איסוף
for _, coin in ipairs(coins) do
    coin.Touched:Connect(function(hit)
        if coin.Transparency > 0 then return end
        local player = game.Players:GetPlayerFromCharacter(hit.Parent)
        if player then
            coin.Transparency = 1
            collectedCoins = collectedCoins + 1

            -- צליל
            local sound = Instance.new("Sound")
            sound.SoundId = "rbxassetid://138677306"
            sound.Volume = 0.5
            sound.Parent = coin
            sound:Play()

            -- עדכון GUI
            for _, gui in ipairs(player.PlayerGui:GetChildren()) do
                if gui.Name == "CollectionGame" then
                    local score = gui:FindFirstChild("Score")
                    if score then
                        score.Text = "🪙 " .. collectedCoins .. " / " .. coinCount
                    end
                end
            end

            -- ניצחון
            if collectedCoins >= coinCount then
                print("🎉 כל המטבעות נאספו!")
                for _, gui in ipairs(player.PlayerGui:GetChildren()) do
                    if gui.Name == "CollectionGame" then
                        local score = gui:FindFirstChild("Score")
                        if score then
                            score.Text = "🎉 ניצחת!"
                            score.TextColor3 = Color3.new(0, 1, 0)
                        end
                    end
                end
            end
        end
    end)
end

print("✅ משחק איסוף מוכן!")
print("🪙 אסוף את כל {num_coins} המטבעות!")
game.Selection:Set(parts)
"""

    # ========================================
    # אובי (Obby) - פארקור
    # ========================================

    def create_obby_game(self, num_stages: int = 10, difficulty: str = "medium") -> str:
        """
        יצירת משחק אובי/פארקור עם:
        - שלבים שונים
        - נקודות שמירה
        - מכשולים
        - פרסים
        """
        self.on_status("בונה משחק אובי...")

        # קושי משפיע על רווחים ומכשולים
        if difficulty == "easy":
            gap_range = (3, 5)
            height_change = 2
        elif difficulty == "hard":
            gap_range = (7, 12)
            height_change = 5
        else:  # medium
            gap_range = (5, 8)
            height_change = 3

        return f"""
local parts = {{}}
local TweenService = game:GetService("TweenService")

print("🏃 בונה משחק אובי...")

-- === נקודת התחלה ===
local spawn = Instance.new("SpawnLocation")
spawn.Name = "ObbySpawn"
spawn.Size = Vector3.new(10, 1, 10)
spawn.Position = Vector3.new(0, 0.5, 0)
spawn.Anchored = true
spawn.BrickColor = BrickColor.new("Lime green")
spawn.Material = Enum.Material.Neon
spawn.Neutral = true
spawn.Parent = workspace
table.insert(parts, spawn)

-- === שלבים ===
local currentX = 15
local currentY = 5
local checkpoints = {{}}

for stage = 1, {num_stages} do
    local stageType = math.random(1, 5)

    if stageType == 1 then
        -- פלטפורמה רגילה
        local platform = Instance.new("Part")
        platform.Name = "Stage_" .. stage
        platform.Size = Vector3.new(6, 1, 6)
        platform.Position = Vector3.new(currentX, currentY, 0)
        platform.Anchored = true
        platform.BrickColor = BrickColor.new("Medium stone grey")
        platform.Material = Enum.Material.Concrete
        platform.Parent = workspace
        table.insert(parts, platform)

    elseif stageType == 2 then
        -- פלטפורמה קטנה (קשה יותר)
        local platform = Instance.new("Part")
        platform.Name = "Stage_" .. stage
        platform.Size = Vector3.new(3, 1, 3)
        platform.Position = Vector3.new(currentX, currentY, 0)
        platform.Anchored = true
        platform.BrickColor = BrickColor.new("Bright red")
        platform.Material = Enum.Material.Neon
        platform.Parent = workspace
        table.insert(parts, platform)

    elseif stageType == 3 then
        -- פלטפורמה נעה
        local platform = Instance.new("Part")
        platform.Name = "Stage_" .. stage .. "_Moving"
        platform.Size = Vector3.new(5, 1, 5)
        platform.Position = Vector3.new(currentX, currentY, 0)
        platform.Anchored = true
        platform.BrickColor = BrickColor.new("Bright blue")
        platform.Material = Enum.Material.SmoothPlastic
        platform.Parent = workspace
        table.insert(parts, platform)

        -- אנימציית תנועה
        local startPos = platform.Position
        local endPos = startPos + Vector3.new(0, 0, 10)
        spawn(function()
            while platform and platform.Parent do
                local t1 = TweenService:Create(platform, TweenInfo.new(2), {{Position = endPos}})
                t1:Play()
                t1.Completed:Wait()
                local t2 = TweenService:Create(platform, TweenInfo.new(2), {{Position = startPos}})
                t2:Play()
                t2.Completed:Wait()
            end
        end)

    elseif stageType == 4 then
        -- קיר לטיפוס
        local wall = Instance.new("Part")
        wall.Name = "Stage_" .. stage .. "_Wall"
        wall.Size = Vector3.new(6, 10, 1)
        wall.Position = Vector3.new(currentX, currentY + 5, 0)
        wall.Anchored = true
        wall.BrickColor = BrickColor.new("Brown")
        wall.Material = Enum.Material.Brick
        wall.Parent = workspace
        table.insert(parts, wall)

        -- מדרגות בצד
        for step = 1, 5 do
            local stepPart = Instance.new("Part")
            stepPart.Name = "Step_" .. step
            stepPart.Size = Vector3.new(2, 0.5, 2)
            stepPart.Position = Vector3.new(currentX + 4, currentY + step * 2, (step % 2 == 0) and 2 or -2)
            stepPart.Anchored = true
            stepPart.BrickColor = BrickColor.new("Brick yellow")
            stepPart.Material = Enum.Material.Concrete
            stepPart.Parent = workspace
            table.insert(parts, stepPart)
        end

        currentY = currentY + 10

    elseif stageType == 5 then
        -- כרית קפיצה
        local jumpPad = Instance.new("Part")
        jumpPad.Name = "Stage_" .. stage .. "_JumpPad"
        jumpPad.Size = Vector3.new(5, 1, 5)
        jumpPad.Position = Vector3.new(currentX, currentY, 0)
        jumpPad.Anchored = true
        jumpPad.BrickColor = BrickColor.new("Lime green")
        jumpPad.Material = Enum.Material.Neon
        jumpPad.Parent = workspace
        table.insert(parts, jumpPad)

        jumpPad.Touched:Connect(function(hit)
            local humanoid = hit.Parent:FindFirstChild("Humanoid")
            if humanoid then
                local rootPart = hit.Parent:FindFirstChild("HumanoidRootPart")
                if rootPart then
                    rootPart.Velocity = Vector3.new(rootPart.Velocity.X, 80, rootPart.Velocity.Z)
                end
            end
        end)

        currentY = currentY + 8
    end

    -- נקודת שמירה (כל 3 שלבים)
    if stage % 3 == 0 then
        local checkpoint = Instance.new("Part")
        checkpoint.Name = "Checkpoint_" .. stage
        checkpoint.Size = Vector3.new(8, 0.5, 8)
        checkpoint.Position = Vector3.new(currentX, currentY + 0.25, 0)
        checkpoint.Anchored = true
        checkpoint.BrickColor = BrickColor.new("Bright yellow")
        checkpoint.Material = Enum.Material.Neon
        checkpoint.CanCollide = false
        checkpoint.Transparency = 0.5
        checkpoint.Parent = workspace
        table.insert(parts, checkpoint)
        table.insert(checkpoints, checkpoint)

        checkpoint.Touched:Connect(function(hit)
            local player = game.Players:GetPlayerFromCharacter(hit.Parent)
            if player then
                player.RespawnLocation = spawn
                print("📍 נקודת שמירה!", stage)
            end
        end)
    end

    -- קידום מיקום
    currentX = currentX + math.random({gap_range[0]}, {gap_range[1]})
    currentY = currentY + math.random(-{height_change}, {height_change})
    if currentY < 3 then currentY = 3 end
end

-- === סיום ===
local finish = Instance.new("Part")
finish.Name = "ObbyFinish"
finish.Size = Vector3.new(10, 1, 10)
finish.Position = Vector3.new(currentX + 10, currentY, 0)
finish.Anchored = true
finish.BrickColor = BrickColor.new("Gold")
finish.Material = Enum.Material.Neon
finish.Parent = workspace
table.insert(parts, finish)

-- גביע בסיום
local trophy = Instance.new("Part")
trophy.Name = "Trophy"
trophy.Shape = Enum.PartType.Cylinder
trophy.Size = Vector3.new(3, 2, 2)
trophy.Position = Vector3.new(currentX + 10, currentY + 2, 0)
trophy.Anchored = true
trophy.BrickColor = BrickColor.new("Gold")
trophy.Material = Enum.Material.Neon
trophy.Parent = workspace
table.insert(parts, trophy)

finish.Touched:Connect(function(hit)
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        print("🏆 " .. player.Name .. " סיים את האובי!")
    end
end)

print("✅ אובי עם {num_stages} שלבים מוכן!")
print("🏃 התחל לקפוץ!")
game.Selection:Set(parts)
"""

    # ========================================
    # פארק שעשועים
    # ========================================

    def create_playground(self) -> str:
        """
        יצירת פארק שעשועים עם:
        - מגלשה
        - נדנדות
        - קרוסלה
        - טרמפולינה
        """
        self.on_status("בונה פארק שעשועים...")

        return """
local parts = {}
local TweenService = game:GetService("TweenService")

print("🎡 בונה פארק שעשועים...")

-- === רצפה ===
local ground = Instance.new("Part")
ground.Name = "Playground"
ground.Size = Vector3.new(100, 1, 100)
ground.Position = Vector3.new(0, 0.5, 0)
ground.Anchored = true
ground.BrickColor = BrickColor.new("Bright green")
ground.Material = Enum.Material.Grass
ground.Parent = workspace
table.insert(parts, ground)

-- === מגלשה ===
local slideBase = Instance.new("Part")
slideBase.Name = "SlideBase"
slideBase.Size = Vector3.new(6, 15, 6)
slideBase.Position = Vector3.new(-30, 7.5, 0)
slideBase.Anchored = true
slideBase.BrickColor = BrickColor.new("Bright red")
slideBase.Material = Enum.Material.SmoothPlastic
slideBase.Parent = workspace
table.insert(parts, slideBase)

local slide = Instance.new("Part")
slide.Name = "Slide"
slide.Size = Vector3.new(4, 1, 20)
slide.CFrame = CFrame.new(-30, 8, 13) * CFrame.Angles(math.rad(30), 0, 0)
slide.Anchored = true
slide.BrickColor = BrickColor.new("Bright yellow")
slide.Material = Enum.Material.SmoothPlastic
slide.Parent = workspace
table.insert(parts, slide)

-- מדרגות למגלשה
for i = 1, 7 do
    local step = Instance.new("Part")
    step.Name = "SlideStep_" .. i
    step.Size = Vector3.new(4, 1, 2)
    step.Position = Vector3.new(-30, i * 2, -5)
    step.Anchored = true
    step.BrickColor = BrickColor.new("Medium stone grey")
    step.Material = Enum.Material.Metal
    step.Parent = workspace
    table.insert(parts, step)
end

-- === נדנדות ===
local swingFrame = Instance.new("Part")
swingFrame.Name = "SwingFrame"
swingFrame.Size = Vector3.new(12, 10, 1)
swingFrame.Position = Vector3.new(20, 6, 0)
swingFrame.Anchored = true
swingFrame.BrickColor = BrickColor.new("Bright blue")
swingFrame.Material = Enum.Material.Metal
swingFrame.Parent = workspace
table.insert(parts, swingFrame)

for i = -1, 1, 2 do
    local seat = Instance.new("Seat")
    seat.Name = "SwingSeat_" .. (i == -1 and "Left" or "Right")
    seat.Size = Vector3.new(3, 0.5, 2)
    seat.Position = Vector3.new(20 + i * 3, 2, 0)
    seat.Anchored = false
    seat.BrickColor = BrickColor.new("Black")
    seat.Material = Enum.Material.Rubber
    seat.Parent = workspace
    table.insert(parts, seat)

    -- חבלים
    local rope = Instance.new("Part")
    rope.Name = "SwingRope"
    rope.Size = Vector3.new(0.2, 8, 0.2)
    rope.Position = Vector3.new(20 + i * 3, 6, 0)
    rope.Anchored = true
    rope.BrickColor = BrickColor.new("Brown")
    rope.Material = Enum.Material.Rope
    rope.Parent = workspace
    table.insert(parts, rope)
end

-- === קרוסלה ===
local carouselBase = Instance.new("Part")
carouselBase.Name = "CarouselBase"
carouselBase.Shape = Enum.PartType.Cylinder
carouselBase.Size = Vector3.new(2, 12, 12)
carouselBase.CFrame = CFrame.new(0, 1, -30) * CFrame.Angles(0, 0, math.rad(90))
carouselBase.Anchored = true
carouselBase.BrickColor = BrickColor.new("Bright violet")
carouselBase.Material = Enum.Material.SmoothPlastic
carouselBase.Parent = workspace
table.insert(parts, carouselBase)

-- אנימציית סיבוב
spawn(function()
    local angle = 0
    while carouselBase and carouselBase.Parent do
        angle = angle + 0.02
        carouselBase.CFrame = CFrame.new(0, 1, -30) * CFrame.Angles(0, angle, math.rad(90))
        wait()
    end
end)

-- === טרמפולינה ===
local trampoline = Instance.new("Part")
trampoline.Name = "Trampoline"
trampoline.Shape = Enum.PartType.Cylinder
trampoline.Size = Vector3.new(2, 10, 10)
trampoline.CFrame = CFrame.new(-20, 1, 30) * CFrame.Angles(0, 0, math.rad(90))
trampoline.Anchored = true
trampoline.BrickColor = BrickColor.new("Bright orange")
trampoline.Material = Enum.Material.Fabric
trampoline.Parent = workspace
table.insert(parts, trampoline)

-- קפיצה על הטרמפולינה
trampoline.Touched:Connect(function(hit)
    local humanoid = hit.Parent:FindFirstChild("Humanoid")
    if humanoid then
        local rootPart = hit.Parent:FindFirstChild("HumanoidRootPart")
        if rootPart and rootPart.Velocity.Y < 0 then
            rootPart.Velocity = Vector3.new(rootPart.Velocity.X, 60, rootPart.Velocity.Z)

            local sound = Instance.new("Sound")
            sound.SoundId = "rbxassetid://145487017"
            sound.Parent = trampoline
            sound:Play()
        end
    end
end)

-- === ספסלים ===
for i = 1, 4 do
    local bench = Instance.new("Seat")
    bench.Name = "Bench_" .. i
    bench.Size = Vector3.new(6, 1, 2)
    bench.Position = Vector3.new(40, 1.5, -30 + i * 15)
    bench.Anchored = true
    bench.BrickColor = BrickColor.new("Reddish brown")
    bench.Material = Enum.Material.Wood
    bench.Parent = workspace
    table.insert(parts, bench)
end

-- === עצים ===
for i = 1, 6 do
    local trunk = Instance.new("Part")
    trunk.Name = "Tree_" .. i .. "_Trunk"
    trunk.Shape = Enum.PartType.Cylinder
    trunk.Size = Vector3.new(8, 2, 2)
    local x = math.random(-45, 45)
    local z = math.random(-45, 45)
    trunk.CFrame = CFrame.new(x, 4, z) * CFrame.Angles(0, 0, math.rad(90))
    trunk.Anchored = true
    trunk.BrickColor = BrickColor.new("Reddish brown")
    trunk.Material = Enum.Material.Wood
    trunk.Parent = workspace
    table.insert(parts, trunk)

    local leaves = Instance.new("Part")
    leaves.Name = "Tree_" .. i .. "_Leaves"
    leaves.Shape = Enum.PartType.Ball
    leaves.Size = Vector3.new(8, 8, 8)
    leaves.Position = Vector3.new(x, 10, z)
    leaves.Anchored = true
    leaves.BrickColor = BrickColor.new("Bright green")
    leaves.Material = Enum.Material.Grass
    leaves.Parent = workspace
    table.insert(parts, leaves)
end

print("✅ פארק שעשועים מוכן!")
print("🎡 יש מגלשה, נדנדות, קרוסלה וטרמפולינה!")
game.Selection:Set(parts)
"""

    # ========================================
    # שיטה כללית ליצירת משחק
    # ========================================

    def create_game(self, game_type: GameType, params: Dict = None) -> str:
        """
        יצירת משחק לפי סוג.

        Args:
            game_type: סוג המשחק
            params: פרמטרים נוספים

        Returns:
            קוד Lua
        """
        params = params or {}

        if game_type == GameType.RACING:
            return self.create_racing_game(**params)
        elif game_type == GameType.COLLECTION:
            return self.create_collection_game(**params)
        elif game_type == GameType.OBBY:
            return self.create_obby_game(**params)
        elif game_type == GameType.PLAYGROUND:
            return self.create_playground()
        else:
            return f"-- סוג משחק לא נתמך: {game_type.value}"


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת Game Templates")
    print("=" * 40)

    templates = GameTemplates()

    print("\n1. משחק מירוץ:")
    print(templates.create_racing_game()[:300] + "...")

    print("\n2. משחק איסוף:")
    print(templates.create_collection_game()[:300] + "...")

    print("\n3. אובי:")
    print(templates.create_obby_game()[:300] + "...")
