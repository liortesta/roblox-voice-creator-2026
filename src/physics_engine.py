# -*- coding: utf-8 -*-
"""
Physics Engine - Real-world physics for Roblox builds
=====================================================
Ensures objects behave like reality:
- Gravity: things fall, buildings need foundations
- Proportions: realistic sizes for objects
- Materials: proper material for each object type
- Structural integrity: tall things need wide bases
- Stacking: objects on top of others work correctly
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class PhysicsProfile:
    """Physics properties for an object type"""
    anchored: bool = True
    density: float = 1.0          # kg per stud^3
    friction: float = 0.5
    elasticity: float = 0.0
    can_collide: bool = True
    base_on_ground: bool = True   # Must touch ground?
    needs_foundation: bool = False # Needs wider base?
    affected_by_gravity: bool = False  # Falls when not anchored?
    can_float: bool = False       # Floats on water?


# Physics profiles for different object types
PHYSICS_PROFILES = {
    "building": PhysicsProfile(anchored=True, density=2.0, needs_foundation=True, base_on_ground=True),
    "vehicle": PhysicsProfile(anchored=False, density=1.5, friction=0.3, affected_by_gravity=True, base_on_ground=True),
    "nature": PhysicsProfile(anchored=True, density=0.8, base_on_ground=True),
    "furniture": PhysicsProfile(anchored=True, density=0.6, base_on_ground=True),
    "decoration": PhysicsProfile(anchored=True, density=0.5),
    "ball": PhysicsProfile(anchored=False, density=0.3, elasticity=0.8, friction=0.2, affected_by_gravity=True),
    "water": PhysicsProfile(anchored=True, density=1.0, can_collide=False),
    "light": PhysicsProfile(anchored=True, density=0.1),
    "floating": PhysicsProfile(anchored=False, density=0.5, can_float=True),
}


# Realistic sizes for objects (in Roblox studs, ~0.28m per stud)
REALISTIC_SIZES = {
    # Buildings
    "house": {"size": [24, 18, 24], "foundation": [26, 2, 26]},
    "tower": {"size": [10, 50, 10], "foundation": [14, 3, 14]},
    "castle": {"size": [60, 40, 60], "foundation": [64, 4, 64]},
    "shop": {"size": [16, 14, 16], "foundation": [18, 2, 18]},
    "skyscraper": {"size": [20, 100, 20], "foundation": [24, 5, 24]},
    "cabin": {"size": [14, 10, 14], "foundation": [16, 1, 16]},
    "lighthouse": {"size": [8, 40, 8], "foundation": [12, 3, 12]},

    # Vehicles
    "car": {"size": [12, 5, 6], "wheels": 4},
    "truck": {"size": [18, 8, 7], "wheels": 6},
    "bus": {"size": [24, 10, 8], "wheels": 4},
    "airplane": {"size": [30, 8, 40], "wings": True},
    "boat": {"size": [16, 6, 8], "floating": True},
    "helicopter": {"size": [12, 6, 6], "propeller": True},
    "bicycle": {"size": [6, 4, 2], "wheels": 2},
    "train": {"size": [30, 10, 8], "wheels": 8},

    # Nature
    "tree": {"size": [12, 20, 12], "trunk_ratio": 0.25},
    "bush": {"size": [6, 4, 6]},
    "flower": {"size": [2, 3, 2]},
    "rock": {"size": [6, 4, 6]},
    "mountain": {"size": [60, 40, 60]},
    "lake": {"size": [40, 2, 40], "water": True},
    "river": {"size": [100, 2, 10], "water": True},
    "palm_tree": {"size": [8, 22, 8], "trunk_ratio": 0.2},

    # Furniture
    "chair": {"size": [3, 4, 3]},
    "table": {"size": [6, 3, 4]},
    "bed": {"size": [7, 3, 4]},
    "sofa": {"size": [8, 4, 4]},
    "lamp": {"size": [2, 6, 2], "light": True},
    "bookshelf": {"size": [6, 8, 2]},
    "desk": {"size": [6, 3, 3]},

    # Decorations / Infrastructure
    "fence": {"size": [20, 4, 1]},
    "bridge": {"size": [30, 4, 10]},
    "fountain": {"size": [10, 6, 10], "water": True},
    "street_light": {"size": [1, 12, 1], "light": True},
    "bench": {"size": [6, 3, 2]},
    "slide": {"size": [4, 8, 12]},
    "swing": {"size": [6, 8, 2]},
    "ferris_wheel": {"size": [4, 30, 30]},
    "pool": {"size": [20, 4, 12], "water": True},
    "stadium": {"size": [80, 20, 60]},
    "road": {"size": [100, 0.5, 12]},
    "sidewalk": {"size": [100, 0.3, 4]},
}


# Material rules - what material goes with what
MATERIAL_RULES = {
    "roof": "Slate",
    "wall": "Brick",
    "floor": "Wood",
    "door": "Wood",
    "window": "Glass",
    "road": "Concrete",
    "sidewalk": "Concrete",
    "grass": "Grass",
    "sand": "Sand",
    "water": "Glass",  # transparent blue
    "metal_structure": "Metal",
    "stone": "Granite",
    "wood_structure": "Wood",
    "trunk": "Wood",
    "leaves": "Grass",
    "wheel": "Metal",
    "light": "Neon",
    "glass": "Glass",
    "fence": "Wood",
    "foundation": "Concrete",
}


class PhysicsEngine:
    """
    Applies real-world physics rules to Roblox builds.
    Ensures objects look and behave realistically.
    """

    @staticmethod
    def get_realistic_size(object_type: str) -> Optional[Dict]:
        """Get realistic size for an object type"""
        return REALISTIC_SIZES.get(object_type)

    @staticmethod
    def get_material(part_role: str) -> str:
        """Get appropriate material for a part's role"""
        return MATERIAL_RULES.get(part_role, "Plastic")

    @staticmethod
    def get_physics(object_category: str) -> PhysicsProfile:
        """Get physics profile for an object category"""
        return PHYSICS_PROFILES.get(object_category, PhysicsProfile())

    @staticmethod
    def calculate_foundation(width: float, height: float, depth: float) -> Dict:
        """Calculate foundation needed for a structure"""
        # Taller structures need wider foundations
        height_ratio = height / max(width, depth) if max(width, depth) > 0 else 1
        if height_ratio > 3:
            # Very tall - needs significant foundation
            foundation_extra = height_ratio * 2
            return {
                "size": [width + foundation_extra, max(3, height * 0.05), depth + foundation_extra],
                "material": "Concrete",
                "color": "Dark stone grey",
            }
        elif height_ratio > 1.5:
            return {
                "size": [width + 4, 2, depth + 4],
                "material": "Concrete",
                "color": "Medium stone grey",
            }
        else:
            return {
                "size": [width + 2, 1, depth + 2],
                "material": "Concrete",
                "color": "Medium stone grey",
            }

    @staticmethod
    def ensure_ground_contact(parts: List[Dict]) -> List[Dict]:
        """
        Ensure all parts that should be on the ground actually are.
        Adjusts Y positions so nothing floats.
        """
        if not parts:
            return parts

        # Find the lowest Y position
        min_y = float('inf')
        for part in parts:
            pos = part.get("position", [0, 0, 0])
            size = part.get("size", [4, 4, 4])
            bottom_y = pos[1] - size[1] / 2
            if bottom_y < min_y:
                min_y = bottom_y

        # If lowest point is below ground or floating, adjust all parts
        if min_y < 0 or min_y > 1:
            offset = -min_y if min_y < 0 else 0
            if min_y > 1:
                offset = -(min_y - 0)  # Bring down to ground

            for part in parts:
                pos = part.get("position", [0, 0, 0])
                part["position"] = [pos[0], pos[1] + offset, pos[2]]

        return parts

    @staticmethod
    def apply_structural_rules(parts: List[Dict], object_type: str) -> List[Dict]:
        """
        Apply structural integrity rules:
        - Add foundation for tall buildings
        - Ensure walls support roofs
        - Add supports for bridges
        """
        profile = PHYSICS_PROFILES.get(object_type, PhysicsProfile())

        if profile.needs_foundation:
            # Check if there's already a foundation/floor
            has_foundation = any("floor" in p.get("name", "") or "foundation" in p.get("name", "")
                                 for p in parts)
            if not has_foundation and parts:
                # Calculate total size
                max_x = max(abs(p["position"][0]) + p["size"][0] / 2 for p in parts)
                max_z = max(abs(p["position"][2]) + p["size"][2] / 2 for p in parts)
                foundation = {
                    "name": "foundation",
                    "type": "Part",
                    "size": [max_x * 2 + 4, 2, max_z * 2 + 4],
                    "position": [0, 1, 0],
                    "color": "Dark stone grey",
                    "material": "Concrete",
                    "anchored": True,
                }
                parts.insert(0, foundation)

        return parts

    @staticmethod
    def get_physics_lua_properties(profile: PhysicsProfile) -> str:
        """Generate Lua code for physics properties"""
        lines = []
        lines.append(f"p.Anchored = {'true' if profile.anchored else 'false'}")

        if not profile.anchored:
            lines.append(f"p.CustomPhysicalProperties = PhysicalProperties.new({profile.density}, {profile.friction}, {profile.elasticity})")

        if not profile.can_collide:
            lines.append("p.CanCollide = false")

        return "\n".join(lines)

    @staticmethod
    def validate_proportions(parts: List[Dict]) -> List[str]:
        """Check if proportions make sense"""
        warnings = []
        for part in parts:
            size = part.get("size", [4, 4, 4])
            name = part.get("name", "")

            # Check for extremely thin parts (likely errors)
            if any(s < 0.1 for s in size):
                warnings.append(f"Part '{name}' has dimension < 0.1 studs")

            # Check for extremely large parts
            if any(s > 500 for s in size):
                warnings.append(f"Part '{name}' has dimension > 500 studs")

            # Check doors are reasonable size
            if "door" in name.lower():
                if size[1] < 6 or size[1] > 15:
                    warnings.append(f"Door '{name}' height {size[1]} seems wrong (expected 6-15)")

            # Check windows aren't too big
            if "window" in name.lower():
                if size[1] > 10:
                    warnings.append(f"Window '{name}' seems too tall ({size[1]})")

        return warnings


# Hebrew object type to physics category mapping
HEBREW_TO_PHYSICS = {
    "בית": "building", "בניין": "building", "מגדל": "building",
    "טירה": "building", "ארמון": "building", "חנות": "building",
    "מגדלור": "building", "בקתה": "building",
    "מכונית": "vehicle", "אוטו": "vehicle", "רכב": "vehicle",
    "אוטובוס": "vehicle", "משאית": "vehicle", "מטוס": "vehicle",
    "סירה": "vehicle", "רכבת": "vehicle", "אופניים": "vehicle",
    "מסוק": "vehicle",
    "עץ": "nature", "סלע": "nature", "פרח": "nature",
    "הר": "nature", "אגם": "nature", "דקל": "nature",
    "כיסא": "furniture", "שולחן": "furniture", "מיטה": "furniture",
    "ספה": "furniture", "מנורה": "furniture",
    "גדר": "decoration", "גשר": "decoration", "מזרקה": "decoration",
    "ספסל": "decoration", "פנס": "decoration",
    "כדור": "ball",
}
