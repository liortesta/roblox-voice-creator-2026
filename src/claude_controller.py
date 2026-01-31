"""
Roblox Voice Creator - Claude Controller
=========================================
הלב של המערכת! משתמש ב-Claude Computer Use API לשליטה על Roblox Studio.
תומך ב-OpenRouter ו-Anthropic ישירות.

המודול הזה:
1. מקבל פקודות קוליות בעברית מהילד
2. מתרגם אותן לפעולות ב-Roblox Studio
3. משתמש ב-Computer Use לביצוע הפעולות
"""

import anthropic
import base64
import json
import re
import os
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
import time
import pyautogui


class UserInterventionDetector:
    """מזהה אם המשתמש נגע במחשב בזמן שהמערכת עובדת"""

    def __init__(self):
        self.last_mouse_pos = None
        self.intervention_detected = False
        self.monitoring = False

    def start_monitoring(self):
        """התחל לעקוב"""
        self.last_mouse_pos = pyautogui.position()
        self.intervention_detected = False
        self.monitoring = True

    def check_intervention(self) -> bool:
        """בדוק אם המשתמש זז את העכבר"""
        if not self.monitoring:
            return False

        current_pos = pyautogui.position()

        # אם העכבר זז והפונקציה לא הזיזה אותו
        if self.last_mouse_pos and current_pos != self.last_mouse_pos:
            # בדוק אם זה שינוי גדול (יותר מ-50 פיקסלים)
            distance = ((current_pos.x - self.last_mouse_pos.x)**2 +
                       (current_pos.y - self.last_mouse_pos.y)**2)**0.5

            if distance > 50:
                self.intervention_detected = True
                return True

        return False

    def update_position(self, x: int, y: int):
        """עדכן מיקום אחרי פעולה שלנו"""
        self.last_mouse_pos = type('Point', (), {'x': x, 'y': y})()

    def stop_monitoring(self):
        """עצור מעקב"""
        self.monitoring = False


class CommandType(Enum):
    """סוגי פקודות שהמערכת תומכת בהן"""
    CREATE_OBJECT = "create_object"      # יצירת אובייקט (קוביה, כדור, דמות)
    MODIFY_OBJECT = "modify_object"      # שינוי אובייקט (צבע, גודל)
    ADD_BEHAVIOR = "add_behavior"        # הוספת התנהגות (ריצה, קפיצה)
    DELETE_OBJECT = "delete_object"      # מחיקת אובייקט
    PLAY_TEST = "play_test"              # הרצת/עצירת משחק
    COMPLEX = "complex"                  # פקודה מורכבת


@dataclass
class ParsedCommand:
    """פקודה מפורשת"""
    original_text: str           # הטקסט המקורי
    command_type: CommandType    # סוג הפקודה
    action: str                  # הפעולה (למשל: "create", "color", "run")
    target: Optional[str]        # המטרה (למשל: "קוביה", "דמות")
    parameters: Dict[str, Any]   # פרמטרים נוספים (צבע, גודל, מהירות)
    confidence: float            # רמת ביטחון בפירוש (0-1)


