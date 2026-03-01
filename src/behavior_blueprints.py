"""
Behavior Blueprints - ספריית התנהגויות מוכנות לאובייקטים
========================================================
כמו Blueprint Schema לאובייקטים, אבל עבור לוגיקה וסקריפטים.
המשתמש אומר "תוסיף ריצה לדמות" → המערכת מוצאת את ה-behavior המתאים
ומייצרת Lua שיוצר Script בתוך האובייקט.

Key insight: Plugin can write .Source on Script objects!
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import re


# ============================================
# BEHAVIOR SPEC - מפרט התנהגות
# ============================================

@dataclass
class BehaviorSpec:
    """מפרט של התנהגות שאפשר להוסיף לאובייקט."""
    name: str                    # English name
    hebrew_name: str             # שם בעברית
    description: str             # תיאור קצר
    category: str                # קטגוריה: movement, interaction, game_system, effect, npc
    script_type: str             # "Script" or "LocalScript"
    run_context: str             # "Server" or "Client" (for modern RunContext)
    target_type: str             # "part", "model", "humanoid", "any"
    script_source: str           # קוד Lua שירוץ בתוך הסקריפט
    requires_humanoid: bool = False
    requires_click: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)


# ============================================
# MOVEMENT BEHAVIORS - התנהגויות תנועה
# ============================================

BEHAVIOR_RUN = BehaviorSpec(
    name="run",
    hebrew_name="ריצה",
    description="הדמות רצה קדימה ומשנה כיוון",
    category="movement",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
local rootPart = script.Parent:FindFirstChild("HumanoidRootPart") or script.Parent.PrimaryPart

if humanoid and rootPart then
    humanoid.WalkSpeed = {speed}

    -- ריצה בכיוונים שונים
    local waypoints = {waypoints_lua}
    local currentWP = 1

    while true do
        local target = waypoints[currentWP]
        humanoid:MoveTo(rootPart.Position + Vector3.new(target[1], 0, target[2]))
        humanoid.MoveToFinished:Wait()
        currentWP = (currentWP % #waypoints) + 1
        task.wait(0.5)
    end
end
""",
    parameters={"speed": 16, "waypoints_lua": "{{20,0},{0,20},{-20,0},{0,-20}}"}
)

BEHAVIOR_FOLLOW_PLAYER = BehaviorSpec(
    name="follow_player",
    hebrew_name="עקוב אחרי שחקן",
    description="NPC עוקב אחרי השחקן הקרוב",
    category="movement",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
local rootPart = script.Parent:FindFirstChild("HumanoidRootPart") or script.Parent.PrimaryPart
local Players = game:GetService("Players")

if humanoid and rootPart then
    humanoid.WalkSpeed = {speed}

    while true do
        -- מצא את השחקן הכי קרוב
        local closestPlayer = nil
        local closestDist = {follow_range}

        for _, player in pairs(Players:GetPlayers()) do
            if player.Character and player.Character:FindFirstChild("HumanoidRootPart") then
                local dist = (player.Character.HumanoidRootPart.Position - rootPart.Position).Magnitude
                if dist < closestDist then
                    closestDist = dist
                    closestPlayer = player
                end
            end
        end

        if closestPlayer and closestPlayer.Character then
            humanoid:MoveTo(closestPlayer.Character.HumanoidRootPart.Position)
        end

        task.wait(0.3)
    end
end
""",
    parameters={"speed": 14, "follow_range": 100}
)

BEHAVIOR_PATROL = BehaviorSpec(
    name="patrol",
    hebrew_name="סיור",
    description="NPC מסייר בין נקודות",
    category="movement",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
local rootPart = script.Parent:FindFirstChild("HumanoidRootPart") or script.Parent.PrimaryPart

if humanoid and rootPart then
    humanoid.WalkSpeed = {speed}
    local startPos = rootPart.Position

    -- נקודות סיור
    local patrolPoints = {{
        startPos + Vector3.new({patrol_radius}, 0, 0),
        startPos + Vector3.new(0, 0, {patrol_radius}),
        startPos + Vector3.new(-{patrol_radius}, 0, 0),
        startPos + Vector3.new(0, 0, -{patrol_radius}),
    }}

    local currentPoint = 1
    while true do
        humanoid:MoveTo(patrolPoints[currentPoint])
        humanoid.MoveToFinished:Wait()
        task.wait({wait_time})
        currentPoint = (currentPoint % #patrolPoints) + 1
    end
end
""",
    parameters={"speed": 10, "patrol_radius": 30, "wait_time": 2}
)

