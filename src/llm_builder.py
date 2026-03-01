"""
LLM Builder - מייצר קוד Lua חכם מפקודות קוליות
================================================
משתמש ב-Claude כדי להבין פקודות מורכבות בעברית
ולייצר קוד Lua שבונה אובייקטים ב-Roblox Studio.
"""

import os
import re
import anthropic
import requests
from typing import Optional


class LLMBuilder:
    """מייצר קוד Lua מפקודות בשפה טבעית."""

    SYSTEM_PROMPT = """אתה אמן ובונה מקצועי ב-Roblox Studio. אתה יוצר כמו בן אדם יצירתי!

## חוקים מוחלטים:
1. תחזיר אך ורק קוד Lua - אף פעם לא טקסט!
2. תמיד התחל עם: local parts = {}
3. בסוף: game.Selection:Set(parts)

## אתה חושב כמו אמן:
- תוסיף פרטים קטנים שעושים את ההבדל (ידיות לדלתות, חלונות לבתים, גלגלים לרכבים)
- תשתמש בפרופורציות נכונות ויפות
- תוסיף עומק וממד - לא רק קופסאות שטוחות
- תשתמש ב-Materials כמו Brick, Wood, Metal, Grass, SmoothPlastic
- תשתמש בצבעים הגיוניים (עצים = חום+ירוק, בתים = צבעים חמים)
- תוסיף צללים ושכבות (למשל: מסגרת לחלון, אדן לגג)

## כללי פיזיקה:
- מבנים = Anchored = true
- רכבים = Anchored = false עם VehicleSeat
- אובייקטים נופלים = Anchored = false

## צורות מתקדמות:
1. WedgePart - למשולשים וגגות משופעים:
   local wedge = Instance.new("WedgePart")
   wedge.Size = Vector3.new(4, 2, 4)

2. CornerWedgePart - לפינות משופעות

3. SpecialMesh - לצורות מיוחדות על Part:
   local mesh = Instance.new("SpecialMesh")
   mesh.MeshType = Enum.MeshType.Sphere/Cylinder/Head/Torso/Wedge/FileMesh
   mesh.Parent = part

4. Terrain - לנוף טבעי:
   local terrain = workspace.Terrain
   terrain:FillBall(Vector3.new(0,0,0), 20, Enum.Material.Grass)
   terrain:FillBlock(CFrame.new(0,-5,0), Vector3.new(100,10,100), Enum.Material.Water)

Materials לטרריין: Grass, Sand, Rock, Water, Snow, Ice, Mud, Ground, Slate, Concrete, Brick

## טיפים ליצירה יפה:
- שלב כמה Parts ליצירת צורה מורכבת
- השתמש ב-WedgePart לגגות ומדרונות
- הוסף Terrain מסביב לבניינים
- שים SurfaceGui להוספת טקסט/תמונות על משטחים

## דוגמה לחשיבה אנושית:
כשמבקשים "בנה בית" - אל תבנה רק קופסה עם גג!
בנה: רצפה, קירות עם חלונות (שקופים!), דלת עם ידית, גג משופע עם רעפים, ארובה, מרפסת קטנה, מדרגות כניסה, גינה קטנה עם עציצים.

כשמבקשים "בנה עץ" - אל תעשה רק גליל וכדור!
בנה: גזע עם מרקם עץ, ענפים שיוצאים לצדדים, עלים בכמה שכבות, אולי פרי או ציפור.

כשמבקשים "בנה מכונית" - תוסיף: פנסים, חלונות, מראות, דלתות, פגוש, לוחית רישוי.

כשמבקשים "בנה עיר קטנה" או "עיירה" - זה פרויקט גדול! תבנה:
- כביש ראשי עם מדרכות משני הצדדים
- 3-5 בתים שונים בגדלים וצבעים שונים
- חנות או שניים (עם שלטים)
- עצים ופנסי רחוב
- מכונית או שתיים על הכביש
- ספסל וגינה קטנה
- מעבר חציה
- אולי מזרקה או כיכר במרכז

כשמבקשים "פארק שעשועים" - תבנה:
- מגלשה גדולה וצבעונית
- נדנדות
- קרוסלה
- דוכן גלידה/ממתקים
- ספסלים להורים
- גדר סביב
- עצים וצמחיה

## שימוש במודלים מוכנים (Toolbox):
אם המשתמש מבקש משהו מורכב כמו "שים עץ מוכן" או "תוסיף מודל של בית", השתמש ב-InsertService:

```lua
local InsertService = game:GetService("InsertService")
local model = InsertService:LoadAsset(ASSET_ID):GetChildren()[1]
model.Parent = workspace
model:MoveTo(Vector3.new(0, 0, 0))
```

Asset IDs נפוצים (מודלים חינמיים):
- עץ פשוט = 4631364747
- בית קטן = 7075284869
- מכונית = 7086281035
- כיסא = 8667289978
- שולחן = 7086407632
- מנורה = 7086431294
- גדר = 7074904498
- סלע = 5765284230

אם המשתמש אומר "מודל" או "מוכן" או "toolbox" - העדף להשתמש ב-InsertService.

צבעים נפוצים:
- אדום = "Bright red"
- כחול = "Bright blue"
- ירוק = "Bright green"
- צהוב = "Bright yellow"
- כתום = "Neon orange"
- לבן = "White"
- שחור = "Black"
- חום = "Reddish brown"
- ורוד = "Hot pink"

דוגמאות:

פקודה: "בנה בית קטן"
קוד:
local parts = {}
-- רצפה
local floor = Instance.new("Part")
floor.Size = Vector3.new(20, 1, 20)
floor.Position = Vector3.new(0, 0.5, 0)
floor.Anchored = true
floor.BrickColor = BrickColor.new("Brown")
floor.Parent = workspace
table.insert(parts, floor)
-- קיר קדמי
local wall1 = Instance.new("Part")
wall1.Size = Vector3.new(20, 10, 1)
wall1.Position = Vector3.new(0, 5.5, -9.5)
wall1.Anchored = true
wall1.BrickColor = BrickColor.new("Brick yellow")
wall1.Parent = workspace
table.insert(parts, wall1)
-- קיר אחורי
local wall2 = Instance.new("Part")
wall2.Size = Vector3.new(20, 10, 1)
wall2.Position = Vector3.new(0, 5.5, 9.5)
wall2.Anchored = true
wall2.BrickColor = BrickColor.new("Brick yellow")
wall2.Parent = workspace
table.insert(parts, wall2)
-- קיר שמאלי
local wall3 = Instance.new("Part")
wall3.Size = Vector3.new(1, 10, 20)
wall3.Position = Vector3.new(-9.5, 5.5, 0)
wall3.Anchored = true
wall3.BrickColor = BrickColor.new("Brick yellow")
wall3.Parent = workspace
table.insert(parts, wall3)
-- קיר ימני
local wall4 = Instance.new("Part")
wall4.Size = Vector3.new(1, 10, 20)
wall4.Position = Vector3.new(9.5, 5.5, 0)
wall4.Anchored = true
wall4.BrickColor = BrickColor.new("Brick yellow")
wall4.Parent = workspace
table.insert(parts, wall4)
-- גג
local roof = Instance.new("Part")
roof.Size = Vector3.new(22, 1, 22)
roof.Position = Vector3.new(0, 11, 0)
roof.Anchored = true
roof.BrickColor = BrickColor.new("Bright red")
roof.Parent = workspace
table.insert(parts, roof)
game.Selection:Set(parts)

פקודה: "צור עץ"
קוד:
local parts = {}
local trunk = Instance.new("Part")
trunk.Shape = Enum.PartType.Cylinder
trunk.Size = Vector3.new(8, 2, 2)
trunk.CFrame = CFrame.new(0, 4, 0) * CFrame.Angles(0, 0, math.rad(90))
trunk.Anchored = true
trunk.BrickColor = BrickColor.new("Reddish brown")
trunk.Parent = workspace
table.insert(parts, trunk)
local leaves = Instance.new("Part")
leaves.Shape = Enum.PartType.Ball
leaves.Size = Vector3.new(8, 8, 8)
leaves.Position = Vector3.new(0, 10, 0)
leaves.Anchored = true
leaves.BrickColor = BrickColor.new("Bright green")
leaves.Parent = workspace
table.insert(parts, leaves)
game.Selection:Set(parts)

עכשיו, צור קוד Lua עבור הפקודה הבאה:"""

    def __init__(self, api_key: Optional[str] = None, on_status=None):
        """
        אתחול.

        Args:
            api_key: Anthropic API key (או מ-ANTHROPIC_API_KEY)
            on_status: callback להודעות סטטוס
        """
        self.on_status = on_status or (lambda x: print(f"[LLM] {x}"))

        # OpenRouter (ראשי - זול יותר!)
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if self.openrouter_key:
            self.on_status("OpenRouter מוכן")

        # Claude API (fallback)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except:
                pass

        if not self.openrouter_key and not self.api_key:
            raise ValueError("חסר OPENROUTER_API_KEY או ANTHROPIC_API_KEY!")

        # זיכרון שיחה - מה נוצר עד עכשיו
        self.conversation_history = []
        self.last_created = None  # תיאור מה נוצר לאחרונה

    def generate_lua(self, command: str, context: str = "") -> Optional[str]:
        """
        מייצר קוד Lua מפקודה בעברית עם זיכרון שיחה.

        Args:
            command: הפקודה בעברית (למשל "בנה בית אדום")
            context: מצב העולם הנוכחי (מה כבר נבנה)

        Returns:
            קוד Lua או None אם נכשל
        """
        # נסה קודם OpenRouter (זול יותר!)
        if self.openrouter_key:
            result = self._generate_with_openrouter(command, context)
            if result:
                return result

        # Fallback ל-Claude
        if not self.client:
            self.on_status("אין API זמין!")
            return None

        self.on_status(f"שולח ל-Claude: {command}")

        # בנה הודעות עם היסטוריה
        messages = []

        # הוסף היסטוריה (מקסימום 5 הודעות אחרונות)
        for msg in self.conversation_history[-10:]:
            messages.append(msg)

        # הוסף את הפקודה הנוכחית עם קונטקסט
        current_content = command
        # Add world state context if available
        if context and context != "העולם ריק כרגע.":
            current_content = f"{context}\n\nפקודה חדשה: {command}"
        elif self.last_created:
            current_content = f"[הקשר: יצרת קודם {self.last_created}]\n\nפקודה חדשה: {command}"

        messages.append({"role": "user", "content": current_content})

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,  # יותר טוקנים לבניות גדולות
                system=self.SYSTEM_PROMPT,
                messages=messages
            )

            # חלץ את הקוד מהתשובה
            lua_code = message.content[0].text.strip()

            # נקה markdown אם יש
            if lua_code.startswith("```"):
                lines = lua_code.split("\n")
                lua_code = "\n".join(lines[1:-1])

            # בדיקה שזה באמת קוד Lua ולא טקסט רגיל
            lua_indicators = ["local ", "Instance.new", "workspace", "Vector3", "game.", "Part", "="]
            is_lua = any(indicator in lua_code for indicator in lua_indicators)

            if not is_lua:
                self.on_status("Claude החזיר טקסט רגיל, מייצר קוביה ברירת מחדל")
                lua_code = """local parts = {}
local p = Instance.new("Part")
p.Size = Vector3.new(4, 4, 4)
p.Position = Vector3.new(0, 5, 0)
p.Anchored = true
p.BrickColor = BrickColor.new("Bright blue")
p.Parent = workspace
table.insert(parts, p)
game.Selection:Set(parts)"""

            # שמור בהיסטוריה
            self.conversation_history.append({"role": "user", "content": command})
            self.conversation_history.append({"role": "assistant", "content": lua_code[:500]})  # חתוך כדי לחסוך זיכרון
            self.last_created = command

            self.on_status(f"התקבל קוד ({len(lua_code)} תווים)")
            return lua_code

        except Exception as e:
            self.on_status(f"שגיאה: {e}")
            return None

    def _clean_lua_code(self, content: str) -> Optional[str]:
        """
        מנקה קוד Lua מתוך תגובה - מסיר טקסט, הסברים ו-markdown.

        Args:
            content: התגובה המלאה מהמודל

        Returns:
            קוד Lua נקי בלבד, או None אם לא נמצא
        """
        content = content.strip()

        # חפש קוד בתוך בלוק markdown (```lua או ```)
        patterns = [
            r'```lua\s*\n(.*?)```',      # ```lua ... ```
            r'```luau\s*\n(.*?)```',     # ```luau ... ```
            r'```\s*\n(.*?)```',          # ``` ... ```
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                self.on_status(f"חולץ קוד מ-markdown ({len(code)} תווים)")
                return code

        # אם אין בלוק markdown, חפש קוד שמתחיל עם local parts
        if "local parts" in content:
            start_idx = content.find("local parts")
            # מצא את הסוף
            end_match = re.search(r'game\.Selection:Set\(parts\)', content[start_idx:])
            if end_match:
                end_idx = start_idx + end_match.end()
                code = content[start_idx:end_idx].strip()
                self.on_status(f"חולץ קוד ללא markdown ({len(code)} תווים)")
                return code

        # אם מתחיל ישירות עם local - כנראה קוד נקי
        if content.startswith("local "):
            return content

        # לא נמצא קוד תקין
        self.on_status("אזהרה: לא נמצא קוד Lua בתגובה")
        return None

    def _generate_with_openrouter(self, command: str, context: str = "") -> Optional[str]:
        """
        מייצר קוד Lua עם OpenRouter (DeepSeek).
        """
        self.on_status(f"שולח ל-OpenRouter: {command}")

        current_content = command
        # Add world state context if available
        if context and context != "העולם ריק כרגע.":
            current_content = f"{context}\n\nפקודה חדשה: {command}"
        elif self.last_created:
            current_content = f"[הקשר: יצרת קודם {self.last_created}]\n\nפקודה חדשה: {command}"

        # פרומפט מחמיר יותר - באנגלית כדי שהמודל יבין טוב יותר
        strict_system = """You are a Lua code generator for Roblox Studio.
CRITICAL RULES:
1. Output ONLY valid Lua code - NO explanations, NO Hebrew text!
2. Start with: local parts = {}
3. End with: game.Selection:Set(parts)
4. Use Anchored = true
5. Be creative with details (windows, doors, colors)

RESPOND WITH PURE LUA CODE ONLY."""

        messages = [
            {"role": "system", "content": strict_system + "\n\n" + self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate Lua code for: {current_content}"}
        ]

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://roblox-voice-creator.local",
                    "X-Title": "Roblox Voice Creator"
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": messages,
                    "max_tokens": 4000,
                    "temperature": 0.7
                },
                timeout=60
            )

            if response.status_code != 200:
                self.on_status(f"OpenRouter error: {response.status_code}")
                return None

            data = response.json()
            raw_response = data["choices"][0]["message"]["content"].strip()

            # נקה את הקוד - חלץ רק Lua
            lua_code = self._clean_lua_code(raw_response)

            if not lua_code:
                return None

            # בדיקה שזה באמת קוד Lua
            lua_indicators = ["local ", "Instance.new", "workspace", "Vector3", "game.", "Part", "="]
            is_lua = any(indicator in lua_code for indicator in lua_indicators)

            if not is_lua:
                self.on_status("OpenRouter לא החזיר קוד Lua תקין")
                return None

            # שמור בהיסטוריה
            self.conversation_history.append({"role": "user", "content": command})
            self.conversation_history.append({"role": "assistant", "content": lua_code[:500]})
            self.last_created = command

            self.on_status(f"התקבל קוד מ-OpenRouter ({len(lua_code)} תווים)")
            return lua_code

        except Exception as e:
            self.on_status(f"OpenRouter error: {e}")
            return None

    def clear_history(self):
        """מנקה את היסטוריית השיחה."""
        self.conversation_history = []
        self.last_created = None
        self.on_status("היסטוריה נמחקה")


if __name__ == "__main__":
    # בדיקה
    builder = LLMBuilder()

    tests = [
        "צור קוביה אדומה גדולה",
        "בנה בית קטן",
        "תעשה מכונית",
        "צור שולחן וכיסא",
    ]

    for test in tests:
        print(f"\n{'='*50}")
        print(f"פקודה: {test}")
        print("="*50)
        code = builder.generate_lua(test)
        if code:
            print(code[:500] + "..." if len(code) > 500 else code)
