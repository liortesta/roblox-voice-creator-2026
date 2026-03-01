# -*- coding: utf-8 -*-
"""
Multi-Agent System - מערכת מרובת סוכנים
========================================

מערכת סוכנים חכמה שמשתמשת ב-OpenRouter לגישה למודלים שונים:
- Coordinator: מבין את הבקשה ומחליט איזה סוכן לשלוח
- CodeAgent: מתמחה בכתיבת קוד Lua
- DesignAgent: מתמחה בעיצוב ואסתטיקה
- GameLogicAgent: מתמחה בלוגיקה של משחקים
- StoryAgent: מתמחה ביצירת סיפורים ועולמות

שימוש ב-OpenRouter מאפשר:
- גישה ל-400+ מודלים
- Fallback אוטומטי
- בחירת מודל אופטימלי לכל משימה
- עלויות נמוכות יותר
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional, List
from enum import Enum, auto
from dataclasses import dataclass

# תיקון קידוד
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))


class AgentType(Enum):
    """סוגי סוכנים"""
    COORDINATOR = auto()    # מתאם ראשי
    CODE = auto()           # כותב קוד
    DESIGN = auto()         # מעצב
    GAME_LOGIC = auto()     # לוגיקת משחק
    STORY = auto()          # סיפור ועולם


@dataclass
class AgentConfig:
    """הגדרות סוכן"""
    name: str
    model: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4000


# הגדרות סוכנים
AGENT_CONFIGS = {
    AgentType.COORDINATOR: AgentConfig(
        name="Coordinator",
        model="anthropic/claude-3.5-sonnet",  # Claude לתיאום
        system_prompt="""אתה מתאם ראשי במערכת יצירת משחקי Roblox.
תפקידך לנתח את הבקשה של המשתמש ולהחליט איזה סוכנים צריכים לטפל בה.

הסוכנים הזמינים:
1. CODE - לכתיבת קוד Lua
2. DESIGN - לעיצוב ויזואלי (צבעים, סידור, אסתטיקה)
3. GAME_LOGIC - ללוגיקה של משחק (נקודות, חיים, כללים)
4. STORY - לסיפור ועולם (דמויות, עלילה, אווירה)

החזר JSON עם:
{
    "agents": ["CODE", "DESIGN"],  // רשימת סוכנים נדרשים
    "task_breakdown": {
        "CODE": "תיאור המשימה לסוכן הקוד",
        "DESIGN": "תיאור המשימה לסוכן העיצוב"
    },
    "priority": "CODE"  // מי מתחיל ראשון
}""",
        temperature=0.3
    ),

    AgentType.CODE: AgentConfig(
        name="CodeAgent",
        model="deepseek/deepseek-coder",  # DeepSeek Coder - מומחה קוד
        system_prompt="""אתה מומחה לכתיבת קוד Lua עבור Roblox Studio.

כללים:
1. כתוב קוד Lua תקין בלבד - ללא הסברים!
2. התחל עם: local parts = {}
3. סיים עם: game.Selection:Set(parts)
4. השתמש ב-Anchored = true
5. הוסף פרטים: חלונות, דלתות, גגות
6. Materials: Brick, Wood, Metal, Glass, Neon
7. BrickColor.new() לצבעים

דוגמה לקוביה:
local parts = {}
local p = Instance.new("Part")
p.Size = Vector3.new(4,4,4)
p.Position = Vector3.new(0,2,0)
p.Anchored = true
p.BrickColor = BrickColor.new("Bright blue")
p.Parent = workspace
table.insert(parts, p)
game.Selection:Set(parts)""",
        temperature=0.2,  # יותר דטרמיניסטי לקוד
        max_tokens=8000
    ),

    AgentType.DESIGN: AgentConfig(
        name="DesignAgent",
        model="openai/gpt-4o-mini",  # GPT-4o mini - טוב לעיצוב
        system_prompt="""אתה מומחה לעיצוב ויזואלי במשחקי Roblox.

תפקידך:
1. להציע פלטת צבעים מתאימה
2. לתכנן סידור אובייקטים
3. להוסיף פרטים אסתטיים
4. ליצור אווירה

החזר JSON עם:
{
    "color_palette": ["Bright blue", "White", "Dark green"],
    "layout": [
        {"object": "בית", "position": [0, 5, 0], "size": [20, 15, 20]},
        {"object": "עץ", "position": [15, 5, 0], "size": [4, 10, 4]}
    ],
    "details": ["חלונות עם מסגרת", "גג אדום", "דלת עץ"],
    "atmosphere": "כפרי ונעים"
}""",
        temperature=0.8  # יותר יצירתי
    ),

    AgentType.GAME_LOGIC: AgentConfig(
        name="GameLogicAgent",
        model="anthropic/claude-3-haiku",  # Claude Haiku - מהיר ללוגיקה
        system_prompt="""אתה מומחה ללוגיקת משחקים ב-Roblox.