BEHAVIOR_JUMP = BehaviorSpec(
    name="jump",
    hebrew_name="קפיצה",
    description="הדמות קופצת מדי פעם",
    category="movement",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
if humanoid then
    humanoid.JumpPower = {jump_power}
    while true do
        task.wait({interval})
        humanoid.Jump = true
    end
end
""",
    parameters={"jump_power": 50, "interval": 3}
)

BEHAVIOR_FLY = BehaviorSpec(
    name="fly",
    hebrew_name="עפיפה",
    description="האובייקט מרחף ועף",
    category="movement",
    script_type="Script",
    run_context="Server",
    target_type="any",
    script_source="""
local part = script.Parent
if part:IsA("BasePart") then
    part.Anchored = true
    local startPos = part.Position
    local t = 0
    while part and part.Parent do
        t = t + 0.02
        local newY = startPos.Y + math.sin(t * {speed}) * {height}
        local newX = startPos.X + math.cos(t * {speed} * 0.7) * {radius}
        part.Position = Vector3.new(newX, newY, startPos.Z)
        task.wait(0.03)
    end
elseif part:IsA("Model") then
    local primary = part.PrimaryPart or part:FindFirstChildOfClass("BasePart")
    if primary then
        local startPos = primary.Position
        local t = 0
        while part and part.Parent do
            t = t + 0.02
            local newY = startPos.Y + math.sin(t * {speed}) * {height}
            part:SetPrimaryPartCFrame(CFrame.new(primary.Position.X, newY, primary.Position.Z))
            task.wait(0.03)
        end
    end
end
""",
    parameters={"speed": 2, "height": 5, "radius": 10}
)


# ============================================
# INTERACTION BEHAVIORS - אינטראקציות
# ============================================

BEHAVIOR_CLICK_DOOR = BehaviorSpec(
    name="click_door",
    hebrew_name="דלת בלחיצה",
    description="דלת שנפתחת ונסגרת בלחיצה",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    requires_click=True,
    script_source="""
local TweenService = game:GetService("TweenService")
local part = script.Parent
local isOpen = false
local originalCFrame = part.CFrame
local openCFrame = originalCFrame * CFrame.Angles(0, math.rad(90), 0) + Vector3.new({offset_x}, 0, {offset_z})

local tweenInfo = TweenInfo.new(0.5, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut)

local clickDetector = part:FindFirstChildOfClass("ClickDetector")
if not clickDetector then
    clickDetector = Instance.new("ClickDetector")
    clickDetector.MaxActivationDistance = 15
    clickDetector.Parent = part
end

clickDetector.MouseClick:Connect(function(player)
    if isOpen then
        local tween = TweenService:Create(part, tweenInfo, {{CFrame = originalCFrame}})
        tween:Play()
        isOpen = false
    else
        local tween = TweenService:Create(part, tweenInfo, {{CFrame = openCFrame}})
        tween:Play()
        isOpen = true
    end
end)
""",
    parameters={"offset_x": 3, "offset_z": 3}
)

BEHAVIOR_PROXIMITY_INTERACT = BehaviorSpec(
    name="proximity_interact",
    hebrew_name="אינטראקציה בקרבה",
    description="כשהשחקן מתקרב מופיע UI לאינטראקציה",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="any",
    script_source="""
local part = script.Parent
if part:IsA("Model") then
    part = part.PrimaryPart or part:FindFirstChildOfClass("BasePart")
end
if not part then return end

local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "{action_text}"
prompt.ObjectText = "{object_text}"
prompt.MaxActivationDistance = {distance}
prompt.HoldDuration = {hold_duration}
prompt.Parent = part

prompt.Triggered:Connect(function(player)
    print(player.Name .. " interacted with " .. script.Parent.Name)
    {on_trigger_code}
end)
""",
    parameters={
        "action_text": "Interact",
        "object_text": "",
        "distance": 10,
        "hold_duration": 0,
        "on_trigger_code": "-- Custom action here"
    }
)

BEHAVIOR_COLLECT_COIN = BehaviorSpec(
    name="collect_coin",
    hebrew_name="איסוף מטבע",
    description="אובייקט שנאסף ונותן נקודות",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent
part.Anchored = true
part.CanCollide = false

-- אנימציית סיבוב
task.spawn(function()
    while part and part.Parent do
        part.CFrame = part.CFrame * CFrame.Angles(0, math.rad(2), 0)
        task.wait(0.03)
    end
end)

local debounce = {{}}
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce[player.UserId] then
        debounce[player.UserId] = true

        -- נקודות
        local ls = player:FindFirstChild("leaderstats")
        if ls then
            local coins = ls:FindFirstChild("Coins") or ls:FindFirstChild("Score")
            if coins then
                coins.Value = coins.Value + {points}
            end
        end

        -- אפקט איסוף
        part.Transparency = 1

        -- Respawn after delay
        task.wait({respawn_time})
        if part and part.Parent then
            part.Transparency = 0
            debounce[player.UserId] = nil
        end
    end
end)
""",
    parameters={"points": 1, "respawn_time": 5}
)

