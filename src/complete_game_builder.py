"""
Complete Game Builder - בונה משחקים מלא
=========================================
מודול שמשלב את כל היכולות ליצירת משחק מלא:
- עולם פיזי עם התנגשויות
- לוגיקת משחק (חיים, נקודות, שלבים)
- זיכרון והקשר
- אינטראקציות
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

# תיקון קידוד Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


class GameMode(Enum):
    """מצבי משחק."""
    RACING = "racing"           # מירוץ
    OBBY = "obby"               # פארקור
    COLLECTION = "collection"   # איסוף
    ADVENTURE = "adventure"     # הרפתקה
    SURVIVAL = "survival"       # הישרדות
    TYCOON = "tycoon"           # טייקון
    ROLEPLAY = "roleplay"       # משחק תפקידים
    CUSTOM = "custom"           # מותאם אישית


@dataclass
class GameBlueprint:
    """תכנית משחק מלאה."""
    name: str
    mode: GameMode
    description: str = ""

    # הגדרות עולם
    world_size: Tuple[float, float, float] = (500, 100, 500)
    terrain_type: str = "flat"  # flat, hills, islands

    # הגדרות משחק
    lives: int = 3
    max_health: int = 100
    starting_score: int = 0

    # שלבים
    levels: int = 1
    level_progression: str = "linear"  # linear, open

    # אובייקטים
    collectibles: int = 0
    enemies: int = 0
    npcs: int = 0
    checkpoints: int = 0
    power_ups: int = 0

    # אינטראקציות
    has_doors: bool = False
    has_teleports: bool = False
    has_vehicles: bool = False

    # נוספים
    custom_elements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompleteGameBuilder:
    """
    בונה משחקים מלא - יוצר משחקים שלמים עם כל הלוגיקה.
    """

    def __init__(self, on_status=None):
        """אתחול הבונה."""
        self.on_status = on_status or (lambda x: print(f"[GameBuilder] {x}"))

        # טען את המודולים הנדרשים
        from world_state import WorldState
        from game_systems import GameSystemsGenerator, GameConfig
        from agent_memory import AgentMemory, SharedAgentContext

        self.world_state = WorldState(on_status=self.on_status)
        self.game_systems = GameSystemsGenerator()
        self.shared_context = SharedAgentContext()
        self.shared_context.set_world_state(self.world_state)
        self.memory = self.shared_context.memory

    def analyze_request(self, request: str) -> GameBlueprint:
        """
        ניתוח בקשת משתמש ויצירת תכנית משחק.

        Args:
            request: הבקשה בעברית

        Returns:
            תכנית משחק
        """
        request_lower = request.lower()

        # זיהוי מצב משחק
        mode = GameMode.CUSTOM
        name = "משחק"

        if any(w in request_lower for w in ["מירוץ", "רייסינג", "מכוניות"]):
            mode = GameMode.RACING
            name = "משחק מירוץ"
        elif any(w in request_lower for w in ["אובי", "פארקור", "קפיצות"]):
            mode = GameMode.OBBY
            name = "אובי פארקור"
        elif any(w in request_lower for w in ["איסוף", "מטבעות", "אוסף"]):
            mode = GameMode.COLLECTION
            name = "משחק איסוף"
        elif any(w in request_lower for w in ["הרפתקה", "הרפתקאות", "מסע"]):
            mode = GameMode.ADVENTURE
            name = "הרפתקה"
        elif any(w in request_lower for w in ["הישרדות", "survival", "שרוד"]):
            mode = GameMode.SURVIVAL
            name = "משחק הישרדות"
        elif any(w in request_lower for w in ["טייקון", "עסק", "בנה"]):
            mode = GameMode.TYCOON
            name = "טייקון"

        # חילוץ פרטים מהבקשה
        blueprint = GameBlueprint(name=name, mode=mode, description=request)

        # זיהוי מספרים
        import re
        numbers = re.findall(r'\d+', request)
        if numbers:
            # ניחוש חכם מה המספר מייצג
            num = int(numbers[0])
            if any(w in request_lower for w in ["חיים", "lives"]):
                blueprint.lives = num
            elif any(w in request_lower for w in ["שלב", "שלבים", "level"]):
                blueprint.levels = num
            elif any(w in request_lower for w in ["מטבע", "נקודות", "כוכב"]):
                blueprint.collectibles = num
            elif any(w in request_lower for w in ["אויב", "אויבים", "מפלצת"]):
                blueprint.enemies = num

        # ברירות מחדל לפי מצב משחק
        if mode == GameMode.RACING:
            blueprint.has_vehicles = True
            blueprint.checkpoints = 5
            blueprint.levels = 3

        elif mode == GameMode.OBBY:
            blueprint.checkpoints = 10
            blueprint.levels = 5
            blueprint.collectibles = 20

        elif mode == GameMode.COLLECTION:
            blueprint.collectibles = 50
            blueprint.power_ups = 5

        elif mode == GameMode.ADVENTURE:
            blueprint.npcs = 5
            blueprint.enemies = 10
            blueprint.collectibles = 30
            blueprint.has_doors = True

        elif mode == GameMode.SURVIVAL:
            blueprint.enemies = 20
            blueprint.collectibles = 15
            blueprint.power_ups = 10

        self.on_status(f"תכנית משחק: {blueprint.name} ({blueprint.mode.value})")
        return blueprint

    def build_complete_game(self, blueprint: GameBlueprint) -> str:
        """
        בניית משחק מלא מתכנית.

        Args:
            blueprint: תכנית המשחק

        Returns:
            קוד Lua מלא
        """
        from game_systems import GameConfig

        self.on_status(f"בונה: {blueprint.name}")

        # צור קונפיגורציה
        config = GameConfig(
            game_name=blueprint.name,
            max_lives=blueprint.lives,
            max_health=blueprint.max_health,
            total_levels=blueprint.levels,
            has_checkpoints=blueprint.checkpoints > 0,
            has_enemies=blueprint.enemies > 0,
            has_collectibles=blueprint.collectibles > 0
        )

        # בנה את המשחק לפי סוג
        lua_parts = []

        # 1. הערות ותיאור
        lua_parts.append(f"""
