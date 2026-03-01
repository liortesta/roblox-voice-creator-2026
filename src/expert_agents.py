"""
Expert Agents System - מערכת סוכנים מומחים לרובלוקס
===================================================
כל סוכן מתמחה בתחום ספציפי:
- Builder: בנייה ועיצוב
- Logic: סקריפטים ולוגיקה
- GameDesigner: מערכות משחק
- UI: ממשקים גרפיים
- Coordinator: תיאום בין הסוכנים
"""

import os
import re
import json
import requests
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum, auto
from dataclasses import dataclass


class ExpertType(Enum):
    """סוגי סוכנים מומחים."""
    BUILDER = "builder"           # בנייה ועיצוב 3D
    LOGIC = "logic"               # סקריפטים ולוגיקה
    GAME_DESIGNER = "game"        # מערכות משחק
    UI_EXPERT = "ui"              # ממשקים גרפיים
    COORDINATOR = "coordinator"   # מתאם ראשי


@dataclass
class AgentResponse:
    """תשובה מסוכן."""
    success: bool
    code: str = ""
    message: str = ""
    agent: str = ""
    needs_followup: bool = False
    followup_agents: List[str] = None


class BaseExpert:
    """מחלקת בסיס לסוכן מומחה."""

    EXPERT_TYPE = ExpertType.BUILDER
    MODEL = "deepseek/deepseek-chat"

    def __init__(self, api_key: str, on_status=None):
        self.api_key = api_key
        self.on_status = on_status or print

    def get_system_prompt(self) -> str:
        """פרומפט מערכת - לדרוס במחלקות יורשות."""
        return ""

    def generate(self, prompt: str, context: str = "") -> AgentResponse:
        """שליחת בקשה למודל."""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.MODEL,
                    "messages": [
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": f"Context: {context}\n\nRequest: {prompt}"}
                    ],
                    "max_tokens": 6000,
                    "temperature": 0.5
                },
                timeout=90
            )

            if response.status_code != 200:
                return AgentResponse(success=False, message=f"Error: {response.status_code}")

            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_response(content)

        except Exception as e:
            return AgentResponse(success=False, message=str(e))

    def _parse_response(self, content: str) -> AgentResponse:
        """פרסור תשובה - לדרוס במחלקות יורשות."""
        return AgentResponse(success=True, code=content, agent=self.EXPERT_TYPE.value)


class BuilderExpert(BaseExpert):
    """סוכן מומחה לבנייה ועיצוב 3D."""

    EXPERT_TYPE = ExpertType.BUILDER

    def get_system_prompt(self) -> str:
        return """You are a MASTER 3D BUILDER for Roblox Studio.
You specialize in creating beautiful, detailed structures and environments.

YOUR EXPERTISE:
- Architecture: houses, buildings, castles, cities
- Nature: trees, mountains, rivers, forests
- Vehicles: cars, planes, boats, trains
- Props: furniture, decorations, items
- Terrain: landscapes, paths, gardens

BUILDING STYLE:
- Use realistic proportions
- Add small details (windows, doors, handles)
- Use appropriate materials (Brick, Wood, Metal, Glass)
- Apply good colors (BrickColor or Color3)
- Create depth with multiple parts

CODE FORMAT:
```lua
local parts = {}

-- [Your building code here]
-- Use Instance.new("Part"), WedgePart, etc.
-- Set Size, Position, BrickColor, Material
-- table.insert(parts, part)

game.Selection:Set(parts)
```

OUTPUT ONLY LUA CODE. NO EXPLANATIONS."""


