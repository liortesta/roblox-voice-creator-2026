"""
Smart Agent System - מערכת סוכנים חכמה
========================================
סוכן ראשי שמבין פקודות מורכבות ומתאם בין כל המודולים:
- הבנת שפה טבעית בעברית
- מעקב אחר מצב העולם
- יצירת סקריפטים אינטראקטיביים
- תבניות משחק מוכנות
- הבנה מרחבית
"""

import os
import re
import anthropic
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum, auto

from world_state import WorldState, WorldObject, ObjectType, SpatialRelation
from script_generator import ScriptGenerator, InteractionType
from game_templates import GameTemplates, GameType


class CommandIntent(Enum):
    """כוונות אפשריות של פקודה."""
    CREATE_OBJECT = auto()       # יצירת אובייקט (בית, עץ)
    CREATE_GAME = auto()         # יצירת משחק שלם
    CREATE_INTERACTION = auto()  # יצירת אלמנט אינטראקטיבי
    MODIFY_OBJECT = auto()       # עריכת אובייקט קיים
    SPATIAL_COMMAND = auto()     # פקודה מרחבית (שים X ליד Y)
    DELETE = auto()              # מחיקה
    QUERY = auto()               # שאלה על העולם
    UNKNOWN = auto()             # לא ידוע


class SmartAgent:
    """
    סוכן חכם שמבין פקודות מורכבות ומתאם את כל המערכת.

    הסוכן:
    1. מנתח את הפקודה ומבין את הכוונה
    2. מחפש קונטקסט מהעולם (מה קיים, איפה)
    3. מייצר קוד Lua מתאים
    4. מעדכן את מצב העולם
    """

    # מילות מפתח לזיהוי כוונות
    GAME_KEYWORDS = [
        "משחק", "מירוץ", "אובי", "פארקור", "איסוף", "מבוך",
        "מגרש", "אצטדיון", "זירה", "פארק שעשועים"
    ]

    INTERACTION_KEYWORDS = [
        "דלת", "כפתור", "מטבע", "טלפורט", "קפיצה", "נע", "נעה",
        "אינטראקטיבי", "נפתח", "נפתחת", "לאסוף", "ללחוץ"
    ]

    SPATIAL_KEYWORDS = [
        "ליד", "לצד", "מעל", "מתחת", "מאחורי", "לפני",
        "משמאל", "מימין", "מסביב", "על", "בתוך", "קרוב"
    ]

    MODIFY_KEYWORDS = [
        "תשנה", "תעדכן", "תזיז", "הזז", "סובב", "תסובב",
        "צבע", "תצבע", "הגדל", "תגדיל", "הקטן", "תקטין"
    ]

    def __init__(self, on_status=None):
        """
        אתחול הסוכן החכם.
        """
        self.on_status = on_status or (lambda x: print(f"[SmartAgent] {x}"))

        # מודולים
        self.world_state = WorldState(on_status=self.on_status)
        self.script_generator = ScriptGenerator(on_status=self.on_status)
        self.game_templates = GameTemplates(on_status=self.on_status)

        # Claude API
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.on_status("Claude API מוכן")
        else:
            self.on_status("אזהרה: אין Claude API key")

        # היסטוריית שיחה
        self.conversation_history: List[Dict] = []

    # ========================================
    # ניתוח פקודות
    # ========================================

    def analyze_command(self, text: str) -> Tuple[CommandIntent, Dict[str, Any]]:
        """
        ניתוח פקודה והבנת הכוונה.

        Args:
            text: הפקודה בעברית

        Returns:
            (כוונה, מידע נוסף)
        """
        text_lower = text.lower()
        info = {"original_text": text}

        # בדיקת משחק
        for kw in self.GAME_KEYWORDS:
            if kw in text_lower:
                info["game_keyword"] = kw
                return (CommandIntent.CREATE_GAME, info)

        # בדיקת אינטראקציה
        for kw in self.INTERACTION_KEYWORDS:
            if kw in text_lower:
                info["interaction_keyword"] = kw
                return (CommandIntent.CREATE_INTERACTION, info)

        # בדיקת פקודה מרחבית
        for kw in self.SPATIAL_KEYWORDS:
            if kw in text_lower:
                # נסה לזהות את האובייקטים
                spatial_result = self.world_state.parse_spatial_reference(text)
                if spatial_result:
                    info["spatial_relation"] = spatial_result[0]
                    info["reference_object"] = spatial_result[1]
                    return (CommandIntent.SPATIAL_COMMAND, info)

        # בדיקת עריכה
        for kw in self.MODIFY_KEYWORDS:
            if kw in text_lower:
                return (CommandIntent.MODIFY_OBJECT, info)

        # בדיקת מחיקה
        if any(w in text_lower for w in ["מחק", "תמחק", "הסר", "תסיר"]):
            return (CommandIntent.DELETE, info)

        # בדיקת שאלה
        if any(w in text_lower for w in ["מה", "איפה", "איך", "כמה", "האם"]):
            return (CommandIntent.QUERY, info)

        # ברירת מחדל - יצירת אובייקט
        return (CommandIntent.CREATE_OBJECT, info)

    # ========================================
    # עיבוד פקודות
    # ========================================

    def process_command(self, text: str) -> Dict[str, Any]:
        """
        עיבוד פקודה והחזרת קוד Lua.

        Args:
            text: הפקודה בעברית

        Returns:
            dict עם lua_code, success, message
        """
        self.on_status(f"מעבד: {text}")

        # נתח את הפקודה
        intent, info = self.analyze_command(text)
        self.on_status(f"כוונה: {intent.name}")

        # טפל לפי כוונה
        if intent == CommandIntent.CREATE_GAME:
            return self._handle_game_creation(text, info)

        elif intent == CommandIntent.CREATE_INTERACTION:
            return self._handle_interaction_creation(text, info)

        elif intent == CommandIntent.SPATIAL_COMMAND:
            return self._handle_spatial_command(text, info)

        elif intent == CommandIntent.MODIFY_OBJECT:
            return self._handle_modification(text, info)

        elif intent == CommandIntent.DELETE:
            return self._handle_deletion(text, info)

        elif intent == CommandIntent.QUERY:
            return self._handle_query(text, info)

        else:  # CREATE_OBJECT
            return self._handle_object_creation(text, info)

    def _handle_game_creation(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול ביצירת משחק."""
        text_lower = text.lower()

        # זיהוי סוג המשחק
        if any(w in text_lower for w in ["מירוץ", "רייסינג", "מכוניות"]):
            lua_code = self.game_templates.create_racing_game()
            game_name = "משחק מירוץ"

        elif any(w in text_lower for w in ["איסוף", "מטבעות", "אוסף"]):
            lua_code = self.game_templates.create_collection_game()
            game_name = "משחק איסוף"

        elif any(w in text_lower for w in ["אובי", "פארקור", "קפיצות"]):
            difficulty = "medium"
            if "קל" in text_lower:
                difficulty = "easy"
            elif "קשה" in text_lower:
                difficulty = "hard"
            lua_code = self.game_templates.create_obby_game(difficulty=difficulty)
            game_name = "אובי"

        elif any(w in text_lower for w in ["פארק שעשועים", "גן שעשועים", "פארק משחקים"]):
            lua_code = self.game_templates.create_playground()
            game_name = "פארק שעשועים"

        else:
            # ברירת מחדל - שלח ל-Claude
            return self._generate_with_claude(text)

        return {
            "success": True,
            "lua_code": lua_code,
            "message": f"יצרתי {game_name}!",
            "intent": "game"
        }

    def _handle_interaction_creation(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול ביצירת אלמנט אינטראקטיבי."""
        text_lower = text.lower()

        if "דלת" in text_lower:
            direction = "up"
            if "סיבוב" in text_lower or "מסתובב" in text_lower:
                direction = "rotate"
            elif "שמאל" in text_lower:
                direction = "left"
            lua_code = self.script_generator.create_door(open_direction=direction)
            msg = "דלת שנפתחת"

        elif "כפתור" in text_lower or "לחצן" in text_lower:
            action = "print"
            if "פיצוץ" in text_lower or "מתפוצץ" in text_lower:
                action = "explode"
            elif "יוצר" in text_lower or "מייצר" in text_lower:
                action = "spawn"
            lua_code = self.script_generator.create_button(action=action)
            msg = "כפתור"

        elif any(w in text_lower for w in ["מטבע", "כסף", "נקודה", "יהלום", "כוכב"]):
            item_type = "coin"
            if "יהלום" in text_lower:
                item_type = "gem"
            elif "כוכב" in text_lower:
                item_type = "star"
            elif "לב" in text_lower:
                item_type = "heart"
            lua_code = self.script_generator.create_collectible(item_type=item_type)
            msg = f"פריט לאיסוף ({item_type})"

        elif any(w in text_lower for w in ["קפיצה", "קופץ", "טרמפולינה"]):
            power = 100
            if "חזק" in text_lower or "גבוה" in text_lower:
                power = 150
            lua_code = self.script_generator.create_jump_pad(power=power)
            msg = "כרית קפיצה"

        elif any(w in text_lower for w in ["טלפורט", "מעביר", "משגר"]):
            lua_code = self.script_generator.create_teleporter()
            msg = "טלפורטר"

        elif any(w in text_lower for w in ["פלטפורמה נעה", "במה נעה", "משטח נע"]):
            direction = "horizontal"
            if "אנכי" in text_lower or "למעלה" in text_lower:
                direction = "vertical"
            lua_code = self.script_generator.create_moving_platform(direction=direction)
            msg = "פלטפורמה נעה"

        elif "npc" in text_lower or "דמות" in text_lower or "בובה" in text_lower:
            lua_code = self.script_generator.create_npc()
            msg = "NPC"

        else:
            return self._generate_with_claude(text)

        return {
            "success": True,
            "lua_code": lua_code,
            "message": f"יצרתי {msg}!",
            "intent": "interaction"
        }

    def _handle_spatial_command(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול בפקודה מרחבית."""
        relation = info.get("spatial_relation")
        reference = info.get("reference_object")

        if not reference:
            return {
                "success": False,
                "error": "לא מצאתי את האובייקט להתייחסות",
                "hint": "נסה לציין במפורש למשל: 'ליד הבית הכחול'"
            }

        # חשב מיקום יחסי
        position = self.world_state.calculate_relative_position(reference, relation)
        self.on_status(f"מיקום מחושב: {position} ({relation.value} {reference.name})")

        # בנה את הפקודה עם המיקום
        context = f"""
הקשר מרחבי:
- מיקום מחושב: x={position[0]}, y={position[1]}, z={position[2]}
- יחס: {relation.value}
- אובייקט התייחסות: {reference.name} במיקום {reference.position}

העולם הנוכחי:
{self.world_state.get_context_for_llm()}

הפקודה: {text}

צור את האובייקט במיקום המחושב. השתמש בקואורדינטות: Vector3.new({position[0]}, {position[1]}, {position[2]})
"""
        return self._generate_with_claude(context, is_spatial=True)

    def _handle_modification(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול בעריכת אובייקט."""
        # מצא את האובייקט לעריכה
        last = self.world_state.get_last_created()

        if not last:
            return {
                "success": False,
                "error": "אין אובייקט לעריכה",
                "hint": "קודם צור משהו ואז תוכל לערוך אותו"
            }

        context = f"""
עריכת אובייקט קיים:
- שם: {last.name}
- מיקום: {last.position}
- גודל: {last.size}
- צבע: {last.color}

הפקודה: {text}

צור קוד Lua שמשנה את האובייקט הנבחר (game.Selection:Get()[1]).
"""
        return self._generate_with_claude(context, is_modification=True)

    def _handle_deletion(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול במחיקה."""
        lua_code = """
local selected = game.Selection:Get()
for _, obj in ipairs(selected) do
    if obj:IsA("BasePart") or obj:IsA("Model") then
        obj:Destroy()
        print("🗑️ נמחק: " .. obj.Name)
    end
end
print("✅ המחיקה הושלמה")
"""
        return {
            "success": True,
            "lua_code": lua_code,
            "message": "מחקתי את האובייקטים הנבחרים",
            "intent": "delete"
        }

    def _handle_query(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול בשאלה."""
        context = self.world_state.get_context_for_llm()

        return {
            "success": True,
            "lua_code": f'print([[\n{context}\n]])',
            "message": context,
            "intent": "query"
        }

    def _handle_object_creation(self, text: str, info: Dict) -> Dict[str, Any]:
        """טיפול ביצירת אובייקט."""
        return self._generate_with_claude(text)

    # ========================================
    # יצירה עם Claude
    # ========================================

    def _generate_with_claude(self, text: str, is_spatial: bool = False,
                              is_modification: bool = False) -> Dict[str, Any]:
        """
        יצירת קוד Lua עם Claude.
        """
        if not self.client:
            return {
                "success": False,
                "error": "Claude API לא זמין",
                "hint": "הגדר ANTHROPIC_API_KEY"
            }

        # בנה את ההקשר
        world_context = self.world_state.get_context_for_llm()

        system_prompt = f"""אתה סוכן חכם ליצירת משחקי Roblox. אתה מבין עברית ויוצר קוד Lua מקצועי.

## מצב העולם הנוכחי:
{world_context}

## כללים:
1. החזר אך ורק קוד Lua תקין - בלי הסברים!
2. התחל עם: local parts = {{}}
3. סיים עם: game.Selection:Set(parts)
4. השתמש ב-Anchored = true לבניינים
5. הוסף פרטים יפים: חלונות, דלתות, גגות משופעים
6. השתמש ב-Materials: Brick, Wood, Metal, Glass, Neon
7. אם יש התייחסות מרחבית - השתמש במיקום שניתן

## דוגמאות לצורות:
- WedgePart לגגות משופעים
- SpecialMesh לצורות מיוחדות
- Terrain לנוף טבעי

צור קוד עבור:"""

        try:
            self.on_status("שולח ל-Claude...")

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=6000,
                system=system_prompt,
                messages=[{"role": "user", "content": text}]
            )

            lua_code = response.content[0].text.strip()

            # נקה markdown
            if lua_code.startswith("```"):
                lines = lua_code.split("\n")
                lua_code = "\n".join(lines[1:-1])

            # וודא שזה קוד Lua
            if not any(x in lua_code for x in ["local", "Instance", "workspace", "Vector3"]):
                self.on_status("Claude לא החזיר קוד Lua תקין")
                return {
                    "success": False,
                    "error": "התקבלה תשובה שאינה קוד Lua"
                }

            self.on_status(f"התקבל קוד ({len(lua_code)} תווים)")

            # עדכן היסטוריה
            self.conversation_history.append({
                "role": "user",
                "content": text
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": lua_code[:500]
            })

            return {
                "success": True,
                "lua_code": lua_code,
                "message": f"יצרתי: {text}",
                "intent": "create"
            }

        except Exception as e:
            self.on_status(f"שגיאת Claude: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================
    # עדכון מצב העולם
    # ========================================

    def update_world_state(self, name: str, object_type: str,
                          position: Tuple[float, float, float],
                          size: Tuple[float, float, float] = (4, 4, 4),
                          color: str = None) -> str:
        """
        עדכון מצב העולם אחרי יצירה.

        Returns:
            מזהה האובייקט
        """
        # המר סוג
        type_map = {
            "בית": ObjectType.BUILDING,
            "מכונית": ObjectType.VEHICLE,
            "עץ": ObjectType.NATURE,
            "כיסא": ObjectType.FURNITURE,
            "שולחן": ObjectType.FURNITURE,
        }

        obj_type = type_map.get(object_type, ObjectType.CUSTOM)

        obj = WorldObject(
            id="",
            name=name,
            object_type=obj_type,
            position=position,
            size=size,
            color=color
        )

        return self.world_state.add_object(obj)

    # ========================================
    # ממשק ציבורי
    # ========================================

    def execute(self, command: str) -> Dict[str, Any]:
        """
        ביצוע פקודה קולית.

        Args:
            command: הפקודה בעברית

        Returns:
            dict עם lua_code, success, message
        """
        return self.process_command(command)

    def get_world_summary(self) -> str:
        """קבלת סיכום העולם."""
        return self.world_state.get_context_for_llm()

    def clear_world(self):
        """ניקוי העולם."""
        self.world_state.clear()
        self.conversation_history.clear()

    def save_world(self, filepath: str):
        """שמירת העולם."""
        self.world_state.save_to_file(filepath)

    def load_world(self, filepath: str):
        """טעינת עולם."""
        self.world_state.load_from_file(filepath)


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת Smart Agent")
    print("=" * 40)

    agent = SmartAgent()

    # בדיקת ניתוח פקודות
    test_commands = [
        "בנה משחק מירוץ",
        "צור דלת שנפתחת",
        "שים עץ ליד הבית",
        "בנה בית כחול",
        "תגדיל את זה",
        "מה יש בעולם?",
    ]

    for cmd in test_commands:
        intent, info = agent.analyze_command(cmd)
        print(f"\nפקודה: {cmd}")
        print(f"  כוונה: {intent.name}")
