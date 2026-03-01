"""
Blueprint Schema - Two-Phase Generation System
==============================================
Phase 1: LLM generates JSON spec (blueprint)
Phase 2: Python converts JSON to deterministic Lua code

This eliminates randomness and Hebrew text in LLM output.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class PartType(str, Enum):
    PART = "Part"
    WEDGE = "WedgePart"
    CORNER_WEDGE = "CornerWedgePart"
    SPAWN = "SpawnLocation"
    CYLINDER = "Part"  # Shape = Cylinder


class Material(str, Enum):
    PLASTIC = "Plastic"
    WOOD = "Wood"
    BRICK = "Brick"
    CONCRETE = "Concrete"
    METAL = "Metal"
    GLASS = "Glass"
    NEON = "Neon"
    GRASS = "Grass"
    SAND = "Sand"
    FABRIC = "Fabric"
    MARBLE = "Marble"
    GRANITE = "Granite"
    ICE = "Ice"
    SLATE = "Slate"
    COBBLESTONE = "Cobblestone"


# Common BrickColors for Roblox
COLORS = {
    "red": "Bright red",
    "blue": "Bright blue",
    "green": "Bright green",
    "yellow": "Bright yellow",
    "white": "White",
    "black": "Black",
    "brown": "Reddish brown",
    "gray": "Medium stone grey",
    "orange": "Bright orange",
    "pink": "Pink",
    "purple": "Bright violet",
    "cyan": "Cyan",
    "beige": "Brick yellow",
    "dark_green": "Dark green",
    "light_blue": "Light blue",
    "tan": "Nougat",
}


@dataclass
class PartSpec:
    """Specification for a single part."""
    name: str
    type: str = "Part"
    size: List[float] = field(default_factory=lambda: [4, 1, 2])
    position: List[float] = field(default_factory=lambda: [0, 0, 0])
    color: str = "Medium stone grey"
    material: str = "Plastic"
    anchored: bool = True
    rotation: Optional[List[float]] = None  # [rx, ry, rz] in degrees
    transparency: float = 0.0
    shape: Optional[str] = None  # "Ball", "Cylinder" for Part

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BlueprintSpec:
    """
    Full blueprint specification for an object or scene.
    LLM should return this structure as JSON.
    """
    name: str
    description: str
    parts: List[Dict] = field(default_factory=list)
    scripts: List[Dict] = field(default_factory=list)  # NEW: embedded scripts
    base_position: List[float] = field(default_factory=lambda: [0, 0, 0])
    total_size: List[float] = field(default_factory=lambda: [20, 10, 20])

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'BlueprintSpec':
        return cls(
            name=data.get("name", "Creation"),
            description=data.get("description", ""),
            parts=data.get("parts", []),
            scripts=data.get("scripts", []),
            base_position=data.get("base_position", [0, 0, 0]),
            total_size=data.get("total_size", [20, 10, 20])
        )


# Pre-defined blueprints for common objects (instant response)
PRESET_BLUEPRINTS = {
    "house": BlueprintSpec(
        name="House",
        description="A simple house with walls, roof, door and windows",
        total_size=[24, 18, 24],
        parts=[
            # Floor
            {"name": "floor", "type": "Part", "size": [24, 1, 24], "position": [0, 0.5, 0], "color": "Reddish brown", "material": "Wood"},
            # Walls
            {"name": "wall_front", "type": "Part", "size": [24, 12, 1], "position": [0, 7, 11.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_back", "type": "Part", "size": [24, 12, 1], "position": [0, 7, -11.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_left", "type": "Part", "size": [1, 12, 22], "position": [-11.5, 7, 0], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_right", "type": "Part", "size": [1, 12, 22], "position": [11.5, 7, 0], "color": "Brick yellow", "material": "Brick"},
            # Roof
            {"name": "roof_left", "type": "WedgePart", "size": [24, 6, 13], "position": [-6, 16, 0], "color": "Dark orange", "material": "Slate", "rotation": [0, -90, 0]},
            {"name": "roof_right", "type": "WedgePart", "size": [24, 6, 13], "position": [6, 16, 0], "color": "Dark orange", "material": "Slate", "rotation": [0, 90, 0]},
            # Door (hole represented by transparent part)
            {"name": "door", "type": "Part", "size": [4, 8, 1], "position": [0, 4.5, 11.5], "color": "Reddish brown", "material": "Wood"},
            # Windows
            {"name": "window_left", "type": "Part", "size": [4, 4, 0.5], "position": [-6, 8, 11.75], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            {"name": "window_right", "type": "Part", "size": [4, 4, 0.5], "position": [6, 8, 11.75], "color": "Light blue", "material": "Glass", "transparency": 0.5},
        ]
    ),

    "tree": BlueprintSpec(
        name="Tree",
        description="A simple tree with trunk and foliage",
        total_size=[12, 20, 12],
        parts=[
            # Trunk
            {"name": "trunk", "type": "Part", "size": [3, 10, 3], "position": [0, 5, 0], "color": "Reddish brown", "material": "Wood"},
            # Foliage layers
            {"name": "foliage_1", "type": "Part", "size": [12, 4, 12], "position": [0, 12, 0], "color": "Dark green", "material": "Grass"},
            {"name": "foliage_2", "type": "Part", "size": [9, 4, 9], "position": [0, 15, 0], "color": "Bright green", "material": "Grass"},
            {"name": "foliage_3", "type": "Part", "size": [6, 4, 6], "position": [0, 18, 0], "color": "Dark green", "material": "Grass"},
        ]
    ),

    "car": BlueprintSpec(
        name="Car",
        description="A simple car with body and wheels",
        total_size=[12, 6, 6],
        parts=[
            # Body base
            {"name": "body", "type": "Part", "size": [12, 3, 6], "position": [0, 2, 0], "color": "Bright red", "material": "Metal"},
            # Cabin
            {"name": "cabin", "type": "Part", "size": [6, 3, 5], "position": [0, 5, 0], "color": "Bright red", "material": "Metal"},
            # Windshield
            {"name": "windshield", "type": "Part", "size": [0.5, 2.5, 4], "position": [2.75, 5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            # Rear window
            {"name": "rear_window", "type": "Part", "size": [0.5, 2.5, 4], "position": [-2.75, 5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            # Wheels
            {"name": "wheel_fl", "type": "Part", "size": [1, 2, 2], "position": [4, 1, 3.5], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_fr", "type": "Part", "size": [1, 2, 2], "position": [4, 1, -3.5], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_bl", "type": "Part", "size": [1, 2, 2], "position": [-4, 1, 3.5], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_br", "type": "Part", "size": [1, 2, 2], "position": [-4, 1, -3.5], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            # Headlights
            {"name": "headlight_l", "type": "Part", "size": [0.5, 1, 1], "position": [6.25, 2.5, 2], "color": "Bright yellow", "material": "Neon"},
            {"name": "headlight_r", "type": "Part", "size": [0.5, 1, 1], "position": [6.25, 2.5, -2], "color": "Bright yellow", "material": "Neon"},
        ]
    ),

    "driveable_car": BlueprintSpec(
        name="DriveableCar",
        description="A car you can actually drive!",
        total_size=[14, 7, 7],
        parts=[
            # Body base
            {"name": "body", "type": "Part", "size": [14, 3, 7], "position": [0, 2, 0], "color": "Bright red", "material": "Metal"},
            # Cabin
            {"name": "cabin", "type": "Part", "size": [7, 3, 6], "position": [0, 5, 0], "color": "Bright red", "material": "Metal"},
            # Windshield
            {"name": "windshield", "type": "Part", "size": [0.5, 2.5, 5], "position": [3, 5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            # Rear window
            {"name": "rear_window", "type": "Part", "size": [0.5, 2.5, 5], "position": [-3, 5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            # Driver seat (VehicleSeat!)
            {"name": "driver_seat", "type": "VehicleSeat", "size": [2, 1, 2], "position": [0, 3.5, 1.5], "color": "Black", "material": "Fabric"},
            # Wheels
            {"name": "wheel_fl", "type": "Part", "size": [1, 2.5, 2.5], "position": [5, 1.25, 4], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_fr", "type": "Part", "size": [1, 2.5, 2.5], "position": [5, 1.25, -4], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_bl", "type": "Part", "size": [1, 2.5, 2.5], "position": [-5, 1.25, 4], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_br", "type": "Part", "size": [1, 2.5, 2.5], "position": [-5, 1.25, -4], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            # Headlights
            {"name": "headlight_l", "type": "Part", "size": [0.5, 1, 1], "position": [7.25, 2.5, 2], "color": "Bright yellow", "material": "Neon"},
            {"name": "headlight_r", "type": "Part", "size": [0.5, 1, 1], "position": [7.25, 2.5, -2], "color": "Bright yellow", "material": "Neon"},
        ],
        scripts=[
            {
                "name": "DriveScript",
                "parent": "driver_seat",
                "source": "local seat = script.Parent\\nseat.MaxSpeed = 60\\nseat.Torque = 20\\nseat.TurnSpeed = 3\\n\\n-- Weld all car parts together\\nlocal model = seat.Parent\\nif model:IsA('Model') then\\n    local primaryPart = nil\\n    for _, part in ipairs(model:GetChildren()) do\\n        if part:IsA('BasePart') and part.Name == 'body' then\\n            primaryPart = part\\n            break\\n        end\\n    end\\n    if primaryPart then\\n        model.PrimaryPart = primaryPart\\n        for _, part in ipairs(model:GetChildren()) do\\n            if part:IsA('BasePart') and part ~= primaryPart then\\n                local weld = Instance.new('WeldConstraint')\\n                weld.Part0 = primaryPart\\n                weld.Part1 = part\\n                weld.Parent = part\\n                part.Anchored = false\\n            end\\n        end\\n        primaryPart.Anchored = false\\n    end\\nend\\nprint('Car ready to drive!')"
            }
        ]
    ),

    "enterable_house": BlueprintSpec(
        name="EnterableHouse",
        description="A house with a working door you can open!",
        total_size=[26, 18, 26],
        parts=[
            # Floor
            {"name": "floor", "type": "Part", "size": [26, 1, 26], "position": [0, 0.5, 0], "color": "Reddish brown", "material": "Wood"},
            # Walls (with gap for door)
            {"name": "wall_front_left", "type": "Part", "size": [9, 12, 1], "position": [-8.5, 7, 12.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_front_right", "type": "Part", "size": [9, 12, 1], "position": [8.5, 7, 12.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_front_top", "type": "Part", "size": [8, 4, 1], "position": [0, 11, 12.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_back", "type": "Part", "size": [26, 12, 1], "position": [0, 7, -12.5], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_left", "type": "Part", "size": [1, 12, 24], "position": [-12.5, 7, 0], "color": "Brick yellow", "material": "Brick"},
            {"name": "wall_right", "type": "Part", "size": [1, 12, 24], "position": [12.5, 7, 0], "color": "Brick yellow", "material": "Brick"},
            # Roof
            {"name": "roof_left", "type": "WedgePart", "size": [26, 6, 14], "position": [-6.5, 16, 0], "color": "Dark orange", "material": "Slate", "rotation": [0, -90, 0]},
            {"name": "roof_right", "type": "WedgePart", "size": [26, 6, 14], "position": [6.5, 16, 0], "color": "Dark orange", "material": "Slate", "rotation": [0, 90, 0]},
            # Door (clickable!)
            {"name": "door", "type": "Part", "size": [5, 8, 1], "position": [0, 5, 12.5], "color": "Reddish brown", "material": "Wood"},
            # Windows
            {"name": "window_left", "type": "Part", "size": [4, 4, 0.5], "position": [-7, 8, 12.75], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            {"name": "window_right", "type": "Part", "size": [4, 4, 0.5], "position": [7, 8, 12.75], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            # Interior - Table
            {"name": "table", "type": "Part", "size": [5, 0.5, 3], "position": [0, 3.25, -4], "color": "Brown", "material": "Wood"},
            # Interior - Table legs
            {"name": "table_leg1", "type": "Part", "size": [0.5, 3, 0.5], "position": [2, 1.5, -2.5], "color": "Brown", "material": "Wood"},
            {"name": "table_leg2", "type": "Part", "size": [0.5, 3, 0.5], "position": [-2, 1.5, -2.5], "color": "Brown", "material": "Wood"},
            {"name": "table_leg3", "type": "Part", "size": [0.5, 3, 0.5], "position": [2, 1.5, -5.5], "color": "Brown", "material": "Wood"},
            {"name": "table_leg4", "type": "Part", "size": [0.5, 3, 0.5], "position": [-2, 1.5, -5.5], "color": "Brown", "material": "Wood"},
            # Light inside
            {"name": "ceiling_light", "type": "Part", "size": [2, 0.5, 2], "position": [0, 12.75, 0], "color": "Bright yellow", "material": "Neon"},
        ],
        scripts=[
            {
                "name": "DoorScript",
                "parent": "door",
                "source": "local door = script.Parent\\nlocal clickDetector = Instance.new('ClickDetector')\\nclickDetector.MaxActivationDistance = 15\\nclickDetector.Parent = door\\n\\nlocal isOpen = false\\nlocal closedPos = door.Position\\nlocal openPos = closedPos + Vector3.new(5, 0, 0)\\n\\nclickDetector.MouseClick:Connect(function()\\n    if isOpen then\\n        door.Position = closedPos\\n        isOpen = false\\n    else\\n        door.Position = openPos\\n        isOpen = true\\n    end\\nend)\\nprint('Click the door to open/close!')"
            },
            {
                "name": "LightScript",
                "parent": "ceiling_light",
                "source": "local light = script.Parent\\nlocal pointLight = Instance.new('PointLight')\\npointLight.Color = Color3.fromRGB(255, 255, 200)\\npointLight.Brightness = 2\\npointLight.Range = 25\\npointLight.Parent = light"
            }
        ]
    ),

    "tower": BlueprintSpec(
        name="Tower",
        description="A tall tower with multiple floors",
        total_size=[10, 50, 10],
        parts=[
            # Base
            {"name": "base", "type": "Part", "size": [12, 2, 12], "position": [0, 1, 0], "color": "Dark stone grey", "material": "Concrete"},
            # Tower floors
            {"name": "floor1", "type": "Part", "size": [10, 10, 10], "position": [0, 7, 0], "color": "Medium stone grey", "material": "Concrete"},
            {"name": "floor2", "type": "Part", "size": [10, 10, 10], "position": [0, 17, 0], "color": "Medium stone grey", "material": "Concrete"},
            {"name": "floor3", "type": "Part", "size": [10, 10, 10], "position": [0, 27, 0], "color": "Medium stone grey", "material": "Concrete"},
            {"name": "floor4", "type": "Part", "size": [10, 10, 10], "position": [0, 37, 0], "color": "Medium stone grey", "material": "Concrete"},
            # Top
            {"name": "top", "type": "Part", "size": [8, 8, 8], "position": [0, 46, 0], "color": "Dark stone grey", "material": "Metal"},
            # Windows on each floor
            {"name": "window1", "type": "Part", "size": [6, 4, 0.5], "position": [0, 9, 5.25], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            {"name": "window2", "type": "Part", "size": [6, 4, 0.5], "position": [0, 19, 5.25], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            {"name": "window3", "type": "Part", "size": [6, 4, 0.5], "position": [0, 29, 5.25], "color": "Light blue", "material": "Glass", "transparency": 0.5},
            {"name": "window4", "type": "Part", "size": [6, 4, 0.5], "position": [0, 39, 5.25], "color": "Light blue", "material": "Glass", "transparency": 0.5},
        ]
    ),

    "platform": BlueprintSpec(
        name="Platform",
        description="A simple platform/stage",
        total_size=[30, 3, 20],
        parts=[
            {"name": "platform", "type": "Part", "size": [30, 3, 20], "position": [0, 1.5, 0], "color": "Medium stone grey", "material": "Concrete"},
            {"name": "edge_front", "type": "Part", "size": [30, 1, 1], "position": [0, 3.5, 10.5], "color": "Dark stone grey", "material": "Metal"},
            {"name": "edge_back", "type": "Part", "size": [30, 1, 1], "position": [0, 3.5, -10.5], "color": "Dark stone grey", "material": "Metal"},
        ]
    ),

    "cube": BlueprintSpec(
        name="Cube",
        description="A simple cube",
        total_size=[10, 10, 10],
        parts=[
            {"name": "cube", "type": "Part", "size": [10, 10, 10], "position": [0, 5, 0], "color": "Medium stone grey", "material": "Plastic"},
        ]
    ),

    "ball": BlueprintSpec(
        name="Ball",
        description="A simple sphere",
        total_size=[10, 10, 10],
        parts=[
            {"name": "ball", "type": "Part", "size": [10, 10, 10], "position": [0, 5, 0], "color": "Bright red", "material": "Plastic", "shape": "Ball"},
        ]
    ),

    "bridge": BlueprintSpec(
        name="Bridge",
        description="A sturdy bridge with railings",
        total_size=[40, 8, 12],
        parts=[
            # Foundation pillars
            {"name": "pillar_l", "type": "Part", "size": [4, 12, 4], "position": [-14, 6, 0], "color": "Dark stone grey", "material": "Concrete"},
            {"name": "pillar_r", "type": "Part", "size": [4, 12, 4], "position": [14, 6, 0], "color": "Dark stone grey", "material": "Concrete"},
            # Road surface
            {"name": "road", "type": "Part", "size": [40, 1, 12], "position": [0, 12, 0], "color": "Medium stone grey", "material": "Concrete"},
            # Railings
            {"name": "rail_l", "type": "Part", "size": [40, 3, 0.5], "position": [0, 14, 6], "color": "Dark stone grey", "material": "Metal"},
            {"name": "rail_r", "type": "Part", "size": [40, 3, 0.5], "position": [0, 14, -6], "color": "Dark stone grey", "material": "Metal"},
            # Rail posts
            {"name": "post_l1", "type": "Part", "size": [0.5, 3, 0.5], "position": [-15, 14, 6], "color": "Dark stone grey", "material": "Metal"},
            {"name": "post_l2", "type": "Part", "size": [0.5, 3, 0.5], "position": [-5, 14, 6], "color": "Dark stone grey", "material": "Metal"},
            {"name": "post_l3", "type": "Part", "size": [0.5, 3, 0.5], "position": [5, 14, 6], "color": "Dark stone grey", "material": "Metal"},
            {"name": "post_l4", "type": "Part", "size": [0.5, 3, 0.5], "position": [15, 14, 6], "color": "Dark stone grey", "material": "Metal"},
        ]
    ),

    "fountain": BlueprintSpec(
        name="Fountain",
        description="A decorative fountain with water",
        total_size=[14, 8, 14],
        parts=[
            # Base pool
            {"name": "pool_base", "type": "Part", "size": [14, 2, 14], "position": [0, 1, 0], "color": "Medium stone grey", "material": "Marble"},
            # Pool wall ring (using 4 walls)
            {"name": "pool_wall_f", "type": "Part", "size": [14, 3, 1], "position": [0, 2.5, 6.5], "color": "White", "material": "Marble"},
            {"name": "pool_wall_b", "type": "Part", "size": [14, 3, 1], "position": [0, 2.5, -6.5], "color": "White", "material": "Marble"},
            {"name": "pool_wall_l", "type": "Part", "size": [1, 3, 12], "position": [-6.5, 2.5, 0], "color": "White", "material": "Marble"},
            {"name": "pool_wall_r", "type": "Part", "size": [1, 3, 12], "position": [6.5, 2.5, 0], "color": "White", "material": "Marble"},
            # Water
            {"name": "water", "type": "Part", "size": [12, 1.5, 12], "position": [0, 2, 0], "color": "Cyan", "material": "Glass", "transparency": 0.4},
            # Center column
            {"name": "column", "type": "Part", "size": [2, 6, 2], "position": [0, 5, 0], "color": "White", "material": "Marble"},
            # Top bowl
            {"name": "top_bowl", "type": "Part", "size": [4, 1, 4], "position": [0, 7.5, 0], "color": "White", "material": "Marble"},
        ]
    ),

    "bench": BlueprintSpec(
        name="Bench",
        description="A park bench",
        total_size=[8, 4, 3],
        parts=[
            {"name": "seat", "type": "Part", "size": [8, 0.5, 3], "position": [0, 2, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "back", "type": "Part", "size": [8, 3, 0.5], "position": [0, 3.5, -1.25], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_l", "type": "Part", "size": [0.5, 2, 3], "position": [-3.5, 1, 0], "color": "Black", "material": "Metal"},
            {"name": "leg_r", "type": "Part", "size": [0.5, 2, 3], "position": [3.5, 1, 0], "color": "Black", "material": "Metal"},
        ]
    ),

    "street_light": BlueprintSpec(
        name="StreetLight",
        description="A street lamp with light",
        total_size=[2, 14, 2],
        parts=[
            {"name": "base", "type": "Part", "size": [3, 1, 3], "position": [0, 0.5, 0], "color": "Dark stone grey", "material": "Metal"},
            {"name": "pole", "type": "Part", "size": [1, 12, 1], "position": [0, 7, 0], "color": "Dark stone grey", "material": "Metal", "shape": "Cylinder"},
            {"name": "arm", "type": "Part", "size": [4, 0.5, 0.5], "position": [2, 13, 0], "color": "Dark stone grey", "material": "Metal"},
            {"name": "light_housing", "type": "Part", "size": [2, 1, 2], "position": [3.5, 12.5, 0], "color": "Bright yellow", "material": "Neon"},
        ]
    ),

    "chair": BlueprintSpec(
        name="Chair",
        description="A simple chair",
        total_size=[3, 5, 3],
        parts=[
            {"name": "seat", "type": "Part", "size": [3, 0.5, 3], "position": [0, 2, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "back", "type": "Part", "size": [3, 3, 0.5], "position": [0, 3.75, -1.25], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_fl", "type": "Part", "size": [0.4, 2, 0.4], "position": [-1.2, 1, 1.2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_fr", "type": "Part", "size": [0.4, 2, 0.4], "position": [1.2, 1, 1.2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_bl", "type": "Part", "size": [0.4, 2, 0.4], "position": [-1.2, 1, -1.2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_br", "type": "Part", "size": [0.4, 2, 0.4], "position": [1.2, 1, -1.2], "color": "Reddish brown", "material": "Wood"},
        ]
    ),

    "table": BlueprintSpec(
        name="Table",
        description="A dining table",
        total_size=[8, 4, 5],
        parts=[
            {"name": "top", "type": "Part", "size": [8, 0.5, 5], "position": [0, 3, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_fl", "type": "Part", "size": [0.5, 3, 0.5], "position": [-3.5, 1.5, 2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_fr", "type": "Part", "size": [0.5, 3, 0.5], "position": [3.5, 1.5, 2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_bl", "type": "Part", "size": [0.5, 3, 0.5], "position": [-3.5, 1.5, -2], "color": "Reddish brown", "material": "Wood"},
            {"name": "leg_br", "type": "Part", "size": [0.5, 3, 0.5], "position": [3.5, 1.5, -2], "color": "Reddish brown", "material": "Wood"},
        ]
    ),

    "fence": BlueprintSpec(
        name="Fence",
        description="A wooden fence section",
        total_size=[20, 5, 1],
        parts=[
            {"name": "rail_top", "type": "Part", "size": [20, 0.5, 0.5], "position": [0, 4, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "rail_bottom", "type": "Part", "size": [20, 0.5, 0.5], "position": [0, 2, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "post1", "type": "Part", "size": [0.5, 5, 0.5], "position": [-9, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "post2", "type": "Part", "size": [0.5, 5, 0.5], "position": [-3, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "post3", "type": "Part", "size": [0.5, 5, 0.5], "position": [3, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "post4", "type": "Part", "size": [0.5, 5, 0.5], "position": [9, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
        ]
    ),

    "slide": BlueprintSpec(
        name="Slide",
        description="A playground slide",
        total_size=[4, 10, 14],
        parts=[
            # Ladder
            {"name": "ladder_l", "type": "Part", "size": [0.5, 10, 0.5], "position": [-1.5, 5, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "ladder_r", "type": "Part", "size": [0.5, 10, 0.5], "position": [1.5, 5, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "rung1", "type": "Part", "size": [3, 0.3, 0.3], "position": [0, 2, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "rung2", "type": "Part", "size": [3, 0.3, 0.3], "position": [0, 4, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "rung3", "type": "Part", "size": [3, 0.3, 0.3], "position": [0, 6, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "rung4", "type": "Part", "size": [3, 0.3, 0.3], "position": [0, 8, -5], "color": "Bright blue", "material": "Metal"},
            # Platform
            {"name": "platform", "type": "Part", "size": [4, 0.5, 4], "position": [0, 10, -5], "color": "Bright blue", "material": "Metal"},
            # Slide surface (angled)
            {"name": "slide_surface", "type": "WedgePart", "size": [4, 10, 14], "position": [0, 5, 2], "color": "Bright yellow", "material": "Plastic"},
        ]
    ),

    "swing": BlueprintSpec(
        name="Swing",
        description="A swing set",
        total_size=[8, 10, 4],
        parts=[
            # Frame
            {"name": "frame_l", "type": "Part", "size": [0.5, 10, 0.5], "position": [-3.5, 5, 0], "color": "Bright red", "material": "Metal"},
            {"name": "frame_r", "type": "Part", "size": [0.5, 10, 0.5], "position": [3.5, 5, 0], "color": "Bright red", "material": "Metal"},
            {"name": "frame_top", "type": "Part", "size": [8, 0.5, 0.5], "position": [0, 10, 0], "color": "Bright red", "material": "Metal"},
            # Chains (represented as thin parts)
            {"name": "chain_l", "type": "Part", "size": [0.2, 6, 0.2], "position": [-1, 6.5, 0], "color": "Medium stone grey", "material": "Metal"},
            {"name": "chain_r", "type": "Part", "size": [0.2, 6, 0.2], "position": [1, 6.5, 0], "color": "Medium stone grey", "material": "Metal"},
            # Seat
            {"name": "seat", "type": "Part", "size": [3, 0.3, 2], "position": [0, 3.5, 0], "color": "Black", "material": "Plastic"},
        ]
    ),

    "boat": BlueprintSpec(
        name="Boat",
        description="A small boat",
        total_size=[16, 6, 8],
        parts=[
            # Hull
            {"name": "hull_bottom", "type": "Part", "size": [16, 1, 8], "position": [0, 0.5, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "hull_l", "type": "Part", "size": [16, 3, 0.5], "position": [0, 2.5, 3.75], "color": "Reddish brown", "material": "Wood"},
            {"name": "hull_r", "type": "Part", "size": [16, 3, 0.5], "position": [0, 2.5, -3.75], "color": "Reddish brown", "material": "Wood"},
            {"name": "hull_back", "type": "Part", "size": [0.5, 3, 7], "position": [-7.75, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            # Bow (front)
            {"name": "bow", "type": "WedgePart", "size": [7, 3, 3], "position": [6.5, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            # Mast
            {"name": "mast", "type": "Part", "size": [0.5, 10, 0.5], "position": [0, 6, 0], "color": "Reddish brown", "material": "Wood"},
            # Sail
            {"name": "sail", "type": "Part", "size": [0.2, 7, 5], "position": [0, 7, 2.5], "color": "White", "material": "Fabric"},
        ]
    ),

    "helicopter": BlueprintSpec(
        name="Helicopter",
        description="A helicopter",
        total_size=[14, 8, 6],
        parts=[
            # Body
            {"name": "body", "type": "Part", "size": [8, 4, 5], "position": [0, 3, 0], "color": "Bright blue", "material": "Metal"},
            # Cockpit glass
            {"name": "cockpit", "type": "Part", "size": [3, 3, 4.5], "position": [4, 3.5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.4},
            # Tail boom
            {"name": "tail", "type": "Part", "size": [6, 1.5, 1.5], "position": [-7, 3, 0], "color": "Bright blue", "material": "Metal"},
            # Main rotor
            {"name": "rotor", "type": "Part", "size": [14, 0.3, 1], "position": [0, 5.5, 0], "color": "Medium stone grey", "material": "Metal"},
            # Tail rotor
            {"name": "tail_rotor", "type": "Part", "size": [0.3, 3, 0.5], "position": [-10, 3.5, 0.75], "color": "Medium stone grey", "material": "Metal"},
            # Skids
            {"name": "skid_l", "type": "Part", "size": [6, 0.3, 0.3], "position": [0, 0.5, 2.5], "color": "Black", "material": "Metal"},
            {"name": "skid_r", "type": "Part", "size": [6, 0.3, 0.3], "position": [0, 0.5, -2.5], "color": "Black", "material": "Metal"},
        ]
    ),

    "airplane": BlueprintSpec(
        name="Airplane",
        description="A small airplane",
        total_size=[16, 6, 20],
        parts=[
            # Fuselage
            {"name": "fuselage", "type": "Part", "size": [16, 4, 4], "position": [0, 3, 0], "color": "White", "material": "Metal"},
            # Nose
            {"name": "nose", "type": "WedgePart", "size": [4, 3, 3], "position": [9, 3, 0], "color": "White", "material": "Metal"},
            # Wings
            {"name": "wing_l", "type": "Part", "size": [6, 0.5, 8], "position": [0, 3, 6], "color": "White", "material": "Metal"},
            {"name": "wing_r", "type": "Part", "size": [6, 0.5, 8], "position": [0, 3, -6], "color": "White", "material": "Metal"},
            # Tail
            {"name": "tail_v", "type": "WedgePart", "size": [2, 4, 3], "position": [-7, 5.5, 0], "color": "Bright blue", "material": "Metal"},
            {"name": "tail_h", "type": "Part", "size": [2, 0.3, 6], "position": [-7, 5, 0], "color": "White", "material": "Metal"},
            # Cockpit
            {"name": "cockpit", "type": "Part", "size": [4, 2, 3], "position": [5, 4.5, 0], "color": "Light blue", "material": "Glass", "transparency": 0.4},
            # Wheels
            {"name": "wheel_f", "type": "Part", "size": [1, 1.5, 1.5], "position": [5, 0.75, 0], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_bl", "type": "Part", "size": [1, 1.5, 1.5], "position": [-2, 0.75, 2], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "wheel_br", "type": "Part", "size": [1, 1.5, 1.5], "position": [-2, 0.75, -2], "color": "Black", "material": "Metal", "shape": "Cylinder"},
        ]
    ),

    "pool": BlueprintSpec(
        name="Pool",
        description="A swimming pool",
        total_size=[22, 4, 14],
        parts=[
            # Pool walls
            {"name": "wall_f", "type": "Part", "size": [22, 4, 1], "position": [0, 2, 6.5], "color": "Light blue", "material": "Concrete"},
            {"name": "wall_b", "type": "Part", "size": [22, 4, 1], "position": [0, 2, -6.5], "color": "Light blue", "material": "Concrete"},
            {"name": "wall_l", "type": "Part", "size": [1, 4, 12], "position": [-10.5, 2, 0], "color": "Light blue", "material": "Concrete"},
            {"name": "wall_r", "type": "Part", "size": [1, 4, 12], "position": [10.5, 2, 0], "color": "Light blue", "material": "Concrete"},
            # Pool floor
            {"name": "pool_floor", "type": "Part", "size": [20, 0.5, 12], "position": [0, 0.25, 0], "color": "Light blue", "material": "Concrete"},
            # Water
            {"name": "water", "type": "Part", "size": [20, 3, 12], "position": [0, 2, 0], "color": "Cyan", "material": "Glass", "transparency": 0.3},
            # Deck
            {"name": "deck", "type": "Part", "size": [26, 0.5, 18], "position": [0, 0.25, 0], "color": "Nougat", "material": "Concrete"},
        ]
    ),

    "rock": BlueprintSpec(
        name="Rock",
        description="A natural rock formation",
        total_size=[8, 5, 7],
        parts=[
            {"name": "base", "type": "Part", "size": [8, 3, 7], "position": [0, 1.5, 0], "color": "Medium stone grey", "material": "Granite"},
            {"name": "top", "type": "Part", "size": [5, 3, 5], "position": [0.5, 4, 0.5], "color": "Dark stone grey", "material": "Granite"},
            {"name": "detail", "type": "Part", "size": [3, 2, 3], "position": [-1, 5, -1], "color": "Medium stone grey", "material": "Granite"},
        ]
    ),

    "flower": BlueprintSpec(
        name="Flower",
        description="A colorful flower",
        total_size=[3, 4, 3],
        parts=[
            {"name": "stem", "type": "Part", "size": [0.3, 3, 0.3], "position": [0, 1.5, 0], "color": "Dark green", "material": "Grass"},
            {"name": "petal1", "type": "Part", "size": [1.5, 0.3, 1.5], "position": [0, 3.2, 0], "color": "Pink", "material": "Plastic", "shape": "Ball"},
            {"name": "petal2", "type": "Part", "size": [2, 0.3, 2], "position": [0, 3, 0], "color": "Bright red", "material": "Plastic", "shape": "Ball"},
            {"name": "center", "type": "Part", "size": [0.8, 0.5, 0.8], "position": [0, 3.4, 0], "color": "Bright yellow", "material": "Plastic", "shape": "Ball"},
        ]
    ),

    "lamp": BlueprintSpec(
        name="Lamp",
        description="A floor lamp",
        total_size=[2, 7, 2],
        parts=[
            {"name": "base", "type": "Part", "size": [2, 0.5, 2], "position": [0, 0.25, 0], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "pole", "type": "Part", "size": [0.5, 6, 0.5], "position": [0, 3.5, 0], "color": "Black", "material": "Metal", "shape": "Cylinder"},
            {"name": "shade", "type": "Part", "size": [3, 2, 3], "position": [0, 6.5, 0], "color": "Brick yellow", "material": "Fabric"},
            {"name": "bulb", "type": "Part", "size": [1, 1, 1], "position": [0, 6, 0], "color": "Bright yellow", "material": "Neon", "shape": "Ball"},
        ]
    ),

    # ====== NEW v4.0 Blueprints ======

    "rocket": BlueprintSpec(
        name="Rocket",
        description="A space rocket ready for launch",
        total_size=[6, 30, 6],
        parts=[
            {"name": "body", "type": "Part", "size": [6, 18, 6], "position": [0, 11, 0], "color": "White", "material": "Metal"},
            {"name": "nose_cone", "type": "WedgePart", "size": [5, 8, 5], "position": [0, 24, 0], "color": "Bright red", "material": "Metal"},
            {"name": "window", "type": "Part", "size": [2, 2, 0.5], "position": [0, 16, 3], "color": "Light blue", "material": "Glass", "transparency": 0.3, "shape": "Cylinder"},
            {"name": "fin_l", "type": "WedgePart", "size": [1, 6, 4], "position": [-3, 3, 0], "color": "Bright red", "material": "Metal"},
            {"name": "fin_r", "type": "WedgePart", "size": [1, 6, 4], "position": [3, 3, 0], "color": "Bright red", "material": "Metal"},
            {"name": "fin_b", "type": "WedgePart", "size": [4, 6, 1], "position": [0, 3, -3], "color": "Bright red", "material": "Metal"},
            {"name": "engine", "type": "Part", "size": [4, 3, 4], "position": [0, 0.5, 0], "color": "Dark stone grey", "material": "Metal", "shape": "Cylinder"},
            {"name": "flame", "type": "Part", "size": [3, 4, 3], "position": [0, -2, 0], "color": "Bright orange", "material": "Neon"},
        ]
    ),

    "soccer_field": BlueprintSpec(
        name="SoccerField",
        description="A soccer field with goals",
        total_size=[80, 2, 50],
        parts=[
            {"name": "field", "type": "Part", "size": [80, 1, 50], "position": [0, 0.5, 0], "color": "Bright green", "material": "Grass"},
            {"name": "center_line", "type": "Part", "size": [0.5, 0.1, 50], "position": [0, 1.1, 0], "color": "White", "material": "Plastic"},
            {"name": "center_circle", "type": "Part", "size": [16, 0.1, 16], "position": [0, 1.1, 0], "color": "White", "material": "Plastic", "shape": "Cylinder"},
            {"name": "goal_l_back", "type": "Part", "size": [1, 8, 16], "position": [-40, 4, 0], "color": "White", "material": "Metal"},
            {"name": "goal_l_top", "type": "Part", "size": [6, 0.5, 16], "position": [-37, 8, 0], "color": "White", "material": "Metal"},
            {"name": "goal_r_back", "type": "Part", "size": [1, 8, 16], "position": [40, 4, 0], "color": "White", "material": "Metal"},
            {"name": "goal_r_top", "type": "Part", "size": [6, 0.5, 16], "position": [37, 8, 0], "color": "White", "material": "Metal"},
            {"name": "ball", "type": "Part", "size": [3, 3, 3], "position": [0, 2.5, 0], "color": "White", "material": "Plastic", "shape": "Ball"},
        ]
    ),

    "cake": BlueprintSpec(
        name="Cake",
        description="A birthday cake with candles",
        total_size=[10, 10, 10],
        parts=[
            {"name": "plate", "type": "Part", "size": [12, 0.5, 12], "position": [0, 0.25, 0], "color": "White", "material": "Marble", "shape": "Cylinder"},
            {"name": "bottom_layer", "type": "Part", "size": [10, 3, 10], "position": [0, 2, 0], "color": "Pink", "material": "Plastic", "shape": "Cylinder"},
            {"name": "top_layer", "type": "Part", "size": [7, 3, 7], "position": [0, 5, 0], "color": "Bright red", "material": "Plastic", "shape": "Cylinder"},
            {"name": "frosting", "type": "Part", "size": [7.5, 0.5, 7.5], "position": [0, 6.5, 0], "color": "White", "material": "Plastic", "shape": "Cylinder"},
            {"name": "candle1", "type": "Part", "size": [0.3, 2, 0.3], "position": [-1, 7.5, -1], "color": "Bright blue", "material": "Plastic"},
            {"name": "candle2", "type": "Part", "size": [0.3, 2, 0.3], "position": [1, 7.5, 1], "color": "Bright yellow", "material": "Plastic"},
            {"name": "candle3", "type": "Part", "size": [0.3, 2, 0.3], "position": [0, 7.5, 0], "color": "Bright red", "material": "Plastic"},
            {"name": "flame1", "type": "Part", "size": [0.4, 0.6, 0.4], "position": [-1, 8.8, -1], "color": "Bright orange", "material": "Neon", "shape": "Ball"},
            {"name": "flame2", "type": "Part", "size": [0.4, 0.6, 0.4], "position": [1, 8.8, 1], "color": "Bright orange", "material": "Neon", "shape": "Ball"},
            {"name": "flame3", "type": "Part", "size": [0.4, 0.6, 0.4], "position": [0, 8.8, 0], "color": "Bright orange", "material": "Neon", "shape": "Ball"},
        ]
    ),

    "guitar": BlueprintSpec(
        name="Guitar",
        description="An acoustic guitar",
        total_size=[4, 14, 2],
        parts=[
            {"name": "body", "type": "Part", "size": [4, 5, 1.5], "position": [0, 2.5, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "sound_hole", "type": "Part", "size": [2, 2, 0.2], "position": [0, 3, 0.8], "color": "Black", "material": "Plastic", "shape": "Cylinder"},
            {"name": "neck", "type": "Part", "size": [1.2, 8, 0.8], "position": [0, 9, 0], "color": "Reddish brown", "material": "Wood"},
            {"name": "head", "type": "Part", "size": [1.5, 2, 0.8], "position": [0, 13.5, 0], "color": "Dark stone grey", "material": "Wood"},
            {"name": "bridge", "type": "Part", "size": [3, 0.3, 0.3], "position": [0, 1, 0.8], "color": "Black", "material": "Plastic"},
            {"name": "strings", "type": "Part", "size": [0.1, 12, 0.05], "position": [0, 7, 0.8], "color": "Medium stone grey", "material": "Metal"},
        ]
    ),

    "ice_cream": BlueprintSpec(
        name="IceCream",
        description="A giant ice cream cone",
        total_size=[4, 10, 4],
        parts=[
            {"name": "cone", "type": "WedgePart", "size": [4, 6, 4], "position": [0, 3, 0], "color": "Brick yellow", "material": "Wood"},
            {"name": "scoop1", "type": "Part", "size": [4, 4, 4], "position": [0, 7, 0], "color": "Pink", "material": "Plastic", "shape": "Ball"},
            {"name": "scoop2", "type": "Part", "size": [3.5, 3.5, 3.5], "position": [0, 9.5, 0], "color": "Bright yellow", "material": "Plastic", "shape": "Ball"},
            {"name": "scoop3", "type": "Part", "size": [3, 3, 3], "position": [0, 11.5, 0], "color": "Reddish brown", "material": "Plastic", "shape": "Ball"},
            {"name": "cherry", "type": "Part", "size": [1, 1, 1], "position": [0, 13, 0], "color": "Bright red", "material": "Plastic", "shape": "Ball"},
        ]
    ),

    "dog": BlueprintSpec(
        name="Dog",
        description="A cute blocky dog",
        total_size=[8, 6, 4],
        parts=[
            {"name": "body", "type": "Part", "size": [6, 3, 3], "position": [0, 3.5, 0], "color": "Reddish brown", "material": "Plastic"},
            {"name": "head", "type": "Part", "size": [3, 3, 3], "position": [4, 5, 0], "color": "Reddish brown", "material": "Plastic"},
            {"name": "nose", "type": "Part", "size": [1, 1, 1], "position": [5.5, 4.5, 0], "color": "Black", "material": "Plastic", "shape": "Ball"},
            {"name": "eye_l", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [5, 5.5, 1], "color": "Black", "material": "Plastic", "shape": "Ball"},
            {"name": "eye_r", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [5, 5.5, -1], "color": "Black", "material": "Plastic", "shape": "Ball"},
            {"name": "ear_l", "type": "Part", "size": [0.5, 2, 1], "position": [4, 6.5, 1.5], "color": "Reddish brown", "material": "Plastic"},
            {"name": "ear_r", "type": "Part", "size": [0.5, 2, 1], "position": [4, 6.5, -1.5], "color": "Reddish brown", "material": "Plastic"},
            {"name": "tail", "type": "Part", "size": [0.5, 2, 0.5], "position": [-3.5, 5, 0], "color": "Reddish brown", "material": "Plastic"},
            {"name": "leg_fl", "type": "Part", "size": [1, 2, 1], "position": [2, 1, 1], "color": "Reddish brown", "material": "Plastic"},
            {"name": "leg_fr", "type": "Part", "size": [1, 2, 1], "position": [2, 1, -1], "color": "Reddish brown", "material": "Plastic"},
            {"name": "leg_bl", "type": "Part", "size": [1, 2, 1], "position": [-2, 1, 1], "color": "Reddish brown", "material": "Plastic"},
            {"name": "leg_br", "type": "Part", "size": [1, 2, 1], "position": [-2, 1, -1], "color": "Reddish brown", "material": "Plastic"},
        ]
    ),

    "cat": BlueprintSpec(
        name="Cat",
        description="A cute blocky cat",
        total_size=[6, 5, 3],
        parts=[
            {"name": "body", "type": "Part", "size": [5, 2.5, 2.5], "position": [0, 3, 0], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "head", "type": "Part", "size": [2.5, 2.5, 2.5], "position": [3, 4.5, 0], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "ear_l", "type": "WedgePart", "size": [0.3, 1, 0.8], "position": [3.5, 6, 0.8], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "ear_r", "type": "WedgePart", "size": [0.3, 1, 0.8], "position": [3.5, 6, -0.8], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "nose", "type": "Part", "size": [0.4, 0.3, 0.3], "position": [4.3, 4.3, 0], "color": "Pink", "material": "Plastic", "shape": "Ball"},
            {"name": "eye_l", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [4, 5, 0.7], "color": "Bright green", "material": "Neon", "shape": "Ball"},
            {"name": "eye_r", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [4, 5, -0.7], "color": "Bright green", "material": "Neon", "shape": "Ball"},
            {"name": "tail", "type": "Part", "size": [0.4, 3, 0.4], "position": [-3, 4, 0], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "leg_fl", "type": "Part", "size": [0.8, 1.5, 0.8], "position": [1.5, 1, 0.8], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "leg_fr", "type": "Part", "size": [0.8, 1.5, 0.8], "position": [1.5, 1, -0.8], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "leg_bl", "type": "Part", "size": [0.8, 1.5, 0.8], "position": [-1.5, 1, 0.8], "color": "Medium stone grey", "material": "Plastic"},
            {"name": "leg_br", "type": "Part", "size": [0.8, 1.5, 0.8], "position": [-1.5, 1, -0.8], "color": "Medium stone grey", "material": "Plastic"},
        ]
    ),

    "piano": BlueprintSpec(
        name="Piano",
        description="An upright piano",
        total_size=[10, 8, 4],
        parts=[
            {"name": "body", "type": "Part", "size": [10, 7, 3], "position": [0, 3.5, 0], "color": "Black", "material": "Wood"},
            {"name": "top", "type": "Part", "size": [10, 0.5, 3.5], "position": [0, 7.25, 0], "color": "Black", "material": "Wood"},
            {"name": "keyboard", "type": "Part", "size": [9, 0.3, 1.5], "position": [0, 3.5, 2], "color": "White", "material": "Plastic"},
            {"name": "black_keys", "type": "Part", "size": [8, 0.3, 0.8], "position": [0, 3.7, 1.5], "color": "Black", "material": "Plastic"},
            {"name": "leg_l", "type": "Part", "size": [0.5, 3, 0.5], "position": [-4.5, 1.5, 1.5], "color": "Black", "material": "Wood"},
            {"name": "leg_r", "type": "Part", "size": [0.5, 3, 0.5], "position": [4.5, 1.5, 1.5], "color": "Black", "material": "Wood"},
            {"name": "pedals", "type": "Part", "size": [3, 0.5, 0.5], "position": [0, 0.5, 1.5], "color": "Bright yellow", "material": "Metal"},
        ]
    ),

    "star": BlueprintSpec(
        name="Star",
        description="A glowing star",
        total_size=[10, 10, 3],
        parts=[
            {"name": "center", "type": "Part", "size": [5, 5, 2], "position": [0, 5, 0], "color": "Bright yellow", "material": "Neon"},
            {"name": "point_top", "type": "WedgePart", "size": [2, 4, 2], "position": [0, 9, 0], "color": "Bright yellow", "material": "Neon"},
            {"name": "point_bottom", "type": "WedgePart", "size": [2, 4, 2], "position": [0, 1, 0], "color": "Bright yellow", "material": "Neon"},
            {"name": "point_left", "type": "Part", "size": [4, 2, 2], "position": [-4, 5, 0], "color": "Bright yellow", "material": "Neon"},
            {"name": "point_right", "type": "Part", "size": [4, 2, 2], "position": [4, 5, 0], "color": "Bright yellow", "material": "Neon"},
        ]
    ),

    "spaceship": BlueprintSpec(
        name="Spaceship",
        description="A futuristic spaceship",
        total_size=[20, 6, 12],
        parts=[
            {"name": "hull", "type": "Part", "size": [16, 3, 6], "position": [0, 3, 0], "color": "Medium stone grey", "material": "Metal"},
            {"name": "cockpit", "type": "Part", "size": [4, 2.5, 4], "position": [7, 4, 0], "color": "Light blue", "material": "Glass", "transparency": 0.3},
            {"name": "nose", "type": "WedgePart", "size": [5, 2, 4], "position": [10, 3, 0], "color": "Medium stone grey", "material": "Metal"},
            {"name": "wing_l", "type": "WedgePart", "size": [8, 0.5, 5], "position": [-2, 3, 5], "color": "Bright blue", "material": "Metal"},
            {"name": "wing_r", "type": "WedgePart", "size": [8, 0.5, 5], "position": [-2, 3, -5], "color": "Bright blue", "material": "Metal"},
            {"name": "engine_l", "type": "Part", "size": [3, 2, 2], "position": [-8, 3, 3], "color": "Dark stone grey", "material": "Metal", "shape": "Cylinder"},
            {"name": "engine_r", "type": "Part", "size": [3, 2, 2], "position": [-8, 3, -3], "color": "Dark stone grey", "material": "Metal", "shape": "Cylinder"},
            {"name": "exhaust_l", "type": "Part", "size": [1, 1.5, 1.5], "position": [-9.5, 3, 3], "color": "Cyan", "material": "Neon"},
            {"name": "exhaust_r", "type": "Part", "size": [1, 1.5, 1.5], "position": [-9.5, 3, -3], "color": "Cyan", "material": "Neon"},
        ]
    ),

    # ====== v5.0 INTERACTIVE PRESETS — with Scripts! ======

    "spinning_coin": BlueprintSpec(
        name="SpinningCoin",
        description="A gold spinning coin that can be collected",
        total_size=[4, 4, 4],
        parts=[
            {"name": "coin", "type": "Part", "size": [0.5, 4, 4], "position": [0, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "SpinScript", "parent": "coin", "source": "local coin = script.Parent\\nwhile coin.Parent do\\n    coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n    wait(0.03)\\nend"},
            {"name": "CollectScript", "parent": "coin", "source": "local coin = script.Parent\\ncoin.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid then\\n        local sound = Instance.new('Sound', workspace)\\n        sound.SoundId = 'rbxasset://sounds/electronicPing.wav'\\n        sound.PlaybackSpeed = 2\\n        sound:Play()\\n        coin:Destroy()\\n    end\\nend)"},
        ]
    ),

    "trampoline": BlueprintSpec(
        name="Trampoline",
        description="A trampoline that launches players up!",
        total_size=[10, 2, 10],
        parts=[
            {"name": "frame", "type": "Part", "size": [10, 2, 10], "position": [0, 1, 0], "color": "Bright blue", "material": "Metal", "shape": "Cylinder"},
            {"name": "surface", "type": "Part", "size": [8, 0.3, 8], "position": [0, 2.2, 0], "color": "Bright yellow", "material": "Neon", "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "BounceScript", "parent": "surface", "source": "local pad = script.Parent\\npad.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    local root = hit.Parent:FindFirstChild('HumanoidRootPart')\\n    if humanoid and root then\\n        root.Velocity = Vector3.new(root.Velocity.X, 120, root.Velocity.Z)\\n        local sound = Instance.new('Sound', pad)\\n        sound.SoundId = 'rbxasset://sounds/electronicPing.wav'\\n        sound.PlaybackSpeed = 0.8\\n        sound:Play()\\n        game.Debris:AddItem(sound, 2)\\n    end\\nend)"},
        ]
    ),

    "lava_floor": BlueprintSpec(
        name="LavaFloor",
        description="Dangerous lava floor that damages players!",
        total_size=[20, 1, 20],
        parts=[
            {"name": "lava", "type": "Part", "size": [20, 1, 20], "position": [0, 0.5, 0], "color": "Bright orange", "material": "Neon"},
            {"name": "glow1", "type": "Part", "size": [18, 0.5, 18], "position": [0, 0.3, 0], "color": "Bright red", "material": "Neon", "transparency": 0.3},
        ],
        scripts=[
            {"name": "DamageScript", "parent": "lava", "source": "local lava = script.Parent\\nlava.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid then\\n        humanoid.Health = humanoid.Health - 15\\n    end\\nend)"},
        ]
    ),

    "speed_boost": BlueprintSpec(
        name="SpeedBoost",
        description="A speed boost pad that makes players run faster!",
        total_size=[8, 1, 8],
        parts=[
            {"name": "pad", "type": "Part", "size": [8, 0.5, 8], "position": [0, 0.25, 0], "color": "Lime green", "material": "Neon"},
            {"name": "arrow1", "type": "WedgePart", "size": [2, 0.3, 3], "position": [0, 0.6, 0], "color": "White", "material": "Neon"},
            {"name": "arrow2", "type": "WedgePart", "size": [2, 0.3, 3], "position": [0, 0.6, -3], "color": "White", "material": "Neon"},
        ],
        scripts=[
            {"name": "SpeedScript", "parent": "pad", "source": "local pad = script.Parent\\nlocal debounce = {}\\npad.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid and not debounce[humanoid] then\\n        debounce[humanoid] = true\\n        humanoid.WalkSpeed = 50\\n        wait(5)\\n        if humanoid and humanoid.Parent then\\n            humanoid.WalkSpeed = 16\\n        end\\n        debounce[humanoid] = nil\\n    end\\nend)"},
        ]
    ),

    "teleporter": BlueprintSpec(
        name="Teleporter",
        description="A teleporter pad with glowing effect",
        total_size=[6, 8, 6],
        parts=[
            {"name": "base", "type": "Part", "size": [6, 1, 6], "position": [0, 0.5, 0], "color": "Bright violet", "material": "Neon", "shape": "Cylinder"},
            {"name": "ring1", "type": "Part", "size": [7, 0.5, 7], "position": [0, 3, 0], "color": "Cyan", "material": "Neon", "transparency": 0.5, "shape": "Cylinder"},
            {"name": "ring2", "type": "Part", "size": [5, 0.5, 5], "position": [0, 5, 0], "color": "Bright violet", "material": "Neon", "transparency": 0.5, "shape": "Cylinder"},
            {"name": "ring3", "type": "Part", "size": [3, 0.5, 3], "position": [0, 7, 0], "color": "Cyan", "material": "Neon", "transparency": 0.5, "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "TeleportScript", "parent": "base", "source": "local pad = script.Parent\\npad.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    local root = hit.Parent:FindFirstChild('HumanoidRootPart')\\n    if humanoid and root then\\n        root.CFrame = root.CFrame + Vector3.new(50, 20, 0)\\n    end\\nend)"},
        ]
    ),

    "checkpoint": BlueprintSpec(
        name="Checkpoint",
        description="A checkpoint/spawn point with flag",
        total_size=[6, 12, 6],
        parts=[
            {"name": "spawn", "type": "SpawnLocation", "size": [6, 1, 6], "position": [0, 0.5, 0], "color": "Bright green", "material": "Neon"},
            {"name": "pole", "type": "Part", "size": [0.5, 10, 0.5], "position": [2.5, 6, 2.5], "color": "White", "material": "Metal"},
            {"name": "flag", "type": "Part", "size": [3, 2, 0.2], "position": [4, 10, 2.5], "color": "Bright red", "material": "Fabric"},
        ],
        scripts=[]
    ),

    "spinning_platform": BlueprintSpec(
        name="SpinningPlatform",
        description="A platform that rotates - try to stay on!",
        total_size=[14, 2, 14],
        parts=[
            {"name": "base_pillar", "type": "Part", "size": [3, 8, 3], "position": [0, 4, 0], "color": "Dark stone grey", "material": "Concrete"},
            {"name": "platform", "type": "Part", "size": [14, 1.5, 14], "position": [0, 8.75, 0], "color": "Bright blue", "material": "Metal", "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "SpinScript", "parent": "platform", "source": "local platform = script.Parent\\nwhile platform.Parent do\\n    platform.CFrame = platform.CFrame * CFrame.Angles(0, math.rad(1), 0)\\n    wait(0.03)\\nend"},
        ]
    ),

    "fire_pit": BlueprintSpec(
        name="FirePit",
        description="A campfire with fire effect",
        total_size=[6, 4, 6],
        parts=[
            {"name": "pit_base", "type": "Part", "size": [6, 1, 6], "position": [0, 0.5, 0], "color": "Dark stone grey", "material": "Slate", "shape": "Cylinder"},
            {"name": "logs1", "type": "Part", "size": [4, 0.8, 0.8], "position": [0, 1.4, 0], "color": "Reddish brown", "material": "Wood", "shape": "Cylinder"},
            {"name": "logs2", "type": "Part", "size": [4, 0.8, 0.8], "position": [0, 1.4, 0], "color": "Reddish brown", "material": "Wood", "shape": "Cylinder", "rotation": [0, 90, 0]},
            {"name": "flame_core", "type": "Part", "size": [2, 3, 2], "position": [0, 3, 0], "color": "Bright orange", "material": "Neon", "transparency": 0.3},
            {"name": "flame_tip", "type": "Part", "size": [1, 2, 1], "position": [0, 4.5, 0], "color": "Bright yellow", "material": "Neon", "transparency": 0.4},
        ],
        scripts=[
            {"name": "FireEffect", "parent": "flame_core", "source": "local fire = Instance.new('Fire')\\nfire.Size = 10\\nfire.Heat = 15\\nfire.Color = Color3.fromRGB(255, 100, 0)\\nfire.SecondaryColor = Color3.fromRGB(255, 200, 0)\\nfire.Parent = script.Parent\\nlocal light = Instance.new('PointLight')\\nlight.Brightness = 2\\nlight.Color = Color3.fromRGB(255, 150, 0)\\nlight.Range = 30\\nlight.Parent = script.Parent"},
        ]
    ),

    "coin_trail": BlueprintSpec(
        name="CoinTrail",
        description="A trail of collectible spinning coins",
        total_size=[40, 5, 5],
        parts=[
            {"name": "coin1", "type": "Part", "size": [0.5, 3, 3], "position": [-15, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin2", "type": "Part", "size": [0.5, 3, 3], "position": [-7.5, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin3", "type": "Part", "size": [0.5, 3, 3], "position": [0, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin4", "type": "Part", "size": [0.5, 3, 3], "position": [7.5, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin5", "type": "Part", "size": [0.5, 3, 3], "position": [15, 5, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "SpinAndCollect", "parent": "coin1", "source": "local coin = script.Parent\\nspawn(function()\\n    while coin.Parent do\\n        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n        wait(0.03)\\n    end\\nend)\\ncoin.Touched:Connect(function(hit)\\n    if hit.Parent:FindFirstChild('Humanoid') then coin:Destroy() end\\nend)"},
            {"name": "SpinAndCollect", "parent": "coin2", "source": "local coin = script.Parent\\nspawn(function()\\n    while coin.Parent do\\n        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n        wait(0.03)\\n    end\\nend)\\ncoin.Touched:Connect(function(hit)\\n    if hit.Parent:FindFirstChild('Humanoid') then coin:Destroy() end\\nend)"},
            {"name": "SpinAndCollect", "parent": "coin3", "source": "local coin = script.Parent\\nspawn(function()\\n    while coin.Parent do\\n        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n        wait(0.03)\\n    end\\nend)\\ncoin.Touched:Connect(function(hit)\\n    if hit.Parent:FindFirstChild('Humanoid') then coin:Destroy() end\\nend)"},
            {"name": "SpinAndCollect", "parent": "coin4", "source": "local coin = script.Parent\\nspawn(function()\\n    while coin.Parent do\\n        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n        wait(0.03)\\n    end\\nend)\\ncoin.Touched:Connect(function(hit)\\n    if hit.Parent:FindFirstChild('Humanoid') then coin:Destroy() end\\nend)"},
            {"name": "SpinAndCollect", "parent": "coin5", "source": "local coin = script.Parent\\nspawn(function()\\n    while coin.Parent do\\n        coin.CFrame = coin.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n        wait(0.03)\\n    end\\nend)\\ncoin.Touched:Connect(function(hit)\\n    if hit.Parent:FindFirstChild('Humanoid') then coin:Destroy() end\\nend)"},
        ]
    ),
    # ====== v5.0 GAME SYSTEMS — Leaderboard, Health, Coin Counter ======

    "leaderboard": BlueprintSpec(
        name="Leaderboard",
        description="A leaderboard system that tracks player coins",
        total_size=[4, 8, 2],
        parts=[
            {"name": "board", "type": "Part", "size": [8, 10, 1], "position": [0, 7, 0], "color": "Dark stone grey", "material": "Metal"},
            {"name": "screen", "type": "Part", "size": [7, 8, 0.2], "position": [0, 7, 0.6], "color": "Black", "material": "Neon"},
            {"name": "title_bar", "type": "Part", "size": [7, 1.5, 0.3], "position": [0, 11.5, 0.6], "color": "Gold", "material": "Neon"},
        ],
        scripts=[
            {"name": "LeaderboardScript", "parent": "board", "source": "local DataStoreService = game:GetService('DataStoreService')\\nlocal Players = game:GetService('Players')\\n\\nPlayers.PlayerAdded:Connect(function(player)\\n    local leaderstats = Instance.new('Folder')\\n    leaderstats.Name = 'leaderstats'\\n    leaderstats.Parent = player\\n\\n    local coins = Instance.new('IntValue')\\n    coins.Name = 'Coins'\\n    coins.Value = 0\\n    coins.Parent = leaderstats\\n\\n    local score = Instance.new('IntValue')\\n    score.Name = 'Score'\\n    score.Value = 0\\n    score.Parent = leaderstats\\nend)"},
        ]
    ),

    "health_pickup": BlueprintSpec(
        name="HealthPickup",
        description="A health pickup that heals players",
        total_size=[3, 3, 3],
        parts=[
            {"name": "heart", "type": "Part", "size": [3, 3, 3], "position": [0, 4, 0], "color": "Bright red", "material": "Neon", "shape": "Ball"},
            {"name": "glow_ring", "type": "Part", "size": [4, 0.3, 4], "position": [0, 2.5, 0], "color": "Pink", "material": "Neon", "transparency": 0.4, "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "HealScript", "parent": "heart", "source": "local heart = script.Parent\\nspawn(function()\\n    while heart.Parent do\\n        heart.CFrame = heart.CFrame * CFrame.Angles(0, math.rad(2), 0)\\n        wait(0.03)\\n    end\\nend)\\nheart.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid and humanoid.Health < humanoid.MaxHealth then\\n        humanoid.Health = humanoid.MaxHealth\\n        local sound = Instance.new('Sound', workspace)\\n        sound.SoundId = 'rbxasset://sounds/electronicPing.wav'\\n        sound.PlaybackSpeed = 1.5\\n        sound:Play()\\n        heart:Destroy()\\n    end\\nend)"},
        ]
    ),

    "kill_brick": BlueprintSpec(
        name="KillBrick",
        description="A brick that instantly kills players on touch",
        total_size=[10, 1, 10],
        parts=[
            {"name": "killzone", "type": "Part", "size": [10, 1, 10], "position": [0, 0.5, 0], "color": "Really red", "material": "Neon"},
        ],
        scripts=[
            {"name": "KillScript", "parent": "killzone", "source": "local brick = script.Parent\\nbrick.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid then\\n        humanoid.Health = 0\\n    end\\nend)"},
        ]
    ),

    "moving_platform": BlueprintSpec(
        name="MovingPlatform",
        description="A platform that moves back and forth",
        total_size=[8, 1, 8],
        parts=[
            {"name": "platform", "type": "Part", "size": [8, 1.5, 8], "position": [0, 5, 0], "color": "Bright green", "material": "Metal"},
            {"name": "arrow_l", "type": "WedgePart", "size": [2, 0.3, 2], "position": [-4.5, 6, 0], "color": "White", "material": "Neon"},
            {"name": "arrow_r", "type": "WedgePart", "size": [2, 0.3, 2], "position": [4.5, 6, 0], "color": "White", "material": "Neon"},
        ],
        scripts=[
            {"name": "MoveScript", "parent": "platform", "source": "local platform = script.Parent\\nlocal origin = platform.Position\\nlocal distance = 30\\nlocal speed = 0.02\\nlocal t = 0\\nwhile platform.Parent do\\n    t = t + speed\\n    platform.Position = origin + Vector3.new(math.sin(t) * distance, 0, 0)\\n    wait(0.03)\\nend"},
        ]
    ),

    "guard_npc": BlueprintSpec(
        name="GuardNPC",
        description="A guard that patrols back and forth",
        total_size=[4, 10, 4],
        parts=[
            {"name": "torso", "type": "Part", "size": [2, 2.5, 1.5], "position": [0, 4.25, 0], "color": "Bright blue", "material": "Plastic"},
            {"name": "head", "type": "Part", "size": [1.5, 1.5, 1.5], "position": [0, 6, 0], "color": "Nougat", "material": "Plastic", "shape": "Ball"},
            {"name": "helmet", "type": "Part", "size": [1.8, 1, 1.8], "position": [0, 6.8, 0], "color": "Dark stone grey", "material": "Metal"},
            {"name": "leg_l", "type": "Part", "size": [0.8, 2.5, 0.8], "position": [-0.5, 1.25, 0], "color": "Dark blue", "material": "Plastic"},
            {"name": "leg_r", "type": "Part", "size": [0.8, 2.5, 0.8], "position": [0.5, 1.25, 0], "color": "Dark blue", "material": "Plastic"},
            {"name": "arm_l", "type": "Part", "size": [0.6, 2, 0.6], "position": [-1.3, 4, 0], "color": "Bright blue", "material": "Plastic"},
            {"name": "arm_r", "type": "Part", "size": [0.6, 2, 0.6], "position": [1.3, 4, 0], "color": "Bright blue", "material": "Plastic"},
            {"name": "sword", "type": "Part", "size": [0.3, 3, 0.1], "position": [1.6, 4.5, 0], "color": "Medium stone grey", "material": "Metal"},
        ],
        scripts=[
            {"name": "PatrolScript", "parent": "torso", "source": "local npc = script.Parent.Parent or script.Parent\\nlocal origin = script.Parent.Position\\nlocal distance = 25\\nlocal speed = 0.05\\nlocal t = 0\\nwhile script.Parent and script.Parent.Parent do\\n    t = t + speed\\n    local offset = math.sin(t) * distance\\n    for _, part in ipairs(npc:GetChildren()) do\\n        if part:IsA('BasePart') then\\n            part.Position = part.Position + Vector3.new(offset * 0.02, 0, 0)\\n        end\\n    end\\n    wait(0.03)\\nend"},
        ]
    ),

    "enemy_npc": BlueprintSpec(
        name="EnemyNPC",
        description="A red enemy that damages players on touch",
        total_size=[4, 8, 4],
        parts=[
            {"name": "torso", "type": "Part", "size": [2.5, 3, 1.5], "position": [0, 4.5, 0], "color": "Bright red", "material": "Plastic"},
            {"name": "head", "type": "Part", "size": [2, 2, 2], "position": [0, 6.5, 0], "color": "Bright red", "material": "Plastic"},
            {"name": "eye_l", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [-0.5, 6.8, 1], "color": "Bright yellow", "material": "Neon", "shape": "Ball"},
            {"name": "eye_r", "type": "Part", "size": [0.5, 0.5, 0.3], "position": [0.5, 6.8, 1], "color": "Bright yellow", "material": "Neon", "shape": "Ball"},
            {"name": "leg_l", "type": "Part", "size": [1, 3, 1], "position": [-0.7, 1.5, 0], "color": "Bright red", "material": "Plastic"},
            {"name": "leg_r", "type": "Part", "size": [1, 3, 1], "position": [0.7, 1.5, 0], "color": "Bright red", "material": "Plastic"},
        ],
        scripts=[
            {"name": "DamageScript", "parent": "torso", "source": "local torso = script.Parent\\ntorso.Touched:Connect(function(hit)\\n    local humanoid = hit.Parent:FindFirstChild('Humanoid')\\n    if humanoid then\\n        humanoid.Health = humanoid.Health - 25\\n    end\\nend)"},
        ]
    ),

    "friendly_npc": BlueprintSpec(
        name="FriendlyNPC",
        description="A friendly character that waves",
        total_size=[4, 8, 4],
        parts=[
            {"name": "torso", "type": "Part", "size": [2, 2.5, 1.5], "position": [0, 4.25, 0], "color": "Bright green", "material": "Plastic"},
            {"name": "head", "type": "Part", "size": [1.5, 1.5, 1.5], "position": [0, 6, 0], "color": "Nougat", "material": "Plastic", "shape": "Ball"},
            {"name": "hat", "type": "Part", "size": [2, 0.5, 2], "position": [0, 7, 0], "color": "Bright green", "material": "Fabric", "shape": "Cylinder"},
            {"name": "leg_l", "type": "Part", "size": [0.8, 2.5, 0.8], "position": [-0.5, 1.25, 0], "color": "Bright green", "material": "Plastic"},
            {"name": "leg_r", "type": "Part", "size": [0.8, 2.5, 0.8], "position": [0.5, 1.25, 0], "color": "Bright green", "material": "Plastic"},
            {"name": "arm_l", "type": "Part", "size": [0.6, 2, 0.6], "position": [-1.3, 4, 0], "color": "Bright green", "material": "Plastic"},
            {"name": "arm_r", "type": "Part", "size": [0.6, 2, 0.6], "position": [1.3, 4, 0], "color": "Bright green", "material": "Plastic"},
        ],
        scripts=[
            {"name": "WaveScript", "parent": "arm_r", "source": "local arm = script.Parent\\nlocal origin = arm.Position\\nwhile arm and arm.Parent do\\n    for i = 0, 60, 3 do\\n        arm.Position = origin + Vector3.new(0, math.sin(math.rad(i * 6)) * 1.5, 0)\\n        wait(0.03)\\n    end\\n    wait(2)\\nend"},
        ]
    ),

    "rain": BlueprintSpec(
        name="Rain",
        description="Rain weather effect with dark clouds",
        total_size=[200, 100, 200],
        parts=[
            {"name": "cloud1", "type": "Part", "size": [60, 8, 40], "position": [-30, 80, -20], "color": "Dark stone grey", "material": "Plastic", "transparency": 0.3},
            {"name": "cloud2", "type": "Part", "size": [50, 6, 35], "position": [30, 85, 20], "color": "Dark stone grey", "material": "Plastic", "transparency": 0.3},
            {"name": "cloud3", "type": "Part", "size": [45, 7, 30], "position": [0, 82, -30], "color": "Medium stone grey", "material": "Plastic", "transparency": 0.4},
        ],
        scripts=[
            {"name": "RainScript", "parent": "cloud1", "source": "local Lighting = game:GetService('Lighting')\\nLighting.Brightness = 1\\nLighting.FogEnd = 300\\nLighting.FogColor = Color3.fromRGB(120, 120, 130)\\nlocal atmosphere = Instance.new('Atmosphere')\\natmosphere.Density = 0.4\\natmosphere.Offset = 0.25\\natmosphere.Color = Color3.fromRGB(150, 155, 165)\\natmosphere.Parent = Lighting\\nfor _, cloud in ipairs(script.Parent.Parent:GetChildren()) do\\n    if cloud:IsA('BasePart') then\\n        local emitter = Instance.new('ParticleEmitter')\\n        emitter.Rate = 80\\n        emitter.Lifetime = NumberRange.new(2, 4)\\n        emitter.Speed = NumberRange.new(30, 50)\\n        emitter.Size = NumberSequence.new(0.1)\\n        emitter.Transparency = NumberSequence.new(0.3)\\n        emitter.Color = ColorSequence.new(Color3.fromRGB(180, 200, 255))\\n        emitter.EmissionDirection = Enum.NormalId.Bottom\\n        emitter.Parent = cloud\\n    end\\nend"},
        ]
    ),

    "snow": BlueprintSpec(
        name="Snow",
        description="Snowy weather with white ground",
        total_size=[200, 100, 200],
        parts=[
            {"name": "snow_ground", "type": "Part", "size": [200, 0.5, 200], "position": [0, 0.25, 0], "color": "White", "material": "Glass", "transparency": 0.1},
            {"name": "cloud1", "type": "Part", "size": [60, 8, 40], "position": [-20, 80, -10], "color": "White", "material": "Plastic", "transparency": 0.4},
            {"name": "cloud2", "type": "Part", "size": [50, 6, 35], "position": [25, 85, 15], "color": "White", "material": "Plastic", "transparency": 0.4},
        ],
        scripts=[
            {"name": "SnowScript", "parent": "cloud1", "source": "local Lighting = game:GetService('Lighting')\\nLighting.Brightness = 2\\nLighting.FogEnd = 250\\nLighting.FogColor = Color3.fromRGB(220, 225, 235)\\nlocal atmosphere = Instance.new('Atmosphere')\\natmosphere.Density = 0.3\\natmosphere.Color = Color3.fromRGB(230, 235, 245)\\natmosphere.Parent = Lighting\\nfor _, cloud in ipairs(script.Parent.Parent:GetChildren()) do\\n    if cloud:IsA('BasePart') and cloud.Name:find('cloud') then\\n        local emitter = Instance.new('ParticleEmitter')\\n        emitter.Rate = 40\\n        emitter.Lifetime = NumberRange.new(5, 8)\\n        emitter.Speed = NumberRange.new(3, 8)\\n        emitter.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(1, 0.5)})\\n        emitter.Color = ColorSequence.new(Color3.new(1, 1, 1))\\n        emitter.EmissionDirection = Enum.NormalId.Bottom\\n        emitter.SpreadAngle = Vector2.new(40, 40)\\n        emitter.Parent = cloud\\n    end\\nend"},
        ]
    ),

    "night": BlueprintSpec(
        name="Night",
        description="Nighttime with stars and moon",
        total_size=[10, 10, 10],
        parts=[
            {"name": "moon", "type": "Part", "size": [15, 15, 1], "position": [80, 120, -80], "color": "White", "material": "Neon", "shape": "Cylinder", "transparency": 0.1},
        ],
        scripts=[
            {"name": "NightScript", "parent": "moon", "source": "local Lighting = game:GetService('Lighting')\\nLighting.ClockTime = 0\\nLighting.Brightness = 0.5\\nLighting.Ambient = Color3.fromRGB(30, 30, 50)\\nLighting.OutdoorAmbient = Color3.fromRGB(40, 40, 70)\\nLighting.FogEnd = 500\\nLighting.FogColor = Color3.fromRGB(10, 10, 30)\\nlocal sky = Instance.new('Sky')\\nsky.StarCount = 5000\\nsky.Parent = Lighting\\nlocal bloom = Instance.new('BloomEffect')\\nbloom.Intensity = 0.3\\nbloom.Threshold = 1.5\\nbloom.Size = 20\\nbloom.Parent = Lighting"},
        ]
    ),

    "sunset": BlueprintSpec(
        name="Sunset",
        description="Beautiful sunset lighting",
        total_size=[10, 10, 10],
        parts=[
            {"name": "sun_glow", "type": "Part", "size": [20, 20, 1], "position": [100, 40, -100], "color": "Bright orange", "material": "Neon", "transparency": 0.5, "shape": "Cylinder"},
        ],
        scripts=[
            {"name": "SunsetScript", "parent": "sun_glow", "source": "local Lighting = game:GetService('Lighting')\\nLighting.ClockTime = 18\\nLighting.Brightness = 2\\nLighting.Ambient = Color3.fromRGB(80, 50, 30)\\nLighting.OutdoorAmbient = Color3.fromRGB(120, 80, 40)\\nLighting.FogEnd = 800\\nLighting.FogColor = Color3.fromRGB(200, 120, 60)\\nlocal atmosphere = Instance.new('Atmosphere')\\natmosphere.Density = 0.3\\natmosphere.Offset = 0.5\\natmosphere.Color = Color3.fromRGB(255, 150, 80)\\natmosphere.Decay = Color3.fromRGB(200, 100, 50)\\natmosphere.Parent = Lighting\\nlocal bloom = Instance.new('BloomEffect')\\nbloom.Intensity = 0.5\\nbloom.Threshold = 1\\nbloom.Size = 30\\nbloom.Parent = Lighting"},
        ]
    ),

    "fog": BlueprintSpec(
        name="Fog",
        description="Thick mysterious fog",
        total_size=[10, 10, 10],
        parts=[
            {"name": "fog_marker", "type": "Part", "size": [1, 1, 1], "position": [0, 0.5, 0], "color": "White", "material": "Plastic", "transparency": 1},
        ],
        scripts=[
            {"name": "FogScript", "parent": "fog_marker", "source": "local Lighting = game:GetService('Lighting')\\nLighting.FogEnd = 100\\nLighting.FogStart = 10\\nLighting.FogColor = Color3.fromRGB(200, 200, 210)\\nlocal atmosphere = Instance.new('Atmosphere')\\natmosphere.Density = 0.8\\natmosphere.Offset = 0\\natmosphere.Color = Color3.fromRGB(200, 200, 210)\\natmosphere.Parent = Lighting"},
        ]
    ),

    "coin_collector_game": BlueprintSpec(
        name="CoinCollectorGame",
        description="Complete coin collector mini-game with scoring",
        total_size=[80, 20, 80],
        parts=[
            {"name": "arena_floor", "type": "Part", "size": [80, 1, 80], "position": [0, 0.5, 0], "color": "Bright green", "material": "Grass"},
            {"name": "wall_f", "type": "Part", "size": [80, 10, 2], "position": [0, 5, 41], "color": "Dark stone grey", "material": "Concrete", "transparency": 0.5},
            {"name": "wall_b", "type": "Part", "size": [80, 10, 2], "position": [0, 5, -41], "color": "Dark stone grey", "material": "Concrete", "transparency": 0.5},
            {"name": "wall_l", "type": "Part", "size": [2, 10, 80], "position": [-41, 5, 0], "color": "Dark stone grey", "material": "Concrete", "transparency": 0.5},
            {"name": "wall_r", "type": "Part", "size": [2, 10, 80], "position": [41, 5, 0], "color": "Dark stone grey", "material": "Concrete", "transparency": 0.5},
            {"name": "coin1", "type": "Part", "size": [0.5, 3, 3], "position": [-20, 4, -15], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin2", "type": "Part", "size": [0.5, 3, 3], "position": [15, 4, 20], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin3", "type": "Part", "size": [0.5, 3, 3], "position": [-10, 4, 25], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin4", "type": "Part", "size": [0.5, 3, 3], "position": [25, 4, -10], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "coin5", "type": "Part", "size": [0.5, 3, 3], "position": [0, 4, 0], "color": "Gold", "material": "Neon", "shape": "Cylinder"},
            {"name": "spawn", "type": "SpawnLocation", "size": [8, 1, 8], "position": [0, 0.5, -35], "color": "Bright green", "material": "Neon"},
        ],
        scripts=[
            {"name": "GameScript", "parent": "arena_floor", "source": "local Players = game:GetService('Players')\\nPlayers.PlayerAdded:Connect(function(player)\\n    local ls = Instance.new('Folder')\\n    ls.Name = 'leaderstats'\\n    ls.Parent = player\\n    local coins = Instance.new('IntValue')\\n    coins.Name = 'Coins'\\n    coins.Value = 0\\n    coins.Parent = ls\\nend)\\nfor _, part in ipairs(script.Parent.Parent:GetChildren()) do\\n    if part:IsA('BasePart') and part.Name:find('coin') then\\n        spawn(function()\\n            while part.Parent do\\n                part.CFrame = part.CFrame * CFrame.Angles(0, math.rad(3), 0)\\n                wait(0.03)\\n            end\\n        end)\\n        part.Touched:Connect(function(hit)\\n            local player = game.Players:GetPlayerFromCharacter(hit.Parent)\\n            if player and player:FindFirstChild('leaderstats') then\\n                player.leaderstats.Coins.Value = player.leaderstats.Coins.Value + 10\\n                local s = Instance.new('Sound', workspace)\\n                s.SoundId = 'rbxasset://sounds/electronicPing.wav'\\n                s.PlaybackSpeed = 2\\n                s:Play()\\n                part:Destroy()\\n            end\\n        end)\\n    end\\nend"},
        ]
    ),

    "race_track": BlueprintSpec(
        name="RaceTrack",
        description="A race track with speed boosts and timer",
        total_size=[120, 5, 40],
        parts=[
            {"name": "track", "type": "Part", "size": [120, 1, 20], "position": [0, 0.5, 0], "color": "Dark stone grey", "material": "Concrete"},
            {"name": "line_start", "type": "Part", "size": [1, 0.1, 20], "position": [-55, 1.1, 0], "color": "White", "material": "Neon"},
            {"name": "line_finish", "type": "Part", "size": [1, 0.1, 20], "position": [55, 1.1, 0], "color": "Bright yellow", "material": "Neon"},
            {"name": "boost1", "type": "Part", "size": [6, 0.2, 20], "position": [-25, 1.1, 0], "color": "Lime green", "material": "Neon"},
            {"name": "boost2", "type": "Part", "size": [6, 0.2, 20], "position": [15, 1.1, 0], "color": "Lime green", "material": "Neon"},
            {"name": "wall_l", "type": "Part", "size": [120, 3, 1], "position": [0, 2, 10.5], "color": "Bright red", "material": "Metal"},
            {"name": "wall_r", "type": "Part", "size": [120, 3, 1], "position": [0, 2, -10.5], "color": "Bright red", "material": "Metal"},
            {"name": "arch", "type": "Part", "size": [1, 8, 22], "position": [55, 5, 0], "color": "Bright yellow", "material": "Neon", "transparency": 0.5},
            {"name": "spawn", "type": "SpawnLocation", "size": [8, 1, 8], "position": [-55, 0.5, 0], "color": "Bright green", "material": "Neon"},
        ],
        scripts=[
            {"name": "BoostScript", "parent": "boost1", "source": "script.Parent.Touched:Connect(function(hit)\\n    local h = hit.Parent:FindFirstChild('Humanoid')\\n    if h then h.WalkSpeed = 60 wait(3) if h.Parent then h.WalkSpeed = 16 end end\\nend)"},
            {"name": "BoostScript2", "parent": "boost2", "source": "script.Parent.Touched:Connect(function(hit)\\n    local h = hit.Parent:FindFirstChild('Humanoid')\\n    if h then h.WalkSpeed = 60 wait(3) if h.Parent then h.WalkSpeed = 16 end end\\nend)"},
            {"name": "FinishScript", "parent": "line_finish", "source": "script.Parent.Touched:Connect(function(hit)\\n    local h = hit.Parent:FindFirstChild('Humanoid')\\n    if h then\\n        local s = Instance.new('Sound', workspace)\\n        s.SoundId = 'rbxasset://sounds/electronicPing.wav'\\n        s.PlaybackSpeed = 1.5\\n        s:Play()\\n    end\\nend)"},
        ]
    ),
}


# Hebrew to English object mapping (expanded for v4.0)
HEBREW_OBJECTS = {
    # Buildings
    "בית": "enterable_house", "עץ": "tree", "מכונית": "driveable_car", "רכב": "driveable_car", "אוטו": "driveable_car",
    "רכב נוסע": "driveable_car", "מכונית נוסעת": "driveable_car",
    "בית עם דלת": "enterable_house", "בית פתוח": "enterable_house", "בית אמיתי": "enterable_house",
    "מגדל": "tower", "בניין": "tower",
    # Shapes
    "במה": "platform", "פלטפורמה": "platform", "קוביה": "cube", "קובייה": "cube",
    "כדור": "ball",
    # Infrastructure
    "גשר": "bridge", "מזרקה": "fountain", "ספסל": "bench", "גדר": "fence",
    "פנס": "street_light", "פנס רחוב": "street_light",
    # Furniture
    "כיסא": "chair", "שולחן": "table", "מנורה": "lamp",
    # Playground
    "מגלשה": "slide", "נדנדה": "swing",
    # Vehicles
    "סירה": "boat", "מסוק": "helicopter", "מטוס": "airplane",
    # Nature
    "סלע": "rock", "אבן": "rock", "פרח": "flower",
    # Fun
    "בריכה": "pool", "בריכת שחייה": "pool",
    # NEW v4.0 — Space
    "רקטה": "rocket", "טיל": "rocket", "חללית": "spaceship",
    # NEW v4.0 — Sports
    "מגרש כדורגל": "soccer_field", "כדורגל": "soccer_field",
    # NEW v4.0 — Animals
    "כלב": "dog", "חתול": "cat",
    # NEW v4.0 — Food
    "עוגה": "cake", "עוגת יום הולדת": "cake",
    "גלידה": "ice_cream",
    # NEW v4.0 — Music
    "גיטרה": "guitar", "פסנתר": "piano",
    # NEW v4.0 — Other
    "כוכב": "star",
    # NEW v5.0 — Interactive
    "מטבע": "spinning_coin", "מטבעות": "coin_trail", "שביל מטבעות": "coin_trail",
    "טרמפולינה": "trampoline", "קפיצה": "trampoline", "קפיץ": "trampoline",
    "לבה": "lava_floor", "רצפת לבה": "lava_floor",
    "מהירות": "speed_boost", "ספיד": "speed_boost", "בוסט": "speed_boost",
    "טלפורט": "teleporter", "שער קסם": "teleporter", "פורטל": "teleporter",
    "צ'קפוינט": "checkpoint", "נקודת שמירה": "checkpoint",
    "במה מסתובבת": "spinning_platform", "פלטפורמה מסתובבת": "spinning_platform",
    "מדורה": "fire_pit", "אש": "fire_pit", "מוקד": "fire_pit",
    # NEW v5.0 — Game Systems
    "לידרבורד": "leaderboard", "טבלת ניקוד": "leaderboard", "ניקוד": "leaderboard",
    "חיים": "health_pickup", "לב": "health_pickup", "ריפוי": "health_pickup",
    "קיל בריק": "kill_brick", "לבנת מוות": "kill_brick",
    "במה נעה": "moving_platform", "פלטפורמה נעה": "moving_platform",
    # NEW v6.0 — NPCs
    "שומר": "guard_npc", "שומר ביטחון": "guard_npc", "חייל": "guard_npc",
    "אויב": "enemy_npc", "מפלצת": "enemy_npc", "זומבי": "enemy_npc",
    "חבר": "friendly_npc", "דמות": "friendly_npc", "בן אדם": "friendly_npc",
    # NEW v6.0 — Weather & Lighting
    "גשם": "rain", "מטר": "rain",
    "שלג": "snow",
    "לילה": "night", "חושך": "night",
    "שקיעה": "sunset",
    "ערפל": "fog",
    # NEW v6.0 — Mini-games
    "משחק מטבעות": "coin_collector_game", "אסוף מטבעות": "coin_collector_game",
    "מירוץ": "race_track", "מסלול מירוץ": "race_track",
}

# English to preset mapping (for English voice commands)
ENGLISH_OBJECTS = {
    # Buildings
    "house": "enterable_house", "simple house": "house", "home": "enterable_house",
    "castle": "tower", "tower": "tower", "building": "tower",
    # Vehicles
    "car": "driveable_car", "vehicle": "driveable_car", "automobile": "driveable_car",
    "simple car": "car", "basic car": "car",
    "boat": "boat", "ship": "boat",
    "helicopter": "helicopter", "chopper": "helicopter",
    "airplane": "airplane", "plane": "airplane", "jet": "airplane",
    # Nature
    "tree": "tree", "big tree": "tree", "large tree": "tree",
    "rock": "rock", "stone": "rock", "boulder": "rock",
    "flower": "flower", "plant": "flower",
    # Furniture
    "table": "table", "desk": "table",
    "chair": "chair", "seat": "chair",
    "lamp": "lamp", "light": "lamp",
    # Infrastructure
    "bridge": "bridge",
    "fountain": "fountain", "water fountain": "fountain",
    "bench": "bench", "park bench": "bench",
    "fence": "fence", "wall fence": "fence",
    "street light": "street_light", "streetlight": "street_light", "lamp post": "street_light",
    # Shapes
    "platform": "platform", "stage": "platform",
    "cube": "cube", "block": "cube", "box": "cube",
    "ball": "ball", "sphere": "ball",
    # Playground
    "slide": "slide",
    "swing": "swing",
    # Fun
    "pool": "pool", "swimming pool": "pool",
    # Space
    "rocket": "rocket", "missile": "rocket",
    "spaceship": "spaceship", "space ship": "spaceship", "ufo": "spaceship",
    # Sports
    "soccer field": "soccer_field", "football field": "soccer_field", "soccer": "soccer_field",
    # Animals
    "dog": "dog", "puppy": "dog",
    "cat": "cat", "kitten": "cat",
    # Food
    "cake": "cake", "birthday cake": "cake",
    "ice cream": "ice_cream", "icecream": "ice_cream",
    # Music
    "guitar": "guitar",
    "piano": "piano",
    # Other
    "star": "star",
    # Interactive (v5.0)
    "coin": "spinning_coin", "spinning coin": "spinning_coin",
    "coin trail": "coin_trail", "coins": "coin_trail",
    "trampoline": "trampoline", "bounce pad": "trampoline",
    "lava": "lava_floor", "lava floor": "lava_floor",
    "speed boost": "speed_boost", "speed pad": "speed_boost", "boost": "speed_boost",
    "teleport": "teleporter", "teleporter": "teleporter", "portal": "teleporter",
    "checkpoint": "checkpoint", "spawn point": "checkpoint", "save point": "checkpoint",
    "spinning platform": "spinning_platform", "rotating platform": "spinning_platform",
    "campfire": "fire_pit", "fire": "fire_pit", "bonfire": "fire_pit", "fireplace": "fire_pit",
    # Game Systems (v5.0)
    "leaderboard": "leaderboard", "scoreboard": "leaderboard", "score": "leaderboard",
    "health pickup": "health_pickup", "heart": "health_pickup", "health": "health_pickup",
    "kill brick": "kill_brick", "death brick": "kill_brick",
    "moving platform": "moving_platform",
    # NPCs (v6.0)
    "guard": "guard_npc", "soldier": "guard_npc", "security": "guard_npc",
    "enemy": "enemy_npc", "monster": "enemy_npc", "zombie": "enemy_npc",
    "friend": "friendly_npc", "friendly npc": "friendly_npc", "npc": "friendly_npc", "character": "friendly_npc",
    # Weather & Lighting (v6.0)
    "rain": "rain",
    "snow": "snow",
    "night": "night", "dark": "night", "darkness": "night",
    "sunset": "sunset",
    "fog": "fog", "mist": "fog",
    # Mini-games (v6.0)
    "coin game": "coin_collector_game", "coin collector": "coin_collector_game", "collect coins": "coin_collector_game",
    "race": "race_track", "race track": "race_track", "racing": "race_track",
}

# English color mapping
ENGLISH_COLORS = {
    "red": "Bright red",
    "blue": "Bright blue",
    "green": "Bright green",
    "yellow": "Bright yellow",
    "white": "White",
    "black": "Black",
    "brown": "Reddish brown",
    "gray": "Medium stone grey", "grey": "Medium stone grey",
    "orange": "Bright orange",
    "pink": "Pink",
    "purple": "Bright violet",
    "cyan": "Light blue", "light blue": "Light blue",
    "gold": "Gold", "golden": "Gold",
}

# Hebrew color mapping
HEBREW_COLORS = {
    "אדום": "Bright red",
    "כחול": "Bright blue",
    "ירוק": "Bright green",
    "צהוב": "Bright yellow",
    "לבן": "White",
    "שחור": "Black",
    "חום": "Reddish brown",
    "אפור": "Medium stone grey",
    "כתום": "Bright orange",
    "ורוד": "Pink",
    "סגול": "Bright violet",
    "תכלת": "Light blue",
}


def get_blueprint_for_command(hebrew_text: str) -> Optional[BlueprintSpec]:
    """
    Try to match Hebrew or English command to a preset blueprint.
    Returns None if no match found (needs LLM).
    """
    text_lower = hebrew_text.lower().strip()

    # Complex commands with multiple objects should go to LLM
    # Detect by commas or many descriptors
    comma_count = text_lower.count(',') + text_lower.count('،')
    if comma_count >= 2:
        return None  # Complex scene → LLM

    # Compound phrases that should NOT trigger sub-word matches
    COMPOUND_EXCLUSIONS = {
        "כדור הארץ": "כדור",      # Earth ≠ ball
        "כדור סל": "כדור",         # basketball ≠ ball
        "מגרש משחקים": "משחק",     # playground ≠ game
        "פנס רחוב": "פנס",         # already handled but safe
    }

    # Remove compound phrases from text before simple matching
    filtered_text = text_lower
    for compound, sub_word in COMPOUND_EXCLUSIONS.items():
        if compound in filtered_text:
            filtered_text = filtered_text.replace(compound, "")

    # Find object type — match LONGEST keys first to prefer specific matches
    object_type = None

    # Try Hebrew objects first
    sorted_objects = sorted(HEBREW_OBJECTS.items(), key=lambda x: len(x[0]), reverse=True)
    for heb, eng in sorted_objects:
        if heb in filtered_text:
            object_type = eng
            break

    # If no Hebrew match, try English objects
    if not object_type:
        sorted_english = sorted(ENGLISH_OBJECTS.items(), key=lambda x: len(x[0]), reverse=True)
        for eng_word, preset_name in sorted_english:
            if eng_word in filtered_text:
                object_type = preset_name
                break

    if not object_type or object_type not in PRESET_BLUEPRINTS:
        return None

    # Clone the blueprint
    blueprint = PRESET_BLUEPRINTS[object_type]
    result = BlueprintSpec(
        name=blueprint.name,
        description=blueprint.description,
        parts=[p.copy() for p in blueprint.parts],
        scripts=[s.copy() for s in blueprint.scripts],
        base_position=blueprint.base_position.copy(),
        total_size=blueprint.total_size.copy()
    )

    # Find color modification — check Hebrew colors first, then English
    color_found = False
    for heb_color, eng_color in HEBREW_COLORS.items():
        if heb_color in text_lower:
            for part in result.parts:
                if "window" not in part["name"] and "wheel" not in part["name"] and "glass" not in part.get("material", "").lower():
                    if part["name"] in ["body", "cabin", "cube", "ball", "foliage_1", "foliage_2", "foliage_3"]:
                        continue  # Skip specific parts
                    if "floor" in part["name"] or "wall" in part["name"] or "roof" in part["name"]:
                        part["color"] = eng_color
            color_found = True
            break

    if not color_found:
        for color_word, eng_color in ENGLISH_COLORS.items():
            if color_word in text_lower:
                for part in result.parts:
                    if "window" not in part["name"] and "wheel" not in part["name"] and "glass" not in part.get("material", "").lower():
                        if part["name"] in ["body", "cabin", "cube", "ball", "foliage_1", "foliage_2", "foliage_3"]:
                            continue
                        if "floor" in part["name"] or "wall" in part["name"] or "roof" in part["name"]:
                            part["color"] = eng_color
                break

    return result


def get_json_prompt_for_llm() -> str:
    """
    Returns the system prompt that instructs LLM to return JSON blueprints.
    """
    return """You are a JSON blueprint generator for Roblox Studio.
