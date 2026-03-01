"""
Direct Roblox Controller - שליטה דרך HTTP Server
=================================================
שולח פקודות Lua דרך HTTP Server ל-Plugin ב-Roblox Studio.

גרסה 2.0 - עם תמיכה בסוכן חכם!
- הבנת פקודות מורכבות
- מעקב מצב העולם
- תבניות משחק מוכנות
- אלמנטים אינטראקטיביים
"""

import requests
import time
import sys
import os
from typing import Dict, Any, Optional

# תיקון קידוד Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def safe_print(text: str):
    """הדפסה בטוחה שמתמודדת עם אימוג'י ב-Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # הסר אימוג'י ותווים בעייתיים
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


# ניסיון לייבא את הסוכן החכם
try:
    from .smart_agent import SmartAgent
    SMART_AGENT_AVAILABLE = True
except ImportError:
    try:
        from smart_agent import SmartAgent
        SMART_AGENT_AVAILABLE = True
    except ImportError:
        SMART_AGENT_AVAILABLE = False
        print("Warning: Smart Agent not available, using basic mode")

try:
    from .llm_builder import LLMBuilder
    from .robust_generator import RobustLuaGenerator
    from .world_state import WorldState, WorldObject, ObjectType
    from .behavior_blueprints import (
        find_behavior_for_command, generate_behavior_lua,
        ALL_BEHAVIORS, list_behaviors_by_category,
    )
    from .game_systems_builder import find_game_system, generate_game_system_lua, GAME_SYSTEMS
    BEHAVIORS_AVAILABLE = True
    GAME_SYSTEMS_AVAILABLE = True
except ImportError:
    from llm_builder import LLMBuilder
    from robust_generator import RobustLuaGenerator
    from world_state import WorldState, WorldObject, ObjectType
    try:
        from behavior_blueprints import (
            find_behavior_for_command, generate_behavior_lua,
            ALL_BEHAVIORS, list_behaviors_by_category,
        )
        BEHAVIORS_AVAILABLE = True
    except ImportError:
        BEHAVIORS_AVAILABLE = False
        find_behavior_for_command = None
        generate_behavior_lua = None
        ALL_BEHAVIORS = {}
        list_behaviors_by_category = None
    try:
        from game_systems_builder import find_game_system, generate_game_system_lua, GAME_SYSTEMS
        GAME_SYSTEMS_AVAILABLE = True
    except ImportError:
        GAME_SYSTEMS_AVAILABLE = False
        find_game_system = None
        generate_game_system_lua = None
        GAME_SYSTEMS = {}


def normalize_hebrew_text(text: str) -> str:
    """
    נרמול טקסט עברי - תיקון שגיאות נפוצות מזיהוי קולי.
    """
    # תיקונים נפוצים מזיהוי קולי
    corrections = {
        # שגיאות נפוצות בזיהוי
        "בני": "בנה",  # לפעמים Whisper שומע "בני" במקום "בנה"
        "תיצור": "צור",
        "תבנה": "בנה",
        "תשים": "שים",
        # צבעים
        "כחולא": "כחול",
        "אדומא": "אדום",
        "ירוקא": "ירוק",
        # אובייקטים
        "בייט": "בית",
        "וויט": "בית",
        "עיץ": "עץ",
        "קוביא": "קוביה",
    }

    result = text
    for wrong, correct in corrections.items():
        result = result.replace(wrong, correct)

    return result


class DirectRobloxController:
    """
    שליטה ישירה ב-Roblox Studio דרך HTTP Server.

    איך זה עובד:
    1. Python מריץ HTTP Server על localhost:8080
    2. ה-Plugin ב-Roblox שואל כל חצי שנייה אם יש פקודה
    3. כשיש פקודה - מריץ אותה!

    דוגמה:
        controller = DirectRobloxController()
        controller.execute_voice_command("תוסיף קוביה כחולה")
    """

    SERVER_URL = "http://127.0.0.1:8080"

    # מיפוי צבעים עברית -> Roblox (עם וריאציות)
    COLORS = {
        # אדום
        "אדום": "Bright red",
        "אדומה": "Bright red",
        "אדומים": "Bright red",
        # כחול
        "כחול": "Bright blue",
        "כחולה": "Bright blue",
        "כחולים": "Bright blue",
        # ירוק
        "ירוק": "Bright green",
        "ירוקה": "Bright green",
        "ירוקים": "Bright green",
        # צהוב
        "צהוב": "Bright yellow",
        "צהובה": "Bright yellow",
        "צהובים": "Bright yellow",
        # כתום
        "כתום": "Neon orange",
        "כתומה": "Neon orange",
        "כתומים": "Neon orange",
        "תפוז": "Neon orange",
        # סגול
        "סגול": "Bright violet",
        "סגולה": "Bright violet",
        "סגולים": "Bright violet",
        # ורוד
        "ורוד": "Hot pink",
        "ורודה": "Hot pink",
        "ורודים": "Hot pink",
        "ורוד": "Hot pink",
        # לבן
        "לבן": "White",
        "לבנה": "White",
        "לבנים": "White",
        # שחור
        "שחור": "Black",
        "שחורה": "Black",
        "שחורים": "Black",
        # חום
        "חום": "Brown",
        "חומה": "Brown",
        "חומים": "Brown",
        # תכלת
        "תכלת": "Cyan",
        "תכולה": "Cyan",
        # זהב
        "זהב": "Gold",
        "זהובה": "Gold",
        "מוזהב": "Gold",
        # אפור
        "אפור": "Medium stone grey",
        "אפורה": "Medium stone grey",
    }

    # מיפוי צורות (עם וריאציות)
    SHAPES = {
        "קוביה": "cube",
        "קובייה": "cube",
        "ריבוע": "cube",
        "כדור": "ball",
        "עיגול": "ball",
        "גליל": "cylinder",
        "צינור": "cylinder",
    }

    # מודלים מוכנים מ-Toolbox (Asset IDs) - עם הרבה וריאציות!
    READY_MODELS = {
        # עצים
        "עץ": 4631364747,
        "עצים": 4631364747,
        "אילן": 4631364747,
        # בתים
        "בית": 7075284869,
        "בתים": 7075284869,
        "ביתון": 7075284869,
        "בניין": 7075284869,
        # מכוניות
        "מכונית": 7086281035,
        "רכב": 7086281035,
        "אוטו": 7086281035,
        "מכוניות": 7086281035,
        # ריהוט
        "כיסא": 8667289978,
        "כסא": 8667289978,  # שגיאת כתיב נפוצה
        "כיסאות": 8667289978,
        "שולחן": 7086407632,
        "שולחנות": 7086407632,
        "מנורה": 7086431294,
        "אור": 7086431294,
        "פנס": 7086431294,
        # גדרות
        "גדר": 7074904498,
        "גדרות": 7074904498,
        # סלעים
        "סלע": 5765284230,
        "אבן": 5765284230,
        "סלעים": 5765284230,
        "אבנים": 5765284230,
    }

    def __init__(self, on_status=None, use_smart_agent=True):
        """
        אתחול.

        Args:
            on_status: callback להודעות סטטוס
            use_smart_agent: האם להשתמש בסוכן החכם
        """
        self.on_status = on_status or (lambda x: safe_print(f"[Controller] {x}"))

        # World State - זיכרון של מה שנבנה
        self.world_state = WorldState(on_status=self.on_status)
        self.memory_file = os.path.join(os.path.dirname(__file__), "..", "data", "world_memory.json")
        self._load_memory()
        self.on_status("World Memory ready!")

        # סוכן חכם (גרסה 2.0)
        self.smart_agent = None
        if use_smart_agent and SMART_AGENT_AVAILABLE:
            try:
                self.smart_agent = SmartAgent(on_status=self.on_status)
                self.on_status("Smart Agent ready!")
            except Exception as e:
                self.on_status(f"Smart Agent not available: {e}")

        # LLM Builder לפקודות מורכבות (fallback)
        try:
            self.llm_builder = LLMBuilder(on_status=self.on_status)
            self.on_status("LLM Builder ready!")
        except Exception as e:
            self.on_status(f"LLM not available: {e}")
            self.llm_builder = None

        # Two-Phase Generator (new simplified system)
        try:
            self.robust_gen = RobustLuaGenerator(on_status=self.on_status)
            # Sync positions from world memory to prevent overlap after restart!
            self.robust_gen.sync_from_world_state(self.world_state)
            self.on_status("Two-Phase Generator ready!")
        except Exception as e:
            self.on_status(f"Robust Generator not available: {e}")
            self.robust_gen = None

        # Context memory — remember last build for "improve" / "add more"
        self.last_build_context = None
        self.last_build_type = None

        # Undo stack — stores Lua code to undo last builds
        self.undo_stack = []
        self.max_undo = 20

    def _check_server(self) -> bool:
        """בדיקה שהשרת פעיל."""
        try:
            response = requests.get(f"{self.SERVER_URL}/health", timeout=1)
            return response.status_code == 200
        except:
            return False

    def _send_command(self, lua_code: str) -> bool:
        """
        שליחת קוד Lua דרך HTTP Server.

        Args:
            lua_code: קוד Lua להרצה

        Returns:
            True אם הצליח
        """
        try:
            self.on_status(f"שולח: {lua_code}")

            response = requests.post(
                f"{self.SERVER_URL}/command",
                json={"command": lua_code},
                timeout=2
            )

            if response.status_code == 200:
                self.on_status("נשלח בהצלחה!")
                return True
            else:
                self.on_status(f"שגיאה: {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.on_status("שרת לא פעיל! ודא שהאפליקציה רצה.")
            return False
        except Exception as e:
            self.on_status(f"שגיאה: {e}")
            return False

    # ========================================
    # פקודות פשוטות (קוראות ל-Plugin)
    # ========================================

    def create_part(self, shape: str = "cube", color: str = None) -> bool:
        """יצירת Part."""
        if color:
            lua = f'VC.{shape}("{color}")'
        else:
            lua = f'VC.{shape}()'
        return self._send_command(lua)

    def set_color(self, color: str) -> bool:
        """שינוי צבע."""
        lua = f'VC.color("{color}")'
        return self._send_command(lua)

    def make_bigger(self, multiplier: float = 2) -> bool:
        """הגדלה."""
        lua = f'VC.bigger({multiplier})'
        return self._send_command(lua)

    def make_smaller(self, multiplier: float = 0.5) -> bool:
        """הקטנה."""
        lua = f'VC.smaller({multiplier})'
        return self._send_command(lua)

    def delete_selected(self) -> bool:
        """מחיקה."""
        return self._send_command('VC.delete()')

    def select_last(self) -> bool:
        """בחירת האחרון."""
        return self._send_command('VC.selectLast()')

    def load_ready_model(self, asset_id: int, position: tuple = (0, 5, 0)) -> bool:
        """
        טעינת מודל מוכן מ-Toolbox.

        Args:
            asset_id: מזהה המודל ב-Roblox
            position: מיקום (x, y, z)

        Returns:
            True אם הצליח
        """
        lua_code = f"VC.loadModel({asset_id}, {position[0]}, {position[1]}, {position[2]})"
        return self._send_command(lua_code)

    def build_world(self) -> bool:
        """
        בניית עולם שלם עם מודלים מוכנים!
        """
        lua_code = """