class LogicExpert(BaseExpert):
    """סוכן מומחה ללוגיקה וסקריפטים."""

    EXPERT_TYPE = ExpertType.LOGIC

    def get_system_prompt(self) -> str:
        return """You are a MASTER SCRIPTER for Roblox.
You specialize in game logic, interactions, and systems.

YOUR EXPERTISE:
- Player interactions (touch, click, proximity)
- Game mechanics (health, damage, respawn)
- Physics (forces, velocity, constraints)
- Data management (leaderstats, saves)
- Events and signals
- Animations and tweens
- Sound effects

SCRIPT TYPES YOU CREATE:
1. Server Scripts (game.ServerScriptService)
2. Local Scripts (game.StarterPlayer)
3. Module Scripts (shared logic)

IMPORTANT PATTERNS:
```lua
-- Touch detection
part.Touched:Connect(function(hit)
    local player = game.Players:GetPlayerFromCharacter(hit.Parent)
    if player then
        -- Do something
    end
end)

-- Proximity Prompt
local prompt = Instance.new("ProximityPrompt")
prompt.Parent = part
prompt.Triggered:Connect(function(player)
    -- Do something
end)

-- Tween animation
local TweenService = game:GetService("TweenService")
local tween = TweenService:Create(part, TweenInfo.new(1), {Position = Vector3.new(0,10,0)})
tween:Play()
```

OUTPUT FORMAT - Return a table with script info:
```lua
return {
    scripts = {
        {
            name = "GameScript",
            type = "Server",  -- or "Local" or "Module"
            parent = "ServerScriptService",
            code = [[
                -- Script code here
            ]]
        }
    },
    parts_code = [[
        -- Code to create parts (if needed)
    ]]
}
```"""


class GameDesignerExpert(BaseExpert):
    """סוכן מומחה למערכות משחק."""

    EXPERT_TYPE = ExpertType.GAME_DESIGNER

    def get_system_prompt(self) -> str:
        return """You are a GAME DESIGNER for Roblox.
You design complete game systems with progression, balance, and fun mechanics.

YOUR EXPERTISE:
- Game loops (core gameplay cycle)
- Progression systems (levels, XP, unlocks)
- Economy (coins, currency, shops)
- Difficulty balancing
- Player engagement
- Rewards and achievements
- Multiplayer systems
- Rounds and matches

GAME TYPES YOU DESIGN:
1. Obby (obstacle course) - checkpoints, difficulty curve
2. Tycoon - income, upgrades, automation
3. Simulator - clicking, rebirths, pets
4. Combat - weapons, health, respawn
5. Racing - tracks, vehicles, leaderboards
6. Collection - items, rarity, trading

OUTPUT FORMAT - Return a game design document:
```lua
return {
    game_type = "obby",
    name = "Epic Obby",

    -- Core systems
    systems = {
        lives = {
            max = 3,
            respawn_time = 3
        },
        checkpoints = {
            enabled = true,
            save_progress = true
        },
        timer = {
            enabled = true,
            show_best_time = true
        }
    },

    -- Levels/stages
    levels = {
        {name = "Easy Start", difficulty = 1},
        {name = "Lava Jump", difficulty = 2},
        -- ...
    },

    -- Rewards
    rewards = {
        completion = {coins = 100, badge = "Obby Master"},
        speedrun = {coins = 500, title = "Speed Demon"}
    },

    -- Build instructions for Builder agent
    build_instructions = [[
        Create an obstacle course with:
        - Starting platform (green)
        - 10 jumping platforms with increasing gaps
        - 3 checkpoints (yellow flags)
        - Lava floor (red neon parts)
        - Finish platform with trophy
    ]],

    -- Logic instructions for Logic agent
    logic_instructions = [[
        Create scripts for:
        - Checkpoint system (save spawn point)
        - Death on lava touch
        - Lives counter GUI
        - Timer display
        - Win celebration
    ]]
}
```"""


class UIExpert(BaseExpert):
    """סוכן מומחה לממשקים גרפיים."""

    EXPERT_TYPE = ExpertType.UI_EXPERT

    def get_system_prompt(self) -> str:
        return """You are a UI/UX DESIGNER for Roblox.
You create beautiful, functional user interfaces.

YOUR EXPERTISE:
- ScreenGui (full screen overlays)
- BillboardGui (floating above objects)
- SurfaceGui (on part surfaces)
- Buttons and interactions
- Animations and transitions
- Responsive design
- Color schemes and typography

UI ELEMENTS:
- Frame, TextLabel, TextButton, ImageLabel
- ScrollingFrame for lists
- UICorner for rounded corners
- UIGradient for gradients
- UIPadding, UIListLayout for layout

DESIGN PRINCIPLES:
- Clean and readable
- Consistent color scheme
- Good contrast
- Appropriate sizing
- Smooth animations

OUTPUT FORMAT:
```lua
local parts = {}

-- Create ScreenGui
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "GameUI"
screenGui.ResetOnSpawn = false
screenGui.Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui")

-- Main Frame
local mainFrame = Instance.new("Frame")
mainFrame.Size = UDim2.new(0, 300, 0, 100)
mainFrame.Position = UDim2.new(0.5, -150, 0, 10)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
mainFrame.BorderSizePixel = 0
mainFrame.Parent = screenGui

-- Add corner rounding
local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 10)
corner.Parent = mainFrame

-- [More UI code...]

table.insert(parts, screenGui)
game.Selection:Set(parts)
```"""


