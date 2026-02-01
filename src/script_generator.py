"""
Script Generator - מחולל סקריפטים אינטראקטיביים
=================================================
יוצר קוד Lua לאלמנטים אינטראקטיביים במשחק:
- דלתות שנפתחות
- מטבעות לאיסוף
- כפתורים
- NPCs
- מערכות משחק
"""

from typing import Optional, Dict, List, Any
from enum import Enum


class InteractionType(Enum):
    """סוגי אינטראקציות."""
    DOOR = "door"                    # דלת שנפתחת
    COLLECTIBLE = "collectible"      # פריט לאיסוף
    BUTTON = "button"                # כפתור
    TELEPORTER = "teleporter"        # טלפורט
    CHECKPOINT = "checkpoint"        # נקודת שמירה
    DAMAGE_ZONE = "damage_zone"      # אזור נזק
    HEAL_ZONE = "heal_zone"          # אזור ריפוי
    SPEED_BOOST = "speed_boost"      # בוסט מהירות
    JUMP_PAD = "jump_pad"            # כרית קפיצה
    NPC = "npc"                       # דמות לא שחקן
    ENEMY = "enemy"                   # אויב
    MOVING_PLATFORM = "moving_platform"  # פלטפורמה נעה
    SPINNING = "spinning"             # סיבוב