BEHAVIOR_TOUCH_DAMAGE = BehaviorSpec(
    name="touch_damage",
    hebrew_name="נזק בנגיעה",
    description="גורם נזק כשנוגעים",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent

local debounce = {{}}
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce[player.UserId] then
        debounce[player.UserId] = true
        local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
        if humanoid then
            humanoid:TakeDamage({damage})
        end
        task.wait(1)
        debounce[player.UserId] = nil
    end
end)
""",
    parameters={"damage": 25}
)

BEHAVIOR_TOUCH_HEAL = BehaviorSpec(
    name="touch_heal",
    hebrew_name="ריפוי בנגיעה",
    description="מרפא כשנוגעים",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent

local debounce = {{}}
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce[player.UserId] then
        debounce[player.UserId] = true
        local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
        if humanoid then
            humanoid.Health = math.min(humanoid.Health + {heal_amount}, humanoid.MaxHealth)
        end
        task.wait(2)
        debounce[player.UserId] = nil
    end
end)
""",
    parameters={"heal_amount": 30}
)

BEHAVIOR_TELEPORT = BehaviorSpec(
    name="teleport",
    hebrew_name="טלפורט",
    description="מטלפרט את השחקן למקום אחר",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent

local debounce = {{}}
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce[player.UserId] then
        debounce[player.UserId] = true
        local rootPart = hit.Parent:FindFirstChild("HumanoidRootPart")
        if rootPart then
            rootPart.CFrame = CFrame.new({dest_x}, {dest_y}, {dest_z})
        end
        task.wait(3)
        debounce[player.UserId] = nil
    end
end)
""",
    parameters={"dest_x": 0, "dest_y": 50, "dest_z": 0}
)

BEHAVIOR_TRAMPOLINE = BehaviorSpec(
    name="trampoline",
    hebrew_name="טרמפולינה",
    description="קופץ את השחקן למעלה",
    category="interaction",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local part = script.Parent
part.Touched:Connect(function(hit)
    local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
    local rootPart = hit.Parent:FindFirstChild("HumanoidRootPart")
    if humanoid and rootPart then
        rootPart.AssemblyLinearVelocity = Vector3.new(
            rootPart.AssemblyLinearVelocity.X,
            {bounce_force},
            rootPart.AssemblyLinearVelocity.Z
        )
    end
end)
""",
    parameters={"bounce_force": 80}
)


# ============================================
# NPC BEHAVIORS - התנהגויות דמויות
# ============================================

BEHAVIOR_NPC_TALK = BehaviorSpec(
    name="npc_talk",
    hebrew_name="דמות מדברת",
    description="NPC שמדבר כשמתקרבים",
    category="npc",
    script_type="Script",
    run_context="Server",
    target_type="model",
    script_source="""
local part = script.Parent
if part:IsA("Model") then
    part = part.PrimaryPart or part:FindFirstChildOfClass("BasePart")
end
if not part then return end

-- BillboardGui for dialog
local gui = Instance.new("BillboardGui")
gui.Size = UDim2.new(0, 200, 0, 50)
gui.StudsOffset = Vector3.new(0, 4, 0)
gui.Adornee = part
gui.AlwaysOnTop = true
gui.Parent = part

local label = Instance.new("TextLabel")
label.Size = UDim2.new(1, 0, 1, 0)
label.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
label.BackgroundTransparency = 0.3
label.TextColor3 = Color3.fromRGB(255, 255, 255)
label.TextScaled = true
label.Font = Enum.Font.GothamBold
label.Text = ""
label.Parent = gui

local messages = {messages_lua}
local msgIndex = 1

local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "Talk"
prompt.ObjectText = "{npc_name}"
prompt.MaxActivationDistance = 12
prompt.Parent = part

prompt.Triggered:Connect(function(player)
    label.Text = messages[msgIndex]
    msgIndex = (msgIndex % #messages) + 1
    task.wait(4)
    label.Text = ""
end)
""",
    parameters={
        "npc_name": "NPC",
        "messages_lua": '{{"Hello!","How are you?","Nice to meet you!"}}'
    }
)