-- ==========================================
-- {blueprint.name}
-- תיאור: {blueprint.description[:100]}
-- נוצר על ידי Roblox Voice Creator
-- ==========================================
""")

        # 2. מערכת משחק בסיסית
        lua_parts.append(self.game_systems.create_game_manager(config))

        # 3. ממשק משתמש
        lua_parts.append(self.game_systems.create_game_ui(config))

        # 4. תוכן לפי סוג המשחק
        if blueprint.mode == GameMode.RACING:
            lua_parts.append(self._create_racing_content(blueprint))
        elif blueprint.mode == GameMode.OBBY:
            lua_parts.append(self._create_obby_content(blueprint))
        elif blueprint.mode == GameMode.COLLECTION:
            lua_parts.append(self._create_collection_content(blueprint))
        elif blueprint.mode == GameMode.ADVENTURE:
            lua_parts.append(self._create_adventure_content(blueprint))
        elif blueprint.mode == GameMode.SURVIVAL:
            lua_parts.append(self._create_survival_content(blueprint))
        else:
            lua_parts.append(self._create_custom_content(blueprint))

        # 5. אלמנטים נוספים
        if blueprint.collectibles > 0:
            lua_parts.append(self.game_systems.create_collectibles(
                count=blueprint.collectibles,
                value=10
            ))

        if blueprint.enemies > 0:
            lua_parts.append(self.game_systems.create_enemies(
                count=blueprint.enemies,
                damage=10
            ))

        if blueprint.power_ups > 0:
            lua_parts.append(self.game_systems.create_powerups())

        if blueprint.checkpoints > 0:
            lua_parts.append(self.game_systems.create_checkpoints())

        # 6. אתחול סופי
        lua_parts.append("""
-- ==========================================
-- אתחול המשחק
-- ==========================================
print("🎮 " .. GameManager.config.gameName .. " מוכן!")
print("❤️ חיים: " .. GameManager.state.lives)
print("🎯 שלב: " .. GameManager.state.level)
""")

        # שמור בזיכרון
        self.memory.remember_game_config(
            blueprint.mode.value,
            {
                "name": blueprint.name,
                "lives": blueprint.lives,
                "levels": blueprint.levels,
                "collectibles": blueprint.collectibles
            }
        )
        self.memory.save()

        return "\n".join(lua_parts)

    def _create_racing_content(self, blueprint: GameBlueprint) -> str:
        """תוכן למשחק מירוץ."""
        return """