class CoordinatorAgent(BaseExpert):
    """סוכן מתאם - מתכנן ומפעיל את הסוכנים האחרים."""

    EXPERT_TYPE = ExpertType.COORDINATOR

    def __init__(self, api_key: str, on_status=None):
        super().__init__(api_key, on_status)
        self.experts = {
            ExpertType.BUILDER: BuilderExpert(api_key, on_status),
            ExpertType.LOGIC: LogicExpert(api_key, on_status),
            ExpertType.GAME_DESIGNER: GameDesignerExpert(api_key, on_status),
            ExpertType.UI_EXPERT: UIExpert(api_key, on_status),
        }

    def get_system_prompt(self) -> str:
        return """You are the COORDINATOR for a team of expert Roblox agents.
Your job is to analyze requests and decide which experts to use.

AVAILABLE EXPERTS:
1. BUILDER - Creates 3D objects, structures, environments
2. LOGIC - Creates scripts, interactions, game mechanics
3. GAME_DESIGNER - Designs game systems, progression, balance
4. UI_EXPERT - Creates user interfaces, HUDs, menus

ANALYZE THE REQUEST AND RETURN A PLAN:
```json
{
    "understanding": "What the user wants",
    "complexity": "simple|medium|complex",
    "steps": [
        {
            "expert": "GAME_DESIGNER",
            "task": "Design the game system",
            "order": 1
        },
        {
            "expert": "BUILDER",
            "task": "Build the environment",
            "order": 2
        },
        {
            "expert": "LOGIC",
            "task": "Add game logic",
            "order": 3
        },
        {
            "expert": "UI_EXPERT",
            "task": "Create the HUD",
            "order": 4
        }
    ],
    "notes": "Any special considerations"
}
```

For simple requests (just build something), use only BUILDER.
For interactive things, add LOGIC.
For full games, start with GAME_DESIGNER, then BUILDER, LOGIC, UI_EXPERT."""

    def analyze_request(self, request: str) -> Dict:
        """נתח את הבקשה והחזר תוכנית."""
        response = self.generate(request)

        try:
            # חפש JSON בתשובה
            json_match = re.search(r'\{[\s\S]*\}', response.code)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # ברירת מחדל - רק בנייה
        return {
            "understanding": request,
            "complexity": "simple",
            "steps": [{"expert": "BUILDER", "task": request, "order": 1}]
        }

    def execute_plan(self, plan: Dict, context: str = "") -> List[AgentResponse]:
        """הפעל את התוכנית - שלח לכל סוכן את המשימה שלו."""
        results = []
        accumulated_context = context

        steps = sorted(plan.get("steps", []), key=lambda x: x.get("order", 0))

        for step in steps:
            expert_name = step.get("expert", "BUILDER")
            task = step.get("task", "")

            self.on_status(f"🤖 {expert_name}: {task[:50]}...")

            # מצא את הסוכן
            expert_type = {
                "BUILDER": ExpertType.BUILDER,
                "LOGIC": ExpertType.LOGIC,
                "GAME_DESIGNER": ExpertType.GAME_DESIGNER,
                "UI_EXPERT": ExpertType.UI_EXPERT,
            }.get(expert_name, ExpertType.BUILDER)

            expert = self.experts.get(expert_type)
            if expert:
                result = expert.generate(task, accumulated_context)
                result.agent = expert_name
                results.append(result)

                # הוסף את התוצאה להקשר הבא
                if result.success and result.code:
                    accumulated_context += f"\n\n[{expert_name} created]:\n{result.code[:500]}"

        return results