BEHAVIOR_NPC_ATTACK = BehaviorSpec(
    name="npc_attack",
    hebrew_name="אויב תוקף",
    description="NPC שרודף ותוקף שחקנים",
    category="npc",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
local rootPart = script.Parent:FindFirstChild("HumanoidRootPart") or script.Parent.PrimaryPart
local Players = game:GetService("Players")

if not humanoid or not rootPart then return end

humanoid.WalkSpeed = {speed}
local attackRange = {attack_range}
local attackDamage = {damage}
local attackCooldown = {cooldown}
local lastAttack = 0

while true do
    local closestPlayer = nil
    local closestDist = {chase_range}

    for _, player in pairs(Players:GetPlayers()) do
        if player.Character and player.Character:FindFirstChild("HumanoidRootPart") then
            local pHumanoid = player.Character:FindFirstChildOfClass("Humanoid")
            if pHumanoid and pHumanoid.Health > 0 then
                local dist = (player.Character.HumanoidRootPart.Position - rootPart.Position).Magnitude
                if dist < closestDist then
                    closestDist = dist
                    closestPlayer = player
                end
            end
        end
    end

    if closestPlayer and closestPlayer.Character then
        humanoid:MoveTo(closestPlayer.Character.HumanoidRootPart.Position)

        -- תקיפה אם קרוב מספיק
        if closestDist < attackRange and tick() - lastAttack > attackCooldown then
            local pHumanoid = closestPlayer.Character:FindFirstChildOfClass("Humanoid")
            if pHumanoid then
                pHumanoid:TakeDamage(attackDamage)
                lastAttack = tick()
            end
        end
    end

    task.wait(0.3)
end
""",
    parameters={"speed": 18, "attack_range": 5, "damage": 15, "cooldown": 1.5, "chase_range": 60}
)

BEHAVIOR_NPC_FRIENDLY = BehaviorSpec(
    name="npc_friendly",
    hebrew_name="דמות ידידותית",
    description="NPC חברותי שהולך סביב ומנופף",
    category="npc",
    script_type="Script",
    run_context="Server",
    target_type="model",
    requires_humanoid=True,
    script_source="""
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
local rootPart = script.Parent:FindFirstChild("HumanoidRootPart") or script.Parent.PrimaryPart

if not humanoid or not rootPart then return end

humanoid.WalkSpeed = {speed}
local startPos = rootPart.Position

-- סיור קצר סביב
while true do
    local offsetX = math.random(-{wander_radius}, {wander_radius})
    local offsetZ = math.random(-{wander_radius}, {wander_radius})
    local targetPos = startPos + Vector3.new(offsetX, 0, offsetZ)

    humanoid:MoveTo(targetPos)
    humanoid.MoveToFinished:Wait()
    task.wait(math.random(2, 5))
end
""",
    parameters={"speed": 8, "wander_radius": 20}
)


# ============================================
# GAME SYSTEM BEHAVIORS - מערכות משחק
# ============================================

BEHAVIOR_LEADERBOARD = BehaviorSpec(
    name="leaderboard",
    hebrew_name="לוח תוצאות",
    description="מערכת ניקוד עם לידרבורד",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="any",
    script_source="""
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local coins = Instance.new("IntValue")
    coins.Name = "Coins"
    coins.Value = 0
    coins.Parent = leaderstats

    local score = Instance.new("IntValue")
    score.Name = "Score"
    score.Value = 0
    score.Parent = leaderstats

    local kills = Instance.new("IntValue")
    kills.Name = "Kills"
    kills.Value = 0
    kills.Parent = leaderstats
end)

-- Initialize existing players
for _, player in pairs(Players:GetPlayers()) do
    if not player:FindFirstChild("leaderstats") then
        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local coins = Instance.new("IntValue")
        coins.Name = "Coins"
        coins.Value = 0
        coins.Parent = leaderstats

        local score = Instance.new("IntValue")
        score.Name = "Score"
        score.Value = 0
        score.Parent = leaderstats
    end
end

print("Leaderboard system active!")
""",
    parameters={}
)

BEHAVIOR_CHECKPOINT = BehaviorSpec(
    name="checkpoint",
    hebrew_name="צ'קפוינט",
    description="נקודת שמירה - שחקן חוזר לפה אחרי מוות",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local checkpoint = script.Parent
checkpoint.Anchored = true

-- Visual indicator
checkpoint.BrickColor = BrickColor.new("Bright green")
checkpoint.Material = Enum.Material.Neon
checkpoint.Transparency = 0.3

local playerCheckpoints = {{}}

checkpoint.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        playerCheckpoints[player.UserId] = checkpoint.Position + Vector3.new(0, 5, 0)

        -- Visual feedback
        checkpoint.BrickColor = BrickColor.new("Bright yellow")
        task.wait(0.5)
        checkpoint.BrickColor = BrickColor.new("Bright green")
    end
end)

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        task.wait(0.5)
        local savedPos = playerCheckpoints[player.UserId]
        if savedPos then
            local rootPart = character:WaitForChild("HumanoidRootPart", 5)
            if rootPart then
                rootPart.CFrame = CFrame.new(savedPos)
            end
        end
    end)
end)
""",
    parameters={}
)