Your task is to create detailed JSON specifications for 3D objects and scenes.

OUTPUT FORMAT - Return ONLY valid JSON, no explanations:
{
  "name": "Object Name",
  "description": "Brief description",
  "total_size": [width, height, depth],
  "base_position": [0, 0, 0],
  "parts": [
    {
      "name": "part_name",
      "type": "Part",
      "size": [width, height, depth],
      "position": [x, y, z],
      "color": "BrickColor name",
      "material": "Material name",
      "anchored": true,
      "rotation": [rx, ry, rz],
      "transparency": 0.0,
      "shape": null
    }
  ]
}

PART TYPES:
- "Part" - standard block
- "WedgePart" - triangular prism (for roofs)
- "CornerWedgePart" - corner piece
- "SpawnLocation" - player spawn point

MATERIALS: Plastic, Wood, Brick, Concrete, Metal, Glass, Neon, Grass, Sand, Fabric, Marble, Granite, Ice, Slate, Cobblestone

COLORS (BrickColor names):
- Basic: "Bright red", "Bright blue", "Bright green", "Bright yellow", "White", "Black"
- Building: "Brick yellow", "Reddish brown", "Medium stone grey", "Dark stone grey"
- Nature: "Dark green", "Bright green", "Sand", "Nougat"
- Other: "Bright orange", "Pink", "Bright violet", "Light blue", "Cyan"

