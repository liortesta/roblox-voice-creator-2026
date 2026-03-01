"""
OpenRouter Client - לקוח OpenRouter
====================================
גישה ל-400+ מודלים דרך API אחד.
משמש כתחליף ל-Claude API כשנגמרים טוקנים.
"""

import os
import re
import requests
from typing import Dict, Any, Optional, List


class OpenRouterClient:
    """
    לקוח OpenRouter - תחליף ל-Claude API.
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # מודלים מומלצים — דור 2026 (מהזול ליקר)
    MODELS = {
        "cheap": "deepseek/deepseek-chat",             # DeepSeek V3.2 — עוקף GPT-5!
        "coding": "deepseek/deepseek-chat",            # V3.2 מומחה קוד + reasoning
        "good": "anthropic/claude-3.5-haiku",          # Haiku 3.5 — מהיר ואיכותי
        "best": "anthropic/claude-sonnet-4-5-20250929", # Claude Sonnet 4.5
        "fast": "meta-llama/llama-4-scout",            # Llama 4 Scout — מהיר מאוד
        "reasoning": "deepseek/deepseek-r1",           # DeepSeek R1 — reasoning מעולה
    }

    def __init__(self, api_key: str = None, on_status=None):
        """
        אתחול הלקוח.

        Args:
            api_key: מפתח OpenRouter (או מ-.env)
            on_status: callback לסטטוס
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.on_status = on_status or (lambda x: print(f"[OpenRouter] {x}"))
        self.default_model = self.MODELS["cheap"]  # ברירת מחדל: זול וטוב

        if not self.api_key:
            self.on_status("אזהרה: אין OPENROUTER_API_KEY")

    def generate(self, prompt: str, system_prompt: str = None,
                 model: str = None, max_tokens: int = 4000) -> Dict[str, Any]:
        """
        יצירת תשובה מהמודל.

        Args:
            prompt: הפרומפט
            system_prompt: הנחיות מערכת
            model: שם המודל (או מפתח מ-MODELS)
            max_tokens: מקסימום טוקנים

        Returns:
            dict עם content, model, success
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "אין מפתח OpenRouter",
                "hint": "הוסף OPENROUTER_API_KEY ל-.env"
            }

        # בחר מודל
        if model in self.MODELS:
            model = self.MODELS[model]
        elif model is None:
            model = self.default_model

        self.on_status(f"משתמש במודל: {model}")

        # בנה הודעות
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # שלח בקשה
        try:
            response = requests.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://roblox-voice-creator.local",
                    "X-Title": "Roblox Voice Creator"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"שגיאה {response.status_code}: {response.text}"
                }

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            self.on_status(f"התקבלה תשובה ({len(content)} תווים)")

            return {
                "success": True,
                "content": content,
                "model": model,
                "usage": data.get("usage", {})
            }

        except Exception as e:
            self.on_status(f"שגיאה: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _clean_lua_code(self, content: str) -> str:
        """
        מנקה קוד Lua מתוך תגובה - מסיר טקסט, הסברים ו-markdown.

        Args:
            content: התגובה המלאה מהמודל

        Returns:
            קוד Lua נקי בלבד
        """
        content = content.strip()

        # חפש קוד בתוך בלוק markdown (```lua או ```)
        # תבנית: ```lua או ``` ואז הקוד ואז ```
        patterns = [
            r'```lua\s*\n(.*?)```',      # ```lua ... ```
            r'```luau\s*\n(.*?)```',     # ```luau ... ```
            r'```\s*\n(.*?)```',          # ``` ... ```
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                self.on_status(f"נמצא קוד בתוך בלוק markdown ({len(code)} תווים)")
                return code

        # אם אין בלוק markdown, חפש קוד שמתחיל עם local parts
        if "local parts" in content:
            # מצא את ההתחלה של הקוד
            start_idx = content.find("local parts")
            # מצא את הסוף (game.Selection או סוף הטקסט)
            end_match = re.search(r'game\.Selection:Set\(parts\)', content[start_idx:])
            if end_match:
                end_idx = start_idx + end_match.end()
                code = content[start_idx:end_idx].strip()
                self.on_status(f"נמצא קוד ללא markdown ({len(code)} תווים)")
                return code

        # אם עדיין לא מצאנו, החזר את התוכן המקורי (יכול להיכשל ברובלוקס)
        self.on_status("אזהרה: לא הצלחתי לחלץ קוד Lua נקי")
        return content

    def generate_lua(self, command: str, world_context: str = "") -> Dict[str, Any]:
        """
        יצירת קוד Lua עבור Roblox.

        Args:
            command: הפקודה בעברית
            world_context: הקשר העולם

        Returns:
            dict עם lua_code, success
        """
        # פרומפט מחמיר מאוד - רק קוד, בלי שום טקסט!
        system_prompt = f"""You are a Lua code generator for Roblox Studio.
You understand Hebrew commands and generate ONLY Lua code.

CRITICAL RULES:
- Output ONLY valid Lua code - NO explanations, NO Hebrew text, NO comments!
- Start IMMEDIATELY with: local parts = {{}}
- End with: game.Selection:Set(parts)
- Use Anchored = true for all parts
- Add details: windows, doors, roofs
- Use Materials: Brick, Wood, Metal, Glass, Neon

World state: {world_context if world_context else "Empty"}

RESPOND WITH PURE LUA CODE ONLY. NO MARKDOWN. NO EXPLANATIONS."""

        result = self.generate(
            prompt=f"Generate Lua code for: {command}",
            system_prompt=system_prompt,
            model="coding"
        )

        if not result.get("success"):
            return result

        # נקה את הקוד - חלץ רק Lua
        lua_code = self._clean_lua_code(result["content"])

        return {
            "success": True,
            "lua_code": lua_code,
            "message": f"נוצר עם {result['model']}",
            "model": result["model"]
        }

    def list_models(self) -> List[str]:
        """רשימת מודלים זמינים."""
        return list(self.MODELS.keys())


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

    print("בדיקת OpenRouter Client")
    print("=" * 40)

    client = OpenRouterClient()

    if client.api_key:
        print("\nמודלים זמינים:")
        for name, model in client.MODELS.items():
            print(f"  {name}: {model}")

        print("\nבודק חיבור...")
        result = client.generate("Say 'Hello' in Hebrew", model="free")

        if result["success"]:
            print(f"תשובה: {result['content']}")
        else:
            print(f"שגיאה: {result['error']}")
    else:
        print("אין מפתח - הוסף OPENROUTER_API_KEY ל-.env")
