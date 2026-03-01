# Contributing to Roblox Voice Creator 🤝

First off — **thank you!** Every contribution makes this project better for kids who want to create games.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/roblox-voice-creator-2026.git
   cd roblox-voice-creator-2026
   ```
3. **Install** dependencies:
   ```bash
   pip install flask requests openai-whisper sounddevice numpy pygame edge-tts
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/my-amazing-feature
   ```

## 📋 What Can I Work On?

### 🟢 Easy — Great First Issues

**Add a new preset object** (`src/blueprint_schema.py`):
- Each preset is a Python dict with parts (name, type, size, position, color, material)
- Look at existing presets like `house` or `tree` for examples
- Add Hebrew keyword mappings in `HEBREW_OBJECT_MAP`

**Add a new Hebrew keyword** (`src/blueprint_schema.py` or `src/behavior_blueprints.py`):
- Find Hebrew words that map to existing presets/behaviors
- Add them to the keyword dictionaries

**Improve documentation**:
- Fix typos, clarify instructions, add examples

### 🟡 Medium

**Add a new behavior** (`src/behavior_blueprints.py`):
- Each behavior is a `BehaviorSpec` with Lua script source
- The Lua runs inside Roblox as a Script/LocalScript
- Test that the Lua is valid and works in Roblox Studio

**Add a new game system** (`src/game_systems_builder.py`):
- Complete game mechanics (inventory, shop, quest system, etc.)
- Include Hebrew detection keywords

**Add a new language**:
- Create keyword mappings for English, Arabic, Spanish, etc.
- The architecture already supports multi-language — just add keyword dicts

### 🔴 Hard

**Extend the Roblox plugin** (`roblox_plugin/VoiceCreator.lua`):
- Add new Lua functions the plugin can execute
- Improve workspace scanning
- Add animation support

**Improve AI generation** (`src/robust_generator.py`):
- Better LLM prompts for more accurate Lua
- New model integrations
- Smarter fallback logic

## 🧪 Testing Your Changes

```bash
# Run the basic module test
python -c "from src.behavior_blueprints import ALL_BEHAVIORS; print(f'{len(ALL_BEHAVIORS)} behaviors OK')"
python -c "from src.game_systems_builder import GAME_SYSTEMS; print(f'{len(GAME_SYSTEMS)} systems OK')"

# Test Hebrew detection
python -c "
from src.behavior_blueprints import find_behavior_for_command
result = find_behavior_for_command('YOUR_HEBREW_COMMAND')
print(f'Detected: {result[0] if result else \"NOT FOUND\"}')
"

# Run the full app (needs Roblox Studio for end-to-end testing)
python src/kids_interface.py
```

## 📝 Pull Request Guidelines

1. **Keep PRs focused** — One feature or fix per PR
2. **Test your changes** — Make sure existing features still work
3. **Write clear commit messages** — Describe what and why
4. **Update keyword counts** — If you add presets/behaviors, update the counts in README
5. **Hebrew accuracy** — If adding Hebrew keywords, make sure they're natural (ask a native speaker!)

## 🏗️ Project Structure Quick Reference

| File | Purpose | When to edit |
|---|---|---|
| `src/blueprint_schema.py` | Object presets + Hebrew mappings | Adding new objects |
| `src/behavior_blueprints.py` | Behavior scripts + Hebrew keywords | Adding game logic |
| `src/game_systems_builder.py` | Complete game systems | Adding game mechanics |
| `src/direct_controller.py` | Command routing + intent detection | Changing how commands are interpreted |
| `src/robust_generator.py` | AI Lua generation | Improving AI output |
| `src/template_builder.py` | Blueprint → Lua conversion | Changing Lua generation format |
| `src/kids_interface.py` | Tkinter UI | Changing the user interface |
| `src/command_server.py` | HTTP bridge to Roblox | Changing communication protocol |
| `roblox_plugin/VoiceCreator.lua` | Roblox Studio plugin | Adding plugin features |

## 💬 Questions?

Open an [issue](https://github.com/liortesta/roblox-voice-creator-2026/issues) with the `question` label. We're happy to help!

## 🙏 Code of Conduct

Be kind. Be respectful. We're building something for children — let's keep our community welcoming for everyone.