local parts = {}
-- בית במרכז
local house = VC.loadModel(7075284869, 0, 0, 0)
if house then table.insert(parts, house) end
-- עצים סביב
VC.loadModel(4631364747, -20, 0, -20)
VC.loadModel(4631364747, 20, 0, -20)
VC.loadModel(4631364747, -20, 0, 20)
VC.loadModel(4631364747, 20, 0, 20)
-- סלעים
VC.loadModel(5765284230, -30, 0, 0)
VC.loadModel(5765284230, 30, 0, 0)
-- גדרות
VC.loadModel(7074904498, 0, 0, -30)
VC.loadModel(7074904498, 0, 0, 30)
-- מכונית
VC.loadModel(7086281035, 15, 0, 0)
print("✅ נבנה עולם שלם!")
"""
        self.on_status("בונה עולם שלם עם מודלים מוכנים!")
        return self._send_command(lua_code)

    def add_multiple_models(self, model_name: str, count: int = 5) -> bool:
        """
        הוספת כמה מודלים זהים במיקומים אקראיים.
        """
        if model_name not in self.READY_MODELS:
            return False

        asset_id = self.READY_MODELS[model_name]
        lua_code = f"""
local parts = {{}}
for i = 1, {count} do
    local x = math.random(-50, 50)
    local z = math.random(-50, 50)
    local model = VC.loadModel({asset_id}, x, 0, z)
    if model then table.insert(parts, model) end
    wait(0.1)