BEHAVIOR_SPEED_BOOST = BehaviorSpec(
    name="speed_boost",
    hebrew_name="הגברת מהירות",
    description="מגביר מהירות השחקן זמנית",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent
part.BrickColor = BrickColor.new("Bright yellow")
part.Material = Enum.Material.Neon

local debounce = {{}}
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce[player.UserId] then
        debounce[player.UserId] = true
        local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
        if humanoid then
            local originalSpeed = humanoid.WalkSpeed
            humanoid.WalkSpeed = {boost_speed}
            task.wait({duration})
            if humanoid then
                humanoid.WalkSpeed = originalSpeed
            end
        end
        debounce[player.UserId] = nil
    end
end)
""",
    parameters={"boost_speed": 50, "duration": 5}
)

BEHAVIOR_KILL_ZONE = BehaviorSpec(
    name="kill_zone",
    hebrew_name="אזור מוות",
    description="הורג שחקנים שנוגעים",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent
part.BrickColor = BrickColor.new("Bright red")
part.Material = Enum.Material.Neon

part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        local humanoid = hit.Parent:FindFirstChildOfClass("Humanoid")
        if humanoid then
            humanoid.Health = 0
        end
    end
end)
""",
    parameters={}
)

BEHAVIOR_SPAWN_POINT = BehaviorSpec(
    name="spawn_point",
    hebrew_name="נקודת לידה",
    description="מקום בו שחקנים מופיעים",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local spawnPart = script.Parent
spawnPart.Anchored = true
spawnPart.CanCollide = false
spawnPart.Transparency = 0.5
spawnPart.BrickColor = BrickColor.new("Bright blue")
spawnPart.Material = Enum.Material.Neon

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function(character)
        task.wait(0.1)
        local rootPart = character:WaitForChild("HumanoidRootPart", 5)
        if rootPart then
            rootPart.CFrame = spawnPart.CFrame + Vector3.new(0, 5, 0)
        end
    end)
end)
""",
    parameters={}
)

BEHAVIOR_TIMER = BehaviorSpec(
    name="timer",
    hebrew_name="טיימר",
    description="שעון עצר שסופר זמן",
    category="game_system",
    script_type="Script",
    run_context="Server",
    target_type="any",
    script_source="""
-- Timer display
local part = script.Parent
if part:IsA("Model") then
    part = part.PrimaryPart or part:FindFirstChildOfClass("BasePart")
end

local gui = Instance.new("BillboardGui")
gui.Size = UDim2.new(0, 200, 0, 80)
gui.StudsOffset = Vector3.new(0, 5, 0)
gui.Adornee = part
gui.AlwaysOnTop = true
gui.Parent = part

local label = Instance.new("TextLabel")
label.Size = UDim2.new(1, 0, 1, 0)
label.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
label.BackgroundTransparency = 0.3
label.TextColor3 = Color3.fromRGB(255, 255, 0)
label.TextScaled = true
label.Font = Enum.Font.GothamBold
label.Parent = gui

local timeLeft = {total_seconds}
while timeLeft > 0 do
    local mins = math.floor(timeLeft / 60)
    local secs = timeLeft % 60
    label.Text = string.format("%02d:%02d", mins, secs)
    task.wait(1)
    timeLeft = timeLeft - 1
end

label.Text = "TIME UP!"
label.TextColor3 = Color3.fromRGB(255, 0, 0)
""",
    parameters={"total_seconds": 120}
)


# ============================================
# PHYSICS BEHAVIORS - פיזיקה
# ============================================

BEHAVIOR_BOUNCE = BehaviorSpec(
    name="bounce",
    hebrew_name="קפיצה",
    description="אובייקט שקופץ",
    category="physics",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local part = script.Parent
part.Anchored = true
local startY = part.Position.Y
local t = 0
while part and part.Parent do
    t = t + 0.05
    local bounce = math.abs(math.sin(t * {speed})) * {height}
    part.Position = Vector3.new(part.Position.X, startY + bounce, part.Position.Z)
    task.wait(0.03)
end
""",
    parameters={"speed": 3, "height": 5}
)

BEHAVIOR_ROTATE_CONTINUOUS = BehaviorSpec(
    name="rotate_continuous",
    hebrew_name="סיבוב רציף",
    description="מסתובב ללא הפסקה",
    category="physics",
    script_type="Script",
    run_context="Server",
    target_type="any",
    script_source="""
local part = script.Parent
if part:IsA("Model") then
    part = part.PrimaryPart or part:FindFirstChildOfClass("BasePart")
end
if not part then return end

part.Anchored = true
while part and part.Parent do
    part.CFrame = part.CFrame * CFrame.Angles(0, math.rad({speed}), 0)
    task.wait(0.03)
end
""",
    parameters={"speed": 2}
)