-- ==========================================
-- עולם מירוץ
-- ==========================================
local RaceWorld = {}

function RaceWorld.create()
    local world = Instance.new("Folder")
    world.Name = "RaceWorld"
    world.Parent = workspace

    -- מסלול ראשי
    local track = Instance.new("Part")
    track.Name = "RaceTrack"
    track.Size = Vector3.new(300, 1, 30)
    track.Position = Vector3.new(0, 0.5, 0)
    track.BrickColor = BrickColor.new("Dark stone grey")
    track.Material = Enum.Material.Concrete
    track.Anchored = true
    track.Parent = world

    -- קווי מסלול
    for i = 1, 10 do
        local line = Instance.new("Part")
        line.Name = "TrackLine_" .. i
        line.Size = Vector3.new(10, 0.1, 1)
        line.Position = Vector3.new(-140 + i * 30, 0.6, 0)
        line.BrickColor = BrickColor.new("White")
        line.Material = Enum.Material.SmoothPlastic
        line.Anchored = true
        line.Parent = world
    end

    -- קו התחלה
    local startLine = Instance.new("Part")
    startLine.Name = "StartLine"
    startLine.Size = Vector3.new(2, 0.1, 30)
    startLine.Position = Vector3.new(-140, 0.6, 0)
    startLine.BrickColor = BrickColor.new("Lime green")
    startLine.Material = Enum.Material.Neon
    startLine.Anchored = true
    startLine.Parent = world

    -- קו סיום
    local finishLine = Instance.new("Part")
    finishLine.Name = "FinishLine"
    finishLine.Size = Vector3.new(2, 0.1, 30)
    finishLine.Position = Vector3.new(140, 0.6, 0)
    finishLine.BrickColor = BrickColor.new("Really red")
    finishLine.Material = Enum.Material.Neon
    finishLine.Anchored = true
    finishLine.Parent = world

    -- יציעים
    for side = -1, 1, 2 do
        local stands = Instance.new("Part")
        stands.Name = "Stands_" .. (side == -1 and "Left" or "Right")
        stands.Size = Vector3.new(200, 15, 20)
        stands.Position = Vector3.new(0, 7.5, side * 35)
        stands.BrickColor = BrickColor.new("Medium stone grey")
        stands.Material = Enum.Material.Concrete
        stands.Anchored = true
        stands.Parent = world
    end

    -- מכוניות
    local carColors = {"Bright red", "Bright blue", "Bright yellow", "Bright green"}
    for i, color in ipairs(carColors) do
        local car = Instance.new("Model")
        car.Name = "Car_" .. i

        local body = Instance.new("Part")
        body.Name = "Body"
        body.Size = Vector3.new(6, 2, 3)
        body.Position = Vector3.new(-130 + (i-1) * 8, 2, 0)
        body.BrickColor = BrickColor.new(color)
        body.Material = Enum.Material.SmoothPlastic
        body.Anchored = true
        body.Parent = car

        car.PrimaryPart = body
        car.Parent = world
    end

    return world
end

RaceWorld.create()
"""

    def _create_obby_content(self, blueprint: GameBlueprint) -> str:
        """תוכן לאובי."""
        return """
-- ==========================================
-- עולם אובי
-- ==========================================
local ObbyWorld = {}