תפקידך ליצור:
1. מערכות נקודות/מטבעות
2. מערכות חיים/בריאות
3. תנאי ניצחון/הפסד
4. אינטראקציות (לחיצות, נגיעות)
5. טיימרים וספירות

החזר קוד Lua עם Scripts שמממשים את הלוגיקה.
השתמש ב:
- ClickDetector לאינטראקציות
- IntValue/NumberValue לנתונים
- RemoteEvents לתקשורת
- Touched events לנגיעות""",
        temperature=0.3
    ),

    AgentType.STORY: AgentConfig(
        name="StoryAgent",
        model="google/gemini-2.0-flash-exp:free",  # Gemini - יצירתי לסיפורים
        system_prompt="""אתה מומחה ליצירת סיפורים ועולמות למשחקי Roblox.

תפקידך:
1. ליצור רקע לעולם המשחק
2. לפתח דמויות עם אישיות
3. לכתוב דיאלוגים
4. להגדיר אווירה ונושא
5. ליצור אתגרים ומשימות

החזר JSON עם:
{
    "world_name": "שם העולם",
    "backstory": "סיפור הרקע",
    "characters": [
        {"name": "שם", "role": "תפקיד", "personality": "אישיות"}
    ],
    "quests": [
        {"name": "משימה", "description": "תיאור", "reward": "פרס"}
    ],
    "atmosphere": "אווירה"
}""",
        temperature=0.9  # הכי יצירתי
    )
}


class OpenRouterClient:
    """לקוח OpenRouter"""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            safe_print("אזהרה: OPENROUTER_API_KEY לא מוגדר")

    def chat(self, model: str, messages: List[Dict],
             temperature: float = 0.7, max_tokens: int = 4000) -> Optional[str]:
        """שליחת בקשה ל-OpenRouter"""
        if not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://roblox-voice-creator.local",
            "X-Title": "Roblox Voice Creator"
        }

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            safe_print(f"שגיאת OpenRouter: {e}")
            return None


class Agent:
    """סוכן בסיסי"""

    def __init__(self, agent_type: AgentType, client: OpenRouterClient,
                 on_status=None):
        self.agent_type = agent_type
        self.config = AGENT_CONFIGS[agent_type]
        self.client = client
        self.on_status = on_status or (lambda x: safe_print(f"[{self.config.name}] {x}"))
        self.conversation_history = []

    def execute(self, task: str, context: str = "") -> Optional[str]:
        """ביצוע משימה"""
        self.on_status(f"מעבד: {task[:50]}...")

        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]

        if context:
            messages.append({
                "role": "user",
                "content": f"הקשר נוכחי:\n{context}"
            })

        # הוסף היסטוריה
        messages.extend(self.conversation_history[-4:])  # רק 4 אחרונים

        messages.append({
            "role": "user",
            "content": task
        })

        result = self.client.chat(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        if result:
            # שמור בהיסטוריה
            self.conversation_history.append({"role": "user", "content": task})
            self.conversation_history.append({"role": "assistant", "content": result[:500]})
            self.on_status("סיים בהצלחה")

        return result


class MultiAgentSystem:
    """מערכת מרובת סוכנים"""

    def __init__(self, on_status=None):
        self.on_status = on_status or (lambda x: safe_print(f"[MultiAgent] {x}"))
        self.client = OpenRouterClient()
        self.agents = {}
        self._init_agents()

        # Fallback ל-Anthropic אם אין OpenRouter
        self.anthropic_client = None
        if not self.client.api_key:
            self._init_anthropic_fallback()

    def _init_agents(self):
        """אתחול סוכנים"""
        for agent_type in AgentType:
            self.agents[agent_type] = Agent(
                agent_type, self.client, self.on_status
            )
        self.on_status("סוכנים מוכנים")

    def _init_anthropic_fallback(self):
        """Fallback ל-Anthropic אם אין OpenRouter"""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.on_status("Fallback: משתמש ב-Anthropic")
        except ImportError:
            pass

    def execute(self, user_request: str, world_context: str = "") -> Dict[str, Any]:
        """
        ביצוע בקשה עם מערכת הסוכנים.

        1. המתאם מנתח את הבקשה
        2. מחליט אילו סוכנים נדרשים
        3. מפעיל אותם בסדר הנכון
        4. משלב את התוצאות
        """
        self.on_status(f"מעבד: {user_request}")

        # אם אין OpenRouter, השתמש ב-fallback פשוט
        if not self.client.api_key:
            return self._fallback_execute(user_request, world_context)

        # שלב 1: המתאם מנתח
        coordinator = self.agents[AgentType.COORDINATOR]
        analysis = coordinator.execute(
            f"נתח את הבקשה הזו והחלט אילו סוכנים נדרשים:\n{user_request}",
            world_context
        )

        if not analysis:
            return {"success": False, "error": "המתאם נכשל"}

        # פרסור התוצאה
        try:
            # נסה לחלץ JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', analysis)
            if json_match:
                task_plan = json.loads(json_match.group())
            else:
                # ברירת מחדל - רק קוד
                task_plan = {
                    "agents": ["CODE"],
                    "task_breakdown": {"CODE": user_request},
                    "priority": "CODE"
                }
        except:
            task_plan = {
                "agents": ["CODE"],
                "task_breakdown": {"CODE": user_request},
                "priority": "CODE"
            }

        self.on_status(f"סוכנים נדרשים: {task_plan.get('agents', [])}")

        # שלב 2: הפעל סוכנים
        results = {}
        lua_code = None

        agent_map = {
            "CODE": AgentType.CODE,
            "DESIGN": AgentType.DESIGN,
            "GAME_LOGIC": AgentType.GAME_LOGIC,
            "STORY": AgentType.STORY
        }

        # קודם כל - עיצוב (אם נדרש)
        if "DESIGN" in task_plan.get("agents", []):
            design_task = task_plan.get("task_breakdown", {}).get("DESIGN", user_request)
            design_result = self.agents[AgentType.DESIGN].execute(design_task, world_context)
            if design_result:
                results["design"] = design_result
                # הוסף לקונטקסט
                world_context += f"\n\nעיצוב:\n{design_result}"

        # סיפור (אם נדרש)
        if "STORY" in task_plan.get("agents", []):
            story_task = task_plan.get("task_breakdown", {}).get("STORY", user_request)
            story_result = self.agents[AgentType.STORY].execute(story_task, world_context)
            if story_result:
                results["story"] = story_result
                world_context += f"\n\nסיפור:\n{story_result}"

        # לוגיקת משחק (אם נדרש)
        if "GAME_LOGIC" in task_plan.get("agents", []):
            logic_task = task_plan.get("task_breakdown", {}).get("GAME_LOGIC", user_request)
            logic_result = self.agents[AgentType.GAME_LOGIC].execute(logic_task, world_context)
            if logic_result:
                results["game_logic"] = logic_result

        # קוד - תמיד בסוף
        if "CODE" in task_plan.get("agents", []):
            code_task = task_plan.get("task_breakdown", {}).get("CODE", user_request)

            # הוסף קונטקסט מהסוכנים האחרים
            enhanced_context = world_context
            if "design" in results:
                enhanced_context += f"\n\nהנחיות עיצוב:\n{results['design']}"

            code_result = self.agents[AgentType.CODE].execute(code_task, enhanced_context)
            if code_result:
                lua_code = self._extract_lua(code_result)
                results["code"] = lua_code

        return {
            "success": bool(lua_code),
            "lua_code": lua_code,
            "results": results,
            "agents_used": task_plan.get("agents", []),
            "message": f"בוצע עם סוכנים: {', '.join(task_plan.get('agents', []))}"
        }

    def _fallback_execute(self, user_request: str, world_context: str) -> Dict[str, Any]:
        """Fallback פשוט עם Anthropic"""
        if not self.anthropic_client:
            return {"success": False, "error": "אין API key זמין"}

        self.on_status("משתמש ב-fallback (Anthropic)")

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=AGENT_CONFIGS[AgentType.CODE].system_prompt,
                messages=[
                    {"role": "user", "content": f"הקשר:\n{world_context}\n\nבקשה:\n{user_request}"}
                ]
            )
            lua_code = self._extract_lua(response.content[0].text)
            return {
                "success": bool(lua_code),
                "lua_code": lua_code,
                "message": "נוצר עם Anthropic fallback"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_lua(self, text: str) -> Optional[str]:
        """חילוץ קוד Lua מטקסט"""
        import re

        # נסה למצוא בלוק קוד
        code_match = re.search(r'```lua\s*([\s\S]*?)```', text)
        if code_match:
            return code_match.group(1).strip()

        code_match = re.search(r'```\s*([\s\S]*?)```', text)
        if code_match:
            return code_match.group(1).strip()

        # אם הטקסט נראה כמו קוד Lua
        if 'local ' in text and 'Instance.new' in text:
            return text.strip()

        return None


# ========================================
# בדיקה
# ========================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 50)
    print("Multi-Agent System Test")
    print("=" * 50)

    system = MultiAgentSystem()

    # בדיקה
    result = system.execute("בנה בית כפרי עם גינה יפה")
    print(f"\nתוצאה: {result.get('success')}")
    print(f"סוכנים: {result.get('agents_used', [])}")
    if result.get('lua_code'):
        print(f"קוד ({len(result['lua_code'])} תווים)")