BEHAVIOR_EXPLODE = BehaviorSpec(
    name="explode",
    hebrew_name="פיצוץ",
    description="מתפוצץ כשנוגעים",
    category="physics",
    script_type="Script",
    run_context="Server",
    target_type="part",
    script_source="""
local Players = game:GetService("Players")
local part = script.Parent

local debounce = false
part.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player and not debounce then
        debounce = true

        local explosion = Instance.new("Explosion")
        explosion.Position = part.Position
        explosion.BlastRadius = {blast_radius}
        explosion.BlastPressure = {blast_pressure}
        explosion.Parent = workspace

        part.Transparency = 1
        part.CanCollide = false

        task.wait({respawn_time})
        if part and part.Parent then
            part.Transparency = 0
            part.CanCollide = true
            debounce = false
        end
    end
end)
""",
    parameters={"blast_radius": 15, "blast_pressure": 50000, "respawn_time": 5}
)


# ============================================
# VEHICLE BEHAVIORS - רכבים
# ============================================

BEHAVIOR_DRIVEABLE = BehaviorSpec(
    name="driveable",
    hebrew_name="נהיגה",
    description="הופך רכב לניתן לנהיגה",
    category="vehicle",
    script_type="Script",
    run_context="Server",
    target_type="model",
    script_source="""
local model = script.Parent
local primary = model.PrimaryPart or model:FindFirstChildOfClass("BasePart")
if not primary then return end

-- Create VehicleSeat
local seat = Instance.new("VehicleSeat")
seat.Name = "DriverSeat"
seat.Size = Vector3.new(2, 1, 2)
seat.Position = primary.Position + Vector3.new(0, 2, 0)
seat.MaxSpeed = {max_speed}
seat.Torque = {torque}
seat.TurnSpeed = {turn_speed}
seat.Anchored = false
seat.Parent = model

-- Weld seat to car body
local weld = Instance.new("WeldConstraint")
weld.Part0 = seat
weld.Part1 = primary
weld.Parent = seat

-- Unanchor all parts so car can move
for _, part in pairs(model:GetDescendants()) do
    if part:IsA("BasePart") then
        part.Anchored = false
    end
end

print("Vehicle is now driveable!")
""",
    parameters={"max_speed": 60, "torque": 20, "turn_speed": 1}
)


# ============================================
# HEBREW KEYWORD → BEHAVIOR MAPPING
# ============================================

HEBREW_BEHAVIOR_KEYWORDS: Dict[str, str] = {
    # תנועה
    "ריצה": "run",
    "לרוץ": "run",
    "רץ": "run",
    "ירוץ": "run",
    "תרוץ": "run",
    "עקוב": "follow_player",
    "לעקוב": "follow_player",
    "יעקוב": "follow_player",
    "עוקב": "follow_player",
    "תעקוב": "follow_player",
    "עקיבה": "follow_player",
    "סיור": "patrol",
    "מסייר": "patrol",
    "סייר": "patrol",
    "יסייר": "patrol",
    "קפיצה": "jump",
    "לקפוץ": "jump",
    "קופץ": "jump",
    "יקפוץ": "jump",
    "תקפוץ": "jump",
    "עפיפה": "fly",
    "לעוף": "fly",
    "עף": "fly",
    "יעוף": "fly",
    "תעוף": "fly",
    "ריחוף": "fly",
    "מרחף": "fly",

    # אינטראקציות
    "דלת": "click_door",
    "נפתחת": "click_door",
    "פתיחה": "click_door",
    "לפתוח": "click_door",
    "מטבע": "collect_coin",
    "מטבעות": "collect_coin",
    "לאסוף": "collect_coin",
    "איסוף": "collect_coin",
    "נזק": "touch_damage",
    "כואב": "touch_damage",
    "פוגע": "touch_damage",
    "ריפוי": "touch_heal",
    "מרפא": "touch_heal",
    "לרפא": "touch_heal",
    "טלפורט": "teleport",
    "להעביר": "teleport",
    "טרמפולינה": "trampoline",
    "קפיץ": "trampoline",
    "קופצני": "trampoline",
    "פיצוץ": "explode",
    "מתפוצץ": "explode",
    "להתפוצץ": "explode",

    # NPC
    "מדבר": "npc_talk",
    "לדבר": "npc_talk",
    "שיחה": "npc_talk",
    "ידבר": "npc_talk",
    "תוקף": "npc_attack",
    "לתקוף": "npc_attack",
    "יתקוף": "npc_attack",
    "אויב": "npc_attack",
    "רודף": "npc_attack",
    "ידידותי": "npc_friendly",
    "חבר": "npc_friendly",
    "חברותי": "npc_friendly",

    # מערכות משחק
    "לידרבורד": "leaderboard",
    "ניקוד": "leaderboard",
    "נקודות": "leaderboard",
    "תוצאות": "leaderboard",
    "צ'קפוינט": "checkpoint",
    "שמירה": "checkpoint",
    "מהירות": "speed_boost",
    "בוסט": "speed_boost",
    "מוות": "kill_zone",
    "לבה": "kill_zone",
    "ספאון": "spawn_point",
    "לידה": "spawn_point",
    "טיימר": "timer",
    "שעון": "timer",
    "ספירה": "timer",

    # פיזיקה
    "קופצני": "bounce",
    "מקפץ": "bounce",
    "סיבוב": "rotate_continuous",
    "מסתובב": "rotate_continuous",
    "להסתובב": "rotate_continuous",

    # רכבים
    "נהיגה": "driveable",
    "לנהוג": "driveable",
    "נוהג": "driveable",
    "נוסע": "driveable",
    "לנסוע": "driveable",
    "ינסע": "driveable",
    "תנסע": "driveable",

    # more NPC talk variants
    "תדבר": "npc_talk",
    "ידבר": "npc_talk",
    "דובר": "npc_talk",
    "מספר": "npc_talk",
}