end
print("✅ נוספו {count} {model_name}!")
"""
        return self._send_command(lua_code)

    # ========================================
    # פקודות ישירות (בלי Plugin)
    # ========================================

    def create_part_direct(self, shape: str = "Block", color: str = None,
                           size: tuple = None, position: tuple = None) -> bool:
        """יצירת Part ישירות (בלי Plugin)."""
        lua_parts = [
            "local p = Instance.new('Part')",
            f"p.Shape = Enum.PartType.{shape}",
            "p.Anchored = true",
        ]

        if color:
            lua_parts.append(f"p.BrickColor = BrickColor.new('{color}')")

        if size:
            lua_parts.append(f"p.Size = Vector3.new({size[0]}, {size[1]}, {size[2]})")
        else:
            lua_parts.append("p.Size = Vector3.new(4, 4, 4)")

        if position:
            lua_parts.append(f"p.Position = Vector3.new({position[0]}, {position[1]}, {position[2]})")
        else:
            lua_parts.append("p.Position = Vector3.new(0, 10, 0)")

        lua_parts.append("p.Parent = workspace")
        lua_parts.append("game.Selection:Set({p})")

        lua = " ".join(lua_parts)
        return self._send_command(lua)

    # ========================================
    # המרת פקודה קולית
    # ========================================

    def execute_voice_command(self, text: str) -> Dict[str, Any]:
        """
        ביצוע פקודה קולית - גרסה פשוטה!
        """
        text_lower = text.lower().strip()
        self.on_status(f"Got: {text}")

        # === התעלם מביטויים שהם לא פקודות בנייה ===
        NOT_BUILD_COMMANDS = [
            "תודה", "תודה רבה", "שלום", "היי", "הי", "ביי", "להתראות",
            "בוקר טוב", "ערב טוב", "לילה טוב", "מה נשמע", "מה קורה",
            "אוקי", "בסדר", "טוב", "יופי", "מעולה", "סבבה", "אחלה",
            "כן", "לא", "אולי", "בטח", "נכון", "לא נכון"
        ]

        # Check if it's just a greeting/thank you (not a build command)
        if any(text_lower == phrase or text_lower.startswith(phrase + " ") for phrase in NOT_BUILD_COMMANDS):
            self.on_status(f"Not a build command: {text}")
            return {
                "success": True,
                "understood": "שיחה",
                "message": "בבקשה! מה לבנות?",
                "not_a_command": True
            }

        # === AI Chat mode — modify/script existing objects ===
        AI_CHAT_WORDS = [
            "תשנה", "שנה את", "שנה סקריפט", "תעדכן", "עדכן את",
            "הוסף סקריפט", "תוסיף סקריפט", "שים סקריפט", "תשים סקריפט",
            "תעשה סקריפט", "עשה סקריפט",
            "שנה מהירות", "תשנה מהירות", "שנה צבע", "תשנה צבע",
            "שנה גודל", "תשנה גודל",
            "תעשה ש", "תגרום ל",
            "סרוק", "סרוק את המשחק",
        ]
        if any(w in text_lower for w in AI_CHAT_WORDS):
            self.on_status("AI Chat mode activated!")
            return self.ai_chat(text)

        # === BEHAVIOR / LOGIC commands — "תוסיף ריצה", "תגרום לו לעקוב", etc. ===
        BEHAVIOR_TRIGGER_WORDS = [
            "תוסיף ריצה", "תוסיף קפיצה", "תוסיף עפיפה", "תוסיף סיבוב",
            "תגרום ל", "שיעקוב", "שירוץ", "שיקפוץ", "שיעוף", "שיסתובב",
            "לרוץ", "לקפוץ", "לעוף", "לנהוג", "לעקוב", "לסייר",
            "ריצה", "קפיצה", "עפיפה", "נהיגה", "סיור",
            "דלת שנפתחת", "דלת בלחיצה", "פתיחה בלחיצה",
            "מטבע לאיסוף", "מטבעות", "לאסוף",
            "נזק בנגיעה", "ריפוי", "מרפא",
            "טלפורט", "טרמפולינה", "קופצני",
            "מדבר", "ידבר", "שיחה",
            "תוקף", "לתקוף", "יתקוף", "אויב שתוקף",
            "ידידותי", "חברותי",
            "לידרבורד", "ניקוד", "נקודות", "תוצאות",
            "צ'קפוינט", "נקודת שמירה",
            "מהירות", "בוסט", "speed boost",
            "אזור מוות", "לבה",
            "ספאון", "נקודת לידה",
            "טיימר", "שעון", "ספירה",
            "פיצוץ", "מתפוצץ",
            "NPC", "npc", "דמות ש",
            "רכב ש", "מכונית ש",
        ]
        # === GAME SYSTEMS — "תוסיף מערכת חיים", "תעשה מירוץ", etc. ===
        if GAME_SYSTEMS_AVAILABLE:
            game_sys = find_game_system(text)
            if game_sys:
                self.on_status(f"Game System: {game_sys['name']} ({game_sys['description']})")
                lua_code = generate_game_system_lua(game_sys['name'])
                success = self._send_command(lua_code)
                return {
                    "success": success,
                    "understood": game_sys['hebrew'],
                    "method": "game_system",
                    "message": f"התקנתי {game_sys['description']}!" if success else "לא הצלחתי להתקין",
                }

        if BEHAVIORS_AVAILABLE and any(w in text_lower for w in BEHAVIOR_TRIGGER_WORDS):
            self.on_status("Behavior/Logic mode detected!")
            return self._execute_behavior_command(text)

        # === Context memory — "שפר", "הוסף עוד", "עוד" ===
        IMPROVE_WORDS = ["שפר", "שדרג", "הוסף עוד", "תוסיף עוד", "תשפר", "תשדרג", "שפר את", "שדרג את"]
        MORE_WORDS = ["עוד", "עוד אחד", "עוד פעם", "שוב"]

        if any(w in text_lower for w in IMPROVE_WORDS) and self.last_build_context:
            last = self.last_build_context
            self.on_status(f"Context memory: improving '{last}'")
            text = f"בנה עוד דברים ליד {last} - הוסף פרטים ושיפורים"
            text_lower = text.lower()

        elif any(text_lower.strip() == w for w in MORE_WORDS) and self.last_build_type:
            last_type = self.last_build_type
            self.on_status(f"Context memory: more '{last_type}'")
            text = f"בנה {last_type}"
            text_lower = text.lower()

        # === Short command recognition — just "בית!" without "בנה" ===
        SHORT_OBJECTS = {
            "בית": "בנה בית", "עץ": "בנה עץ", "מכונית": "בנה מכונית",
            "מגדל": "בנה מגדל", "גשר": "בנה גשר", "מזרקה": "בנה מזרקה",
            "סירה": "בנה סירה", "מסוק": "בנה מסוק", "מטוס": "בנה מטוס",
            "כיסא": "בנה כיסא", "שולחן": "בנה שולחן", "כלב": "בנה כלב",
            "חתול": "בנה חתול", "רקטה": "בנה רקטה", "חללית": "בנה חללית",
            "עוגה": "בנה עוגה", "גלידה": "בנה גלידה", "כוכב": "בנה כוכב",
            "טירה": "בנה טירה", "ארמון": "בנה ארמון", "בריכה": "בנה בריכה",
            "סלע": "בנה סלע", "פרח": "בנה פרח", "כדור": "בנה כדור",
            "מגלשה": "בנה מגלשה", "פנס": "בנה פנס רחוב", "גדר": "בנה גדר",
            # v5.0 Interactive
            "מטבע": "בנה מטבע", "טרמפולינה": "בנה טרמפולינה", "לבה": "בנה לבה",
            "מהירות": "בנה מהירות", "טלפורט": "בנה טלפורט", "מדורה": "בנה מדורה",
            "לידרבורד": "בנה לידרבורד", "לב": "בנה לב", "חיים": "בנה חיים",
            # v6.0 NPCs, Weather, Mini-games
            "שומר": "בנה שומר", "אויב": "בנה אויב", "חבר": "בנה חבר",
            "דמות": "בנה דמות", "מפלצת": "בנה מפלצת", "זומבי": "בנה זומבי",
            "גשם": "בנה גשם", "שלג": "בנה שלג", "לילה": "בנה לילה",
            "שקיעה": "בנה שקיעה", "ערפל": "בנה ערפל",
        }
        clean_cmd = text_lower.strip().rstrip("!").rstrip("?").strip()
        if clean_cmd in SHORT_OBJECTS:
            text = SHORT_OBJECTS[clean_cmd]
            text_lower = text.lower()
            self.on_status(f"Short command: '{clean_cmd}' -> '{text}'")

        # === Check if this looks like a BUILD command ===
        BUILD_WORDS = ["בנה", "תבנה", "צור", "תצור", "תעשה", "עשה", "תוסיף", "הוסף", "שים", "תשים", "תן", "רוצה",
                       "תגרום", "שיעשה", "שירוץ", "שיקפוץ", "שיעוף", "שיסתובב", "שיעקוב", "שיתקוף",
                       "שידבר", "שינהג", "שיפוצץ"]
        OBJECTS = ["בית", "עץ", "מכונית", "רכב", "מגדל", "עיר", "כביש", "גשר", "קוביה", "כדור",
                   "גליל", "במה", "פלטפורמה", "אובי", "obby", "משחק", "גדר", "חומה", "דלת",
                   "חלון", "גג", "רצפה", "קיר", "שולחן", "כיסא", "ספה", "מיטה", "ארון",
                   "מטבע", "טרמפולינה", "לבה", "מהירות", "טלפורט", "מדורה", "לידרבורד",
                   "לב", "חיים", "צ'קפוינט", "במה מסתובבת", "פורטל",
                   "שומר", "אויב", "חבר", "דמות", "מפלצת", "זומבי", "חייל",
                   "גשם", "שלג", "לילה", "שקיעה", "ערפל",
                   "מירוץ", "משחק מטבעות"]

        has_build_word = any(w in text_lower for w in BUILD_WORDS)
        has_object = any(w in text_lower for w in OBJECTS)

        # If no build word AND no object - probably not a build command
        if not has_build_word and not has_object:
            self.on_status(f"Not recognized as build: {text}")
            return {
                "success": False,
                "understood": text,
                "message": "לא הבנתי. נסה: 'בנה בית' או 'צור עץ'",
                "hint": "אמור מה לבנות"
            }

        # === Undo command ===
        if any(w in text_lower for w in ["בטל", "חזור", "אנדו", "undo"]):
            self.on_status("Command: UNDO")
            return self._undo_last()

        # === Save/Load world ===
        if any(w in text_lower for w in ["שמור עולם", "שמור את העולם", "שמור הכל"]):
            self.on_status("Command: SAVE WORLD")
            return self._save_world()

        if any(w in text_lower for w in ["טען עולם", "טען את העולם", "שחזר עולם"]):
            self.on_status("Command: LOAD WORLD")
            return self._load_world()

        # === Clear weather ===
        if any(w in text_lower for w in ["נקה מזג אוויר", "נקה אוויר", "יום רגיל", "בטל מזג אוויר"]):
            self.on_status("Command: CLEAR WEATHER")
            lua = "VC.clearWeather()"
            success = self._send_command(lua)
            return {"success": success, "understood": "ניקוי מזג אוויר", "method": "clear_weather",
                    "message": "ניקיתי את מזג האוויר! ☀️"}

        # === פקודות עריכה פשוטות ===
        if any(w in text_lower for w in ["מחק", "תמחק", "הסר"]):
            self.on_status("Command: DELETE")
            success = self.delete_selected()
            return {"success": success, "understood": "מחיקה", "message": "מחקתי!"}

        if any(w in text_lower for w in ["הגדל", "תגדיל"]):
            self.on_status("Command: BIGGER")
            success = self.make_bigger()
            return {"success": success, "understood": "הגדלה", "message": "הגדלתי!"}

        if any(w in text_lower for w in ["הקטן", "תקטין"]):
            self.on_status("Command: SMALLER")
            success = self.make_smaller()
            return {"success": success, "understood": "הקטנה", "message": "הקטנתי!"}

        # === בנייה - ה-AI מטפל ===
        self.on_status(f"BUILD: {text}")
        return self._build_with_ai(text)

    def _execute_behavior_command(self, text: str) -> Dict[str, Any]:
        """
        Execute a behavior/logic command.
        "תוסיף ריצה לדמות" → finds behavior → generates Script injection Lua → sends
        """
        self.on_status(f"Behavior command: {text}")

        # Try behavior blueprints first (instant, reliable)
        result = find_behavior_for_command(text)
        if result:
            behavior_name, behavior = result

            # Extract target name from text
            target_name = self._extract_behavior_target(text)
            self.on_status(f"Behavior: {behavior.hebrew_name} → {target_name or 'selected'}")

            # Generate Lua
            lua_code = generate_behavior_lua(behavior, target_name=target_name)

            # Send to Roblox
            success = self._send_command(lua_code)

            return {
                "success": success,
                "understood": f"{behavior.hebrew_name}",
                "method": "behavior_blueprint",
                "message": f"הוספתי {behavior.hebrew_name}!" if success else f"לא הצלחתי להוסיף {behavior.hebrew_name}",
                "behavior": behavior_name,
            }

        # Fallback: try AI to generate behavior code
        self.on_status("No preset behavior found, trying AI...")
        return self.ai_chat(text)

    def _extract_behavior_target(self, text: str) -> Optional[str]:
        """Extract target object name from behavior command."""
        import re

        text_lower = text.lower()

        # Known targets
        known = [
            "דמות", "בנאדם", "איש", "שחקן",
            "NPC", "npc", "חייל", "זומבי", "אויב", "שומר", "חבר",
            "מכונית", "רכב", "אוטו",
            "בית", "דלת", "חלון",
            "כדור", "קוביה", "עץ", "סלע",
            "מפלצת", "דרקון",
        ]

        for obj in known:
            if obj in text_lower:
                return obj

        # Try "ל[name]" pattern
        match = re.search(r'ל(\S+)', text)
        if match:
            candidate = match.group(1)
            behavior_words = ["ריצה", "קפיצה", "עפיפה", "נהיגה", "סיבוב",
                            "רוץ", "קפוץ", "עוף", "נהוג", "הסתובב",
                            "עקוב", "סייר", "תקוף", "דבר"]
            if candidate not in behavior_words and len(candidate) > 1:
                return candidate

        return None

    def _build_with_ai(self, text: str) -> Dict[str, Any]:
        """
        Let the AI handle the command directly.
        Uses Two-Phase Generation for reliable results.
        Maintains world context for smart positioning.
        """
        # Extract what object we're building (for clear feedback)
        detected_object = self._detect_object(text)
        self.on_status(f"Request: {text}")
        self.on_status(f"Detected: {detected_object}")

        # Get current world context for smarter generation
        world_context = self.world_state.get_context_for_llm()

        # Check for spatial references ("ליד הבית", "מאחורי העץ")
        spatial_ref = self.world_state.parse_spatial_reference(text)
        position_hint = None
        if spatial_ref:
            relation, ref_obj = spatial_ref
            position_hint = self.world_state.calculate_relative_position(ref_obj, relation)
            self.on_status(f"Position: {relation.value} {ref_obj.name} -> {position_hint}")

        # Check for compound commands ("build a village with X, Y, Z")
        if self.robust_gen and self.robust_gen.is_compound_command(text):
            self.on_status(f"Compound command detected! Building world...")
            result = self.robust_gen.build_world_sequence(text, context=world_context)
            if result.get("success"):
                lua_code = result.get("lua_code")
                built_items = result.get("built_items", [])
                self.on_status(f"World Builder: built {len(built_items)} items")
                # Add animation + sound effects
                bx, bz = self.robust_gen.get_next_position() if self.robust_gen else (0, 0)
                lua_code = self._wrap_with_effects(lua_code, bx, bz)
                success = self._send_command(lua_code)
                if success:
                    for item_name in built_items:
                        self._remember_creation(item_name, item_name, position_hint)
                    # Save context for "improve" / "add more"
                    self.last_build_context = text
                    self.last_build_type = detected_object
                    # Undo stack
                    self.undo_stack.append({"name": f"World({len(built_items)})", "type": "compound"})
                    if len(self.undo_stack) > self.max_undo:
                        self.undo_stack.pop(0)
                return {
                    "success": success,
                    "understood": f"World({len(built_items)} items)",
                    "method": "world_builder",
                    "message": f"בניתי עולם עם {len(built_items)} אובייקטים!"
                }

        # Try Two-Phase Generator first (presets + JSON generation)
        if self.robust_gen:
            result = self.robust_gen.generate(text, context=world_context)

            if result.get("success"):
                lua_code = result.get("lua_code")
                method = result.get("method", "unknown")
                blueprint = result.get("blueprint", detected_object)

                self.on_status(f"Method: {method}")
                self.on_status(f"Building: {blueprint}")
                # Add animation + sound effects
                bx, bz = self.robust_gen.get_next_position() if self.robust_gen else (0, 0)
                lua_code = self._wrap_with_effects(lua_code, bx, bz)
                success = self._send_command(lua_code)

                # Remember what we built!
                if success:
                    self._remember_creation(detected_object, blueprint, position_hint)
                    # Save context for "improve" / "add more"
                    self.last_build_context = blueprint
                    self.last_build_type = detected_object
                    # Undo stack
                    self.undo_stack.append({"name": blueprint, "type": "single"})
                    if len(self.undo_stack) > self.max_undo:
                        self.undo_stack.pop(0)

                return {
                    "success": success,
                    "understood": blueprint,
                    "method": method,
                    "message": f"בניתי {blueprint}!"
                }

        # Fallback to LLM Builder with context
        if self.llm_builder:
            self.on_status(f"Using LLM for: {detected_object}")
            lua_code = self.llm_builder.generate_lua(text, context=world_context)

            if lua_code:
                success = self._send_command(lua_code)
                if success:
                    self._remember_creation(detected_object, detected_object)
                return {
                    "success": success,
                    "understood": detected_object,
                    "method": "llm",
                    "message": f"בניתי {detected_object}!"
                }

        return {
            "success": False,
            "error": "לא הצלחתי לבנות",
            "understood": detected_object
        }

    def _undo_last(self) -> Dict[str, Any]:
        """Undo the last build by removing it from workspace."""
        if not self.undo_stack:
            return {"success": False, "understood": "ביטול", "message": "אין מה לבטל!"}

        undo_info = self.undo_stack.pop()
        undo_name = undo_info.get("name", "Unknown")

        # Send Lua to delete the last created object
        lua_undo = f"""