SHAPE (only for "Part" type):
- null or omit for block
- "Ball" for sphere
- "Cylinder" for cylinder (rotated on Y by default)

ROTATION: [x, y, z] in degrees. Common: [0, 90, 0] for 90-degree turn.

POSITIONING:
- Y is up (height)
- Objects should be placed so their bottom is at Y=0 or above
- Position is the CENTER of the part, so a part with height 10 at Y=5 will have its bottom at Y=0

BUILDING TIPS:
1. Use realistic proportions (doors ~8 studs tall, windows ~4 studs)
2. Add details: windows, doors, decorations
3. Use appropriate materials (Wood for doors, Glass for windows, Brick for walls)
4. Layer parts for depth and detail
5. WedgePart rotation: [0, -90, 0] for left slope, [0, 90, 0] for right slope

EXAMPLE - Simple House:
{
  "name": "House",
  "description": "A simple house",
  "total_size": [20, 15, 20],
  "base_position": [0, 0, 0],
  "parts": [
    {"name": "floor", "type": "Part", "size": [20, 1, 20], "position": [0, 0.5, 0], "color": "Reddish brown", "material": "Wood"},
    {"name": "wall_front", "type": "Part", "size": [20, 10, 1], "position": [0, 6, 9.5], "color": "Brick yellow", "material": "Brick"},
    {"name": "roof", "type": "WedgePart", "size": [20, 5, 10], "position": [0, 13.5, 0], "color": "Dark orange", "material": "Slate"}
  ]
}