# ============================================
# BEHAVIOR REGISTRY - כל ההתנהגויות
# ============================================

ALL_BEHAVIORS: Dict[str, BehaviorSpec] = {
    "run": BEHAVIOR_RUN,
    "follow_player": BEHAVIOR_FOLLOW_PLAYER,
    "patrol": BEHAVIOR_PATROL,
    "jump": BEHAVIOR_JUMP,
    "fly": BEHAVIOR_FLY,
    "click_door": BEHAVIOR_CLICK_DOOR,
    "proximity_interact": BEHAVIOR_PROXIMITY_INTERACT,
    "collect_coin": BEHAVIOR_COLLECT_COIN,
    "touch_damage": BEHAVIOR_TOUCH_DAMAGE,
    "touch_heal": BEHAVIOR_TOUCH_HEAL,
    "teleport": BEHAVIOR_TELEPORT,
    "trampoline": BEHAVIOR_TRAMPOLINE,
    "npc_talk": BEHAVIOR_NPC_TALK,
    "npc_attack": BEHAVIOR_NPC_ATTACK,
    "npc_friendly": BEHAVIOR_NPC_FRIENDLY,
    "leaderboard": BEHAVIOR_LEADERBOARD,
    "checkpoint": BEHAVIOR_CHECKPOINT,
    "speed_boost": BEHAVIOR_SPEED_BOOST,
    "kill_zone": BEHAVIOR_KILL_ZONE,
    "spawn_point": BEHAVIOR_SPAWN_POINT,
    "timer": BEHAVIOR_TIMER,
    "bounce": BEHAVIOR_BOUNCE,
    "rotate_continuous": BEHAVIOR_ROTATE_CONTINUOUS,
    "explode": BEHAVIOR_EXPLODE,
    "driveable": BEHAVIOR_DRIVEABLE,
}


# ============================================
# BEHAVIOR FINDER - מוצא התנהגות מתאימה
# ============================================

