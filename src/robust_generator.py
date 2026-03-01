"""
Robust Lua Generator - מחולל קוד Lua חזק ואמין
==============================================
מערכת Two-Phase Generation:
  Phase 1: נסה preset או בקש JSON מה-LLM
  Phase 2: המר JSON ל-Lua דטרמיניסטי

מערכת רוטציה בין מודלים עם בדיקות ותיקונים אוטומטיים.
"""

import os
import re
import json
import subprocess
import shutil
import requests
from typing import Dict, Any, Optional, List, Tuple

# Two-Phase imports - handle both package and direct imports
try:
    from .blueprint_schema import (
        BlueprintSpec, PRESET_BLUEPRINTS, get_blueprint_for_command,
        get_json_prompt_for_llm, parse_blueprint_from_llm_response,
        validate_blueprint, HEBREW_OBJECTS,
    )
    from .template_builder import TemplateBuilder, CityBuilder, ObbyBuilder
    from .physics_engine import PhysicsEngine, HEBREW_TO_PHYSICS
    from .behavior_blueprints import (
        find_behavior_for_command, generate_behavior_lua,
        ALL_BEHAVIORS, list_behaviors_by_category, BehaviorSpec,
    )
except ImportError:
    from blueprint_schema import (
        BlueprintSpec, PRESET_BLUEPRINTS, get_blueprint_for_command,
        get_json_prompt_for_llm, parse_blueprint_from_llm_response,
        validate_blueprint, HEBREW_OBJECTS,
    )
    from template_builder import TemplateBuilder, CityBuilder, ObbyBuilder
    try:
        from physics_engine import PhysicsEngine, HEBREW_TO_PHYSICS
    except ImportError:
        PhysicsEngine = None
        HEBREW_TO_PHYSICS = {}
    try:
        from behavior_blueprints import (
            find_behavior_for_command, generate_behavior_lua,
            ALL_BEHAVIORS, list_behaviors_by_category, BehaviorSpec,
        )
    except ImportError:
        find_behavior_for_command = None
        generate_behavior_lua = None
        ALL_BEHAVIORS = {}
        list_behaviors_by_category = None
        BehaviorSpec = None