class ExpertAgentSystem:
    """
    מערכת הסוכנים המומחים הראשית.

    שימוש:
        system = ExpertAgentSystem()
        result = system.process("בנה משחק מירוץ מלא עם GUI וחיים")
    """

    def __init__(self, on_status=None):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.on_status = on_status or (lambda x: print(f"[ExpertSystem] {x}"))

        if not self.api_key:
            self.on_status("אזהרה: אין OPENROUTER_API_KEY")
            self.coordinator = None
        else:
            self.coordinator = CoordinatorAgent(self.api_key, self.on_status)
            self.on_status("מערכת סוכנים מומחים מוכנה")

    def process(self, request: str, context: str = "") -> Dict[str, Any]:
        """
        עיבוד בקשה מלאה.

        Args:
            request: הבקשה בעברית/אנגלית
            context: הקשר נוסף (מצב העולם)

        Returns:
            dict עם success, codes (רשימת קודים), messages
        """
        if not self.coordinator:
            return {"success": False, "error": "אין API key"}

        self.on_status(f"מנתח בקשה: {request[:50]}...")

        # שלב 1: נתח את הבקשה
        plan = self.coordinator.analyze_request(request)
        self.on_status(f"תוכנית: {len(plan.get('steps', []))} שלבים")

        # שלב 2: הפעל את התוכנית
        results = self.coordinator.execute_plan(plan, context)

        # שלב 3: אסוף תוצאות
        codes = []
        messages = []
        all_success = True

        for result in results:
            if result.success and result.code:
                # חלץ קוד Lua
                lua_code = self._extract_lua(result.code)
                if lua_code:
                    codes.append({
                        "agent": result.agent,
                        "code": lua_code
                    })
                messages.append(f"✅ {result.agent}")
            else:
                all_success = False
                messages.append(f"❌ {result.agent}: {result.message}")

        return {
            "success": all_success and len(codes) > 0,
            "codes": codes,
            "messages": messages,
            "plan": plan,
            "combined_code": self._combine_codes(codes)
        }

    def _extract_lua(self, content: str) -> Optional[str]:
        """חילוץ קוד Lua מתשובה."""
        # חפש בלוק lua
        patterns = [
            r'```lua\s*\n(.*?)```',
            r'```luau\s*\n(.*?)```',
            r'```\s*\n(.*?)```',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # אם מתחיל ב-local
        if content.strip().startswith("local "):
            return content.strip()

        return None

    def _combine_codes(self, codes: List[Dict]) -> str:
        """שילוב כל הקודים לקוד אחד."""
        if not codes:
            return ""

        combined = ["local parts = {}"]

        for item in codes:
            code = item["code"]
            agent = item["agent"]

            # הסר את ה-local parts ו-game.Selection
            code = re.sub(r'local parts\s*=\s*\{\}', '', code)
            code = re.sub(r'game\.Selection:Set\(parts\)', '', code)

            combined.append(f"\n-- ========== {agent} ==========")
            combined.append(code.strip())

        combined.append("\ngame.Selection:Set(parts)")

        return "\n".join(combined)

    def quick_build(self, request: str) -> Dict[str, Any]:
        """בנייה מהירה - רק Builder agent."""
        if not self.coordinator:
            return {"success": False, "error": "אין API key"}

        builder = self.coordinator.experts[ExpertType.BUILDER]
        result = builder.generate(request)

        if result.success:
            lua_code = self._extract_lua(result.code)
            return {
                "success": True,
                "lua_code": lua_code,
                "agent": "BUILDER"
            }

        return {"success": False, "error": result.message}


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

    print("בדיקת Expert Agents System")
    print("=" * 50)

    system = ExpertAgentSystem()

    # בדיקה פשוטה
    print("\n📦 בדיקת בנייה פשוטה:")
    result = system.quick_build("בנה בית קטן עם גג אדום")
    if result["success"]:
        print(f"הצלחה! ({len(result.get('lua_code', ''))} תווים)")
    else:
        print(f"נכשל: {result.get('error')}")

    # בדיקה מורכבת
    print("\n🎮 בדיקת משחק מלא:")
    result = system.process("בנה משחק אובי עם 5 שלבים, חיים, ו-GUI")
    if result["success"]:
        print(f"הצלחה! {len(result['codes'])} קודים נוצרו")
        for msg in result["messages"]:
            print(f"  {msg}")
    else:
        print(f"נכשל")