def find_behavior_for_command(text: str) -> Optional[Tuple[str, BehaviorSpec]]:
    """
    מוצא את ההתנהגות המתאימה לפקודה בעברית.

    Args:
        text: פקודה בעברית כמו "תוסיף ריצה לדמות"

    Returns:
        (behavior_name, BehaviorSpec) or None
    """
    text_lower = text.lower().strip()

    # חפש מילת מפתח מתאימה - התאמה הכי ארוכה קודם
    best_match = None
    best_len = 0

    for keyword, behavior_name in sorted(
        HEBREW_BEHAVIOR_KEYWORDS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        if keyword in text_lower and len(keyword) > best_len:
            best_match = behavior_name
            best_len = len(keyword)

    if best_match and best_match in ALL_BEHAVIORS:
        return (best_match, ALL_BEHAVIORS[best_match])

    return None


def get_behavior_by_name(name: str) -> Optional[BehaviorSpec]:
    """Get behavior by its English name."""
    return ALL_BEHAVIORS.get(name)


def generate_behavior_lua(behavior: BehaviorSpec, target_name: str = None,
                          custom_params: Dict[str, Any] = None) -> str:
    """
    מייצר קוד Lua שיוצר Script עם ההתנהגות הנדרשת.

    Plugin can write .Source because it runs with elevated permissions!

    Args:
        behavior: מפרט ההתנהגות
        target_name: שם האובייקט המטרה (None = אובייקט נבחר)
        custom_params: פרמטרים מותאמים (אופציונלי)

    Returns:
        Lua code string
    """
    # Merge parameters
    params = dict(behavior.parameters)
    if custom_params:
        params.update(custom_params)

    # Format script source with parameters
    script_source = behavior.script_source
    for key, value in params.items():
        script_source = script_source.replace(f"{{{key}}}", str(value))

    # Escape for Lua string
    # Use [====[ ... ]====] to avoid conflicts with nested brackets
    escaped_source = script_source.replace("\\", "\\\\")

    # Build the Lua code
    if target_name:
        # Target specific object
        find_code = f"""
local target = workspace:FindFirstChild("{target_name}", true)
if not target then
    -- Try to find by partial name match
    for _, child in pairs(workspace:GetDescendants()) do
        if child.Name:lower():find("{target_name.lower()}") then
            target = child
            break
        end
    end
end
"""
    else:
        # Use selected object
        find_code = """
local selected = game.Selection:Get()
local target = selected[1]
"""

    # Handle humanoid requirement
    humanoid_setup = ""
    if behavior.requires_humanoid:
        humanoid_setup = """
-- Ensure target has Humanoid for movement
if target and not target:FindFirstChildOfClass("Humanoid") then
    if target:IsA("Model") then
        local humanoid = Instance.new("Humanoid")
        humanoid.Parent = target
        -- Set PrimaryPart if not set
        if not target.PrimaryPart then
            local primaryCandidate = target:FindFirstChildOfClass("BasePart")
            if primaryCandidate then
                target.PrimaryPart = primaryCandidate
                -- Create HumanoidRootPart if needed
                if not target:FindFirstChild("HumanoidRootPart") then
                    local root = Instance.new("Part")
                    root.Name = "HumanoidRootPart"
                    root.Size = Vector3.new(2, 2, 1)
                    root.Transparency = 1
                    root.CanCollide = false
                    root.Position = primaryCandidate.Position
                    root.Parent = target

                    local weld = Instance.new("WeldConstraint")
                    weld.Part0 = root
                    weld.Part1 = primaryCandidate
                    weld.Parent = root

                    target.PrimaryPart = root
                end
            end
        end
    end
end
"""

    # Handle click detector requirement
    click_setup = ""
    if behavior.requires_click:
        click_setup = """
-- Ensure ClickDetector exists
if target then
    local clickPart = target
    if target:IsA("Model") then
        clickPart = target.PrimaryPart or target:FindFirstChildOfClass("BasePart")
    end
    if clickPart and not clickPart:FindFirstChildOfClass("ClickDetector") then
        local cd = Instance.new("ClickDetector")
        cd.MaxActivationDistance = 15
        cd.Parent = clickPart
    end
end
"""

    lua_code = f"""-- Behavior: {behavior.hebrew_name} ({behavior.name})
{find_code}
if target then
{humanoid_setup}
{click_setup}
    -- Create behavior script
    local behaviorScript = Instance.new("{behavior.script_type}")
    behaviorScript.Name = "Behavior_{behavior.name}"
    behaviorScript.Source = [====[
{escaped_source.strip()}
]====]
    behaviorScript.Parent = target

    print("✅ הוספתי {behavior.hebrew_name} ל-" .. target.Name)
else
    warn("❌ לא מצאתי אובייקט! סמן אובייקט או ציין שם")
end
"""

    return lua_code


def list_behaviors_by_category() -> Dict[str, List[BehaviorSpec]]:
    """מחזיר את כל ההתנהגויות לפי קטגוריה."""
    categories: Dict[str, List[BehaviorSpec]] = {}
    for name, behavior in ALL_BEHAVIORS.items():
        if behavior.category not in categories:
            categories[behavior.category] = []
        categories[behavior.category].append(behavior)
    return categories


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Behavior Blueprints")
    print("=" * 60)

    # Test finding behaviors
    tests = [
        "תוסיף ריצה לדמות",
        "תגרום לו לעקוב אחרי שחקן",
        "תוסיף דלת שנפתחת בלחיצה",
        "תוסיף מטבעות לאיסוף",
        "תעשה לידרבורד",
        "תגרום למכונית לנסוע",
        "שהוא ידבר",
        "תוסיף אויב שתוקף",
    ]

    for test in tests:
        result = find_behavior_for_command(test)
        if result:
            name, behavior = result
            print(f"\n✅ '{test}' → {name} ({behavior.hebrew_name})")
            lua = generate_behavior_lua(behavior, target_name="TestObject")
            print(f"   Generated {len(lua)} chars of Lua")
        else:
            print(f"\n❌ '{test}' → No match")

    # Print all categories
    print("\n\nAll behaviors by category:")
    print("-" * 40)
    for cat, behaviors in list_behaviors_by_category().items():
        print(f"\n{cat}:")
        for b in behaviors:
            print(f"  - {b.hebrew_name} ({b.name})")