OUTPUT ONLY THE JSON. NO MARKDOWN. NO EXPLANATIONS."""


def validate_blueprint(data: Dict) -> tuple[bool, List[str]]:
    """
    Validate a blueprint JSON structure.
    Returns (is_valid, list_of_issues).
    """
    issues = []

    if not isinstance(data, dict):
        return False, ["Blueprint must be a JSON object"]

    # Required fields
    if "name" not in data:
        issues.append("Missing 'name' field")

    if "parts" not in data:
        issues.append("Missing 'parts' field")
    elif not isinstance(data["parts"], list):
        issues.append("'parts' must be an array")
    elif len(data["parts"]) == 0:
        issues.append("'parts' array is empty")
    else:
        # Validate each part
        for i, part in enumerate(data["parts"]):
            if not isinstance(part, dict):
                issues.append(f"Part {i} is not an object")
                continue

            if "name" not in part:
                issues.append(f"Part {i} missing 'name'")

            if "size" not in part:
                issues.append(f"Part {i} missing 'size'")
            elif not isinstance(part["size"], list) or len(part["size"]) != 3:
                issues.append(f"Part {i} 'size' must be [x, y, z]")

            if "position" not in part:
                issues.append(f"Part {i} missing 'position'")
            elif not isinstance(part["position"], list) or len(part["position"]) != 3:
                issues.append(f"Part {i} 'position' must be [x, y, z]")

    return len(issues) == 0, issues


def parse_blueprint_from_llm_response(response: str) -> Optional[BlueprintSpec]:
    """
    Parse LLM response and extract blueprint JSON.
    Handles markdown code blocks and raw JSON.
    """
    import re

    response = response.strip()

    # Try to extract JSON from markdown code block
    patterns = [
        r'```json\s*\n(.*?)```',
        r'```\s*\n(.*?)```',
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            response = match.group(1).strip()
            break

    # Try to find JSON object
    if not response.startswith("{"):
        start = response.find("{")
        if start != -1:
            # Find matching closing brace
            depth = 0
            end = start
            for i, char in enumerate(response[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            response = response[start:end]

    try:
        data = json.loads(response)
        is_valid, issues = validate_blueprint(data)

        if not is_valid:
            print(f"Blueprint validation failed: {issues}")
            return None

        return BlueprintSpec.from_dict(data)

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return None


# Quick test
if __name__ == "__main__":
    print("Testing Blueprint Schema")
    print("=" * 50)

    # Test preset lookup
    test_commands = [
        "בנה בית",
        "צור עץ ירוק",
        "בנה מכונית אדומה",
        "צור מגדל",
    ]

    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        blueprint = get_blueprint_for_command(cmd)
        if blueprint:
            print(f"  Found preset: {blueprint.name}")
            print(f"  Parts: {len(blueprint.parts)}")
        else:
            print("  No preset found - needs LLM")

    # Test JSON validation
    print("\n" + "=" * 50)
    print("Testing JSON validation")

    test_json = {
        "name": "Test House",
        "description": "A test",
        "parts": [
            {"name": "floor", "size": [10, 1, 10], "position": [0, 0.5, 0], "color": "Brown"}
        ]
    }

    is_valid, issues = validate_blueprint(test_json)
    print(f"Valid: {is_valid}, Issues: {issues}")