class ScriptGenerator:
    """
    מחולל סקריפטים לאלמנטים אינטראקטיביים.
    """

    def __init__(self, on_status=None):
        """אתחול."""
        self.on_status = on_status or (lambda x: print(f"[ScriptGen] {x}"))

    # ========================================
    # דלתות ושערים
    # ========================================

    def create_door(self, width: float = 4, height: float = 8, color: str = "Reddish brown",
                    open_direction: str = "up", position: tuple = (0, 4, 0)) -> str:
        """
        יצירת דלת שנפתחת כשמתקרבים.

        Args:
            width: רוחב הדלת
            height: גובה הדלת
            color: צבע
            open_direction: כיוון פתיחה (up/left/right/rotate)
            position: מיקום
        """
        x, y, z = position

        if open_direction == "up":
            open_code = """
                -- פתיחה למעלה
                local goal = {Position = door.Position + Vector3.new(0, door.Size.Y, 0)}
                local closeGoal = {Position = originalPos}
            """
        elif open_direction == "left":
            open_code = """
                -- פתיחה שמאלה
                local goal = {Position = door.Position + Vector3.new(-door.Size.X, 0, 0)}
                local closeGoal = {Position = originalPos}
            """
        elif open_direction == "rotate":
            open_code = """
                -- פתיחה בסיבוב
                local goal = {CFrame = door.CFrame * CFrame.Angles(0, math.rad(90), 0)}
                local closeGoal = {CFrame = originalCFrame}
            """
        else:
            open_code = """
                -- פתיחה ימינה
                local goal = {Position = door.Position + Vector3.new(door.Size.X, 0, 0)}
                local closeGoal = {Position = originalPos}
            """

        return f"""
local parts = {{}}
local TweenService = game:GetService("TweenService")

-- יצירת דלת
local door = Instance.new("Part")
door.Name = "Door"
door.Size = Vector3.new({width}, {height}, 1)
door.Position = Vector3.new({x}, {y}, {z})
door.Anchored = true
door.BrickColor = BrickColor.new("{color}")
door.Material = Enum.Material.Wood
door.Parent = workspace
table.insert(parts, door)

-- מסגרת לדלת
local frame = Instance.new("Part")
frame.Name = "DoorFrame"
frame.Size = Vector3.new({width + 2}, {height + 1}, 0.5)
frame.Position = Vector3.new({x}, {y}, {z} - 0.75)
frame.Anchored = true
frame.BrickColor = BrickColor.new("Dark stone grey")
frame.Material = Enum.Material.Concrete
frame.CanCollide = false
frame.Parent = workspace
table.insert(parts, frame)

-- לוגיקת פתיחה
local originalPos = door.Position
local originalCFrame = door.CFrame
local isOpen = false
local debounce = false

{open_code}

local tweenInfo = TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

-- אזור טריגר
local trigger = Instance.new("Part")
trigger.Name = "DoorTrigger"
trigger.Size = Vector3.new({width + 4}, {height}, 6)
trigger.Position = door.Position
trigger.Anchored = true
trigger.CanCollide = false
trigger.Transparency = 1
trigger.Parent = workspace

trigger.Touched:Connect(function(hit)
    if debounce then return end
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player and not isOpen then
        debounce = true
        isOpen = true
        local tween = TweenService:Create(door, tweenInfo, goal)
        tween:Play()
        tween.Completed:Wait()
        debounce = false
    end
end)

trigger.TouchEnded:Connect(function(hit)
    if debounce then return end
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player and isOpen then
        debounce = true
        wait(0.5)
        isOpen = false
        local tween = TweenService:Create(door, tweenInfo, closeGoal)
        tween:Play()
        tween.Completed:Wait()
        debounce = false
    end
end)

print("✅ נוצרה דלת שנפתחת!")
game.Selection:Set(parts)
"""

    # ========================================
    # פריטים לאיסוף
    # ========================================

    def create_collectible(self, item_type: str = "coin", value: int = 10,
                          color: str = "Gold", position: tuple = (0, 3, 0),
                          respawn: bool = True, respawn_time: float = 5) -> str:
        """
        יצירת פריט לאיסוף (מטבע, יהלום, כוכב...).

        Args:
            item_type: סוג הפריט (coin/gem/star/heart)
            value: ערך
            color: צבע
            position: מיקום
            respawn: האם להופיע מחדש
            respawn_time: זמן עד הופעה מחדש
        """
        x, y, z = position

        # צורה לפי סוג
        if item_type == "coin":
            shape_code = """
local item = Instance.new("Part")
item.Shape = Enum.PartType.Cylinder
item.Size = Vector3.new(0.5, 3, 3)
item.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
"""
        elif item_type == "gem":
            shape_code = """
local item = Instance.new("Part")
item.Shape = Enum.PartType.Ball
item.Size = Vector3.new(2, 2, 2)
item.Position = pos
local mesh = Instance.new("SpecialMesh")
mesh.MeshType = Enum.MeshType.FileMesh
mesh.MeshId = "rbxassetid://9756362978"
mesh.Scale = Vector3.new(0.5, 0.5, 0.5)
mesh.Parent = item
"""
        elif item_type == "star":
            shape_code = """
local item = Instance.new("Part")
item.Size = Vector3.new(2, 2, 0.5)
item.Position = pos
"""
        elif item_type == "heart":
            shape_code = """
local item = Instance.new("Part")
item.Shape = Enum.PartType.Ball
item.Size = Vector3.new(2, 2, 2)
item.Position = pos
item.BrickColor = BrickColor.new("Bright red")
"""
        else:
            shape_code = """
local item = Instance.new("Part")
item.Shape = Enum.PartType.Ball
item.Size = Vector3.new(2, 2, 2)
item.Position = pos
"""

        respawn_code = ""
        if respawn:
            respawn_code = f"""
        -- Respawn
        wait({respawn_time})
        item.Transparency = 0
        item.CanCollide = false
"""

        return f"""
local parts = {{}}
local pos = Vector3.new({x}, {y}, {z})

{shape_code}

item.Name = "Collectible_{item_type}"
item.Anchored = true
item.CanCollide = false
item.BrickColor = BrickColor.new("{color}")
item.Material = Enum.Material.Neon
item.Parent = workspace
table.insert(parts, item)

-- אנימציית סיבוב
local RunService = game:GetService("RunService")
local angle = 0
local connection = RunService.Heartbeat:Connect(function(dt)
    if item and item.Parent then
        angle = angle + dt * 2
        item.CFrame = CFrame.new(item.Position) * CFrame.Angles(0, angle, 0)
    end
end)

-- איסוף
item.Touched:Connect(function(hit)
    if item.Transparency > 0 then return end
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        -- הוסף נקודות
        local leaderstats = player:FindFirstChild("leaderstats")
        if leaderstats then
            local coins = leaderstats:FindFirstChild("Coins")
            if coins then
                coins.Value = coins.Value + {value}
            end
        end

        -- צליל
        local sound = Instance.new("Sound")
        sound.SoundId = "rbxassetid://138677306"
        sound.Volume = 0.5
        sound.Parent = item
        sound:Play()

        item.Transparency = 1
        {respawn_code}
    end
end)

print("✅ נוצר פריט לאיסוף: {item_type} בשווי {value}")
game.Selection:Set(parts)
"""

    # ========================================
    # כפתורים ולחצנים
    # ========================================

    def create_button(self, action: str = "print", action_param: str = "הכפתור נלחץ!",
                     color: str = "Bright red", position: tuple = (0, 2, 0)) -> str:
        """
        יצירת כפתור שעושה פעולה.

        Args:
            action: סוג הפעולה (print/spawn/teleport/explode/open_door)
            action_param: פרמטר לפעולה
            color: צבע
            position: מיקום
        """
        x, y, z = position

        # קוד הפעולה
        if action == "print":
            action_code = f'print("{action_param}")'
        elif action == "spawn":
            action_code = f"""
local part = Instance.new("Part")
part.Size = Vector3.new(4, 4, 4)
part.Position = button.Position + Vector3.new(0, 10, 0)
part.BrickColor = BrickColor.Random()
part.Parent = workspace
"""
        elif action == "explode":
            action_code = """
local explosion = Instance.new("Explosion")
explosion.Position = button.Position + Vector3.new(0, 5, 0)
explosion.BlastRadius = 10
explosion.BlastPressure = 0
explosion.Parent = workspace
"""
        elif action == "teleport":
            action_code = f"""
local char = player.Character
if char then
    char:SetPrimaryPartCFrame(CFrame.new({action_param}))
end
"""
        else:
            action_code = f'print("{action_param}")'

        return f"""
local parts = {{}}
local TweenService = game:GetService("TweenService")

-- בסיס הכפתור
local base = Instance.new("Part")
base.Name = "ButtonBase"
base.Size = Vector3.new(4, 1, 4)
base.Position = Vector3.new({x}, {y - 0.5}, {z})
base.Anchored = true
base.BrickColor = BrickColor.new("Dark stone grey")
base.Material = Enum.Material.Metal
base.Parent = workspace
table.insert(parts, base)

-- הכפתור עצמו
local button = Instance.new("Part")
button.Name = "Button"
button.Shape = Enum.PartType.Cylinder
button.Size = Vector3.new(1, 3, 3)
button.CFrame = CFrame.new({x}, {y + 0.5}, {z}) * CFrame.Angles(0, 0, math.rad(90))
button.Anchored = true
button.BrickColor = BrickColor.new("{color}")
button.Material = Enum.Material.Neon
button.Parent = workspace
table.insert(parts, button)

-- לחיצה
local originalY = button.Position.Y
local debounce = false

button.Touched:Connect(function(hit)
    if debounce then return end
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        debounce = true

        -- אנימציית לחיצה
        local downTween = TweenService:Create(button, TweenInfo.new(0.1), {{Position = button.Position - Vector3.new(0, 0.3, 0)}})
        downTween:Play()
        downTween.Completed:Wait()

        -- פעולה
        {action_code}

        wait(0.2)

        local upTween = TweenService:Create(button, TweenInfo.new(0.1), {{Position = Vector3.new(button.Position.X, originalY, button.Position.Z)}})
        upTween:Play()
        upTween.Completed:Wait()

        wait(0.5)
        debounce = false
    end
end)

print("✅ נוצר כפתור!")
game.Selection:Set(parts)
"""

    # ========================================
    # כרית קפיצה (Jump Pad)
    # ========================================

    def create_jump_pad(self, power: float = 100, color: str = "Lime green",
                       position: tuple = (0, 1, 0)) -> str:
        """יצירת כרית קפיצה."""
        x, y, z = position

        return f"""
local parts = {{}}

local pad = Instance.new("Part")
pad.Name = "JumpPad"
pad.Size = Vector3.new(6, 1, 6)
pad.Position = Vector3.new({x}, {y}, {z})
pad.Anchored = true
pad.BrickColor = BrickColor.new("{color}")
pad.Material = Enum.Material.Neon
pad.Parent = workspace
table.insert(parts, pad)

-- חץ למעלה (דקורציה)
local arrow = Instance.new("Part")
arrow.Name = "Arrow"
arrow.Size = Vector3.new(2, 0.5, 3)
arrow.Position = Vector3.new({x}, {y + 0.75}, {z})
arrow.Anchored = true
arrow.BrickColor = BrickColor.new("White")
arrow.Material = Enum.Material.Neon
arrow.CanCollide = false
arrow.Parent = workspace
table.insert(parts, arrow)

-- קפיצה
pad.Touched:Connect(function(hit)
    local humanoid = hit.Parent:FindFirstChild("Humanoid")
    if humanoid then
        local rootPart = hit.Parent:FindFirstChild("HumanoidRootPart")
        if rootPart then
            rootPart.Velocity = Vector3.new(rootPart.Velocity.X, {power}, rootPart.Velocity.Z)

            -- צליל קפיצה
            local sound = Instance.new("Sound")
            sound.SoundId = "rbxassetid://145487017"
            sound.Volume = 0.5
            sound.Parent = pad
            sound:Play()
        end
    end
end)

print("✅ נוצרה כרית קפיצה!")
game.Selection:Set(parts)
"""

    # ========================================
    # פלטפורמה נעה
    # ========================================

    def create_moving_platform(self, direction: str = "horizontal",
                               distance: float = 20, speed: float = 5,
                               color: str = "Bright blue",
                               position: tuple = (0, 10, 0)) -> str:
        """
        יצירת פלטפורמה נעה.

        Args:
            direction: כיוון תנועה (horizontal/vertical/forward)
            distance: מרחק תנועה
            speed: מהירות
        """
        x, y, z = position

        if direction == "horizontal":
            move_vec = f"Vector3.new({distance}, 0, 0)"
        elif direction == "vertical":
            move_vec = f"Vector3.new(0, {distance}, 0)"
        else:
            move_vec = f"Vector3.new(0, 0, {distance})"

        return f"""
local parts = {{}}
local TweenService = game:GetService("TweenService")

local platform = Instance.new("Part")
platform.Name = "MovingPlatform"
platform.Size = Vector3.new(8, 2, 8)
platform.Position = Vector3.new({x}, {y}, {z})
platform.Anchored = true
platform.BrickColor = BrickColor.new("{color}")
platform.Material = Enum.Material.SmoothPlastic
platform.Parent = workspace
table.insert(parts, platform)

-- תנועה
local startPos = platform.Position
local endPos = startPos + {move_vec}
local moveTime = {distance} / {speed}

local function moveToEnd()
    local tween = TweenService:Create(platform, TweenInfo.new(moveTime, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), {{Position = endPos}})
    tween:Play()
    tween.Completed:Connect(moveToStart)
end

local function moveToStart()
    local tween = TweenService:Create(platform, TweenInfo.new(moveTime, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), {{Position = startPos}})
    tween:Play()
    tween.Completed:Connect(moveToEnd)
end

moveToEnd()

print("✅ נוצרה פלטפורמה נעה!")
game.Selection:Set(parts)
"""

    # ========================================
    # אזור טלפורט
    # ========================================

    def create_teleporter(self, destination: tuple = (100, 5, 0),
                         color: str = "Bright violet",
                         position: tuple = (0, 2, 0)) -> str:
        """יצירת טלפורטר."""
        x, y, z = position
        dx, dy, dz = destination

        return f"""
local parts = {{}}

-- טלפורטר מקור
local teleporter = Instance.new("Part")
teleporter.Name = "Teleporter"
teleporter.Shape = Enum.PartType.Cylinder
teleporter.Size = Vector3.new(1, 6, 6)
teleporter.CFrame = CFrame.new({x}, {y}, {z}) * CFrame.Angles(0, 0, math.rad(90))
teleporter.Anchored = true
teleporter.BrickColor = BrickColor.new("{color}")
teleporter.Material = Enum.Material.Neon
teleporter.CanCollide = false
teleporter.Transparency = 0.3
teleporter.Parent = workspace
table.insert(parts, teleporter)

-- נקודת יעד (סימון)
local destination = Instance.new("Part")
destination.Name = "TeleportDestination"
destination.Shape = Enum.PartType.Cylinder
destination.Size = Vector3.new(1, 6, 6)
destination.CFrame = CFrame.new({dx}, {dy}, {dz}) * CFrame.Angles(0, 0, math.rad(90))
destination.Anchored = true
destination.BrickColor = BrickColor.new("Lime green")
destination.Material = Enum.Material.Neon
destination.CanCollide = false
destination.Transparency = 0.3
destination.Parent = workspace
table.insert(parts, destination)

-- אפקט חלקיקים
local particles = Instance.new("ParticleEmitter")
particles.Color = ColorSequence.new(Color3.fromRGB(150, 0, 255))
particles.Size = NumberSequence.new(0.5)
particles.Lifetime = NumberRange.new(1, 2)
particles.Rate = 20
particles.Speed = NumberRange.new(2, 5)
particles.Parent = teleporter

-- טלפורט
local debounce = false
teleporter.Touched:Connect(function(hit)
    if debounce then return end
    local humanoid = hit.Parent:FindFirstChild("Humanoid")
    if humanoid then
        debounce = true
        local char = hit.Parent
        char:SetPrimaryPartCFrame(CFrame.new({dx}, {dy + 3}, {dz}))

        -- צליל
        local sound = Instance.new("Sound")
        sound.SoundId = "rbxassetid://2767090"
        sound.Volume = 0.5
        sound.Parent = teleporter
        sound:Play()

        wait(1)
        debounce = false
    end
end)

print("✅ נוצר טלפורטר!")
game.Selection:Set(parts)
"""

    # ========================================
    # מערכת חיים (Leaderstats)
    # ========================================

    def create_leaderstats_system(self) -> str:
        """יצירת מערכת נקודות/חיים לשחקנים."""
        return """
-- מערכת Leaderstats - צריך להכניס ל-ServerScriptService!
local code = [[
game.Players.PlayerAdded:Connect(function(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local coins = Instance.new("IntValue")
    coins.Name = "Coins"
    coins.Value = 0
    coins.Parent = leaderstats

    local health = Instance.new("IntValue")
    health.Name = "Lives"
    health.Value = 3
    health.Parent = leaderstats

    local level = Instance.new("IntValue")
    level.Name = "Level"
    level.Value = 1
    level.Parent = leaderstats

    print("נוצר leaderstats עבור " .. player.Name)
end)
]]

-- יצירת Script ב-ServerScriptService
local ServerScriptService = game:GetService("ServerScriptService")
local existingScript = ServerScriptService:FindFirstChild("LeaderstatsScript")
if existingScript then
    existingScript:Destroy()
end

local script = Instance.new("Script")
script.Name = "LeaderstatsScript"
script.Source = code
script.Parent = ServerScriptService

print("✅ נוצרה מערכת Leaderstats!")
print("הערה: יש לאתחל מחדש את המשחק כדי שהסקריפט ירוץ")
"""

    # ========================================
    # NPC בסיסי
    # ========================================

    def create_npc(self, name: str = "NPC", dialog: str = "שלום! ברוך הבא למשחק!",
                  position: tuple = (0, 3, 0)) -> str:
        """יצירת NPC עם דיאלוג."""
        x, y, z = position

        return f"""
local parts = {{}}

-- גוף ה-NPC
local npc = Instance.new("Model")
npc.Name = "{name}"

-- ראש
local head = Instance.new("Part")
head.Name = "Head"
head.Shape = Enum.PartType.Ball
head.Size = Vector3.new(2, 2, 2)
head.Position = Vector3.new({x}, {y + 3}, {z})
head.Anchored = true
head.BrickColor = BrickColor.new("Light orange")
head.Material = Enum.Material.SmoothPlastic
head.Parent = npc
table.insert(parts, head)

-- גוף
local torso = Instance.new("Part")
torso.Name = "Torso"
torso.Size = Vector3.new(2, 3, 1)
torso.Position = Vector3.new({x}, {y + 0.5}, {z})
torso.Anchored = true
torso.BrickColor = BrickColor.new("Bright blue")
torso.Material = Enum.Material.SmoothPlastic
torso.Parent = npc
table.insert(parts, torso)

-- רגליים
local leftLeg = Instance.new("Part")
leftLeg.Name = "LeftLeg"
leftLeg.Size = Vector3.new(1, 2, 1)
leftLeg.Position = Vector3.new({x - 0.5}, {y - 2}, {z})
leftLeg.Anchored = true
leftLeg.BrickColor = BrickColor.new("Dark stone grey")
leftLeg.Parent = npc
table.insert(parts, leftLeg)

local rightLeg = Instance.new("Part")
rightLeg.Name = "RightLeg"
rightLeg.Size = Vector3.new(1, 2, 1)
rightLeg.Position = Vector3.new({x + 0.5}, {y - 2}, {z})
rightLeg.Anchored = true
rightLeg.BrickColor = BrickColor.new("Dark stone grey")
rightLeg.Parent = npc
table.insert(parts, rightLeg)

-- שם מעל הראש
local billboard = Instance.new("BillboardGui")
billboard.Size = UDim2.new(4, 0, 1, 0)
billboard.StudsOffset = Vector3.new(0, 2, 0)
billboard.Adornee = head
billboard.Parent = head

local nameLabel = Instance.new("TextLabel")
nameLabel.Size = UDim2.new(1, 0, 1, 0)
nameLabel.BackgroundTransparency = 1
nameLabel.Text = "{name}"
nameLabel.TextColor3 = Color3.new(1, 1, 1)
nameLabel.TextScaled = true
nameLabel.Font = Enum.Font.GothamBold
nameLabel.Parent = billboard

npc.Parent = workspace

-- אינטראקציה - לחיצה על ה-NPC
local ClickDetector = Instance.new("ClickDetector")
ClickDetector.Parent = torso

local dialogShowing = false
ClickDetector.MouseClick:Connect(function(player)
    if dialogShowing then return end
    dialogShowing = true

    -- בועת דיבור
    local dialog = Instance.new("BillboardGui")
    dialog.Size = UDim2.new(6, 0, 2, 0)
    dialog.StudsOffset = Vector3.new(0, 4, 0)
    dialog.Adornee = head
    dialog.Parent = head

    local bubble = Instance.new("TextLabel")
    bubble.Size = UDim2.new(1, 0, 1, 0)
    bubble.BackgroundColor3 = Color3.new(1, 1, 1)
    bubble.BackgroundTransparency = 0.2
    bubble.Text = "{dialog}"
    bubble.TextColor3 = Color3.new(0, 0, 0)
    bubble.TextScaled = true
    bubble.TextWrapped = true
    bubble.Font = Enum.Font.Gotham
    bubble.Parent = dialog

    wait(3)
    dialog:Destroy()
    dialogShowing = false
end)

print("✅ נוצר NPC: {name}")
game.Selection:Set(parts)
"""

    # ========================================
    # שיטה כללית ליצירת אינטראקציה
    # ========================================

    def generate_interaction(self, interaction_type: InteractionType,
                            params: Dict[str, Any] = None) -> str:
        """
        יצירת אינטראקציה לפי סוג.

        Args:
            interaction_type: סוג האינטראקציה
            params: פרמטרים נוספים

        Returns:
            קוד Lua
        """
        params = params or {}

        if interaction_type == InteractionType.DOOR:
            return self.create_door(**params)
        elif interaction_type == InteractionType.COLLECTIBLE:
            return self.create_collectible(**params)
        elif interaction_type == InteractionType.BUTTON:
            return self.create_button(**params)
        elif interaction_type == InteractionType.JUMP_PAD:
            return self.create_jump_pad(**params)
        elif interaction_type == InteractionType.MOVING_PLATFORM:
            return self.create_moving_platform(**params)
        elif interaction_type == InteractionType.TELEPORTER:
            return self.create_teleporter(**params)
        elif interaction_type == InteractionType.NPC:
            return self.create_npc(**params)
        else:
            return f"-- לא נתמך: {interaction_type.value}"


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת Script Generator")
    print("=" * 40)

    gen = ScriptGenerator()

    print("\n1. דלת:")
    print(gen.create_door()[:200] + "...")

    print("\n2. מטבע:")
    print(gen.create_collectible()[:200] + "...")

    print("\n3. כפתור:")
    print(gen.create_button()[:200] + "...")