for _, child in ipairs(workspace:GetChildren()) do
    if child.Name == "{undo_name}" or child:IsA("Model") and child.Name == "{undo_name}" then
        child:Destroy()
        print("Undo: deleted " .. "{undo_name}")
        break
    end
end
-- Try removing last part if it's not a model
local children = workspace:GetChildren()
for i = #children, 1, -1 do
    local child = children[i]
    if child:IsA("BasePart") or child:IsA("Model") then
        if child.Name ~= "Baseplate" and child.Name ~= "Terrain" then
            child:Destroy()
            print("Undo: removed last object")
            break
        end
    end
end
"""
        success = self._send_command(lua_undo)
        # Also remove from world state
        if hasattr(self.world_state, 'objects') and self.world_state.objects:
            self.world_state.objects.pop()
            self.world_state.save_to_file()

        return {"success": success, "understood": f"ביטול {undo_name}", "method": "undo", "message": f"ביטלתי את {undo_name}!"}

    def _save_world(self) -> Dict[str, Any]:
        """Save the current world to a Lua file for later loading."""
        import json
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, 'saved_world.json')

        # Save world state
        world_data = {
            "objects": [obj.to_dict() if hasattr(obj, 'to_dict') else {"name": str(obj)} for obj in self.world_state.objects],
            "object_count": len(self.world_state.objects),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, ensure_ascii=False, indent=2)

        self.on_status(f"World saved to {save_path}")
        return {"success": True, "understood": "שמירת עולם", "method": "save",
                "message": f"העולם נשמר! ({len(self.world_state.objects)} אובייקטים)"}

    def _load_world(self) -> Dict[str, Any]:
        """Load a previously saved world."""
        import json
        save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'saved_world.json')

        if not os.path.exists(save_path):
            return {"success": False, "understood": "טעינת עולם", "message": "אין עולם שמור!"}

        with open(save_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)

        count = world_data.get("object_count", 0)
        timestamp = world_data.get("timestamp", "")
        self.on_status(f"Loaded world: {count} objects from {timestamp}")
        return {"success": True, "understood": "טעינת עולם", "method": "load",
                "message": f"טענתי עולם עם {count} אובייקטים מ-{timestamp}!"}

    def _get_workspace_scan(self) -> str:
        """Get the latest workspace scan from the HTTP server."""
        try:
            response = requests.get(f"{self.SERVER_URL}/scan", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get("hasScan") and data.get("scan"):
                    return data["scan"]
        except:
            pass
        return None

    def _trigger_scan(self) -> bool:
        """Tell Roblox plugin to scan workspace now."""
        lua_scan = "VC.sendScan()"
        return self._send_command(lua_scan)

    def ai_chat(self, user_message: str) -> Dict[str, Any]:
        """
        AI Chat - scan the game and modify/create scripts based on user request.
        The user describes what they want in Hebrew, AI generates targeted Lua.
        """
        self.on_status(f"AI Chat: {user_message}")

        # Step 1: Get workspace scan
        scan_data = self._get_workspace_scan()
        workspace_description = "העולם ריק כרגע."

        if scan_data and scan_data.get("objects"):
            objects = scan_data["objects"]
            desc_parts = [f"יש {len(objects)} אובייקטים ב-Workspace:"]
            for obj in objects[:30]:  # Limit to 30 objects for context
                name = obj.get("name", "?")
                cls = obj.get("class", "?")
                pos = obj.get("position", [])
                scripts = obj.get("scripts", [])
                children = obj.get("children", [])

                line = f"  - {name} ({cls})"
                if pos:
                    line += f" at ({pos[0]},{pos[1]},{pos[2]})"
                if children:
                    child_names = [c.get("name", "?") for c in children[:5]]
                    line += f" [parts: {', '.join(child_names)}]"
                if scripts:
                    script_names = [s.get("name", "?") for s in scripts]
                    line += f" [scripts: {', '.join(script_names)}]"
                desc_parts.append(line)

            workspace_description = "\n".join(desc_parts)
        else:
            # Try triggering a scan
            self._trigger_scan()
            self.on_status("Triggered workspace scan, using world memory...")
            # Fallback to world_state
            if self.world_state and self.world_state.objects:
                desc_parts = [f"יש {len(self.world_state.objects)} אובייקטים (מהזיכרון):"]
                for obj in self.world_state.objects[-20:]:
                    name = getattr(obj, 'name', str(obj))
                    desc_parts.append(f"  - {name}")
                workspace_description = "\n".join(desc_parts)

        # Step 2: Build prompt for AI
        ai_prompt = f"""אתה AI שמנהל משחק Roblox Studio. אתה רואה את כל מה שיש במשחק ויכול לשנות הכל.

