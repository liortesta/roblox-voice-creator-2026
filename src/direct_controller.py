"""
Direct Roblox Controller - שליטה דרך HTTP Server
=================================================
שולח פקודות Lua דרך HTTP Server ל-Plugin ב-Roblox Studio.

עכשיו עם תמיכה ב-LLM לפקודות מורכבות!
"""

import requests
import time
from typing import Dict, Any, Optional
from llm_builder import LLMBuilder


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

    def __init__(self, on_status=None):
        """
        אתחול.

        Args:
            on_status: callback להודעות סטטוס
        """
        self.on_status = on_status or (lambda x: print(f"[Controller] {x}"))

        # LLM Builder לפקודות מורכבות
        try:
            self.llm_builder = LLMBuilder(on_status=self.on_status)
            self.on_status("LLM Builder מוכן לפקודות מורכבות!")
        except Exception as e:
            self.on_status(f"LLM לא זמין: {e}")
            self.llm_builder = None

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
        ביצוע פקודה קולית.

        Args:
            text: הטקסט שזוהה מהקול

        Returns:
            dict עם success, action, message
        """
        # נרמול טקסט - תיקון שגיאות נפוצות
        text_normalized = normalize_hebrew_text(text)
        text_lower = text_normalized.lower()
        self.on_status(f"מעבד: {text_normalized}")

        # זיהוי צבע
        color = None
        for heb, eng in self.COLORS.items():
            if heb in text_lower:
                color = eng
                break

        # זיהוי צורה
        shape = "cube"  # ברירת מחדל
        for heb, eng in self.SHAPES.items():
            if heb in text_lower:
                shape = eng
                break

        # === שלב 1: זיהוי סוג הפקודה ===
        # מילים שמציינות פעולת בנייה/יצירה
        BUILD_WORDS = ["בנה", "בני", "צור", "תיצור", "תעשה", "תוסיף", "שים", "תשים", "הוסף"]
        # מילים שמציינות פעולת עריכה (על הקיים)
        RESIZE_BIGGER = ["הגדל", "תגדיל", "יותר גדול", "גדל"]
        RESIZE_SMALLER = ["הקטן", "תקטין", "יותר קטן", "קטן"]
        DELETE_WORDS = ["מחק", "תמחק", "הסר", "תסיר"]
        COLOR_WORDS = ["צבע", "תצבע", "לצבוע"]
        SELECT_WORDS = ["בחר", "תבחר", "select"]

        # בדיקה האם זו פקודת בנייה
        is_build_command = any(w in text_lower for w in BUILD_WORDS)

        # מילים שמציינות אובייקט מורכב לבניה
        COMPLEX_OBJECTS = ["בית", "מכונית", "עץ", "אצטדיון", "טירה", "רובוט", "פארק",
                          "גינה", "מגרש", "עיר", "עיירה", "כפר", "שכונה", "רחוב",
                          "כביש", "גשר", "ספינה", "מטוס", "מסוק", "רכבת", "אוטובוס",
                          "חדר", "שולחן", "כיסא", "מיטה", "מנורה", "גדר", "הר", "תירה", "תותח",
                          "סלע", "אבן", "עצים", "בתים", "חנות", "בניין", "מגדל", "ארמון",
                          "בריכה", "מזרקה", "פסל", "גן", "משחקים", "מגלשה", "נדנדה"]

        has_complex_object = any(kw in text_lower for kw in COMPLEX_OBJECTS)

        # === שלב 2: אם זו פקודת בנייה - עדיפות לבנייה! ===
        if is_build_command:
            # === בניית עולם שלם ===
            if any(w in text_lower for w in ["עולם", "עולמות"]):
                self.on_status("בונה עולם שלם!")
                success = self.build_world()
                if success:
                    return {"success": True, "action": "world", "message": "בניתי עולם שלם עם בית, עצים, סלעים, גדרות ומכונית!"}

            # === הוספת כמה מודלים ===
            wants_multiple = any(w in text_lower for w in ["הרבה", "כמה", "מלא", "יער"])

            if wants_multiple:
                for model_name, asset_id in self.READY_MODELS.items():
                    if model_name in text_lower or (model_name == "עץ" and "יער" in text_lower):
                        count = 10 if "יער" in text_lower else 5
                        self.on_status(f"מוסיף {count} {model_name}...")
                        success = self.add_multiple_models(model_name, count)
                        if success:
                            return {"success": True, "action": "multiple_models", "message": f"הוספתי {count} {model_name}!"}

            # === בדיקה אם מבקשים מודל מוכן ===
            wants_ready_model = any(w in text_lower for w in ["מוכן", "מוכנה", "מודל", "toolbox", "קיים", "קיימת"])

            # אם מבקשים מודל מוכן - חפש באוסף המודלים
            if wants_ready_model:
                for model_name, asset_id in self.READY_MODELS.items():
                    if model_name in text_lower:
                        self.on_status(f"טוען מודל מוכן: {model_name}")
                        success = self.load_ready_model(asset_id)
                        if success:
                            return {"success": True, "action": "ready_model", "message": f"הוספתי {model_name} מוכן!"}
                        else:
                            return {"success": False, "error": f"נכשל בטעינת מודל {model_name}"}

            # === בנייה מורכבת עם Claude ===
            if has_complex_object and self.llm_builder:
                self.on_status(f"משתמש ב-Claude לפקודה מורכבת: {text}")
                lua_code = self.llm_builder.generate_lua(text)
                if lua_code:
                    self.on_status(f"מריץ קוד מ-Claude...")
                    success = self._send_command(lua_code)
                    if success:
                        return {"success": True, "action": "llm_build", "message": f"בניתי: {text}!"}
                    else:
                        return {"success": False, "error": "נכשל בהרצת הקוד"}

            # === יצירת צורה פשוטה (קוביה, כדור, גליל) ===
            if shape != "cube" or "קוביה" in text_lower:
                self.on_status(f"יוצר {shape} {color or ''}")
                success = self.create_part(shape=shape, color=color)
                if not success:
                    shape_map = {"cube": "Block", "ball": "Ball", "cylinder": "Cylinder"}
                    success = self.create_part_direct(shape=shape_map.get(shape, "Block"), color=color)
                msg = f"יצרתי {shape}" + (f" {color}" if color else "") + "!"
                return {"success": success, "action": "create", "message": msg}

            # === אם יש מילת בנייה אבל לא זיהינו מה - נסה עם Claude ===
            if self.llm_builder:
                self.on_status(f"משתמש ב-Claude לפקודה: {text}")
                lua_code = self.llm_builder.generate_lua(text)
                if lua_code:
                    success = self._send_command(lua_code)
                    if success:
                        return {"success": True, "action": "llm_build", "message": f"בניתי: {text}!"}

        # === שלב 3: פעולות עריכה (רק אם לא פקודת בנייה!) ===
        # צביעה
        if any(w in text_lower for w in COLOR_WORDS):
            if color:
                self.on_status(f"צובע ב-{color}")
                success = self.set_color(color)
                return {"success": success, "action": "color", "message": f"צבעתי ב-{color}!"}
            else:
                return {"success": False, "error": "לא הבנתי איזה צבע. אמור למשל: תצבע באדום"}

        # הגדלה - רק אם יש מילת פעולה ספציפית (לא סתם "גדול")
        if any(w in text_lower for w in RESIZE_BIGGER) and not is_build_command:
            self.on_status("מגדיל")
            success = self.make_bigger()
            return {"success": success, "action": "resize", "message": "הגדלתי פי 2!"}

        # הקטנה - רק אם יש מילת פעולה ספציפית (לא סתם "קטן")
        if any(w in text_lower for w in RESIZE_SMALLER) and not is_build_command:
            self.on_status("מקטין")
            success = self.make_smaller()
            return {"success": success, "action": "resize", "message": "הקטנתי לחצי!"}

        # מחיקה
        if any(w in text_lower for w in DELETE_WORDS):
            self.on_status("מוחק")
            success = self.delete_selected()
            return {"success": success, "action": "delete", "message": "מחקתי!"}

        # בחירת האחרון
        if any(w in text_lower for w in SELECT_WORDS):
            self.on_status("בוחר")
            success = self.select_last()
            return {"success": success, "action": "select", "message": "בחרתי!"}

        # לא מזוהה - נסה עם LLM!
        else:
            if self.llm_builder:
                self.on_status(f"משתמש ב-Claude לפקודה מורכבת: {text}")

                # בקש מ-Claude לייצר קוד Lua
                lua_code = self.llm_builder.generate_lua(text)

                if lua_code:
                    self.on_status(f"מריץ קוד מ-Claude...")
                    success = self._send_command(lua_code)
                    if success:
                        return {"success": True, "action": "llm_build", "message": f"בניתי: {text}!"}
                    else:
                        return {"success": False, "error": "נכשל בהרצת הקוד"}
                else:
                    return {"success": False, "error": "Claude לא הצליח לייצר קוד"}
            else:
                return {
                    "success": False,
                    "error": f"לא הבנתי את הפקודה: {text}",
                    "hint": "נסה: תוסיף קוביה, תצבע באדום, תגדיל, תמחק"
                }


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
