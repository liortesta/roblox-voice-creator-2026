"""
World State Tracker - מעקב אחר עולם המשחק
==========================================
מודול שזוכר את כל האובייקטים שנוצרו, מיקומם,
ומאפשר פקודות יחסיות כמו "שים עץ ליד הבית".
"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import math


class ObjectType(Enum):
    """סוגי אובייקטים בעולם."""
    BUILDING = "building"      # בית, חנות, מגדל
    VEHICLE = "vehicle"        # מכונית, אופניים
    NATURE = "nature"          # עץ, סלע, פרח
    FURNITURE = "furniture"    # כיסא, שולחן
    DECORATION = "decoration"  # פנס, גדר, ספסל
    CHARACTER = "character"    # דמות, NPC
    INTERACTIVE = "interactive"  # דלת, כפתור, מטבע
    TERRAIN = "terrain"        # הר, אגם, דשא
    ROAD = "road"              # כביש, מדרכה
    CUSTOM = "custom"          # אחר


@dataclass
class WorldObject:
    """אובייקט בעולם המשחק."""
    id: str                           # מזהה ייחודי
    name: str                         # שם בעברית (למשל: "הבית הכחול")
    object_type: ObjectType           # סוג האובייקט
    position: Tuple[float, float, float]  # מיקום (x, y, z)
    size: Tuple[float, float, float]      # גודל (width, height, depth)
    color: Optional[str] = None       # צבע
    properties: Dict[str, Any] = field(default_factory=dict)  # מאפיינים נוספים
    children: List[str] = field(default_factory=list)  # אובייקטים ילדים (למודלים מורכבים)
    created_at: float = field(default_factory=time.time)
    lua_variable: Optional[str] = None  # שם המשתנה ב-Lua (אם יש)

    def get_bounds(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """מחזיר את גבולות האובייקט (min, max)."""
        half_size = (self.size[0]/2, self.size[1]/2, self.size[2]/2)
        min_pos = (
            self.position[0] - half_size[0],
            self.position[1] - half_size[1],
            self.position[2] - half_size[2]
        )
        max_pos = (
            self.position[0] + half_size[0],
            self.position[1] + half_size[1],
            self.position[2] + half_size[2]
        )
        return (min_pos, max_pos)

    def distance_to(self, other: 'WorldObject') -> float:
        """מרחק לאובייקט אחר."""
        return math.sqrt(
            (self.position[0] - other.position[0])**2 +
            (self.position[1] - other.position[1])**2 +
            (self.position[2] - other.position[2])**2
        )

    def to_dict(self) -> dict:
        """המרה למילון."""
        d = asdict(self)
        d['object_type'] = self.object_type.value
        return d

    @staticmethod
    def from_dict(d: dict) -> 'WorldObject':
        """יצירה ממילון."""
        d['object_type'] = ObjectType(d['object_type'])
        d['position'] = tuple(d['position'])
        d['size'] = tuple(d['size'])
        return WorldObject(**d)


class SpatialRelation(Enum):
    """יחסים מרחביים."""
    NEXT_TO = "next_to"       # ליד
    ABOVE = "above"           # מעל
    BELOW = "below"           # מתחת
    IN_FRONT = "in_front"     # מול / לפני
    BEHIND = "behind"         # מאחורי
    LEFT = "left"             # משמאל
    RIGHT = "right"           # מימין
    INSIDE = "inside"         # בתוך
    AROUND = "around"         # מסביב
    ON = "on"                 # על (משטח)
    NEAR = "near"             # קרוב


class WorldState:
    """
    מנהל מצב העולם - זוכר את כל האובייקטים ומיקומם.
    """

    # מיפוי מילים עבריות ליחסים מרחביים
    SPATIAL_WORDS = {
        # ליד
        "ליד": SpatialRelation.NEXT_TO,
        "לצד": SpatialRelation.NEXT_TO,
        "סמוך": SpatialRelation.NEXT_TO,
        "קרוב": SpatialRelation.NEAR,
        # מעל/מתחת
        "מעל": SpatialRelation.ABOVE,
        "על": SpatialRelation.ON,
        "מתחת": SpatialRelation.BELOW,
        "תחת": SpatialRelation.BELOW,
        # לפני/אחרי
        "לפני": SpatialRelation.IN_FRONT,
        "מול": SpatialRelation.IN_FRONT,
        "מאחורי": SpatialRelation.BEHIND,
        "אחרי": SpatialRelation.BEHIND,
        # שמאל/ימין
        "משמאל": SpatialRelation.LEFT,
        "שמאל": SpatialRelation.LEFT,
        "מימין": SpatialRelation.RIGHT,
        "ימין": SpatialRelation.RIGHT,
        # אחר
        "בתוך": SpatialRelation.INSIDE,
        "מסביב": SpatialRelation.AROUND,
        "סביב": SpatialRelation.AROUND,
    }

    # מיפוי מילים לסוגי אובייקטים
    OBJECT_TYPE_WORDS = {
        # בניינים
        "בית": ObjectType.BUILDING,
        "בניין": ObjectType.BUILDING,
        "חנות": ObjectType.BUILDING,
        "מגדל": ObjectType.BUILDING,
        "טירה": ObjectType.BUILDING,
        "ארמון": ObjectType.BUILDING,
        # רכבים
        "מכונית": ObjectType.VEHICLE,
        "אוטו": ObjectType.VEHICLE,
        "רכב": ObjectType.VEHICLE,
        "אופניים": ObjectType.VEHICLE,
        "מטוס": ObjectType.VEHICLE,
        "ספינה": ObjectType.VEHICLE,
        # טבע
        "עץ": ObjectType.NATURE,
        "סלע": ObjectType.NATURE,
        "אבן": ObjectType.NATURE,
        "פרח": ObjectType.NATURE,
        "שיח": ObjectType.NATURE,
        # ריהוט
        "כיסא": ObjectType.FURNITURE,
        "שולחן": ObjectType.FURNITURE,
        "ספה": ObjectType.FURNITURE,
        "מיטה": ObjectType.FURNITURE,
        # קישוט
        "פנס": ObjectType.DECORATION,
        "גדר": ObjectType.DECORATION,
        "ספסל": ObjectType.DECORATION,
        "מנורה": ObjectType.DECORATION,
        "פסל": ObjectType.DECORATION,
        # טרריין
        "הר": ObjectType.TERRAIN,
        "אגם": ObjectType.TERRAIN,
        "נהר": ObjectType.TERRAIN,
        "גבעה": ObjectType.TERRAIN,
        # כבישים
        "כביש": ObjectType.ROAD,
        "מדרכה": ObjectType.ROAD,
        "רחוב": ObjectType.ROAD,
    }

    def __init__(self, on_status=None):
        """אתחול."""
        self.objects: Dict[str, WorldObject] = {}  # מזהה -> אובייקט
        self.object_counter = 0
        self.on_status = on_status or (lambda x: print(f"[WorldState] {x}"))
        self._last_created_id: Optional[str] = None
        self._named_objects: Dict[str, str] = {}  # כינוי -> מזהה

    def generate_id(self) -> str:
        """יצירת מזהה ייחודי."""
        self.object_counter += 1
        return f"obj_{self.object_counter}_{int(time.time())}"

    def add_object(self, obj: WorldObject) -> str:
        """
        הוספת אובייקט לעולם.

        Returns:
            מזהה האובייקט
        """
        if not obj.id:
            obj.id = self.generate_id()

        self.objects[obj.id] = obj
        self._last_created_id = obj.id

        # הוסף לאינדקס שמות
        name_key = obj.name.lower().strip()
        self._named_objects[name_key] = obj.id

        self.on_status(f"נוסף: {obj.name} במיקום {obj.position}")
        return obj.id

    def remove_object(self, obj_id: str) -> bool:
        """הסרת אובייקט."""
        if obj_id in self.objects:
            obj = self.objects[obj_id]
            # הסר מאינדקס שמות
            name_key = obj.name.lower().strip()
            if name_key in self._named_objects:
                del self._named_objects[name_key]
            del self.objects[obj_id]
            self.on_status(f"הוסר: {obj.name}")
            return True
        return False

    def get_object(self, obj_id: str) -> Optional[WorldObject]:
        """קבלת אובייקט לפי מזהה."""
        return self.objects.get(obj_id)

    def get_last_created(self) -> Optional[WorldObject]:
        """קבלת האובייקט האחרון שנוצר."""
        if self._last_created_id:
            return self.objects.get(self._last_created_id)
        return None

    def find_by_name(self, name: str) -> Optional[WorldObject]:
        """
        חיפוש אובייקט לפי שם (חלקי).

        Args:
            name: שם או חלק משם (למשל: "הבית", "עץ")
        """
        name_lower = name.lower().strip()

        # חיפוש מדויק
        if name_lower in self._named_objects:
            return self.objects.get(self._named_objects[name_lower])

        # חיפוש חלקי
        for obj in self.objects.values():
            if name_lower in obj.name.lower():
                return obj

        return None

    def find_by_type(self, obj_type: ObjectType) -> List[WorldObject]:
        """חיפוש כל האובייקטים מסוג מסוים."""
        return [obj for obj in self.objects.values() if obj.object_type == obj_type]

    def find_nearest(self, position: Tuple[float, float, float],
                     obj_type: Optional[ObjectType] = None) -> Optional[WorldObject]:
        """מציאת האובייקט הקרוב ביותר למיקום."""
        min_dist = float('inf')
        nearest = None

        for obj in self.objects.values():
            if obj_type and obj.object_type != obj_type:
                continue

            dist = math.sqrt(
                (obj.position[0] - position[0])**2 +
                (obj.position[1] - position[1])**2 +
                (obj.position[2] - position[2])**2
            )

            if dist < min_dist:
                min_dist = dist
                nearest = obj

        return nearest

    def calculate_relative_position(self, reference: WorldObject,
                                    relation: SpatialRelation,
                                    offset: float = 5.0) -> Tuple[float, float, float]:
        """
        חישוב מיקום יחסי לאובייקט אחר.

        Args:
            reference: אובייקט ההתייחסות
            relation: היחס המרחבי
            offset: מרחק מהאובייקט

        Returns:
            מיקום (x, y, z) יחסי
        """
        x, y, z = reference.position
        ref_size = reference.size

        if relation == SpatialRelation.NEXT_TO:
            # ליד - בצד אקראי
            return (x + ref_size[0]/2 + offset, y, z)

        elif relation == SpatialRelation.LEFT:
            return (x - ref_size[0]/2 - offset, y, z)

        elif relation == SpatialRelation.RIGHT:
            return (x + ref_size[0]/2 + offset, y, z)

        elif relation == SpatialRelation.ABOVE:
            return (x, y + ref_size[1]/2 + offset, z)

        elif relation == SpatialRelation.ON:
            return (x, y + ref_size[1]/2 + 1, z)  # קצת מעל

        elif relation == SpatialRelation.BELOW:
            return (x, y - ref_size[1]/2 - offset, z)

        elif relation == SpatialRelation.IN_FRONT:
            return (x, y, z - ref_size[2]/2 - offset)

        elif relation == SpatialRelation.BEHIND:
            return (x, y, z + ref_size[2]/2 + offset)

        elif relation == SpatialRelation.NEAR:
            return (x + offset, y, z + offset)

        elif relation == SpatialRelation.AROUND:
            # מסביב - מחזיר רשימה של מיקומים
            return (x + offset, y, z)  # נחזיר אחד, לוגיקה מיוחדת לזה

        elif relation == SpatialRelation.INSIDE:
            return (x, y, z)  # באותו מיקום

        return (x + offset, y, z)  # ברירת מחדל

    def calculate_around_positions(self, reference: WorldObject,
                                   count: int = 4,
                                   radius: float = 10.0) -> List[Tuple[float, float, float]]:
        """
        חישוב מיקומים מסביב לאובייקט.

        Args:
            reference: אובייקט ההתייחסות
            count: כמה מיקומים
            radius: רדיוס

        Returns:
            רשימת מיקומים
        """
        positions = []
        x, y, z = reference.position

        for i in range(count):
            angle = (2 * math.pi * i) / count
            new_x = x + radius * math.cos(angle)
            new_z = z + radius * math.sin(angle)
            positions.append((new_x, y, new_z))

        return positions

    def parse_spatial_reference(self, text: str) -> Optional[Tuple[SpatialRelation, WorldObject]]:
        """
        ניתוח התייחסות מרחבית מטקסט.

        Args:
            text: הטקסט (למשל: "ליד הבית", "מאחורי העץ")

        Returns:
            (יחס מרחבי, אובייקט התייחסות) או None
        """
        text_lower = text.lower()

        # מצא יחס מרחבי
        found_relation = None
        for word, relation in self.SPATIAL_WORDS.items():
            if word in text_lower:
                found_relation = relation
                break

        if not found_relation:
            return None

        # מצא אובייקט התייחסות
        found_object = None

        # נסה למצוא שם ספציפי
        for obj in self.objects.values():
            if obj.name.lower() in text_lower:
                found_object = obj
                break

        # אם לא מצאנו, נסה לפי סוג
        if not found_object:
            for word, obj_type in self.OBJECT_TYPE_WORDS.items():
                if word in text_lower:
                    objects_of_type = self.find_by_type(obj_type)
                    if objects_of_type:
                        # קח את האחרון שנוצר מהסוג הזה
                        found_object = max(objects_of_type, key=lambda x: x.created_at)
                        break

        # אם עדיין לא מצאנו, נסה "זה" / "האחרון"
        if not found_object and any(w in text_lower for w in ["זה", "אותו", "האחרון"]):
            found_object = self.get_last_created()

        if found_object:
            return (found_relation, found_object)

        return None

    def get_context_for_llm(self) -> str:
        """
        יצירת תיאור העולם עבור Claude.

        Returns:
            טקסט המתאר את העולם הנוכחי
        """
        if not self.objects:
            return "העולם ריק כרגע."

        lines = ["== מצב העולם הנוכחי =="]

        # קבץ לפי סוגים
        by_type: Dict[ObjectType, List[WorldObject]] = {}
        for obj in self.objects.values():
            if obj.object_type not in by_type:
                by_type[obj.object_type] = []
            by_type[obj.object_type].append(obj)

        for obj_type, objects in by_type.items():
            type_name = {
                ObjectType.BUILDING: "בניינים",
                ObjectType.VEHICLE: "רכבים",
                ObjectType.NATURE: "טבע",
                ObjectType.FURNITURE: "ריהוט",
                ObjectType.DECORATION: "קישוטים",
                ObjectType.TERRAIN: "שטח",
                ObjectType.ROAD: "כבישים",
                ObjectType.CHARACTER: "דמויות",
                ObjectType.INTERACTIVE: "אינטראקטיבי",
                ObjectType.CUSTOM: "אחר",
            }.get(obj_type, "אחר")

            lines.append(f"\n{type_name}:")
            for obj in objects:
                pos_str = f"({obj.position[0]:.0f}, {obj.position[1]:.0f}, {obj.position[2]:.0f})"
                lines.append(f"  - {obj.name} במיקום {pos_str}")

        # הוסף את האובייקט האחרון
        last = self.get_last_created()
        if last:
            lines.append(f"\nהאובייקט האחרון שנוצר: {last.name}")

        return "\n".join(lines)

    def clear(self):
        """ניקוי העולם."""
        self.objects.clear()
        self._named_objects.clear()
        self._last_created_id = None
        self.on_status("העולם נוקה")

    def save_to_file(self, filepath: str):
        """שמירה לקובץ."""
        data = {
            "objects": {k: v.to_dict() for k, v in self.objects.items()},
            "counter": self.object_counter,
            "named_objects": self._named_objects,
            "last_created_id": self._last_created_id,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.on_status(f"נשמר ל-{filepath}")

    def load_from_file(self, filepath: str):
        """טעינה מקובץ."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.objects = {k: WorldObject.from_dict(v) for k, v in data["objects"].items()}
        self.object_counter = data["counter"]
        self._named_objects = data["named_objects"]
        self._last_created_id = data["last_created_id"]
        self.on_status(f"נטען מ-{filepath}: {len(self.objects)} אובייקטים")


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת World State Tracker")
    print("=" * 40)

    world = WorldState()

    # הוסף אובייקטים
    house = WorldObject(
        id="",
        name="הבית הכחול",
        object_type=ObjectType.BUILDING,
        position=(0, 5, 0),
        size=(20, 10, 20),
        color="Bright blue"
    )
    world.add_object(house)

    tree = WorldObject(
        id="",
        name="עץ גדול",
        object_type=ObjectType.NATURE,
        position=(15, 4, 0),
        size=(4, 8, 4),
        color="Bright green"
    )
    world.add_object(tree)

    # בדיקות
    print("\n1. חיפוש לפי שם:")
    found = world.find_by_name("בית")
    print(f"   נמצא: {found.name if found else 'לא נמצא'}")

    print("\n2. חיפוש לפי סוג:")
    buildings = world.find_by_type(ObjectType.BUILDING)
    print(f"   בניינים: {[b.name for b in buildings]}")

    print("\n3. ניתוח יחס מרחבי:")
    result = world.parse_spatial_reference("ליד הבית")
    if result:
        relation, ref_obj = result
        print(f"   יחס: {relation.value}, אובייקט: {ref_obj.name}")
        pos = world.calculate_relative_position(ref_obj, relation)
        print(f"   מיקום מחושב: {pos}")

    print("\n4. קונטקסט ל-LLM:")
    print(world.get_context_for_llm())