## מצב הנוכחי של המשחק:
{workspace_description}

## מה המשתמש מבקש:
{user_message}

## חוקים:
1. תחזיר **רק קוד Lua** - בלי טקסט, בלי הסברים
2. אם המשתמש מבקש לשנות סקריפט - מצא את האובייקט ושנה את ה-Script שלו
3. אם המשתמש מבקש להוסיף סקריפט - צור Script חדש ושים אותו בתוך האובייקט
4. אם המשתמש מבקש לשנות מאפיין (צבע, גודל, מיקום) - שנה את המאפיין ישירות
5. אם המשתמש מבקש לבנות משהו חדש - בנה אותו
6. השתמש ב-workspace:FindFirstChild("Name") או workspace:FindFirstChild("Name", true) למציאת אובייקטים
7. לשינוי סקריפטים: script.Source = [[new code here]]
8. APIs זמינים: workspace, game, Instance, Vector3, CFrame, BrickColor, Enum, Color3, spawn, wait, pcall
9. אפקטים: VC.addFire(part), VC.addSparkles(part), VC.spin(part), VC.rainbow(part), VC.float(part)
10. תאורה: VC.setLighting(clockTime, brightness, ambient), VC.clearWeather()

## דוגמאות:
בקשה: "תעשה את המכונית מהירה יותר"
קוד:
local car = workspace:FindFirstChild("DriveableCar", true)
if car then
    local seat = car:FindFirstChild("driver_seat", true)
    if seat and seat:IsA("VehicleSeat") then
        seat.MaxSpeed = 120
        seat.Torque = 40
        print("Car speed doubled!")
    end