class RobloxController:
    """
    Controller לשליטה על Roblox Studio באמצעות Claude Computer Use.

    השימוש:
    ```python
    controller = RobloxController(api_key="sk-...")
    result = await controller.execute_command("תוסיף קוביה כחולה גדולה")
    ```
    """

    # מיפוי צבעים עברית -> Roblox BrickColor
    COLORS_MAP = {
        "אדום": "Bright red",
        "כחול": "Bright blue",
        "ירוק": "Bright green",
        "צהוב": "Bright yellow",
        "כתום": "Neon orange",
        "סגול": "Bright violet",
        "ורוד": "Hot pink",
        "לבן": "White",
        "שחור": "Black",
        "חום": "Brown",
        "אפור": "Medium stone grey",
        "תכלת": "Cyan",
        "זהב": "Gold",
        "כסף": "Silver",
    }

    # מיפוי צורות עברית -> Roblox Part types
    SHAPES_MAP = {
        "קוביה": "Block",
        "כדור": "Ball",
        "גליל": "Cylinder",
        "טריז": "Wedge",
        "חלק": "Block",
    }

    # מיפוי גדלים עברית -> מכפילים
    SIZES_MAP = {
        "קטן": 0.5,
        "קטנה": 0.5,
        "בינוני": 1.0,
        "בינונית": 1.0,
        "גדול": 2.0,
        "גדולה": 2.0,
        "ענק": 4.0,
        "ענקית": 4.0,
        "ענקי": 4.0,
    }

    # מילות מפתח לזיהוי פקודות
    COMMAND_KEYWORDS = {
        "create": ["תוסיף", "צור", "תיצור", "תעשה", "בנה", "תבנה", "שים", "תשים"],
        "color": ["צבע", "תצבע", "לצבוע"],
        "resize": ["הגדל", "תגדיל", "הקטן", "תקטין", "שנה גודל"],
        "delete": ["מחק", "תמחק", "הסר", "תסיר"],
        "run": ["רוץ", "תרוץ", "ריצה", "לרוץ", "תעשה שירוץ", "שתרוץ", "תגרום לרוץ"],
        "jump": ["קפוץ", "קפיצה", "לקפוץ", "תעשה שיקפוץ", "שתקפוץ"],
        "play": ["הרץ", "תריץ", "שחק", "תשחק", "בדוק"],
        "stop": ["עצור", "תעצור", "הפסק", "תפסיק"],
    }

    # הגדרות Retry
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 2.0  # שניות

    # הגדרות הגבלות
    MAX_SCREENSHOTS = 10  # מקסימום צילומי מסך
    MAX_ACTIONS = 25      # מקסימום פעולות
    TIMEOUT_SECONDS = 60  # timeout בשניות
    ENABLE_INTERVENTION_DETECTION = False  # כבוי - רגיש מדי

    # הגדרות API
    ANTHROPIC_BASE_URL = "https://api.anthropic.com"
    DEFAULT_MODEL = "claude-sonnet-4-20250514"  # Sonnet 4 - תומך ב-Computer Use

    def __init__(
        self,
        api_key: str = None,
        on_status_update: Optional[Callable[[str], None]] = None,
        on_action: Optional[Callable[[str], None]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        model: str = None
    ):
        """
        אתחול ה-Controller.

        Args:
            api_key: מפתח Anthropic API
            on_status_update: callback לעדכוני סטטוס
            on_action: callback לפעולות שמתבצעות
            max_retries: מספר ניסיונות חוזרים בכישלון
            retry_delay: השהייה בין ניסיונות (שניות)
            model: שם המודל (ברירת מחדל: claude-sonnet-4-20250514)
        """
        self.model = model or os.getenv("CLAUDE_MODEL", self.DEFAULT_MODEL)

        # קבלת מפתח מסביבה אם לא סופק
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError("נדרש ANTHROPIC_API_KEY - הגדר בקובץ .env")

        self.api_key = api_key

        # אתחול Anthropic client ישיר
        self.client = anthropic.Anthropic(api_key=api_key)

        self.on_status_update = on_status_update or (lambda x: None)
        self.on_action = on_action or (lambda x: None)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_screenshot = None
        self.conversation_history = []
        self.failed_attempts = 0

        # גודל ומיקום חלון Roblox (יתעדכן בצילום)
        self.roblox_window_offset = (0, 0)
        self.roblox_window_size = (1920, 1080)  # ברירת מחדל
        self.roblox_window_is_maximized = False
        self._detect_roblox_window()

        # זיהוי התערבות משתמש
        self.intervention_detector = None

    def _detect_roblox_window(self):
        """זיהוי גודל ומיקום חלון Roblox Studio."""
        try:
            import pygetwindow as gw
            roblox_windows = gw.getWindowsWithTitle("Roblox Studio")
            if roblox_windows:
                window = roblox_windows[0]

                # תיקון: Windows מחזיר (-8, -8) לחלונות ממוקסמים!
                # במקרה כזה, הקואורדינטות מהתמונה כבר נכונות
                if window.left < 0 or window.top < 0:
                    # חלון ממוקסם - לא צריך offset
                    self.roblox_window_offset = (0, 0)
                    self.roblox_window_is_maximized = True
                    self.on_status_update(f"חלון Roblox ממוקסם - קואורדינטות ישירות!")
                else:
                    # חלון רגיל - צריך להוסיף offset
                    self.roblox_window_offset = (window.left, window.top)
                    self.roblox_window_is_maximized = False

                self.roblox_window_size = (window.width, window.height)
                self.on_status_update(f"מצאתי Roblox Studio: {window.width}x{window.height}")
        except Exception as e:
            self.on_status_update(f"לא הצלחתי לזהות חלון Roblox: {e}")

    def _make_api_call(
        self,
        messages: List[Dict],
        system: str,
        with_computer_use: bool = False
    ):
        """
        ביצוע קריאת API ישירה ל-Anthropic עם תמיכה ב-Computer Use.

        Args:
            messages: רשימת ההודעות
            system: ה-system prompt
            with_computer_use: האם להשתמש ב-Computer Use

        Returns:
            תשובת ה-API (כ-object עם content ו-stop_reason)
        """
        if with_computer_use:
            # עדכן גודל חלון Roblox לפני הקריאה
            self._detect_roblox_window()

            # שימוש ב-beta API עבור Computer Use (גרסת ינואר 2025)
            # גודל החלון מותאם לחלון Roblox Studio
            tools = [
                {
                    "type": "computer_20250124",
                    "name": "computer",
                    "display_width_px": self.roblox_window_size[0],
                    "display_height_px": self.roblox_window_size[1],
                    "display_number": 1,
                }
            ]

            # בגרסה 0.77.0+ משתמשים ב-beta.messages
            return self.client.beta.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                tools=tools,
                messages=messages,
                betas=["computer-use-2025-01-24"]
            )
        else:
            # קריאה רגילה ללא Computer Use
            return self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                messages=messages
            )

    def _build_system_prompt(self) -> str:
        """
        בניית System Prompt מקיף עם כל הידע על Roblox Studio.
        זה הלב של היכולת של Claude להבין ולבצע פקודות.
        """
        return """אתה עוזר מומחה לילדים ביצירת משחקי Roblox Studio.

## התפקיד שלך
אתה עוזר לילד בן 9 ליצור משחקים ב-Roblox Studio. הילד מדבר עברית פשוטה.
אתה צריך להבין מה הוא רוצה ולבצע את הפעולות ב-Roblox Studio באמצעות Computer Use.

## מבנה Roblox Studio
```
┌─────────────────────────────────────────────────────────┐
│  [Home] [Model] [Test] [View] [Plugins]   ← Ribbon     │
├─────────────┬───────────────────────┬───────────────────┤
│  Explorer   │   3D Viewport         │  Properties       │
│             │                       │                   │
│  Workspace  │   [העולם התלת-מימדי]  │  Name: Part       │
│  ├─ Camera  │                       │  Size: 4,1,2      │
│  ├─ Terrain │                       │  Color: ...       │
│  └─ Parts   │                       │  Material: ...    │
└─────────────┴───────────────────────┴───────────────────┘
```

### רכיבים עיקריים:
- **Explorer** (שמאל): עץ האובייקטים - Workspace מכיל את כל מה שנראה במשחק
- **Properties** (ימין): מאפיינים של האובייקט הנבחר
- **Viewport** (מרכז): העולם התלת-מימדי
- **Ribbon** (למעלה): כפתורי פעולות - Home, Model, Test

## איך לבצע פעולות נפוצות

### יצירת Part (קוביה/כדור/גליל):
1. לחץ על tab "Home" בריבון (למעלה)
2. מצא את כפתור "Part" (יש dropdown)
3. לחץ על החץ ליד Part לבחירת צורה: Block/Ball/Cylinder/Wedge
4. ה-Part נוצר ב-Workspace

### שינוי צבע:
1. בחר את האובייקט ב-Explorer או ב-Viewport (לחיצה עליו)
2. ב-Properties (ימין), מצא "BrickColor" או "Color"
3. לחץ ובחר צבע

### שינוי גודל:
1. בחר את האובייקט
2. ב-Properties, מצא "Size"
3. שנה את הערכים (X, Y, Z)

### יצירת דמות (Character):
1. לך ל-Home tab
2. מצא את כפתור "Model" או "Character"
3. או: View → Toolbox → חפש "Character" או "Rig"

### הוספת Script לריצה מהירה:
1. Right-click על הדמות (Character) ב-Explorer
2. Insert Object → Script
3. Double-click לפתיחה
4. כתוב:
```lua
local character = script.Parent
local humanoid = character:FindFirstChildOfClass("Humanoid")
if humanoid then
    humanoid.WalkSpeed = 50  -- מהירות (ברירת מחדל: 16)
end
```
5. Ctrl+S לשמירה

### הוספת קפיצה גבוהה:
```lua
local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
if humanoid then
    humanoid.JumpPower = 100  -- כוח קפיצה (ברירת מחדל: 50)
end
```

### הרצת המשחק לבדיקה:
1. לחץ על כפתור "Play" (משולש ירוק) או F5
2. לעצירה: לחץ "Stop" או F5 שוב

## מיפוי צבעים
- אדום = "Bright red"
- כחול = "Bright blue"
- ירוק = "Bright green"
- צהוב = "Bright yellow"
- כתום = "Neon orange"
- סגול = "Bright violet"
- ורוד = "Hot pink"
- לבן = "White"
- שחור = "Black"
- חום = "Brown"

## כללים חשובים
1. **תמיד תסביר** - לפני כל פעולה, הסבר לילד מה אתה עושה
2. **פעולות קטנות** - עדיף הרבה פעולות קטנות מאשר פעולה מורכבת אחת
3. **אימות** - אחרי כל פעולה, צלם מסך ווודא שהיא הצליחה
4. **שגיאות** - אם משהו לא עובד, נסה דרך אחרת
5. **עברית פשוטה** - דבר בעברית פשוטה שילד בן 9 יבין

## דוגמאות לפקודות וביצוע

### "תוסיף קוביה כחולה"
1. Home tab → Part → Block
2. בחר את ה-Part החדש
3. Properties → BrickColor → Bright blue

### "תעשה שהדמות תרוץ מהר"
1. מצא את הדמות ב-Explorer (מחפש Humanoid)
2. Right-click → Insert Object → Script
3. כתוב קוד WalkSpeed = 50
4. שמור

### "תגדיל את הקוביה"
1. בחר את הקוביה
2. Properties → Size
3. הכפל כל ערך פי 2

## זכור!
- הילד לא מכיר מונחים טכניים
- הסבר בשפה פשוטה
- תן פידבק חיובי ("יופי! הקוביה הכחולה נוצרה!")
- אם לא הבנת, שאל שאלה פשוטה

## חובה לאמת! אסור להזות!
אחרי כל פעולה חשובה - חובה לצלם screenshot ולבדוק שהפעולה הצליחה!

❌ לא נכון:
1. לחיצה על Part
2. "אני מניח שקוביה נוצרה" - אסור!

✅ נכון:
1. לחיצה על Part
2. screenshot מיד!
3. בדיקה: "אני רואה קוביה חדשה ב-Workspace או ב-Viewport?" - כן/לא
4. אם לא רואה - הפעולה נכשלה! נסה שוב במקום אחר!

פעולות שדורשות אימות מיידי:
- לחיצה על Part → screenshot → "רואה קוביה חדשה?"
- שינוי צבע → screenshot → "הצבע השתנה?"
- בחירת אובייקט → screenshot → "רואה סימון כחול?"

אם לא רואה שינוי - הפעולה נכשלה! אל תמשיך הלאה! נסה שוב!

## הגבלות חשובות!
- אל תצלם יותר מ-10 screenshots - חסוך!
- אחרי כל לחיצה - חכה רגע לראות מה קרה
- אם משהו לא עבד אחרי 3 ניסיונות - תסביר לילד מה לעשות ידנית
- עבוד מהר ויעיל - הילד מחכה!
- כפתור Part נמצא בדרך כלל בריבון למעלה - חפש אותו!

## צבעים נפוצים ב-Properties > BrickColor:
- "Bright red", "Bright blue", "Bright green", "Bright yellow"
- "Neon orange", "Bright violet", "Hot pink"
"""

    def _parse_command(self, text: str) -> ParsedCommand:
        """
        פירוש פקודה קולית לאובייקט ParsedCommand.

        Args:
            text: הטקסט המקורי מהילד

        Returns:
            ParsedCommand עם כל הפרטים המפורשים
        """
        text_lower = text.lower()

        # זיהוי סוג הפקודה
        command_type = CommandType.COMPLEX
        action = "unknown"
        target = None
        parameters = {}
        confidence = 0.5

        # בדיקת יצירה
        for keyword in self.COMMAND_KEYWORDS["create"]:
            if keyword in text_lower:
                command_type = CommandType.CREATE_OBJECT
                action = "create"
                confidence = 0.8
                break

        # בדיקת צביעה
        for keyword in self.COMMAND_KEYWORDS["color"]:
            if keyword in text_lower:
                command_type = CommandType.MODIFY_OBJECT
                action = "color"
                confidence = 0.8
                break

        # בדיקת שינוי גודל
        for keyword in self.COMMAND_KEYWORDS["resize"]:
            if keyword in text_lower:
                command_type = CommandType.MODIFY_OBJECT
                action = "resize"
                confidence = 0.8
                break

        # בדיקת מחיקה
        for keyword in self.COMMAND_KEYWORDS["delete"]:
            if keyword in text_lower:
                command_type = CommandType.DELETE_OBJECT
                action = "delete"
                confidence = 0.8
                break

        # בדיקת ריצה/קפיצה
        for keyword in self.COMMAND_KEYWORDS["run"]:
            if keyword in text_lower:
                command_type = CommandType.ADD_BEHAVIOR
                action = "run"
                confidence = 0.8
                break

        for keyword in self.COMMAND_KEYWORDS["jump"]:
            if keyword in text_lower:
                command_type = CommandType.ADD_BEHAVIOR
                action = "jump"
                confidence = 0.8
                break

        # בדיקת הרצה/עצירה
        for keyword in self.COMMAND_KEYWORDS["play"]:
            if keyword in text_lower:
                command_type = CommandType.PLAY_TEST
                action = "play"
                confidence = 0.9
                break

        for keyword in self.COMMAND_KEYWORDS["stop"]:
            if keyword in text_lower:
                command_type = CommandType.PLAY_TEST
                action = "stop"
                confidence = 0.9
                break

        # זיהוי צורה
        for shape_heb, shape_eng in self.SHAPES_MAP.items():
            if shape_heb in text_lower:
                target = shape_eng
                parameters["shape"] = shape_eng
                break

        # זיהוי "דמות"
        if "דמות" in text_lower or "שחקן" in text_lower or "אדם" in text_lower:
            target = "Character"
            parameters["is_character"] = True

        # זיהוי צבע
        for color_heb, color_eng in self.COLORS_MAP.items():
            if color_heb in text_lower:
                parameters["color"] = color_eng
                break

        # זיהוי גודל
        for size_heb, size_mult in self.SIZES_MAP.items():
            if size_heb in text_lower:
                parameters["size_multiplier"] = size_mult
                break

        return ParsedCommand(
            original_text=text,
            command_type=command_type,
            action=action,
            target=target,
            parameters=parameters,
            confidence=confidence
        )

    def _build_action_prompt(self, parsed: ParsedCommand) -> str:
        """
        בניית prompt ספציפי לפעולה על בסיס הפקודה המפורשת.
        """
        prompts = {
            "create": f"""הילד ביקש ליצור {parsed.target or 'אובייקט'}.
{'צבע: ' + parsed.parameters.get('color', '') if 'color' in parsed.parameters else ''}
{'גודל: ' + str(parsed.parameters.get('size_multiplier', 1)) if 'size_multiplier' in parsed.parameters else ''}

בצע את הפעולות הבאות:
1. צלם מסך לראות את המצב הנוכחי
2. נווט ל-Home tab
3. לחץ על Part ובחר את הצורה המתאימה
4. אם יש צבע - שנה ב-Properties
5. אם יש גודל - שנה ב-Properties
6. צלם מסך לאימות""",

            "color": f"""הילד ביקש לצבוע ב{parsed.parameters.get('color', 'צבע לא ידוע')}.

בצע:
1. צלם מסך
2. בחר את האובייקט הנוכחי (או האחרון שנוצר)
3. ב-Properties, מצא BrickColor
4. שנה ל-{parsed.parameters.get('color', '')}
5. צלם מסך לאימות""",

            "resize": f"""הילד ביקש לשנות גודל.
מכפיל: {parsed.parameters.get('size_multiplier', 2)}

בצע:
1. צלם מסך
2. בחר את האובייקט
3. ב-Properties → Size
4. הכפל כל ערך ב-{parsed.parameters.get('size_multiplier', 2)}
5. צלם מסך לאימות""",

            "run": """הילד ביקש שהדמות תרוץ מהר.

בצע:
1. צלם מסך
2. מצא את הדמות ב-Explorer (חפש Humanoid)
3. Right-click → Insert Object → Script
4. כתוב:
   local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
   if humanoid then humanoid.WalkSpeed = 50 end
5. Ctrl+S לשמירה
6. צלם מסך לאימות""",

            "jump": """הילד ביקש קפיצה גבוהה.

בצע:
1. צלם מסך
2. מצא את הדמות ב-Explorer
3. Right-click → Insert Object → Script (אם אין)
4. הוסף:
   local humanoid = script.Parent:FindFirstChildOfClass("Humanoid")
   if humanoid then humanoid.JumpPower = 100 end
5. Ctrl+S לשמירה
6. צלם מסך לאימות""",

            "play": """הילד ביקש להריץ את המשחק.

בצע:
1. לחץ על כפתור Play (משולש ירוק) למעלה, או F5
2. חכה שהמשחק ייטען
3. צלם מסך להראות שהמשחק רץ""",

            "stop": """הילד ביקש לעצור את המשחק.

בצע:
1. לחץ על כפתור Stop (ריבוע אדום) או F5
2. צלם מסך לאימות""",

            "delete": """הילד ביקש למחוק אובייקט.

בצע:
1. צלם מסך
2. בחר את האובייקט ב-Explorer או Viewport
3. לחץ Delete או Right-click → Delete
4. צלם מסך לאימות""",
        }

        return prompts.get(parsed.action, f"""הילד אמר: "{parsed.original_text}"

נסה להבין מה הוא רוצה ובצע את הפעולה המתאימה ב-Roblox Studio.
1. צלם מסך לראות את המצב
2. בצע את הפעולה
3. צלם מסך לאימות
4. הסבר לילד מה עשית""")

    def _focus_roblox_studio(self) -> bool:
        """מיקוד חלון Roblox Studio."""
        try:
            import pygetwindow as gw
            roblox_windows = gw.getWindowsWithTitle("Roblox Studio")
            if roblox_windows:
                roblox_windows[0].activate()
                time.sleep(0.5)
                self.on_status_update("מיקדתי את Roblox Studio")
                return True
            else:
                self.on_status_update("לא מצאתי חלון Roblox Studio פתוח")
                return False
        except ImportError:
            self.on_status_update("pygetwindow לא מותקן - ממשיך בלי מיקוד חלון")
            return True
        except Exception as e:
            self.on_status_update(f"לא הצלחתי למקד Roblox Studio: {e}")
            return True  # ממשיכים בכל מקרה

    def _ensure_roblox_focused(self) -> bool:
        """ודא שRoblox Studio במוקד לפני פעולה."""
        try:
            import pygetwindow as gw
            roblox_windows = gw.getWindowsWithTitle("Roblox Studio")
            if not roblox_windows:
                self.on_status_update("Roblox Studio נסגר או לא נמצא!")
                return False

            window = roblox_windows[0]

            # בדוק אם הוא החלון הפעיל
            try:
                active_window = gw.getActiveWindow()
                if active_window and "Roblox Studio" not in active_window.title:
                    self.on_status_update("Roblox לא במוקד - מחזיר פוקוס...")
                    window.activate()
                    time.sleep(0.3)
            except:
                pass

            return True

        except Exception as e:
            self.on_status_update(f"בעיה עם Roblox: {e}")
            return True  # ממשיכים בכל מקרה

    async def execute_command(self, voice_text: str) -> Dict[str, Any]:
        """
        ביצוע פקודה קולית ב-Roblox Studio עם retry logic.

        Args:
            voice_text: הטקסט שזוהה מהקול

        Returns:
            dict עם תוצאות הביצוע
        """
        self.on_status_update(f"מבין את הפקודה: {voice_text}")

        # נקה היסטוריית שיחה - מתחילים מחדש כל פקודה!
        # זה מונע שגיאות של tool_use ללא tool_result מפקודות קודמות
        self.conversation_history = []

        # מיקוד חלון Roblox Studio
        self._focus_roblox_studio()

        # הדפס מיקום חלון Roblox
        self._detect_roblox_window()
        self.on_status_update(f"📍 חלון Roblox: מיקום ({self.roblox_window_offset[0]}, {self.roblox_window_offset[1]}), גודל {self.roblox_window_size[0]}x{self.roblox_window_size[1]}")

        # פירוש הפקודה
        parsed = self._parse_command(voice_text)
        self.on_status_update(f"זיהיתי: {parsed.action} - {parsed.target or 'כללי'}")

        # ניסיונות חוזרים
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await self._execute_single_attempt(voice_text, parsed, attempt)
                if result["success"]:
                    self.failed_attempts = 0  # איפוס מונה כישלונות
                    return result
                else:
                    last_error = result.get("error", "שגיאה לא ידועה")
                    if attempt < self.max_retries:
                        self.on_status_update(f"נכשל, מנסה שוב ({attempt}/{self.max_retries})...")
                        time.sleep(self.retry_delay)
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    self.on_status_update(f"שגיאה: {e}, מנסה שוב ({attempt}/{self.max_retries})...")
                    time.sleep(self.retry_delay)

        # כל הניסיונות נכשלו
        self.failed_attempts += 1
        self.on_status_update(f"נכשל אחרי {self.max_retries} ניסיונות")
        return {
            "success": False,
            "error": last_error,
            "parsed_command": parsed,
            "attempts": self.max_retries
        }

    async def _execute_single_attempt(
        self,
        voice_text: str,
        parsed: ParsedCommand,
        attempt: int
    ) -> Dict[str, Any]:
        """
        ניסיון בודד לביצוע פקודה.

        Args:
            voice_text: הטקסט המקורי
            parsed: הפקודה המפורשת
            attempt: מספר הניסיון

        Returns:
            dict עם תוצאות הביצוע
        """
        # בניית ה-prompt
        action_prompt = self._build_action_prompt(parsed)

        # הוספת הקשר לניסיון חוזר
        retry_context = ""
        if attempt > 1:
            retry_context = f"\n\n⚠️ זה ניסיון {attempt}. הניסיון הקודם נכשל. נסה גישה אחרת או בדוק שהמסך נכון."

        # הוספה להיסטוריה
        self.conversation_history.append({
            "role": "user",
            "content": f"הילד אמר: \"{voice_text}\"\n\n{action_prompt}{retry_context}"
        })

        self.on_status_update("שולח ל-Claude...")

        # קריאה ל-Claude עם Computer Use
        response = self._make_api_call(
            messages=self.conversation_history,
            system=self._build_system_prompt(),
            with_computer_use=True
        )

        # עיבוד התשובה
        result = self._process_response(response)
        tool_execution_failed = False

        # מונים והגבלות
        total_actions = 0
        screenshot_count = 0
        start_time = time.time()
        user_intervention = False

        # זיהוי התערבות משתמש (כבוי כברירת מחדל - רגיש מדי)
        self.intervention_detector = UserInterventionDetector()
        if self.ENABLE_INTERVENTION_DETECTION:
            self.intervention_detector.start_monitoring()

        # טיפול ב-tool_use (אם Claude רוצה לבצע פעולות)
        while response.stop_reason == "tool_use":
            tool_results = []

            # בדיקת timeout (נמשיך לאסוף tool_results אבל לא נבצע)
            elapsed = time.time() - start_time
            timeout_reached = elapsed > self.TIMEOUT_SECONDS
            if timeout_reached:
                self.on_status_update(f"חלפו {self.TIMEOUT_SECONDS} שניות!")

            # בדיקת התערבות משתמש (רק אם מופעל)
            if self.ENABLE_INTERVENTION_DETECTION and self.intervention_detector.check_intervention():
                self.on_status_update("=" * 50)
                self.on_status_update("זיהיתי שנגעת במחשב! עוצר...")
                self.on_status_update("אל תזיז עכבר בזמן שאני עובד!")
                self.on_status_update("=" * 50)
                user_intervention = True
                # לא עוצרים לגמרי - צריך להחזיר tool_results!
                # break

            # הצג מה Claude חושב (טקסט)
            for block in response.content:
                if hasattr(block, 'text') and block.text:
                    thought = block.text[:150] + ('...' if len(block.text) > 150 else '')
                    self.on_status_update(f"Claude חושב: {thought}")

            # דגל לעצירה מוקדמת (אבל עדיין נחזיר tool_results!)
            should_stop = False

            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    total_actions += 1
                    action_name = block.input.get('action', 'פעולה') if hasattr(block, 'input') else 'פעולה'

                    # בדוק אם צריך לעצור (אבל עדיין שולחים tool_result!)
                    if total_actions > self.MAX_ACTIONS:
                        self.on_status_update(f"הגעתי למקסימום {self.MAX_ACTIONS} פעולות")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Maximum actions reached - stopping"
                        })
                        should_stop = True
                        continue  # לא break! ממשיך לאסוף tool_results

                    # אם כבר צריך לעצור - רק שלח cancelled
                    if should_stop or user_intervention:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Action cancelled"
                        })
                        continue

                    # בדיקת הגבלת screenshots
                    if action_name == 'screenshot':
                        screenshot_count += 1
                        if screenshot_count > self.MAX_SCREENSHOTS:
                            self.on_status_update(f"הגעתי ל-{self.MAX_SCREENSHOTS} screenshots, מדלג!")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Screenshot limit reached - please proceed without additional screenshots"
                            })
                            continue

                    # ודא ש-Roblox במוקד לפני פעולות עכבר
                    if action_name in ['left_click', 'right_click', 'double_click', 'mouse_move']:
                        if not self._ensure_roblox_focused():
                            self.on_status_update("Roblox לא זמין!")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Roblox Studio not available"
                            })
                            should_stop = True
                            continue

                    self.on_action(f"מבצע [{total_actions}/{self.MAX_ACTIONS}]: {action_name}")

                    try:
                        tool_result = await self._execute_tool_with_verification(block)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result["content"]
                        })
                        if not tool_result.get("success", True):
                            tool_execution_failed = True
                    except Exception as e:
                        tool_execution_failed = True
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"שגיאה: {str(e)}",
                            "is_error": True
                        })

            # תמיד שלח את tool_results ל-Claude (חובה!)
            # אחרת יהיה error: "tool_use without tool_result"
            self.conversation_history.append({
                "role": "assistant",
                "content": self._serialize_content(response.content)
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            # עכשיו בדוק אם צריך לעצור
            if should_stop or total_actions > self.MAX_ACTIONS:
                self.on_status_update("עוצר - הגעתי למגבלה")
                break
            if time.time() - start_time > self.TIMEOUT_SECONDS:
                self.on_status_update(f"עוצר - עבר timeout של {self.TIMEOUT_SECONDS} שניות")
                break

            # רק אם ממשיכים - קריאה נוספת ל-API
            response = self._make_api_call(
                messages=self.conversation_history,
                system=self._build_system_prompt(),
                with_computer_use=True
            )
            result = self._process_response(response)

        # עצור את זיהוי ההתערבות
        if self.intervention_detector:
            self.intervention_detector.stop_monitoring()

        # סיכום הפעולות
        elapsed_time = time.time() - start_time
        stop_reason = "הושלם"
        if user_intervention:
            stop_reason = "התערבות משתמש"
        elif elapsed_time > self.TIMEOUT_SECONDS:
            stop_reason = "Timeout"
        elif total_actions > self.MAX_ACTIONS:
            stop_reason = "מקסימום פעולות"

        self.on_status_update("=" * 50)
        self.on_status_update(f"סיכום ביצוע:")
        self.on_status_update(f"  פעולות: {total_actions}/{self.MAX_ACTIONS}")
        self.on_status_update(f"  Screenshots: {screenshot_count}/{self.MAX_SCREENSHOTS}")
        self.on_status_update(f"  זמן: {elapsed_time:.1f} שניות")
        self.on_status_update(f"  סיבת עצירה: {stop_reason}")
        if user_intervention:
            self.on_status_update("  בפעם הבאה - אל תגע במחשב בזמן שאני עובד!")
        self.on_status_update("=" * 50)

        # שמירת התשובה האחרונה
        self.conversation_history.append({
            "role": "assistant",
            "content": self._serialize_content(response.content)
        })

        # בדיקת הצלחה
        if tool_execution_failed or user_intervention:
            return {
                "success": False,
                "error": "התערבות משתמש" if user_intervention else "חלק מהפעולות נכשלו",
                "parsed_command": parsed,
                "response": result
            }

        self.on_status_update("הפעולה הושלמה!")

        return {
            "success": True,
            "parsed_command": parsed,
            "response": result,
            "message": result.get("text", "הפעולה בוצעה בהצלחה!")
        }

    async def _execute_tool_with_verification(self, tool_block) -> Dict[str, Any]:
        """
        ביצוע פעולת כלי עם אימות.

        Args:
            tool_block: הבלוק עם פרטי הכלי מ-Claude

        Returns:
            dict עם התוכן והאם הצליח
        """
        action = tool_block.input.get("action")
        content = await self._execute_tool(tool_block)

        # אימות בסיסי - אם זה screenshot, בדוק שיש תוכן
        if action == "screenshot":
            if isinstance(content, list) and len(content) > 0:
                return {"content": content, "success": True}
            else:
                return {"content": "נכשל לצלם מסך", "success": False}

        # לפעולות אחרות, נניח הצלחה אם לא הייתה שגיאה
        return {"content": content, "success": True}

    async def _execute_tool(self, tool_block) -> str:
        """
        ביצוע פעולת כלי (Computer Use).

        Args:
            tool_block: הבלוק עם פרטי הכלי מ-Claude

        Returns:
            תוצאת הפעולה (בדרך כלל screenshot)
        """
        import pyautogui
        action = tool_block.input.get("action")

        if action == "screenshot":
            # צילום מסך
            self.on_status_update("מצלם מסך...")
            screenshot = await self._take_screenshot()
            time.sleep(0.3)
            return [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": screenshot}}]

        elif action == "mouse_move":
            # קואורדינטות מClaude הן יחסיות לחלון - המר למסך
            window_x = tool_block.input.get("coordinate", [0, 0])[0]
            window_y = tool_block.input.get("coordinate", [0, 0])[1]
            screen_x = window_x + self.roblox_window_offset[0]
            screen_y = window_y + self.roblox_window_offset[1]
            self.on_status_update(f"מזיז עכבר ל: ({window_x}, {window_y}) בחלון -> ({screen_x}, {screen_y}) במסך")
            await self._mouse_move(screen_x, screen_y)
            # עדכן את detector כדי שיידע שזה אנחנו שהזזנו
            if self.intervention_detector:
                self.intervention_detector.update_position(screen_x, screen_y)
            time.sleep(0.3)
            return f"Mouse moved to ({screen_x}, {screen_y})"

        elif action == "left_click":
            # בדוק אם יש coordinate מ-Claude
            coord = tool_block.input.get("coordinate")
            if coord:
                window_x, window_y = coord[0], coord[1]
                screen_x = window_x + self.roblox_window_offset[0]
                screen_y = window_y + self.roblox_window_offset[1]
                self.on_status_update(f"לוחץ: ({window_x}, {window_y}) בחלון -> ({screen_x}, {screen_y}) במסך")
                pyautogui.click(screen_x, screen_y)
                if self.intervention_detector:
                    self.intervention_detector.update_position(screen_x, screen_y)
            else:
                current_pos = pyautogui.position()
                self.on_status_update(f"לוחץ במיקום נוכחי: ({current_pos.x}, {current_pos.y})")
                pyautogui.click()
                if self.intervention_detector:
                    self.intervention_detector.update_position(current_pos.x, current_pos.y)
            time.sleep(0.5)
            return f"Clicked"

        elif action == "right_click":
            # בדוק אם יש coordinate מ-Claude
            coord = tool_block.input.get("coordinate")
            if coord:
                window_x, window_y = coord[0], coord[1]
                screen_x = window_x + self.roblox_window_offset[0]
                screen_y = window_y + self.roblox_window_offset[1]
                self.on_status_update(f"לחיצה ימנית: ({window_x}, {window_y}) בחלון -> ({screen_x}, {screen_y}) במסך")
                pyautogui.rightClick(screen_x, screen_y)
            else:
                current_pos = pyautogui.position()
                self.on_status_update(f"לחיצה ימנית במיקום נוכחי: ({current_pos.x}, {current_pos.y})")
                pyautogui.rightClick()
            time.sleep(0.5)
            return f"Right clicked"

        elif action == "double_click":
            # בדוק אם יש coordinate מ-Claude
            coord = tool_block.input.get("coordinate")
            if coord:
                window_x, window_y = coord[0], coord[1]
                screen_x = window_x + self.roblox_window_offset[0]
                screen_y = window_y + self.roblox_window_offset[1]
                self.on_status_update(f"לחיצה כפולה: ({window_x}, {window_y}) בחלון -> ({screen_x}, {screen_y}) במסך")
                pyautogui.doubleClick(screen_x, screen_y)
            else:
                current_pos = pyautogui.position()
                self.on_status_update(f"לחיצה כפולה במיקום נוכחי: ({current_pos.x}, {current_pos.y})")
                pyautogui.doubleClick()
            time.sleep(0.5)
            return f"Double clicked"

        elif action == "type":
            text = tool_block.input.get("text", "")
            self.on_status_update(f"מקליד: {text[:30]}{'...' if len(text) > 30 else ''}")
            await self._type_text(text)
            time.sleep(0.3)
            return f"Typed: {text}"

        elif action == "key":
            key = tool_block.input.get("key", "")
            self.on_status_update(f"לוחץ מקש: {key}")
            await self._press_key(key)
            time.sleep(0.3)
            return f"Pressed: {key}"

        elif action == "wait":
            # Claude ביקש לחכות
            wait_ms = tool_block.input.get("duration", 1000)
            wait_sec = wait_ms / 1000
            self.on_status_update(f"מחכה {wait_sec} שניות...")
            time.sleep(wait_sec)
            return f"Waited {wait_sec} seconds"

        elif action == "scroll":
            # גלילה
            coord = tool_block.input.get("coordinate", [0, 0])
            direction = tool_block.input.get("direction", "down")
            amount = tool_block.input.get("amount", 3)
            screen_x = coord[0] + self.roblox_window_offset[0]
            screen_y = coord[1] + self.roblox_window_offset[1]
            pyautogui.moveTo(screen_x, screen_y)
            clicks = amount if direction == "down" else -amount
            pyautogui.scroll(clicks)
            self.on_status_update(f"גלילה {direction} ב-({screen_x}, {screen_y})")
            time.sleep(0.3)
            return f"Scrolled {direction}"

        elif action == "drag":
            # גרירה
            start = tool_block.input.get("start_coordinate", [0, 0])
            end = tool_block.input.get("end_coordinate", [0, 0])
            start_x = start[0] + self.roblox_window_offset[0]
            start_y = start[1] + self.roblox_window_offset[1]
            end_x = end[0] + self.roblox_window_offset[0]
            end_y = end[1] + self.roblox_window_offset[1]
            self.on_status_update(f"גורר מ-({start_x}, {start_y}) ל-({end_x}, {end_y})")
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=0.5)
            time.sleep(0.3)
            return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"

        return "Action completed"

    async def _take_screenshot(self) -> str:
        """צילום רק של חלון Roblox Studio והחזרה כ-base64."""
        try:
            import pygetwindow as gw
            from PIL import ImageGrab
            import io

            # מצא את חלון Roblox Studio
            roblox_windows = gw.getWindowsWithTitle("Roblox Studio")

            if not roblox_windows:
                self.on_status_update("לא מצאתי חלון Roblox Studio - מצלם מסך מלא")
                screenshot = ImageGrab.grab()
            else:
                # קבל את החלון הראשון
                window = roblox_windows[0]

                # ודא שהחלון לא ממוזער
                if window.isMinimized:
                    window.restore()
                    time.sleep(0.5)

                # הפוך לחלון פעיל
                try:
                    window.activate()
                    time.sleep(0.3)
                except:
                    pass

                # צלם רק את החלון הזה!
                bbox = (window.left, window.top, window.right, window.bottom)
                screenshot = ImageGrab.grab(bbox=bbox)

                # עדכן את גודל המסך לקואורדינטות נכונות
                self.roblox_window_offset = (window.left, window.top)
                self.roblox_window_size = (window.width, window.height)

                self.on_status_update(f"צילמתי חלון Roblox: {window.width}x{window.height}")

            # המר ל-base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)

            self.last_screenshot = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return self.last_screenshot

        except Exception as e:
            self.on_status_update(f"שגיאה בצילום: {e}")
            # fallback - צלם הכל עם pyautogui
            try:
                import pyautogui
                import io
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                buffer.seek(0)
                self.last_screenshot = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return self.last_screenshot
            except:
                return ""

    async def _mouse_move(self, x: int, y: int):
        """הזזת העכבר למיקום."""
        try:
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)
        except ImportError:
            pass

    async def _mouse_click(self, button: str = "left", double: bool = False):
        """לחיצת עכבר."""
        try:
            import pyautogui
            if double:
                pyautogui.doubleClick()
            else:
                pyautogui.click(button=button)
        except ImportError:
            pass

    async def _type_text(self, text: str):
        """הקלדת טקסט."""
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.05)
        except ImportError:
            pass

    async def _press_key(self, key: str):
        """לחיצה על מקש."""
        try:
            import pyautogui
            pyautogui.press(key)
        except ImportError:
            pass

    def _serialize_content_block(self, block) -> Dict[str, Any]:
        """
        סריאליזציה של בלוק תוכן מ-Claude לפורמט JSON-friendly.

        Args:
            block: בלוק תוכן (TextBlock או ToolUseBlock)

        Returns:
            dict שניתן לשלוח ב-API
        """
        try:
            if hasattr(block, 'text'):
                return {"type": "text", "text": block.text}
            elif hasattr(block, 'type') and block.type == "tool_use":
                return {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                }
            elif hasattr(block, 'model_dump'):
                # Pydantic v2 - שימוש ב-model_dump
                return block.model_dump()
            elif hasattr(block, 'dict'):
                # Pydantic v1 fallback
                return block.dict()
            else:
                # Fallback - נסה להמיר ל-dict
                return dict(block) if hasattr(block, '__iter__') else {"type": "unknown", "data": str(block)}
        except Exception as e:
            # אם הכל נכשל, החזר טקסט פשוט
            return {"type": "text", "text": f"[Error serializing block: {e}]"}

    def _serialize_content(self, content) -> List[Dict[str, Any]]:
        """
        סריאליזציה של כל התוכן מתשובת Claude.

        Args:
            content: רשימת בלוקים מ-response.content

        Returns:
            רשימת dicts לשימוש ב-API
        """
        serialized = []
        for block in content:
            serialized.append(self._serialize_content_block(block))
        return serialized

    def _process_response(self, response) -> Dict[str, Any]:
        """עיבוד תשובת Claude."""
        result = {"text": "", "actions": []}

        try:
            for block in response.content:
                try:
                    if hasattr(block, 'text'):
                        result["text"] += block.text
                    elif hasattr(block, 'type') and block.type == "tool_use":
                        # גישה בטוחה לשדות
                        action = None
                        if hasattr(block, 'input') and isinstance(block.input, dict):
                            action = block.input.get("action")

                        result["actions"].append({
                            "tool": getattr(block, 'name', 'unknown'),
                            "action": action,
                            "details": getattr(block, 'input', {})
                        })
                except Exception as block_error:
                    # לוג של שגיאה בבלוק בודד, ממשיכים לשאר
                    print(f"Warning: Error processing block: {block_error}")
                    continue
        except Exception as e:
            print(f"Warning: Error processing response: {e}")
            result["text"] = f"[Error processing response: {e}]"

        return result

    def get_supported_commands(self) -> List[Dict[str, str]]:
        """
        החזרת רשימת כל הפקודות הנתמכות.
        שימושי להצגה בממשק.
        """
        return [
            # רמה 1 - בסיסי
            {"level": 1, "command": "תוסיף קוביה", "description": "יוצר קוביה חדשה"},
            {"level": 1, "command": "תוסיף כדור", "description": "יוצר כדור חדש"},
            {"level": 1, "command": "תוסיף גליל", "description": "יוצר גליל חדש"},
            {"level": 1, "command": "תוסיף דמות", "description": "יוצר דמות שחקן"},
            {"level": 1, "command": "תצבע באדום/כחול/ירוק...", "description": "צובע את האובייקט"},
            {"level": 1, "command": "תמחק", "description": "מוחק את האובייקט הנבחר"},

            # רמה 2 - בינוני
            {"level": 2, "command": "תוסיף קוביה כחולה", "description": "קוביה עם צבע"},
            {"level": 2, "command": "תגדיל את הקוביה", "description": "מגדיל אובייקט פי 2"},
            {"level": 2, "command": "תקטין את הכדור", "description": "מקטין אובייקט"},
            {"level": 2, "command": "תעשה שהדמות תרוץ", "description": "מוסיף ריצה מהירה"},
            {"level": 2, "command": "תוסיף קפיצה גבוהה", "description": "מוסיף קפיצה חזקה"},
            {"level": 2, "command": "תריץ את המשחק", "description": "מפעיל את המשחק לבדיקה"},
            {"level": 2, "command": "תעצור את המשחק", "description": "עוצר את הבדיקה"},

            # רמה 3 - מתקדם
            {"level": 3, "command": "תוסיף קוביה כחולה גדולה", "description": "קוביה עם צבע וגודל"},
            {"level": 3, "command": "תבנה בית", "description": "בונה מבנה פשוט"},
            {"level": 3, "command": "תעשה דמות שרצה ומקפצת", "description": "דמות עם כל היכולות"},
        ]


# שימוש לדוגמה
if __name__ == "__main__":
    import asyncio
    import os

    async def main():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("נא להגדיר ANTHROPIC_API_KEY")
            return

        controller = RobloxController(
            api_key=api_key,
            on_status_update=lambda s: print(f"[STATUS] {s}"),
            on_action=lambda a: print(f"[ACTION] {a}")
        )

        # בדיקת פירוש פקודות
        test_commands = [
            "תוסיף קוביה כחולה גדולה",
            "תעשה שהדמות תרוץ מהר",
            "תצבע באדום",
            "תגדיל את הכדור",
        ]

        for cmd in test_commands:
            parsed = controller._parse_command(cmd)
            print(f"\nפקודה: {cmd}")
            print(f"  סוג: {parsed.command_type}")
            print(f"  פעולה: {parsed.action}")
            print(f"  מטרה: {parsed.target}")
            print(f"  פרמטרים: {parsed.parameters}")

    asyncio.run(main())
