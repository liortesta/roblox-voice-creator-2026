<div align="center">

# 🎙️ Roblox Voice Creator 2026

### Build Roblox Games by Speaking — Hebrew 🇮🇱 & English 🇺🇸

**The world's first voice-controlled Roblox game builder.**
A 3-year-old can build a 3D game. No coding. No typing. Just speak.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Roblox Studio](https://img.shields.io/badge/Roblox-Studio-red.svg)](https://create.roblox.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Lines of Code](https://img.shields.io/badge/Lines-20%2C000+-purple.svg)](#architecture)

<br>

> **"בנה בית אדום גדול"** / **"build a big red house"** → A large red house appears in Roblox Studio
>
> **"תוסיף ריצה לדמות"** / **"add running to character"** → The character starts running with pathfinding AI
>
> **"תעשה מערכת חיים"** / **"add health system"** → Full health system with GUI, damage, and respawn

<br>

[🚀 Quick Start](#-quick-start) · [🎬 How It Works](#-how-it-works) · [🧠 Features](#-features) · [🤝 Contributing](#-contributing)

</div>

---

## 💡 The Problem

Millions of kids want to create Roblox games, but **Lua scripting is hard**. Even adults struggle with it. The learning curve kills creativity before it starts.

## ✨ The Solution

What if a child could just **say what they want** — in their own language — and it **appears in the game**?

```
🎤 Child speaks Hebrew  →  🧠 AI understands intent  →  🔨 Lua code generated  →  🎮 Object appears in Roblox
```

This isn't a toy demo. It generates **real production Lua** — scripts with physics, pathfinding, interactions, and complete game systems. 20,000 lines of battle-tested code.

---

## 🎬 How It Works

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  🎤 Voice Input  │────▶│  Whisper STT  │────▶│  AI Processing   │────▶│  Roblox Studio  │
│  (Hebrew/Any)    │     │  (OpenAI)     │     │  (Multi-LLM)     │     │  (Plugin v8.0)  │
└─────────────────┘     └──────────────┘     └──────────────────┘     └─────────────────┘
                                                      │
                                              ┌───────┴────────┐
                                              │                │
                                        ┌─────▼─────┐   ┌─────▼─────┐
                                        │  58 Smart  │   │  25 Live  │
                                        │  Presets   │   │ Behaviors │
                                        └───────────┘   └───────────┘
```

### The Pipeline

1. **Speech-to-Text** — OpenAI Whisper transcribes Hebrew speech in real-time
2. **Intent Detection** — 100+ Hebrew keyword mappings understand what the child wants
3. **Blueprint Matching** — 58 preset blueprints for instant object creation (deterministic, no AI delay)
4. **Behavior Engine** — 25 pre-built behavior scripts for live game logic
5. **AI Fallback** — For complex requests, multi-LLM rotation (DeepSeek → Qwen → Claude) generates custom Lua
6. **Plugin Execution** — Roblox Studio plugin receives Lua via HTTP and executes it instantly

**Key insight:** Presets are instant and reliable. AI is the fallback, not the bottleneck. This makes the system feel **magical** — say something, see it appear in under a second.

---

## 🧠 Features

### 🏗️ Voice Building — 58 Presets
Say it, and it appears:

| Hebrew Command | Result |
|---|---|
| "בנה בית אדום" | Red house with walls, door, windows, roof |
| "תעשה מכונית כחולה" | Driveable car with VehicleSeat + physics |
| "בנה עץ ירוק גדול" | Tree with trunk and leaf canopy |
| "תעשה שומר" | NPC guard with patrol behavior |
| "גשם" | Rain particle system |
| "שלג" | Snow weather effect |
| "מדורה" | Campfire with fire + light + smoke |

### 🧬 Live Behaviors — 25 Scripts (v8.0)
Add real game logic by voice:

| Command | What Happens |
|---|---|
| "תוסיף ריצה לדמות" | Character runs with WalkSpeed + direction changes |
| "תגרום לו לעקוב" | NPC follows nearest player with PathfindingService |
| "תוסיף סיור" | NPC patrols between waypoints automatically |
| "דלת שנפתחת בלחיצה" | ClickDetector + TweenService door animation |
| "מטבע לאיסוף" | Collectible coin with spin animation + Touched event |
| "אויב שתוקף" | Enemy NPC with detection radius + damage dealing |
| "תוסיף נהיגה" | Full vehicle system with VehicleSeat + throttle |
| "תעשה טלפורט" | Teleportation pad with particle effects |
| "טרמפולינה" | Bouncing platform with VectorForce |

### 🎮 Game Systems — 6 Complete Systems
Full game mechanics in one command:

| Command | System |
|---|---|
| "מערכת חיים" | Health bar + damage + death + respawn |
| "מערכת כסף" | Currency + leaderboard + earning system |
| "תעשה מירוץ" | Race with checkpoints + timer + finish line |
| "Respawn" | Spawn points + death handling |
| "מחזור יום לילה" | Dynamic lighting cycle with ColorCorrection |
| "מטבעות לאיסוף" | Coin spawner + collection + scoring |

### 🤖 AI Chat (v8.0)
For anything not covered by presets — type in natural Hebrew:

```
"תשנה את המהירות של המכונית ל-100"
"תוסיף סקריפט שהדמות קופצת כל 3 שניות"
"תגרום לכל המטבעות להיעלם אחרי 10 שניות"
```

The AI **scans your entire Roblox workspace** (every object, script, property), understands the current game state, and generates targeted Lua modifications. It's like having a Roblox developer sitting next to you.

### 🔌 Plugin Capabilities (v8.0)
The Roblox Studio plugin (1,200+ lines of Lua) can:
- **Inject Scripts** — Create `Script` and `LocalScript` with `.Source` directly
- **Create NPCs** — Full humanoid characters with animations
- **Build Vehicles** — Working cars with seats and physics
- **Add Interactions** — ClickDetector, ProximityPrompt, Touched events
- **Scan Workspace** — Reads all objects, scripts, properties for AI context
- **Auto-sync** — Polls HTTP server every 0.5s for new commands

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Roblox Studio** (free at [create.roblox.com](https://create.roblox.com))
- **Microphone** (for voice commands)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/liortesta/roblox-voice-creator-2026.git
cd roblox-voice-creator-2026

# 2. Install dependencies
pip install flask requests openai-whisper sounddevice numpy pygame edge-tts

# 3. Copy the plugin to Roblox Studio
# Windows:
copy roblox_plugin\VoiceCreator.lua %LOCALAPPDATA%\Roblox\Plugins\VoiceCreator.lua
# Mac:
cp roblox_plugin/VoiceCreator.lua ~/Documents/Roblox/Plugins/VoiceCreator.lua

# 4. Launch!
python src/kids_interface.py
```

### First Steps
1. Open **Roblox Studio** → Create a new Baseplate
2. Click **"Voice Creator"** in the plugin toolbar — it auto-connects to `localhost:8080`
3. In the app, click the **microphone button** or type a command
4. Say **"בנה בית"** (build a house) — watch it appear!

### Optional: AI Features
For AI Chat and advanced generation, set up an API key:
```bash
# Option A: OpenRouter (access to multiple models)
set OPENROUTER_API_KEY=your-key-here

# Option B: Anthropic Claude
set ANTHROPIC_API_KEY=your-key-here
```

---

## 🏗️ Architecture

```
roblox-voice-creator-2026/
├── src/
│   ├── kids_interface.py        # Kid-friendly Tkinter UI (1,500+ lines)
│   ├── direct_controller.py     # Main orchestrator: Hebrew → Lua
│   ├── robust_generator.py      # Multi-LLM Lua generator with fallback rotation
│   ├── blueprint_schema.py      # 58 preset object blueprints
│   ├── behavior_blueprints.py   # 25 behavior scripts library
│   ├── game_systems_builder.py  # 6 complete game systems
│   ├── template_builder.py      # JSON blueprint → deterministic Lua converter
│   ├── command_server.py        # Flask HTTP bridge (Python ↔ Roblox)
│   └── world_state.py           # World tracking + collision detection
├── roblox_plugin/
│   └── VoiceCreator.lua         # Roblox Studio plugin (1,200+ lines)
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

**~20,000 lines** of Python + Lua

### Design Principles

| Principle | Why |
|---|---|
| **Deterministic first, AI second** | Presets are instant and reliable. AI is the fallback. No waiting. |
| **Hebrew-native** | Not translated English. Built for Hebrew from the ground up with 100+ keyword mappings. |
| **Plugin-as-runtime** | The plugin can inject Scripts with `.Source`, enabling live game logic — not just static parts. |
| **Multi-LLM rotation** | If one model fails, try the next. DeepSeek → Qwen → Claude. Always deliver. |
| **Workspace-aware AI** | AI Chat scans your actual game state before generating code. It sees what you see. |

---

## 🗺️ Roadmap

We're building the future of game creation. Here's what's next:

- [x] **English support** — Full English voice commands (v8.1)
- [ ] **Arabic support** — Voice commands in Arabic
- [ ] **Animation system** — "תגרום לדמות לרקוד" (make the character dance)
- [ ] **Terrain generation** — "תעשה הר עם שלג" (make a snowy mountain)
- [ ] **Sound/Music system** — "תוסיף מוזיקה" (add background music)
- [ ] **Visual behavior editor** — Drag-and-drop behavior nodes
- [ ] **Multiplayer building** — Multiple kids building the same game
- [ ] **Mobile companion app** — Voice control from your phone
- [ ] **One-click publish** — Publish to Roblox directly from the app

**Want to tackle any of these?** See [Contributing](#-contributing)!

---

## 🤝 Contributing

We'd love your help! This project is open source and welcoming to all skill levels.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

### Quick ways to contribute

| Area | What to do | Difficulty |
|---|---|---|
| **New presets** | Add object blueprints in `blueprint_schema.py` | Easy |
| **New behaviors** | Add game logic scripts in `behavior_blueprints.py` | Medium |
| **New languages** | Add English/Arabic/Spanish keyword mappings | Easy |
| **AI prompts** | Improve Lua generation in `robust_generator.py` | Medium |
| **Game systems** | Add new systems in `game_systems_builder.py` | Medium |
| **Bug reports** | Try building games and tell us what breaks | Easy |
| **Plugin features** | Extend `VoiceCreator.lua` capabilities | Hard |

### Tech Stack

| Component | Technology |
|---|---|
| UI | Python Tkinter |
| Speech-to-Text | OpenAI Whisper |
| Text-to-Speech | Microsoft Edge TTS (Hebrew) |
| AI Models | DeepSeek / Qwen / Claude (multi-LLM rotation) |
| HTTP Bridge | Flask |
| Game Engine | Roblox Studio (Luau) |
| Plugin | Roblox Studio Plugin API |

---

## 🌍 Vision

> Every child deserves to be a game creator — regardless of their language, age, or coding ability.

Roblox Voice Creator is a step toward **democratizing game development**. Today it's Hebrew. Tomorrow it's every language. The goal is simple: **if you can imagine it, you can say it, and it becomes real.**

---

## ❓ FAQ

**Is this real?** Yes. 20,000 lines of working code. 58 presets. 25 behaviors. 6 game systems. All tested.

**What age is this for?** 3 years old and up. If a child can speak, they can create.

**Do I need to know Lua?** No. That's the whole point.

**Does it work in English?** Yes! Full English support was added in v8.1. Say "build a house" or "בנה בית" — both work.

**Is it free?** Completely. MIT license. The only cost is optional API keys for AI features.

**Can I use this commercially?** Yes, MIT license allows it. Just give credit.

---

## 📄 License

MIT License — see [LICENSE](LICENSE). Use it, fork it, build on it.

---

<div align="center">

**Built with ❤️ by [Lior Testa](https://github.com/liortesta)**

🇮🇱 Made in Israel

[![Twitter Follow](https://img.shields.io/twitter/follow/TestaLior?style=social)](https://x.com/TestaLior)

If you think voice-controlled game building is the future — **⭐ Star this repo!**

[Report Bug](https://github.com/liortesta/roblox-voice-creator-2026/issues) · [Request Feature](https://github.com/liortesta/roblox-voice-creator-2026/issues) · [Contribute](CONTRIBUTING.md) · [Twitter](https://x.com/TestaLior)

</div>