end

בקשה: "תוסיף סקריפט שכל מי שנוגע בבית מקבל נקודות"
קוד:
local house = workspace:FindFirstChild("EnterableHouse", true)
if house then
    local script = Instance.new("Script")
    script.Name = "ScoreScript"
    script.Source = [[
local Players = game:GetService("Players")
script.Parent.Touched:Connect(function(hit)
    local player = Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        local ls = player:FindFirstChild("leaderstats")
        if ls and ls:FindFirstChild("Score") then
            ls.Score.Value = ls.Score.Value + 1
        end
    end
end)
]]
    script.Parent = house
    print("Score script added!")
end

עכשיו, צור קוד Lua עבור הבקשה של המשתמש:"""

        # Step 3: Send to LLM
        lua_code = None

        if self.llm_builder:
            # Use OpenRouter or Claude
            if self.llm_builder.openrouter_key:
                lua_code = self.llm_builder._generate_with_openrouter(ai_prompt, "")
            elif self.llm_builder.client:
                try:
                    message = self.llm_builder.client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4000,
                        system="אתה AI שיודע Roblox Lua. תחזיר רק קוד Lua, בלי שום טקסט אחר.",
                        messages=[{"role": "user", "content": ai_prompt}]
                    )
                    lua_code = message.content[0].text.strip()
                except Exception as e:
                    self.on_status(f"AI Chat error: {e}")

        if not lua_code:
            return {
                "success": False,
                "understood": "AI Chat",
                "message": "אין AI זמין! צריך OPENROUTER_API_KEY או ANTHROPIC_API_KEY"
            }

        # Clean markdown if present
        if lua_code.startswith("```"):
            lines = lua_code.split("\n")
            lua_code = "\n".join(lines[1:-1])

        self.on_status(f"AI Chat generated {len(lua_code)} chars of Lua")

        # Step 4: Send to Roblox
        success = self._send_command(lua_code)

        return {
            "success": success,
            "understood": user_message,
            "method": "ai_chat",
            "message": f"AI ביצע: {user_message}" if success else "AI לא הצליח לבצע"
        }

    def _wrap_with_effects(self, lua_code: str, x: float = 0, z: float = 0) -> str:
        """Wrap Lua code with build animation, sound, and camera fly-to."""
        prefix = f"pcall(function() VC.playBuildSound() end)\npcall(function() VC.buildEffect({x}, 10, {z}) end)\n"
        suffix = f"\npcall(function() VC.playSuccessSound() end)\npcall(function() VC.flyTo({x}, 10, {z}) end)"
        return prefix + lua_code + suffix

    def _remember_creation(self, object_name: str, blueprint_name: str, position: tuple = None):
        """
        Remember what we just built in world state.
        """
        # Determine object type
        type_map = {
            "בית": ObjectType.BUILDING, "בניין": ObjectType.BUILDING,
            "עיר": ObjectType.BUILDING, "מגדל": ObjectType.BUILDING,
            "ארמון": ObjectType.BUILDING, "טירה": ObjectType.BUILDING,
            "עץ": ObjectType.NATURE, "עצים": ObjectType.NATURE,
            "סלע": ObjectType.NATURE, "פרח": ObjectType.NATURE,
            "מכונית": ObjectType.VEHICLE, "רכב": ObjectType.VEHICLE,
            "כביש": ObjectType.ROAD, "גשר": ObjectType.ROAD,
            "שולחן": ObjectType.FURNITURE, "כיסא": ObjectType.FURNITURE,
            "גדר": ObjectType.DECORATION, "פנס": ObjectType.DECORATION,
        }
        obj_type = type_map.get(object_name, ObjectType.CUSTOM)

        # Default position if not specified — uses 2D grid!
        if not position:
            x, z = self.robust_gen.get_next_position() if self.robust_gen else (0, 0)
            position = (x, 5, z)

        # Create and add object
        obj = WorldObject(
            id="",
            name=blueprint_name or object_name,
            object_type=obj_type,
            position=position,
            size=(20, 10, 20),  # Default size estimate
        )
        self.world_state.add_object(obj)
        self._save_memory()  # Persist to file
        self.on_status(f"Remembered: {obj.name} at {position}")

    def _detect_object(self, text: str) -> str:
        """Detect what object the user wants to build."""
        text_lower = text.lower()

        # Hebrew object names to friendly names
        objects = {
            "בית": "בית",
            "דירה": "בית",
            "בניין": "בניין",
            "עץ": "עץ",
            "עצים": "עצים",
            "מכונית": "מכונית",
            "רכב": "מכונית",
            "אוטו": "מכונית",
            "מגדל": "מגדל",
            "עיר": "עיר",
            "כביש": "כביש",
            "גשר": "גשר",
            "קוביה": "קוביה",
            "כדור": "כדור",
            "גליל": "גליל",
            "במה": "במה",
            "אובי": "אובי",
            "obby": "אובי",
            "משחק": "משחק",
            "גדר": "גדר",
            "חומה": "חומה",
            "שולחן": "שולחן",
            "כיסא": "כיסא",
            "ארמון": "ארמון",
            "טירה": "טירה",
            # v4.0 additions
            "רקטה": "רקטה",
            "חללית": "חללית",
            "כלב": "כלב",
            "חתול": "חתול",
            "עוגה": "עוגה",
            "גלידה": "גלידה",
            "גיטרה": "גיטרה",
            "פסנתר": "פסנתר",
            "כוכב": "כוכב",
            "מגרש כדורגל": "מגרש כדורגל",
            "תחנת חלל": "תחנת חלל",
            "מסלול מירוצים": "מסלול מירוצים",
            "פארק מים": "פארק מים",
            "מגרש משחקים": "מגרש משחקים",
        }

        # Remove compound phrases that cause false matches
        filtered = text_lower
        for compound in ["כדור הארץ", "כדור סל"]:
            filtered = filtered.replace(compound, "")

        # Match LONGEST keys first for accurate detection
        for heb, name in sorted(objects.items(), key=lambda x: len(x[0]), reverse=True):
            if heb in filtered:
                return name

        return text  # Return original if no match


    # ========================================
    # פקודות חכמות נוספות
    # ========================================

    def create_game(self, game_type: str) -> Dict[str, Any]:
        """יצירת משחק שלם."""
        if self.smart_agent:
            result = self.smart_agent.execute(f"צור משחק {game_type}")
            if result.get("lua_code"):
                success = self._send_command(result["lua_code"])
                return {"success": success, "message": result.get("message")}
        return {"success": False, "error": "סוכן חכם לא זמין"}

    def create_interaction(self, interaction_type: str) -> Dict[str, Any]:
        """יצירת אלמנט אינטראקטיבי."""
        if self.smart_agent:
            result = self.smart_agent.execute(f"צור {interaction_type}")
            if result.get("lua_code"):
                success = self._send_command(result["lua_code"])
                return {"success": success, "message": result.get("message")}
        return {"success": False, "error": "סוכן חכם לא זמין"}

    def get_world_info(self) -> str:
        """קבלת מידע על העולם."""
        # Use our world state memory
        return self.world_state.get_context_for_llm()

    def clear_world(self) -> bool:
        """ניקוי העולם."""
        lua_code = "VC.clearWorld()"
        success = self._send_command(lua_code)
        # Clear memory too
        self.world_state.clear()
        self._save_memory()  # Save empty state
        if self.robust_gen:
            self.robust_gen.creation_count = 0
            self.robust_gen.next_x_offset = 0
        return success

    def get_object_count(self) -> int:
        """מספר האובייקטים בעולם."""
        return len(self.world_state.objects)

    def find_object(self, name: str) -> Optional[Any]:
        """חיפוש אובייקט לפי שם."""
        return self.world_state.find_by_name(name)

    def _load_memory(self):
        """Load world state from file if exists."""
        try:
            if os.path.exists(self.memory_file):
                self.world_state.load_from_file(self.memory_file)
                self.on_status(f"Loaded {len(self.world_state.objects)} objects from memory")
        except Exception as e:
            self.on_status(f"Could not load memory: {e}")

    def _save_memory(self):
        """Save world state to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            self.world_state.save_to_file(self.memory_file)
        except Exception as e:
            self.on_status(f"Could not save memory: {e}")


# ========================================
# בדיקה
# ========================================

if __name__ == "__main__":
    print("=" * 50)
    print("בדיקת Direct Roblox Controller")
    print("=" * 50)
    print()
    print("ודא ש:")
    print("1. Roblox Studio פתוח")
    print("2. ה-Plugin VoiceCreator.lua מותקן (אופציונלי)")
    print()

    controller = DirectRobloxController()

    # בדיקות
    tests = [
        "תוסיף קוביה כחולה",
        "תצבע באדום",
        "תגדיל",
        "תוסיף כדור ירוק",
        "תמחק",
    ]

    for test in tests:
        print(f"\n>>> פקודה: {test}")
        input("לחץ Enter להמשיך...")
        result = controller.execute_voice_command(test)
        print(f"    תוצאה: {result}")