class RobustLuaGenerator:
    """
    מחולל Lua חזק עם:
    1. רוטציה בין מודלים
    2. בדיקת קוד לפני שליחה
    3. תיקון שגיאות אוטומטי
    """

    # מודלים לרוטציה (דור 2026 — חזקים משמעותית!)
    MODELS = [
        {
            "name": "DeepSeek V3.2",
            "id": "deepseek/deepseek-chat",
            "strength": "reasoning+coding",
            "cost": "cheap"
        },
        {
            "name": "Qwen3 Coder",
            "id": "qwen/qwen-2.5-coder-32b-instruct",
            "strength": "agentic_coding",
            "cost": "medium"
        },
        {
            "name": "Llama 4 Scout",
            "id": "meta-llama/llama-4-scout",
            "strength": "general+coding",
            "cost": "medium"
        },
        {
            "name": "DeepSeek R1",
            "id": "deepseek/deepseek-r1",
            "strength": "reasoning",
            "cost": "cheap"
        },
        {
            "name": "Mistral Large",
            "id": "mistralai/mistral-large-latest",
            "strength": "general",
            "cost": "medium"
        },
    ]

    # שגיאות Lua נפוצות ותיקונים
    COMMON_FIXES = [
        # Color3.new עם ערכים גבוהים מדי
        (r"Color3\.new\((\d+),\s*(\d+),\s*(\d+)\)", lambda m: f"Color3.fromRGB({m.group(1)}, {m.group(2)}, {m.group(3)})"),
        # חסר Parent
        (r"(Instance\.new\([^)]+\))\s*\n(?!\s*\w+\.Parent)", r"\1\n-- Remember to set Parent!\n"),
        # spawn במקום task.spawn
        (r"\bspawn\s*\(", "task.spawn("),
        # wait במקום task.wait
        (r"\bwait\s*\(", "task.wait("),
        # UDim2.new עם פרמטרים חסרים
        (r"UDim2\.new\(([^,]+),\s*([^,]+)\)", r"UDim2.new(\1, 0, \2, 0)"),
    ]

    # קוד שלא אמור להיות ב-command script (BUT Scripts are OK now with v8.0!)
    FORBIDDEN_IN_COMMAND = [
        # "LocalScript",  # Now allowed via Plugin Script Injection!
        "StarterPlayer",
        "PlayerGui",
        "LocalPlayer",
    ]

    def __init__(self, on_status=None):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.on_status = on_status or (lambda x: print(f"[RobustGen] {x}"))
        self.current_model_index = 0

        # מעקב אחר מיקומים תפוסים - 2D Grid!
        self.occupied_zones = []  # [(x, z, width, depth), ...]
        self.next_x_offset = 0  # היסט X הבא (backwards compat)
        self.creation_count = 0
        self.failed_models = set()

        # 2D Grid settings — פריסה כמו שכונה!
        self.grid_columns = 5       # 5 אובייקטים בשורה
        self.grid_spacing_x = 70    # רווח X בין אובייקטים
        self.grid_spacing_z = 70    # רווח Z בין שורות

        # Claude Code CLI — free with Max plan!
        self.claude_cli_path = shutil.which("claude.cmd") or shutil.which("claude")
        self.claude_cli_available = self.claude_cli_path is not None
        if self.claude_cli_available:
            self.on_status("Claude Code CLI זמין (חינם עם Max plan!)")
        elif not self.api_key:
            self.on_status("Warning: No OPENROUTER_API_KEY and no Claude CLI")

        # Two-Phase builders
        self.template_builder = TemplateBuilder()
        self.city_builder = CityBuilder()
        self.obby_builder = ObbyBuilder()

    # ===========================================
    # TWO-PHASE GENERATION METHODS
    # ===========================================

    def generate_two_phase(self, command: str, context: str = "") -> Dict[str, Any]:
        """
        Two-Phase Generation:
        1. Try preset blueprint (instant)
        2. Try LLM JSON generation → convert to Lua
        3. Fallback to direct Lua generation

        Args:
            command: Hebrew command from user
            context: World context

        Returns:
            Result dict with success, lua_code, etc.
        """
        self.on_status("Two-Phase Generation...")

        # Phase 0: Check for BEHAVIOR command (logic, scripts, interactions)
        behavior_result = self._try_behavior_blueprint(command)
        if behavior_result:
            self.on_status("Found behavior blueprint!")
            return behavior_result

        # Phase 1A: Check for preset blueprint (instant response)
        preset_result = self._try_preset_blueprint(command)
        if preset_result:
            self.on_status("Found preset - instant response!")
            return preset_result

        # Phase 1B: Check for special builders (city, obby)
        special_result = self._try_special_builders(command)
        if special_result:
            self.on_status("Found special builder!")
            return special_result

        # Phase 2: LLM generates JSON, convert to Lua
        json_result = self._generate_via_json(command)
        if json_result:
            self.on_status("Success with JSON to Lua!")
            return json_result

        # Phase 3: Fallback to direct Lua generation (OpenRouter only, no recursion)
        self.on_status("Fallback to direct Lua generation...")
        return self.generate(command, context, use_two_phase=False)

    def _try_preset_blueprint(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Try to match command to a preset blueprint.
        Returns Lua code if found, None otherwise.
        """
        blueprint = get_blueprint_for_command(command)
        if not blueprint:
            return None

        # Get 2D grid position
        base_x, base_z = self.get_next_position(blueprint.total_size[0])

        # Build Lua from blueprint
        lua_code = self.template_builder.build_lua(blueprint, base_x=base_x, base_z=base_z)

        # Register creation
        self.register_creation(base_x, base_z, blueprint.total_size[0], blueprint.total_size[2])

        return {
            "success": True,
            "lua_code": lua_code,
            "method": "preset",
            "blueprint": blueprint.name,
            "attempts": 0,
        }

    def _try_behavior_blueprint(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Phase 0: Check if the command is asking for a BEHAVIOR (logic/script).
        e.g. "תוסיף ריצה לדמות", "תגרום לו לעקוב", "תעשה דלת שנפתחת"

        Returns Lua code that creates a Script with the behavior, or None.
        """
        if not find_behavior_for_command:
            return None

        result = find_behavior_for_command(command)
        if not result:
            return None

        behavior_name, behavior = result

        # Extract target name from command
        target_name = self._extract_target_from_command(command)

        self.on_status(f"Behavior: {behavior.hebrew_name} → target: {target_name or 'selected'}")

        # Generate Lua
        lua_code = generate_behavior_lua(behavior, target_name=target_name)

        return {
            "success": True,
            "lua_code": lua_code,
            "method": "behavior_blueprint",
            "blueprint": behavior.hebrew_name,
            "behavior_name": behavior_name,
            "attempts": 0,
        }

    def _extract_target_from_command(self, command: str) -> Optional[str]:
        """
        Extract the target object name from a Hebrew command.
        "תוסיף ריצה לדמות" → "דמות"
        "תגרום למכונית לנסוע" → "מכונית"
        "תעשה שהבנאדם ירוץ" → "בנאדם"
        """
        import re

        # Patterns for target extraction
        patterns = [
            r'(?:ל|את\s+ה|את\s+)(\S+)',          # ל[target], את ה[target]
            r'(?:של\s+ה|של\s+)(\S+)',              # של ה[target]
            r'(?:שה)(\S+)',                          # שה[target]
            r'(?:ב)(\S+)\s+(?:ל|ש)',               # ב[target] ל/ש
        ]

        # Known object names to look for
        known_objects = [
            "דמות", "בנאדם", "איש", "שחקן", "NPC", "npc",
            "מכונית", "רכב", "אוטו",
            "בית", "דלת", "חלון",
            "כדור", "קוביה",
            "עץ", "סלע",
            "חייל", "זומבי", "אויב", "שומר", "חבר",
            "מפלצת", "דרקון",
        ]

        command_lower = command.lower()

        # First check for known objects
        for obj in known_objects:
            if obj in command_lower:
                return obj

        # Try regex patterns
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                target = match.group(1).strip()
                # Filter out behavior words
                behavior_words = ["ריצה", "קפיצה", "עפיפה", "נהיגה", "סיבוב", "ריפוי", "נזק"]
                if target not in behavior_words and len(target) > 1:
                    return target

        return None

    def _try_special_builders(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Check for special build commands (city, obby).
        """
        command_lower = command.lower()

        # City detection
        if any(word in command_lower for word in ["עיר", "שכונה", "כפר"]):
            # Extract number of houses
            num_houses = 3  # default
            for word in command.split():
                if word.isdigit():
                    num_houses = int(word)
                    break

            # Check for numbers in Hebrew
            hebrew_nums = {"שלוש": 3, "שלושה": 3, "ארבע": 4, "חמש": 5, "שש": 6}
            for heb, num in hebrew_nums.items():
                if heb in command_lower:
                    num_houses = num
                    break

            lua_code = self.city_builder.build_city(num_houses=num_houses)
            self.register_creation(0, 0, num_houses * 50, num_houses * 50)

            return {
                "success": True,
                "lua_code": lua_code,
                "method": "city_builder",
                "num_houses": num_houses,
                "attempts": 0,
            }

        # Obby detection
        if any(word in command_lower for word in ["אובי", "obby", "מכשולים", "קפיצות", "פלטפורמות"]):
            # Extract number of platforms
            num_platforms = 10  # default
            for word in command.split():
                if word.isdigit():
                    num_platforms = int(word)
                    break

            # Determine difficulty
            difficulty = "easy"
            if any(w in command_lower for w in ["קשה", "hard", "מאתגר"]):
                difficulty = "hard"
            elif any(w in command_lower for w in ["בינוני", "medium"]):
                difficulty = "medium"

            lua_code = self.obby_builder.build_obby(num_platforms=num_platforms, difficulty=difficulty)
            self.register_creation(0, 0, 30, num_platforms * 15)

            return {
                "success": True,
                "lua_code": lua_code,
                "method": "obby_builder",
                "num_platforms": num_platforms,
                "difficulty": difficulty,
                "attempts": 0,
            }

        return None

    def _call_claude_cli(self, prompt: str) -> Optional[str]:
        """
        Call Claude Code CLI — free with Max/Pro plan!
        Uses 'claude -p' for one-shot generation.
        """
        if not self.claude_cli_available:
            return None

        try:
            result = subprocess.run(
                [self.claude_cli_path, "-p", prompt, "--max-turns", "1"],
                capture_output=True,
                text=True,
                timeout=45,
                encoding="utf-8",
                errors="replace",
                shell=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()

            if result.stderr:
                self.on_status(f"Claude CLI stderr: {result.stderr[:100]}")
            return None

        except subprocess.TimeoutExpired:
            self.on_status("Claude CLI timeout (45s)")
            return None
        except Exception as e:
            self.on_status(f"Claude CLI error: {e}")
            return None

    def _generate_via_json(self, command: str, max_retries: int = 2) -> Optional[Dict[str, Any]]:
        """
        Phase 2: Ask LLM to generate JSON blueprint, then convert to Lua.
        Priority: Claude CLI (free) → OpenRouter (paid)
        """
        system_prompt = get_json_prompt_for_llm()

        # === Try Claude Code CLI first (FREE with Max plan!) ===
        if self.claude_cli_available:
            self.on_status("JSON Phase - Claude Code CLI (free)")
            # Short focused prompt for CLI (full system prompt is too large for -p flag)
            cli_prompt = (
                'Generate a JSON object for a Roblox build. '
                'Format: {"name":"EnglishName","parts":[{"name":"part1","type":"Part","size":[w,h,d],'
                '"position":[x,y,z],"color":"BrickColor name","material":"Material name"},...]} '
                'ONLY output the JSON, no explanation. '
                f'Build: {command}'
            )
            raw_response = self._call_claude_cli(cli_prompt)
            if raw_response:
                blueprint = parse_blueprint_from_llm_response(raw_response)
                if blueprint:
                    base_x, base_z = self.get_next_position(blueprint.total_size[0])
                    lua_code = self.template_builder.build_lua(blueprint, base_x=base_x, base_z=base_z)
                    is_valid, issues = self._validate_lua_code(lua_code)
                    if is_valid:
                        self.register_creation(base_x, base_z, blueprint.total_size[0], blueprint.total_size[2])
                        self.on_status("Success with Claude CLI (free!)")
                        return {
                            "success": True,
                            "lua_code": lua_code,
                            "method": "two_phase_json",
                            "model": "Claude Code CLI (free)",
                            "blueprint": blueprint.name,
                            "attempts": 1,
                        }
                    else:
                        self.on_status(f"Claude CLI Lua invalid: {issues}")
                else:
                    self.on_status("Claude CLI returned invalid JSON, trying OpenRouter...")
            else:
                self.on_status("Claude CLI failed, trying OpenRouter...")

        # === Fallback: OpenRouter (paid) ===
        if not self.api_key:
            return None

        prompt_simple = f"Create a JSON blueprint for: {command}"

        for attempt in range(max_retries):
            model = self._get_next_model()
            if not model:
                break

            self.on_status(f"JSON Phase - attempt {attempt + 1}: {model['name']}")

            # Call model
            raw_response = self._call_model(model["id"], prompt_simple, system_prompt)
            if not raw_response:
                self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)
                continue

            # Parse JSON
            blueprint = parse_blueprint_from_llm_response(raw_response)
            if not blueprint:
                self.on_status(f"{model['name']} returned invalid JSON")
                self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)
                continue

            # Convert to Lua
            base_x, base_z = self.get_next_position(blueprint.total_size[0])
            lua_code = self.template_builder.build_lua(blueprint, base_x=base_x, base_z=base_z)

            # Validate
            is_valid, issues = self._validate_lua_code(lua_code)
            if is_valid:
                self.register_creation(base_x, base_z, blueprint.total_size[0], blueprint.total_size[2])
                return {
                    "success": True,
                    "lua_code": lua_code,
                    "method": "two_phase_json",
                    "model": model["name"],
                    "blueprint": blueprint.name,
                    "attempts": attempt + 1,
                }

            self.on_status(f"Invalid Lua: {issues}")
            self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)

        return None

    def sync_from_world_state(self, world_state):
        """
        סנכרון מיקומים מ-WorldState — מונע בנייה על בנייה אחרי restart!
        """
        if not world_state or not world_state.objects:
            return

        max_x = 0
        max_z = 0
        for obj in world_state.objects.values():
            obj_right = obj.position[0] + obj.size[0] / 2
            obj_front = obj.position[2] + obj.size[2] / 2
            if obj_right > max_x:
                max_x = obj_right
            if obj_front > max_z:
                max_z = obj_front

        self.creation_count = len(world_state.objects)
        # Set next position past all existing objects
        self.next_x_offset = max_x + 20
        self.on_status(f"Synced positions: {self.creation_count} objects, next X={self.next_x_offset:.0f}")

    def get_next_position(self, estimated_size: int = 50) -> Tuple[int, int]:
        """
        מחזיר את המיקום הבא הפנוי - פריסת Grid 2D!

        Args:
            estimated_size: גודל משוער של האובייקט

        Returns:
            (x, z) - מיקום פנוי ב-Grid
        """
        col = self.creation_count % self.grid_columns
        row = self.creation_count // self.grid_columns

        x = col * self.grid_spacing_x
        z = row * self.grid_spacing_z

        # Keep next_x_offset in sync for backwards compat
        self.next_x_offset = max(self.next_x_offset, x + estimated_size + 20)

        return (x, z)

    def register_creation(self, x: float, z: float, width: float, depth: float):
        """רושם אזור תפוס חדש."""
        self.occupied_zones.append((x, z, width, depth))
        self.creation_count += 1

    def get_position_hint(self) -> str:
        """מחזיר הנחיות מיקום למודל."""
        if self.creation_count == 0:
            return "Place objects starting at position X=0, Z=0."

        next_x, next_z = self.get_next_position()
        return f"""IMPORTANT POSITIONING:
- Previous objects exist! DO NOT place at X=0, Z=0!
- Start your new objects at X={next_x}, Z={next_z}
- This prevents overlap with existing creations
- Objects are arranged in a 2D grid layout"""

    def clear_positions(self):
        """מנקה את רשימת המיקומים."""
        self.occupied_zones.clear()
        self.next_x_offset = 0
        self.creation_count = 0

    def _shift_positions(self, lua_code: str, x_offset: int) -> str:
        """
        מזיז את כל מיקומי X בקוד.

        Args:
            lua_code: קוד Lua מקורי
            x_offset: ההיסט להוסיף ל-X

        Returns:
            קוד עם מיקומים מעודכנים
        """
        if x_offset == 0:
            return lua_code

        # תבניות למציאת מיקומים
        # Position = Vector3.new(X, Y, Z)
        def shift_vector3(match):
            x = float(match.group(1))
            y = match.group(2)
            z = match.group(3)
            new_x = x + x_offset
            return f"Vector3.new({new_x}, {y}, {z})"

        # CFrame.new(X, Y, Z)
        def shift_cframe(match):
            x = float(match.group(1))
            y = match.group(2)
            z = match.group(3)
            rest = match.group(4) if match.lastindex >= 4 else ""
            new_x = x + x_offset
            return f"CFrame.new({new_x}, {y}, {z}{rest})"

        # החל את ההזזה
        result = lua_code

        # Vector3.new(x, y, z)
        result = re.sub(
            r'Vector3\.new\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)',
            shift_vector3,
            result
        )

        # CFrame.new(x, y, z) או CFrame.new(x, y, z) * ...
        result = re.sub(
            r'CFrame\.new\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*(\))',
            shift_cframe,
            result
        )

        return result

    # ===========================================
    # WORLD BUILDER — Multi-Build Chaining
    # ===========================================

    def is_compound_command(self, command: str) -> bool:
        """
        בדיקה אם הפקודה מורכבת (דורשת פירוק למספר בניות).
        """
        command_lower = command.lower()

        # World-level words that imply multiple objects
        world_words = ["כפר", "שכונה", "פארק", "מתחם", "מחנה", "גן חיות", "חווה", "תחנת"]
        if any(w in command_lower for w in world_words):
            return True

        # "עם" (with) + comma = compound: "בנה X עם A, B, C"
        if "עם" in command_lower and "," in command:
            return True

        # Multiple "ו" (and) conjunctions: "בנה A וB וC"
        vav_count = command_lower.count(" ו")
        if vav_count >= 2:
            return True

        return False

    def _decompose_compound(self, command: str) -> List[str]:
        """
        פירוק פקודה מורכבת לתתי-פקודות.
        "בנה כפר עם בתים, עצים, כביש" -> ["בנה בתים", "בנה עצים", "בנה כביש"]
        """
        command_lower = command.lower()
        sub_commands = []

        # Extract items after "עם" (with)
        if "עם" in command_lower:
            parts = command.split("עם", 1)
            items_str = parts[1].strip() if len(parts) > 1 else ""

            # Split by comma first, then handle "ו" conjunction at word START only
            # "5 בתים בצבעים שונים, כבישים, עצים, ומכוניות"
            # -> ["5 בתים בצבעים שונים", "כבישים", "עצים", "ומכוניות"]
            raw_items = [s.strip() for s in items_str.split(",") if s.strip()]

            items = []
            for item in raw_items:
                # Remove leading "ו" conjunction (e.g., "ומכוניות" -> "מכוניות")
                if item.startswith("ו") and len(item) > 1:
                    item = item[1:]
                items.append(item.strip())

            if items:
                for item in items:
                    sub_commands.append(f"בנה {item}")
                return sub_commands

        # Split by " ו" conjunction (space + vav at word start)
        if " ו" in command_lower:
            # Remove build verb first
            clean = command
            for verb in ["בנה ", "צור ", "תבנה ", "תצור ", "עשה ", "תעשה "]:
                if clean.startswith(verb):
                    clean = clean[len(verb):]
                    break

            # Split by " ו" (space before vav = conjunction)
            items = re.split(r' ו(?=\S)', clean)
            for item in items:
                item = item.strip()
                if item:
                    sub_commands.append(f"בנה {item}")
            return sub_commands

        # World-level words: generate default sub-objects
        world_defaults = {
            "כפר": ["בנה בית", "בנה בית", "בנה בית", "בנה עץ", "בנה עץ", "בנה גדר"],
            "שכונה": ["בנה בית", "בנה בית", "בנה בית", "בנה בית", "בנה עץ", "בנה עץ", "בנה מכונית"],
            "פארק": ["בנה עץ", "בנה עץ", "בנה עץ", "בנה ספסל", "בנה ספסל", "בנה בריכה"],
            "חווה": ["בנה בית", "בנה עץ", "בנה גדר", "בנה גדר", "בנה כלב"],
            "גן חיות": ["בנה כלב", "בנה חתול", "בנה עץ", "בנה גדר", "בנה גדר"],
            "מחנה": ["בנה אוהל", "בנה אוהל", "בנה עץ", "בנה עץ", "בנה מדורה"],
        }
        for word, defaults in world_defaults.items():
            if word in command_lower:
                return defaults

        # Fallback: return original as single command
        return [command]

    def build_world_sequence(self, command: str, context: str = "") -> Dict[str, Any]:
        """
        בניית עולם שלם - פירוק פקודה מורכבת למספר בניות רצופות.
        """
        sub_commands = self._decompose_compound(command)
        self.on_status(f"World Builder: {len(sub_commands)} sub-builds")

        all_lua_parts = ["local parts = {}"]
        all_lua_parts.append("")
        built_items = []
        failed_items = []

        for i, sub_cmd in enumerate(sub_commands):
            self.on_status(f"Building {i+1}/{len(sub_commands)}: {sub_cmd}")

            result = self.generate_two_phase(sub_cmd, context)
            if result and result.get("success"):
                lua = result["lua_code"]

                # Strip the "local parts = {}" header and "game.Selection:Set(parts)" footer
                # so we can combine into one script
                lua = lua.replace("local parts = {}", "")
                lua = lua.replace("game.Selection:Set(parts)", "")
                lua = lua.strip()

                if lua:
                    all_lua_parts.append(f"-- [{i+1}] {sub_cmd}")
                    all_lua_parts.append(lua)
                    all_lua_parts.append("")
                    built_items.append(result.get("blueprint", sub_cmd))
            else:
                failed_items.append(sub_cmd)
                self.on_status(f"Failed: {sub_cmd}")

        # Footer
        all_lua_parts.append("game.Selection:Set(parts)")

        combined_lua = "\n".join(all_lua_parts)

        if built_items:
            return {
                "success": True,
                "lua_code": combined_lua,
                "method": "world_builder",
                "blueprint": f"World({len(built_items)} items)",
                "built_items": built_items,
                "failed_items": failed_items,
                "attempts": 1,
            }
        else:
            return {
                "success": False,
                "error": "All sub-builds failed",
                "failed_items": failed_items,
            }

    def _get_next_model(self) -> Optional[Dict]:
        """בחר את המודל הבא לנסות."""
        for i in range(len(self.MODELS)):
            idx = (self.current_model_index + i) % len(self.MODELS)
            model = self.MODELS[idx]
            if model["id"] not in self.failed_models:
                return model
        # אם כולם נכשלו, נקה ונתחיל מחדש
        self.failed_models.clear()
        return self.MODELS[0]

    def _call_model(self, model_id: str, prompt: str, system: str) -> Optional[str]:
        """קריאה למודל ספציפי."""
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://roblox-voice-creator.local",
                    "X-Title": "Roblox Voice Creator"
                },
                json={
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.5  # נמוך יותר = יותר עקבי
                },
                timeout=60
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            self.on_status(f"Error: {e}")
            return None

    def _extract_lua_code(self, content: str) -> Optional[str]:
        """חילוץ קוד Lua מתגובה."""
        content = content.strip()

        # חפש בלוק markdown
        patterns = [
            r'```lua\s*\n(.*?)```',
            r'```luau\s*\n(.*?)```',
            r'```\s*\n(.*?)```',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # חפש קוד ישיר
        if "local parts" in content:
            start = content.find("local parts")
            end_match = re.search(r'game\.Selection:Set\(parts\)', content[start:])
            if end_match:
                return content[start:start + end_match.end()].strip()

        if content.startswith("local "):
            return content

        return None

    def _validate_lua_code(self, code: str, is_behavior: bool = False) -> Tuple[bool, List[str]]:
        """בדיקת תקינות קוד Lua."""
        issues = []

        # בדיקות בסיסיות
        if not code or len(code) < 20:
            issues.append("Code too short")

        # Behavior scripts have different structure (no parts table)
        if not is_behavior:
            if "local parts" not in code:
                issues.append("Missing 'local parts = {}'")

            if "game.Selection:Set(parts)" not in code:
                issues.append("Missing 'game.Selection:Set(parts)'")

        # בדיקת קוד אסור (LocalScript וכו')
        for forbidden in self.FORBIDDEN_IN_COMMAND:
            if forbidden in code:
                issues.append(f"Forbidden code: {forbidden} (doesn't work in command script)")

        # בדיקת סוגריים מאוזנים
        if code.count("(") != code.count(")"):
            issues.append("Unbalanced parentheses ()")

        if code.count("{") != code.count("}"):
            issues.append("Unbalanced braces {}")

        if code.count("[") != code.count("]"):
            issues.append("Unbalanced brackets []")

        # בדיקת Instance.new תקין
        instance_matches = re.findall(r'Instance\.new\("([^"]+)"\)', code)
        valid_types = [
            "Part", "WedgePart", "CornerWedgePart", "SpawnLocation",
            "Model", "Folder", "Sound", "PointLight", "SpotLight",
            "SurfaceGui", "TextLabel", "TextButton", "Frame", "Script",
            "BillboardGui", "Beam", "Attachment", "Fire", "Smoke"
        ]
        for inst_type in instance_matches:
            if inst_type not in valid_types:
                # לא בהכרח שגיאה, אבל אזהרה
                pass

        return len(issues) == 0, issues

    def _fix_common_issues(self, code: str) -> str:
        """תיקון שגיאות נפוצות."""
        fixed = code

        for pattern, replacement in self.COMMON_FIXES:
            if callable(replacement):
                fixed = re.sub(pattern, replacement, fixed)
            else:
                fixed = re.sub(pattern, replacement, fixed)

        # הסר קוד שלא עובד ב-command script
        lines = fixed.split("\n")
        cleaned_lines = []
        skip_until_end = False

        for line in lines:
            # דלג על בלוקים של LocalScript
            if "LocalScript" in line or "StarterPlayer" in line:
                skip_until_end = True
                continue

            if skip_until_end:
                if line.strip().startswith("]]"):
                    skip_until_end = False
                continue

            # הסר שורות עם קוד אסור
            has_forbidden = False
            for forbidden in self.FORBIDDEN_IN_COMMAND:
                if forbidden in line and "Name" not in line:
                    has_forbidden = True
                    break

            if not has_forbidden:
                cleaned_lines.append(line)

        fixed = "\n".join(cleaned_lines)

        # וודא שיש את הסיום הנכון
        if "game.Selection:Set(parts)" not in fixed:
            fixed += "\ngame.Selection:Set(parts)"

        return fixed

    def _simplify_for_command_script(self, code: str) -> str:
        """
        פשט קוד למשהו שעובד בוודאות ב-command script.
        מסיר GUI, LocalScript, וכל דבר שדורש RunTime.
        """
        lines = code.split("\n")
        safe_lines = []
        in_unsafe_block = False

        for line in lines:
            # דלג על בלוקים לא בטוחים
            if any(x in line for x in ["guiCode", "LocalScript", "[[", "]]", "spawn(", "task.spawn("]):
                if "[[" in line:
                    in_unsafe_block = True
                if "]]" in line:
                    in_unsafe_block = False
                continue

            if in_unsafe_block:
                continue

            # דלג על Touch events ו-RunService
            if any(x in line for x in [".Touched:Connect", "RunService", "Heartbeat", "PlayerGui"]):
                continue

            safe_lines.append(line)

        result = "\n".join(safe_lines)

        # נקה שורות ריקות מיותרות
        result = re.sub(r'\n{3,}', '\n\n', result)

        return result

    def generate(self, command: str, context: str = "", max_retries: int = 3,
                 use_two_phase: bool = True) -> Dict[str, Any]:
        """
        יצירת קוד Lua עם רוטציה בין מודלים.

        Args:
            command: פקודה בעברית
            context: הקשר עולמי
            max_retries: מספר ניסיונות מקסימלי
            use_two_phase: האם להשתמש ב-Two-Phase Generation (ברירת מחדל: כן)

        Returns:
            Dict עם success, lua_code, וכו'
        """
        # Try Two-Phase first if enabled
        if use_two_phase:
            result = self.generate_two_phase(command, context)
            if result and result.get("success"):
                return result

        # Original direct generation
        if not self.api_key and not self.claude_cli_available:
            return {"success": False, "error": "No API key and no Claude CLI"}

        # קבל הנחיות מיקום
        position_hint = self.get_position_hint()

        system_prompt = f"""You are an EXPERT Lua code generator for Roblox Studio COMMAND SCRIPTS.
You build objects with REALISTIC PHYSICS and PROPORTIONS.

CRITICAL - This code runs in a PLUGIN COMMAND SCRIPT, NOT a LocalScript!
FORBIDDEN: LocalPlayer, PlayerGui, StarterPlayer, LocalScript, spawn(), task.spawn(), RunService, .Touched events

{position_hint}

PHYSICS RULES (VERY IMPORTANT):
1. GRAVITY: Objects must rest on the ground. Y position = half the object height (bottom at Y=0)
2. FOUNDATIONS: Buildings need foundation/floor. Tall buildings need WIDER bases for stability
3. PROPORTIONS: Doors=4x8 studs, Windows=4x4, Person height=6 studs, Car=12x5x6
4. MATERIALS: Wood for doors/floors, Brick for walls, Glass for windows (transparency=0.5), Metal for vehicles, Concrete for foundations, Grass for nature
5. STRUCTURAL: Walls support roofs. Pillars support bridges. Legs support tables. No floating parts!
6. VEHICLES: Anchored=false, with proper wheels touching ground at Y=wheel_radius
7. STACKING: Objects ON other objects must have their Y = base_object_top + half_height
8. WATER: Use Glass material with Cyan color and transparency=0.3-0.5

CREATIVE RULES:
- Add DETAILS: door handles, window frames, chimneys, balconies, steps
- Use VARIED materials (not everything Plastic!)
- Add DEPTH with layered parts
- Use WedgePart for roofs, slopes, ramps
- Add lighting: Neon material parts for lamps/headlights

FORMAT:
1. Start with: local parts = {{}}
2. Create objects with Instance.new()
3. Set properties with PHYSICS in mind
4. table.insert(parts, obj)
5. End with: game.Selection:Set(parts)

World context: {context if context else "Empty world"}

OUTPUT ONLY VALID LUA CODE. NO EXPLANATIONS. NO MARKDOWN."""

        prompt = f"Create Lua code for: {command}"

        tried_models = []

        for attempt in range(max_retries):
            model = self._get_next_model()
            if not model:
                break

            self.on_status(f"Attempt {attempt + 1}: {model['name']}")
            tried_models.append(model['name'])

            # קריאה למודל
            raw_response = self._call_model(model["id"], prompt, system_prompt)

            if not raw_response:
                self.failed_models.add(model["id"])
                self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)
                continue

            # חילוץ קוד
            lua_code = self._extract_lua_code(raw_response)

            if not lua_code:
                self.on_status(f"{model['name']} returned invalid code")
                self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)
                continue

            # פישוט לקוד בטוח
            lua_code = self._simplify_for_command_script(lua_code)

            # תיקון שגיאות נפוצות
            lua_code = self._fix_common_issues(lua_code)

            # בדיקת תקינות
            is_valid, issues = self._validate_lua_code(lua_code)

            if is_valid:
                self.on_status(f"Valid code from {model['name']} ({len(lua_code)} chars)")

                # הזז את כל המיקומים אם יש יצירות קודמות
                if self.creation_count > 0:
                    lua_code = self._shift_positions(lua_code, self.next_x_offset)
                    self.on_status(f"Shifted positions by X={self.next_x_offset}")

                # רשום את היצירה ועדכן מיקום הבא
                self.register_creation(self.next_x_offset, 0, 100, 100)

                # אפס את הכישלונות אחרי הצלחה
                self.failed_models.clear()
                return {
                    "success": True,
                    "lua_code": lua_code,
                    "model": model["name"],
                    "attempts": attempt + 1,
                    "tried_models": tried_models
                }
            else:
                self.on_status(f"Code issues: {', '.join(issues)}")
                # נסה לתקן שוב
                lua_code = self._fix_common_issues(lua_code)
                is_valid, _ = self._validate_lua_code(lua_code)
                if is_valid:
                    return {
                        "success": True,
                        "lua_code": lua_code,
                        "model": model["name"],
                        "attempts": attempt + 1,
                        "fixed": True
                    }

            self.current_model_index = (self.current_model_index + 1) % len(self.MODELS)

        return {
            "success": False,
            "error": "All models failed",
            "tried_models": tried_models
        }


# בדיקות
if __name__ == "__main__":
    from dotenv import load_dotenv
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

    print("=" * 60)
    print("Testing Two-Phase Robust Generator")
    print("=" * 60)

    gen = RobustLuaGenerator()

    # Test preset blueprints (instant)
    preset_tests = [
        "בנה בית",
        "צור עץ ירוק",
        "בנה מכונית אדומה",
        "צור מגדל",
    ]

    print("\n[PRESETS] Testing instant response:")
    print("-" * 40)
    for test in preset_tests:
        print(f"\n> Command: {test}")
        result = gen.generate(test)
        if result["success"]:
            method = result.get("method", "unknown")
            print(f"  [OK] Method: {method}")
            if "blueprint" in result:
                print(f"  Blueprint: {result['blueprint']}")
            print(f"  Code: {len(result['lua_code'])} chars")
        else:
            print(f"  [FAIL] {result.get('error')}")

    # Test special builders
    special_tests = [
        "בנה עיר עם 3 בתים",
        "צור אובי עם 5 פלטפורמות",
    ]

    print("\n\n[SPECIAL] Testing special builders:")
    print("-" * 40)
    for test in special_tests:
        print(f"\n> Command: {test}")
        result = gen.generate(test)
        if result["success"]:
            method = result.get("method", "unknown")
            print(f"  [OK] Method: {method}")
            if "num_houses" in result:
                print(f"  Houses: {result['num_houses']}")
            if "num_platforms" in result:
                print(f"  Platforms: {result['num_platforms']}")
            print(f"  Code: {len(result['lua_code'])} chars")
        else:
            print(f"  [FAIL] {result.get('error')}")

    # Test LLM generation (requires API)
    if gen.api_key:
        llm_tests = [
            "בנה ארמון עם 4 מגדלים",
            "צור גשר גדול",
        ]

        print("\n\n[LLM] Testing Two-Phase with LLM:")
        print("-" * 40)
        for test in llm_tests:
            print(f"\n> Command: {test}")
            result = gen.generate(test)
            if result["success"]:
                method = result.get("method", "unknown")
                model = result.get("model", "N/A")
                print(f"  [OK] Method: {method}, Model: {model}")
                print(f"  Code: {len(result['lua_code'])} chars")
                print(f"  First 500 chars:")
                print(result["lua_code"][:500])
            else:
                print(f"  [FAIL] {result.get('error')}")
    else:
        print("\n[WARN] No API key - skipping LLM tests")

    print("\n" + "=" * 60)
    print("Tests completed")
    print("=" * 60)