function ObbyWorld.create()
    local world = Instance.new("Folder")
    world.Name = "ObbyWorld"
    world.Parent = workspace

    -- פלטפורמת התחלה
    local start = Instance.new("Part")
    start.Name = "StartPlatform"
    start.Size = Vector3.new(20, 2, 20)
    start.Position = Vector3.new(0, 1, 0)
    start.BrickColor = BrickColor.new("Bright green")
    start.Material = Enum.Material.Grass
    start.Anchored = true
    start.Parent = world

    -- שלבי אובי
    local platforms = {}
    local positions = {
        Vector3.new(15, 5, 0),
        Vector3.new(30, 10, 5),
        Vector3.new(45, 15, 0),
        Vector3.new(60, 20, -5),
        Vector3.new(75, 25, 0),
        Vector3.new(90, 30, 5),
        Vector3.new(105, 35, 0),
        Vector3.new(120, 40, -5),
        Vector3.new(135, 45, 0),
        Vector3.new(150, 50, 0),
    }

    local materials = {
        Enum.Material.Brick,
        Enum.Material.Wood,
        Enum.Material.Metal,
        Enum.Material.Neon,
    }

    for i, pos in ipairs(positions) do
        local platform = Instance.new("Part")
        platform.Name = "Platform_" .. i
        platform.Size = Vector3.new(8, 1, 8)
        platform.Position = pos
        platform.BrickColor = BrickColor.Random()
        platform.Material = materials[(i % #materials) + 1]
        platform.Anchored = true
        platform.Parent = world

        -- Checkpoint כל 3 פלטפורמות
        if i % 3 == 0 then
            local checkpoint = Instance.new("Part")
            checkpoint.Name = "Checkpoint_" .. (i / 3)
            checkpoint.Size = Vector3.new(8, 5, 1)
            checkpoint.Position = pos + Vector3.new(0, 3, 0)
            checkpoint.BrickColor = BrickColor.new("Lime green")
            checkpoint.Material = Enum.Material.Neon
            checkpoint.Transparency = 0.5
            checkpoint.Anchored = true
            checkpoint.CanCollide = false
            checkpoint.Parent = world

            -- סקריפט צ'קפוינט
            local script = Instance.new("Script")
            script.Source = [[
                local checkpoint = script.Parent
                local touched = {}

                checkpoint.Touched:Connect(function(hit)
                    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
                    if player and not touched[player] then
                        touched[player] = true
                        print("✅ " .. player.Name .. " הגיע לצ'קפוינט!")
                    end
                end)
            ]]
            script.Parent = checkpoint
        end
    end

    -- פלטפורמת סיום
    local finish = Instance.new("Part")
    finish.Name = "FinishPlatform"
    finish.Size = Vector3.new(20, 2, 20)
    finish.Position = Vector3.new(170, 55, 0)
    finish.BrickColor = BrickColor.new("Gold")
    finish.Material = Enum.Material.Neon
    finish.Anchored = true
    finish.Parent = world

    -- Kill zone
    local killZone = Instance.new("Part")
    killZone.Name = "KillZone"
    killZone.Size = Vector3.new(500, 1, 100)
    killZone.Position = Vector3.new(85, -20, 0)
    killZone.Transparency = 1
    killZone.Anchored = true
    killZone.CanCollide = false
    killZone.Parent = world

    local killScript = Instance.new("Script")
    killScript.Source = [[
        script.Parent.Touched:Connect(function(hit)
            local humanoid = hit.Parent:FindFirstChild("Humanoid")
            if humanoid then
                humanoid.Health = 0
            end
        end)
    ]]
    killScript.Parent = killZone

    return world
end

ObbyWorld.create()
"""

    def _create_collection_content(self, blueprint: GameBlueprint) -> str:
        """תוכן למשחק איסוף."""
        return """
-- ==========================================
-- עולם איסוף
-- ==========================================
local CollectionWorld = {}

function CollectionWorld.create()
    local world = Instance.new("Folder")
    world.Name = "CollectionWorld"
    world.Parent = workspace

    -- רצפה גדולה
    local floor = Instance.new("Part")
    floor.Name = "Floor"
    floor.Size = Vector3.new(200, 1, 200)
    floor.Position = Vector3.new(0, 0.5, 0)
    floor.BrickColor = BrickColor.new("Medium green")
    floor.Material = Enum.Material.Grass
    floor.Anchored = true
    floor.Parent = world

    -- גדרות
    for i = 1, 4 do
        local wall = Instance.new("Part")
        wall.Name = "Wall_" .. i
        wall.Anchored = true
        wall.Material = Enum.Material.Wood
        wall.BrickColor = BrickColor.new("Brown")

        if i == 1 then
            wall.Size = Vector3.new(200, 5, 2)
            wall.Position = Vector3.new(0, 3, -100)
        elseif i == 2 then
            wall.Size = Vector3.new(200, 5, 2)
            wall.Position = Vector3.new(0, 3, 100)
        elseif i == 3 then
            wall.Size = Vector3.new(2, 5, 200)
            wall.Position = Vector3.new(-100, 3, 0)
        else
            wall.Size = Vector3.new(2, 5, 200)
            wall.Position = Vector3.new(100, 3, 0)
        end

        wall.Parent = world
    end

    -- מכשולים
    for i = 1, 20 do
        local obstacle = Instance.new("Part")
        obstacle.Name = "Obstacle_" .. i
        obstacle.Size = Vector3.new(
            math.random(5, 15),
            math.random(3, 10),
            math.random(5, 15)
        )
        obstacle.Position = Vector3.new(
            math.random(-80, 80),
            obstacle.Size.Y / 2 + 1,
            math.random(-80, 80)
        )
        obstacle.BrickColor = BrickColor.Random()
        obstacle.Material = Enum.Material.Brick
        obstacle.Anchored = true
        obstacle.Parent = world
    end

    -- עצים
    for i = 1, 15 do
        local tree = Instance.new("Model")
        tree.Name = "Tree_" .. i

        local trunk = Instance.new("Part")
        trunk.Name = "Trunk"
        trunk.Size = Vector3.new(2, 8, 2)
        trunk.Position = Vector3.new(
            math.random(-90, 90),
            5,
            math.random(-90, 90)
        )
        trunk.BrickColor = BrickColor.new("Reddish brown")
        trunk.Material = Enum.Material.Wood
        trunk.Anchored = true
        trunk.Parent = tree

        local leaves = Instance.new("Part")
        leaves.Name = "Leaves"
        leaves.Shape = Enum.PartType.Ball
        leaves.Size = Vector3.new(8, 8, 8)
        leaves.Position = trunk.Position + Vector3.new(0, 6, 0)
        leaves.BrickColor = BrickColor.new("Bright green")
        leaves.Material = Enum.Material.Grass
        leaves.Anchored = true
        leaves.Parent = tree

        tree.PrimaryPart = trunk
        tree.Parent = world
    end

    return world
end

CollectionWorld.create()
"""

    def _create_adventure_content(self, blueprint: GameBlueprint) -> str:
        """תוכן למשחק הרפתקה."""
        return """
-- ==========================================
-- עולם הרפתקה
-- ==========================================
local AdventureWorld = {}

function AdventureWorld.create()
    local world = Instance.new("Folder")
    world.Name = "AdventureWorld"
    world.Parent = workspace

    -- כפר התחלתי
    local village = Instance.new("Folder")
    village.Name = "StartVillage"
    village.Parent = world

    -- רצפה
    local ground = Instance.new("Part")
    ground.Name = "VillageGround"
    ground.Size = Vector3.new(100, 1, 100)
    ground.Position = Vector3.new(0, 0.5, 0)
    ground.BrickColor = BrickColor.new("Dirt brown")
    ground.Material = Enum.Material.Grass
    ground.Anchored = true
    ground.Parent = village

    -- בתים
    local housePositions = {
        Vector3.new(-30, 0, -20),
        Vector3.new(30, 0, -20),
        Vector3.new(-30, 0, 20),
        Vector3.new(30, 0, 20),
        Vector3.new(0, 0, -35),
    }

    for i, pos in ipairs(housePositions) do
        local house = Instance.new("Model")
        house.Name = "House_" .. i

        local base = Instance.new("Part")
        base.Name = "Base"
        base.Size = Vector3.new(15, 10, 12)
        base.Position = pos + Vector3.new(0, 6, 0)
        base.BrickColor = BrickColor.new("Brick yellow")
        base.Material = Enum.Material.Brick
        base.Anchored = true
        base.Parent = house

        -- גג
        local roof = Instance.new("WedgePart")
        roof.Name = "Roof"
        roof.Size = Vector3.new(12, 5, 8)
        roof.CFrame = CFrame.new(pos + Vector3.new(0, 13.5, 0)) * CFrame.Angles(0, math.rad(90), 0)
        roof.BrickColor = BrickColor.new("Dark orange")
        roof.Material = Enum.Material.Wood
        roof.Anchored = true
        roof.Parent = house

        -- דלת
        local door = Instance.new("Part")
        door.Name = "Door"
        door.Size = Vector3.new(4, 7, 0.5)
        door.Position = pos + Vector3.new(0, 4.5, 6)
        door.BrickColor = BrickColor.new("Brown")
        door.Material = Enum.Material.Wood
        door.Anchored = true
        door.Parent = house

        house.PrimaryPart = base
        house.Parent = village
    end

    -- באר במרכז
    local well = Instance.new("Model")
    well.Name = "Well"

    local wellBase = Instance.new("Part")
    wellBase.Name = "Base"
    wellBase.Shape = Enum.PartType.Cylinder
    wellBase.Size = Vector3.new(3, 6, 6)
    wellBase.CFrame = CFrame.new(Vector3.new(0, 2, 0)) * CFrame.Angles(0, 0, math.rad(90))
    wellBase.BrickColor = BrickColor.new("Dark stone grey")
    wellBase.Material = Enum.Material.Cobblestone
    wellBase.Anchored = true
    wellBase.Parent = well

    well.Parent = village

    -- שביל ליער
    local path = Instance.new("Part")
    path.Name = "PathToForest"
    path.Size = Vector3.new(10, 0.2, 100)
    path.Position = Vector3.new(0, 0.6, 80)
    path.BrickColor = BrickColor.new("Dirt brown")
    path.Material = Enum.Material.Sand
    path.Anchored = true
    path.Parent = world

    -- יער מסתורי
    local forest = Instance.new("Folder")
    forest.Name = "MysteryForest"
    forest.Parent = world

    for i = 1, 30 do
        local tree = Instance.new("Model")
        tree.Name = "Tree_" .. i

        local trunk = Instance.new("Part")
        trunk.Name = "Trunk"
        trunk.Size = Vector3.new(3, 15, 3)
        trunk.Position = Vector3.new(
            math.random(-60, 60),
            8.5,
            130 + math.random(0, 70)
        )
        trunk.BrickColor = BrickColor.new("Dark taupe")
        trunk.Material = Enum.Material.Wood
        trunk.Anchored = true
        trunk.Parent = tree

        local leaves = Instance.new("Part")
        leaves.Name = "Leaves"
        leaves.Shape = Enum.PartType.Ball
        leaves.Size = Vector3.new(12, 12, 12)
        leaves.Position = trunk.Position + Vector3.new(0, 10, 0)
        leaves.BrickColor = BrickColor.new("Forest green")
        leaves.Material = Enum.Material.Grass
        leaves.Anchored = true
        leaves.Parent = tree

        tree.PrimaryPart = trunk
        tree.Parent = forest
    end

    return world
end

AdventureWorld.create()
"""

    def _create_survival_content(self, blueprint: GameBlueprint) -> str:
        """תוכן למשחק הישרדות."""
        return """
-- ==========================================
-- עולם הישרדות
-- ==========================================
local SurvivalWorld = {}

function SurvivalWorld.create()
    local world = Instance.new("Folder")
    world.Name = "SurvivalWorld"
    world.Parent = workspace

    -- אי מרכזי
    local island = Instance.new("Part")
    island.Name = "Island"
    island.Size = Vector3.new(150, 5, 150)
    island.Position = Vector3.new(0, 2.5, 0)
    island.BrickColor = BrickColor.new("Bright green")
    island.Material = Enum.Material.Grass
    island.Anchored = true
    island.Parent = world

    -- מים סביב
    local water = Instance.new("Part")
    water.Name = "Water"
    water.Size = Vector3.new(500, 1, 500)
    water.Position = Vector3.new(0, 0, 0)
    water.BrickColor = BrickColor.new("Bright blue")
    water.Material = Enum.Material.Glass
    water.Transparency = 0.3
    water.Anchored = true
    water.CanCollide = false
    water.Parent = world

    -- בסיס שחקן
    local base = Instance.new("Model")
    base.Name = "PlayerBase"

    local floor = Instance.new("Part")
    floor.Name = "Floor"
    floor.Size = Vector3.new(20, 1, 20)
    floor.Position = Vector3.new(0, 5.5, 0)
    floor.BrickColor = BrickColor.new("Brown")
    floor.Material = Enum.Material.Wood
    floor.Anchored = true
    floor.Parent = base

    -- קירות
    for i = 1, 4 do
        local wall = Instance.new("Part")
        wall.Name = "Wall_" .. i
        wall.Size = i <= 2 and Vector3.new(20, 8, 1) or Vector3.new(1, 8, 20)
        if i == 1 then
            wall.Position = Vector3.new(0, 10, -10)
        elseif i == 2 then
            wall.Position = Vector3.new(0, 10, 10)
        elseif i == 3 then
            wall.Position = Vector3.new(-10, 10, 0)
        else
            wall.Position = Vector3.new(10, 10, 0)
        end
        wall.BrickColor = BrickColor.new("Brown")
        wall.Material = Enum.Material.Wood
        wall.Anchored = true
        wall.Parent = base
    end

    base.Parent = world

    -- משאבים פזורים
    local resourceTypes = {
        {name = "Wood", color = "Reddish brown", size = Vector3.new(2, 4, 2)},
        {name = "Stone", color = "Medium stone grey", size = Vector3.new(3, 2, 3)},
        {name = "Food", color = "Bright red", size = Vector3.new(1, 1, 1)},
    }

    for i = 1, 30 do
        local resType = resourceTypes[math.random(1, #resourceTypes)]
        local resource = Instance.new("Part")
        resource.Name = resType.name .. "_" .. i
        resource.Size = resType.size
        resource.Position = Vector3.new(
            math.random(-60, 60),
            5 + resType.size.Y / 2,
            math.random(-60, 60)
        )
        resource.BrickColor = BrickColor.new(resType.color)
        resource.Anchored = true
        resource.Parent = world

        -- סקריפט איסוף
        local collectScript = Instance.new("Script")
        collectScript.Source = string.format([[
            local resource = script.Parent
            local collected = false

            resource.Touched:Connect(function(hit)
                if collected then return end
                local player = game.Players:GetPlayerFromCharacter(hit.Parent)
                if player then
                    collected = true
                    print("🎒 " .. player.Name .. " אסף %s!")
                    resource:Destroy()
                end
            end)
        ]], resType.name)
        collectScript.Parent = resource
    end

    return world
end

SurvivalWorld.create()
"""

    def _create_custom_content(self, blueprint: GameBlueprint) -> str:
        """תוכן למשחק מותאם אישית."""
        return f"""
-- ==========================================
-- עולם מותאם אישית
-- ==========================================
local CustomWorld = {{}}

function CustomWorld.create()
    local world = Instance.new("Folder")
    world.Name = "CustomWorld"
    world.Parent = workspace

    -- רצפה בסיסית
    local floor = Instance.new("Part")
    floor.Name = "Floor"
    floor.Size = Vector3.new({blueprint.world_size[0]}, 1, {blueprint.world_size[2]})
    floor.Position = Vector3.new(0, 0.5, 0)
    floor.BrickColor = BrickColor.new("Medium green")
    floor.Material = Enum.Material.Grass
    floor.Anchored = true
    floor.Parent = world

    -- נקודת ספאון
    local spawn = Instance.new("SpawnLocation")
    spawn.Name = "SpawnPoint"
    spawn.Size = Vector3.new(6, 1, 6)
    spawn.Position = Vector3.new(0, 1.5, 0)
    spawn.BrickColor = BrickColor.new("Bright green")
    spawn.Material = Enum.Material.Neon
    spawn.Anchored = true
    spawn.Parent = world

    print("🌍 עולם מותאם אישית נוצר!")
    return world
end

CustomWorld.create()
"""

    def build_from_request(self, request: str) -> Dict[str, Any]:
        """
        בניית משחק מלא מבקשת משתמש.

        Args:
            request: הבקשה בעברית

        Returns:
            dict עם lua_code, success, blueprint
        """
        try:
            # נתח את הבקשה
            blueprint = self.analyze_request(request)

            # בנה את המשחק
            lua_code = self.build_complete_game(blueprint)

            return {
                "success": True,
                "lua_code": lua_code,
                "message": f"יצרתי {blueprint.name} מלא!",
                "blueprint": {
                    "name": blueprint.name,
                    "mode": blueprint.mode.value,
                    "lives": blueprint.lives,
                    "levels": blueprint.levels,
                    "collectibles": blueprint.collectibles,
                    "enemies": blueprint.enemies
                }
            }

        except Exception as e:
            self.on_status(f"שגיאה: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת Complete Game Builder")
    print("=" * 50)

    builder = CompleteGameBuilder()

    # בדיקות
    test_requests = [
        "בנה משחק מירוץ עם 5 חיים",
        "צור אובי עם 10 שלבים",
        "משחק איסוף מטבעות",
        "הרפתקה עם אויבים ומשימות",
    ]

    for request in test_requests:
        print(f"\n{'='*50}")
        print(f"בקשה: {request}")
        print("="*50)

        result = builder.build_from_request(request)

        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"תכנית: {result['blueprint']}")
            print(f"קוד: {len(result['lua_code'])} תווים")
        else:
            print(f"❌ שגיאה: {result['error']}")
