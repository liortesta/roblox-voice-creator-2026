# -*- coding: utf-8 -*-
"""
Voice Creator Kids Edition v3.0 - For Kids Age 3+
===================================================
Ultra-friendly interface with:
- HUGE buttons with big emojis
- Voice-first design (giant mic button)
- Tabbed categories for easy navigation
- Bot character that talks
- Smart object modification
- 16+ ready-made game templates
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os
import sys
from datetime import datetime

# Text-to-Speech — Edge TTS (natural voice) with pyttsx3 fallback
EDGE_TTS_AVAILABLE = False
TTS_AVAILABLE = False
try:
    import edge_tts
    import asyncio
    import pygame
    # Fix Windows asyncio ProactorEventLoop RuntimeError on close
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    EDGE_TTS_AVAILABLE = True
    TTS_AVAILABLE = True
    print("Edge TTS loaded - natural Hebrew voice!")
except ImportError:
    try:
        import pyttsx3
        TTS_AVAILABLE = True
        print("Note: Using pyttsx3 fallback (install edge-tts for natural voice)")
    except ImportError:
        print("Note: No TTS available, voice feedback disabled")

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from direct_controller import DirectRobloxController as DirectController
from command_server import start_server

# ============================================
# THEME - Bright, fun, kid-friendly
# ============================================
THEME = {
    'bg': '#0F0F1A',
    'bg_light': '#1A1A30',
    'card': '#252545',
    'card_hover': '#2E2E55',
    'accent_pink': '#FF6B9D',
    'accent_blue': '#45B7D1',
    'accent_green': '#4ECDC4',
    'accent_yellow': '#FFE66D',
    'accent_purple': '#A78BFA',
    'accent_orange': '#FF9F43',
    'accent_red': '#FF6B6B',
    'accent_cyan': '#22D3EE',
    'text': '#FFFFFF',
    'text_dim': '#8B8BA7',
    'text_dark': '#4A4A6A',
    'success': '#4ADE80',
    'warning': '#FBBF24',
    'error': '#F87171',
    'mic_ready': '#4ADE80',
    'mic_recording': '#F87171',
    'bot_bubble': '#2D2D50',
}

# ============================================
# GAME TEMPLATES - Organized by category
# ============================================
GAME_CATEGORIES = {
    "worlds": {
        "label": "עולמות",
        "icon": "🌍",
        "color": THEME['accent_blue'],
        "games": {
            "עיר קטנה": {
                "icon": "🏙️",
                "command": "בנה עיר קטנה עם 5 בתים בצבעים שונים, כבישים, עצים, ומכוניות"
            },
            "כפר קסום": {
                "icon": "🏡",
                "command": "בנה כפר קסום עם 3 בקתות עץ, שביל אבנים, גשר מעל נחל, ועצים גדולים"
            },
            "אי טרופי": {
                "icon": "🏝️",
                "command": "בנה אי טרופי עם חוף חול, דקלים, צריף במבוק, וסירה קטנה"
            },
            "תחנת חלל": {
                "icon": "🚀",
                "command": "בנה תחנת חלל עם חללית גדולה, כוכבים, כדור הארץ ברקע, ואסטרונאוטים"
            },
        }
    },
    "adventures": {
        "label": "הרפתקאות",
        "icon": "⚔️",
        "color": THEME['accent_red'],
        "games": {
            "טירה קסומה": {
                "icon": "🏰",
                "command": "בנה טירה גדולה עם 4 מגדלים, חומות, שער גדול, וחפיר מים סביב"
            },
            "אובי פארקור": {
                "icon": "🏃",
                "command": "בנה מסלול אובי עם 10 פלטפורמות קפיצה, קירות טיפוס, רצפה מסתובבת, וקו סיום עם זיקוקים"
            },
            "מבוך ענק": {
                "icon": "🔮",
                "command": "בנה מבוך גדול עם קירות גבוהים, מלכודות, אוצר בסוף, ולפידים על הקירות"
            },
            "מערת דרקון": {
                "icon": "🐉",
                "command": "בנה מערה חשוכה עם סטלקטיטים, אוצרות זהב, דרקון גדול, ולבה זורמת"
            },
        }
    },
    "fun": {
        "label": "כיף",
        "icon": "🎉",
        "color": THEME['accent_yellow'],
        "games": {
            "מגרש משחקים": {
                "icon": "🎢",
                "command": "בנה מגרש משחקים עם מגלשה גדולה, נדנדות, מתקן טיפוס, קרוסלה, וספסלים"
            },
            "פארק מים": {
                "icon": "🏊",
                "command": "בנה פארק מים עם בריכה גדולה כחולה, 3 מגלשות מים צבעוניות, כיסאות נוח, ושמשיות"
            },
            "קרקס": {
                "icon": "🎪",
                "command": "בנה קרקס עם אוהל גדול אדום וצהוב, במה במרכז, יציעים, ודגלים צבעוניים"
            },
            "מירוץ מכוניות": {
                "icon": "🏎️",
                "command": "בנה מסלול מירוץ עם 4 מכוניות צבעוניות, מסלול ארוך מתפתל, קהל, ודגלי סיום"
            },
        }
    },
    "action": {
        "label": "אקשן",
        "icon": "⚡",
        "color": THEME['accent_orange'],
        "games": {
            "מסלול מטבעות": {
                "icon": "🪙",
                "command": "בנה שביל מטבעות, טרמפולינה, במה מסתובבת, וצ'קפוינט"
            },
            "מסלול לבה": {
                "icon": "🌋",
                "command": "בנה רצפת לבה, פלטפורמות קפיצה, מטבעות, וצ'קפוינט בסוף"
            },
            "מירוץ מהירות": {
                "icon": "⚡",
                "command": "בנה מסלול עם בוסט מהירות, טרמפולינות, במות מסתובבות, ומטבעות"
            },
            "עולם קסמים": {
                "icon": "🔮",
                "command": "בנה טלפורטים, מדורות, במות מסתובבות עם ניצוצות, ומטבעות מסתובבים"
            },
        }
    },
    "minigames": {
        "label": "מיני-גיימס",
        "icon": "🏆",
        "color": THEME['accent_yellow'],
        "games": {
            "אסוף מטבעות": {
                "icon": "🪙",
                "command": "בנה משחק מטבעות"
            },
            "מירוץ מהירות": {
                "icon": "🏁",
                "command": "בנה מירוץ"
            },
            "אובי מטורף": {
                "icon": "🏃",
                "command": "בנה אובי עם 15 פלטפורמות, לבה, טרמפולינות, מטבעות, וצ'קפוינטים"
            },
            "זירת לחימה": {
                "icon": "⚔️",
                "command": "בנה אויבים, מטבעות, לידרבורד, לבות ריפוי, וצ'קפוינט"
            },
        }
    },
    "nature": {
        "label": "טבע",
        "icon": "🌿",
        "color": THEME['accent_green'],
        "games": {
            "חוות חיות": {
                "icon": "🐄",
                "command": "בנה חווה עם רפת אדומה, גדר עץ, עצי תפוחים, לול תרנגולות, ובריכת ברווזים"
            },
            "גן חיות": {
                "icon": "🦁",
                "command": "בנה גן חיות עם מתחמים לחיות, שבילים, שלטים, עצים, וכניסה גדולה עם שער"
            },
            "יער קסום": {
                "icon": "🌲",
                "command": "בנה יער קסום עם עצים ענקיים, פטריות צבעוניות, נחל, גשר עץ, ובית עץ על עץ"
            },
            "גן פרחים": {
                "icon": "🌸",
                "command": "בנה גן פרחים ענק עם ערוגות צבעוניות, מזרקה במרכז, שבילים, ספסלים, ופרגולה"
            },
        }
    },
    "demo": {
        "label": "עולמות מוכנים",
        "icon": "🌍",
        "color": THEME['accent_purple'],
        "games": {
            "כפר חי": {
                "icon": "🏘️",
                "command": "בנה בית, בית, בית, עץ, עץ, מכונית, שומר, חבר, מדורה, גדר"
            },
            "בסיס צבאי": {
                "icon": "🎖️",
                "command": "בנה שומר, שומר, אויב, אויב, מגדל, גדר, גדר, מדורה, לידרבורד"
            },
            "פארק קסום": {
                "icon": "✨",
                "command": "בנה עץ, עץ, מזרקה, טרמפולינה, מטבע, מטבע, מטבע, חבר, שקיעה"
            },
            "מירוץ אקסטרים": {
                "icon": "🏎️",
                "command": "בנה מירוץ, מכונית, מכונית, מטבע, מטבע, מטבע, לידרבורד"
            },
        }
    },
}

# Quick-build items with BIG icons - Row 1: Common objects
QUICK_BUILDS = [
    {"icon": "🏠", "label": "בית", "cmd": "בנה בית", "color": THEME['accent_orange']},
    {"icon": "🌳", "label": "עץ", "cmd": "בנה עץ", "color": THEME['accent_green']},
    {"icon": "🚗", "label": "מכונית", "cmd": "בנה מכונית", "color": THEME['accent_red']},
    {"icon": "🗼", "label": "מגדל", "cmd": "בנה מגדל", "color": THEME['accent_purple']},
    {"icon": "🌉", "label": "גשר", "cmd": "בנה גשר", "color": THEME['accent_blue']},
    {"icon": "⛲", "label": "מזרקה", "cmd": "בנה מזרקה", "color": THEME['accent_cyan']},
    {"icon": "🚁", "label": "מסוק", "cmd": "בנה מסוק", "color": THEME['accent_pink']},
    {"icon": "✈️", "label": "מטוס", "cmd": "בנה מטוס", "color": THEME['accent_yellow']},
]

# Second row of quick builds
QUICK_BUILDS_2 = [
    {"icon": "⛵", "label": "סירה", "cmd": "בנה סירה", "color": THEME['accent_blue']},
    {"icon": "🪑", "label": "כיסא", "cmd": "בנה כיסא", "color": THEME['accent_orange']},
    {"icon": "🛝", "label": "מגלשה", "cmd": "בנה מגלשה", "color": THEME['accent_yellow']},
    {"icon": "🪨", "label": "סלע", "cmd": "בנה סלע", "color": THEME['accent_purple']},
    {"icon": "🌸", "label": "פרח", "cmd": "בנה פרח", "color": THEME['accent_pink']},
    {"icon": "🏊", "label": "בריכה", "cmd": "בנה בריכה", "color": THEME['accent_cyan']},
    {"icon": "💡", "label": "פנס", "cmd": "בנה פנס רחוב", "color": THEME['accent_yellow']},
    {"icon": "🎯", "label": "כדור", "cmd": "בנה כדור", "color": THEME['accent_red']},
]

# Third row — NEW v4.0 objects
QUICK_BUILDS_3 = [
    {"icon": "🚀", "label": "רקטה", "cmd": "בנה רקטה", "color": THEME['accent_red']},
    {"icon": "🐕", "label": "כלב", "cmd": "בנה כלב", "color": THEME['accent_orange']},
    {"icon": "🐱", "label": "חתול", "cmd": "בנה חתול", "color": THEME['accent_purple']},
    {"icon": "🎂", "label": "עוגה", "cmd": "בנה עוגה", "color": THEME['accent_pink']},
    {"icon": "🍦", "label": "גלידה", "cmd": "בנה גלידה", "color": THEME['accent_cyan']},
    {"icon": "🎸", "label": "גיטרה", "cmd": "בנה גיטרה", "color": THEME['accent_yellow']},
    {"icon": "⭐", "label": "כוכב", "cmd": "בנה כוכב", "color": THEME['accent_yellow']},
    {"icon": "🛸", "label": "חללית", "cmd": "בנה חללית", "color": THEME['accent_blue']},
]

# Fourth row — NEW v5.0 Interactive & Action objects
QUICK_BUILDS_4 = [
    {"icon": "🪙", "label": "מטבע", "cmd": "בנה מטבע", "color": THEME['accent_yellow']},
    {"icon": "🤸", "label": "טרמפולינה", "cmd": "בנה טרמפולינה", "color": THEME['accent_blue']},
    {"icon": "🌋", "label": "לבה", "cmd": "בנה לבה", "color": THEME['accent_red']},
    {"icon": "⚡", "label": "מהירות", "cmd": "בנה מהירות", "color": THEME['accent_green']},
    {"icon": "🌀", "label": "טלפורט", "cmd": "בנה טלפורט", "color": THEME['accent_purple']},
    {"icon": "🔥", "label": "מדורה", "cmd": "בנה מדורה", "color": THEME['accent_orange']},
    {"icon": "💫", "label": "במה מסתובבת", "cmd": "בנה במה מסתובבת", "color": THEME['accent_cyan']},
    {"icon": "🏁", "label": "צ'קפוינט", "cmd": "בנה צ'קפוינט", "color": THEME['accent_pink']},
]

# Fifth row — NEW v6.0 NPCs & Weather
QUICK_BUILDS_5 = [
    {"icon": "💂", "label": "שומר", "cmd": "בנה שומר", "color": THEME['accent_blue']},
    {"icon": "👹", "label": "אויב", "cmd": "בנה אויב", "color": THEME['accent_red']},
    {"icon": "🧑", "label": "חבר", "cmd": "בנה חבר", "color": THEME['accent_green']},
    {"icon": "🌧️", "label": "גשם", "cmd": "בנה גשם", "color": THEME['accent_blue']},
    {"icon": "❄️", "label": "שלג", "cmd": "בנה שלג", "color": THEME['accent_cyan']},
    {"icon": "🌙", "label": "לילה", "cmd": "בנה לילה", "color": THEME['accent_purple']},
    {"icon": "🌅", "label": "שקיעה", "cmd": "בנה שקיעה", "color": THEME['accent_orange']},
    {"icon": "🌫️", "label": "ערפל", "cmd": "בנה ערפל", "color": THEME['accent_purple']},
]

# Modify actions for smart logic
MODIFY_ACTIONS = [
    {"icon": "🚪", "label": "דלת", "cmd": "תוסיף דלת ל{object}", "color": THEME['accent_orange']},
    {"icon": "🪟", "label": "חלון", "cmd": "תוסיף חלונות ל{object}", "color": THEME['accent_blue']},
    {"icon": "🎨", "label": "צבע", "cmd": "תצבע את {object} בצבע אחר", "color": THEME['accent_pink']},
    {"icon": "📐", "label": "הגדל", "cmd": "תגדיל את {object} פי 2", "color": THEME['accent_green']},
    {"icon": "🔄", "label": "סובב", "cmd": "תסובב את {object}", "color": THEME['accent_cyan']},
    {"icon": "📋", "label": "שכפל", "cmd": "תשכפל את {object} ליד", "color": THEME['accent_purple']},
    {"icon": "🌳", "label": "עץ ליד", "cmd": "שים עץ ליד {object}", "color": THEME['accent_green']},
    {"icon": "🗑️", "label": "מחק", "cmd": "מחק את {object}", "color": THEME['accent_red']},
]


# ============================================
# ROBY PERSONALITY — warm, fun, encouraging
# ============================================
ROBY_PERSONALITY = {
    "success": [
        "יופי! בניתי {object}! נראה מעולה!",
        "וואו! תראה מה יצרתי! {object}!",
        "מוכן! {object} נראה מדהים!",
        "תראה תראה! {object} מוכן בשבילך!",
        "סיימתי! {object} יצא מושלם!",
        "הנה! {object} חדש! אני גאה!",
        "איזה יופי! {object} נראה בדיוק כמו אמיתי!",
        "בום! {object} מוכן! אני הכי טוב!",
    ],
    "world_success": [
        "וואו! בניתי עולם שלם! תראה כמה יפה!",
        "סיימתי לבנות! יש פה המון דברים מגניבים!",
        "העולם מוכן! בוא תסתכל מה עשיתי!",
        "איזה כיף! בנינו עולם שלם ביחד!",
    ],
    "thinking": [
        "רגע, אני חושב...",
        "מממ, בוא נראה...",
        "אני עובד על זה...",
        "חושב חושב... רגע!",
        "עובד בשבילך!",
        "בונה בונה! עוד רגע...",
    ],
    "error": [
        "אופס! לא הצלחתי. נסה שוב?",
        "לא הלך... ננסה אחרת?",
        "משהו לא עבד, אבל אני לא מוותר!",
        "הממ, לא יצא. אולי תנסח אחרת?",
    ],
    "happy": [
        "היי! מה נבנה היום?",
        "שלום חבר! בוא ניצור משהו מגניב!",
        "אני מוכן! בוא נבנה עולם!",
        "יש לי רעיונות! בוא נתחיל!",
    ],
    "listening": [
        "מקשיב לך...",
        "אני שומע, דבר!",
        "מקליט... ספר לי!",
    ],
    "greeting": [
        "היי! אני רובי! מה נבנה היום?",
        "שלום! מוכן ליצור דברים מדהימים?",
        "ברוך הבא! בוא נבנה משהו כיף!",
    ],
    "proud": [
        "תראה כמה אובייקטים בנינו! אנחנו צוות מעולה!",
        "העולם שלנו נראה מדהים!",
        "אנחנו בונים מהר! כל הכבוד!",
    ],
    "suggest": [
        "מה עם {suggestion}?",
        "רוצה שאבנה גם {suggestion}?",
        "אולי נוסיף {suggestion}?",
        "יש לי רעיון! בוא נבנה {suggestion}!",
    ],
    "improve": [
        "בוא נשפר! מוסיף עוד דברים!",
        "משדרג את מה שבנינו!",
        "עוד רגע יהיה פי עשר יותר טוב!",
    ],
}

# Suggestions after building — what to build next
BUILD_SUGGESTIONS = {
    "בית": ["עץ ליד הבית", "מכונית", "גדר", "גינה"],
    "עץ": ["עוד עצים", "ספסל", "פרח", "בית"],
    "מכונית": ["כביש", "חניה", "עוד מכונית", "רמזור"],
    "מגדל": ["חומות", "שער", "גשר", "עוד מגדל"],
    "כלב": ["בית לכלב", "חתול", "גדר", "עץ"],
    "חתול": ["כלב", "עץ", "ספסל", "בית"],
    "בריכה": ["כיסא נוח", "מגלשה", "עץ דקל", "שמשיה"],
    "default": ["בית", "עץ", "מכונית", "בריכה"],
}

# ============================================
# MULTI-LANGUAGE — Hebrew Whisper vocabulary boost
# ============================================
WHISPER_HEBREW_VOCAB = (
    "פקודות בנייה ברובלוקס סטודיו. "
    "בנה, צור, תבנה, תעשה, שים, הוסף, מחק, צבע, הגדל, הקטן, סובב, שכפל, "
    "בית, עץ, מכונית, טירה, מגדל, גשר, מזרקה, סירה, מסוק, מטוס, "
    "כיסא, שולחן, ספסל, מנורה, גדר, מגלשה, נדנדה, בריכה, סלע, פרח, כדור, "
    "אדום, כחול, ירוק, צהוב, לבן, שחור, כתום, ורוד, סגול, חום, אפור, "
    "ליד, מעל, מתחת, לפני, מאחורי, בתוך, על, משמאל, מימין, "
    "דלת, חלון, גג, קיר, רצפה, מדרגות, ארובה, מרפסת, "
    "דמות, שחקן, אויב, מטבע, כוכב, לב, חיים, נקודות, "
    "משחק, מירוץ, אובי, הרפתקה, קפיצה, ריצה, עפיפה, שחייה, "
    "עיר, כפר, חווה, פארק שעשועים, מבוך, מסלול, אצטדיון, "
    "רקטה, חללית, כוכב, ירח, כדור הארץ, "
    "כלב, חתול, סוס, דג, ציפור, "
    "עוגה, גלידה, פיצה, פסנתר, גיטרה, "
    "גדול, קטן, ענק, זעיר, ארוך, קצר, גבוה, נמוך, רחב, צר, "
    # v8.0 Behavior & Logic vocabulary
    "ריצה, לרוץ, קפיצה, לקפוץ, עפיפה, לעוף, סיבוב, להסתובב, נהיגה, לנהוג, "
    "עקוב, לעקוב, סיור, מסייר, "
    "תוקף, לתקוף, מדבר, לדבר, ידידותי, חברותי, "
    "דלת, נפתחת, לפתוח, לאסוף, מטבע, נזק, ריפוי, מרפא, "
    "טלפורט, טרמפולינה, פיצוץ, מתפוצץ, "
    "לידרבורד, ניקוד, צ'קפוינט, מהירות, בוסט, מוות, לבה, ספאון, טיימר, "
    "מערכת חיים, מערכת כסף, מירוץ, "
    "סקריפט, התנהגות, לוגיקה"
)

# Multi-language color mappings (for future)
MULTI_LANG_COLORS = {
    # Hebrew
    "אדום": "Bright red", "כחול": "Bright blue", "ירוק": "Bright green",
    "צהוב": "Bright yellow", "לבן": "White", "שחור": "Black",
    "כתום": "Neon orange", "ורוד": "Pink", "סגול": "Bright violet",
    # English
    "red": "Bright red", "blue": "Bright blue", "green": "Bright green",
    "yellow": "Bright yellow", "white": "White", "black": "Black",
    "orange": "Neon orange", "pink": "Pink", "purple": "Bright violet",
    # Russian
    "красный": "Bright red", "синий": "Bright blue", "зеленый": "Bright green",
    "желтый": "Bright yellow", "белый": "White", "черный": "Black",
    # Arabic
    "أحمر": "Bright red", "أزرق": "Bright blue", "أخضر": "Bright green",
    "أصفر": "Bright yellow", "أبيض": "White", "أسود": "Black",
    # Spanish
    "rojo": "Bright red", "azul": "Bright blue", "verde": "Bright green",
    "amarillo": "Bright yellow", "blanco": "White", "negro": "Black",
}

# Multi-language object mappings
MULTI_LANG_OBJECTS = {
    # Russian
    "дом": "house", "дерево": "tree", "машина": "car",
    "башня": "tower", "мост": "bridge", "фонтан": "fountain",
    "лодка": "boat", "вертолет": "helicopter", "самолет": "airplane",
    "стул": "chair", "стол": "table", "камень": "rock", "цветок": "flower",
    # Arabic
    "بيت": "house", "شجرة": "tree", "سيارة": "car",
    "برج": "tower", "جسر": "bridge", "نافورة": "fountain",
    # Spanish
    "casa": "house", "árbol": "tree", "coche": "car",
    "torre": "tower", "puente": "bridge", "fuente": "fountain",
    # English
    "house": "house", "tree": "tree", "car": "car",
    "tower": "tower", "bridge": "bridge", "fountain": "fountain",
    "boat": "boat", "helicopter": "helicopter", "airplane": "airplane",
    "chair": "chair", "table": "table", "rock": "rock", "flower": "flower",
}


class KidsInterface:
    def __init__(self, controller: DirectController):
        self.controller = controller
        self.root = None
        self.is_recording = False
        self.log_text = None
        self.command_entry = None
        self.status_label = None
        self.bot_label = None
        self.current_tab = "worlds"
        self.tab_buttons = {}
        self.tab_frames = {}
        self.object_count_label = None

        # TTS — Edge TTS (natural) or pyttsx3 (fallback)
        self.tts_engine = None
        self.tts_lock = threading.Lock()
        self.use_edge_tts = EDGE_TTS_AVAILABLE
        self.tts_voice = "he-IL-AvriNeural"  # Hebrew male, warm voice for Roby

        if EDGE_TTS_AVAILABLE:
            try:
                pygame.mixer.init()
                print(f"Edge TTS ready — voice: {self.tts_voice}")
            except Exception as e:
                print(f"Pygame mixer init error: {e}")
                self.use_edge_tts = False

        if not self.use_edge_tts and TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                print("Using pyttsx3 fallback TTS")
            except Exception as e:
                print(f"TTS init error: {e}")
                self.tts_engine = None

    def speak(self, text: str):
        """Speak text using Edge TTS (natural) or pyttsx3 (fallback)"""
        if self.use_edge_tts and self.tts_lock.acquire(blocking=False):
            def _speak_edge():
                tmp = None
                try:
                    import tempfile
                    tmp = tempfile.mktemp(suffix=".mp3", prefix="roby_")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    communicate = edge_tts.Communicate(text, self.tts_voice)
                    loop.run_until_complete(communicate.save(tmp))
                    # Properly shutdown transports before closing to avoid RuntimeError on Windows
                    loop.run_until_complete(loop.shutdown_asyncgens())
                    loop.close()
                    pygame.mixer.music.load(tmp)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(50)
                except Exception as e:
                    print(f"Edge TTS error: {e}")
                finally:
                    self.tts_lock.release()
                    if tmp and os.path.exists(tmp):
                        try:
                            os.remove(tmp)
                        except:
                            pass
            threading.Thread(target=_speak_edge, daemon=True).start()
        elif self.tts_engine and self.tts_lock.acquire(blocking=False):
            def _speak_pyttsx3():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    print(f"TTS error: {e}")
                finally:
                    self.tts_lock.release()
            threading.Thread(target=_speak_pyttsx3, daemon=True).start()
        else:
            try:
                import winsound
                winsound.Beep(800, 200)
            except:
                pass

    def bot_say(self, text: str, mood: str = "happy"):
        """Update bot speech bubble and speak with personality"""
        faces = {
            "happy": "😊", "thinking": "🤔", "success": "🎉",
            "error": "😅", "listening": "👂", "excited": "🤩",
            "proud": "😎", "magic": "✨", "love": "🥰",
        }
        face = faces.get(mood, "😊")
        if self.bot_label and self.root:
            self.root.after(0, lambda: self.bot_label.configure(text=f"{face} {text}"))
        self.speak(text)

    def bot_say_random(self, mood: str, object_name: str = ""):
        """Speak a random personality response for Roby"""
        import random
        responses = ROBY_PERSONALITY.get(mood, ROBY_PERSONALITY["happy"])
        text = random.choice(responses)
        if "{object}" in text and object_name:
            text = text.replace("{object}", object_name)
        elif "{object}" in text:
            text = text.replace("{object}", "זה")
        if "{suggestion}" in text and object_name:
            text = text.replace("{suggestion}", object_name)
        elif "{suggestion}" in text:
            text = text.replace("{suggestion}", "משהו מגניב")
        self.bot_say(text, mood)

    def log(self, message: str, level: str = "info"):
        """Add message to log"""
        if not self.log_text:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "💬", "success": "✅", "warning": "⚠️", "error": "❌", "command": "🎤", "build": "🔨"}

        def _log():
            self.log_text.configure(state='normal')
            self.log_text.insert('end', f"[{timestamp}] {icons.get(level, '💬')} {message}\n")
            self.log_text.see('end')
            self.log_text.configure(state='disabled')

        if self.root:
            self.root.after(0, _log)

    # =============================================
    # MAIN WINDOW
    # =============================================
    def create_window(self):
        """Create the main window - modern kid-friendly design"""
        self.root = tk.Tk()
        self.root.title("Voice Creator v8.0 - Kids Edition")
        self.root.configure(bg=THEME['bg'])
        self.root.geometry("1050x800")
        self.root.minsize(800, 650)

        # Responsive grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # Header + Bot
        self.root.grid_rowconfigure(1, weight=0)  # Mic + Input
        self.root.grid_rowconfigure(2, weight=0)  # Quick builds
        self.root.grid_rowconfigure(3, weight=1)  # Tabs + Games (expands)
        self.root.grid_rowconfigure(4, weight=0)  # Log (compact)

        self._create_header()
        self._create_voice_section()
        self._create_quick_build_bar()
        self._create_tabbed_games()
        self._create_log_panel()

        self.bot_say_random("greeting")
        self.log("Voice Creator v8.0 מוכן!", "success")
        self.log("לחץ על המיקרופון או בחר משחק!", "info")

        return self.root

    # =============================================
    # HEADER
    # =============================================
    def _create_header(self):
        header = tk.Frame(self.root, bg=THEME['bg_light'], height=70)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Logo
        logo = tk.Label(header, text="🎮 Voice Creator", font=("Segoe UI", 24, "bold"),
                        bg=THEME['bg_light'], fg=THEME['text'])
        logo.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Bot speech bubble
        bot_frame = tk.Frame(header, bg=THEME['bot_bubble'], padx=15, pady=5)
        bot_frame.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        self.bot_label = tk.Label(bot_frame, text="😊 שלום! אני רובי!",
                                  font=("Segoe UI", 13), bg=THEME['bot_bubble'],
                                  fg=THEME['accent_yellow'], wraplength=400, anchor="w")
        self.bot_label.pack(fill="x")

        # Help button
        help_btn = tk.Button(header, text="📖 מדריך", font=("Segoe UI", 12, "bold"),
                             bg=THEME['accent_purple'], fg="white", relief="flat",
                             cursor="hand2", padx=12, pady=4,
                             command=self._show_help_guide)
        help_btn.grid(row=0, column=2, padx=5, pady=15)

        # Status + Object counter
        status_frame = tk.Frame(header, bg=THEME['bg_light'])
        status_frame.grid(row=0, column=3, padx=15, pady=15, sticky="e")
        self.status_label = tk.Label(status_frame, text="🟢 מחובר",
                                     font=("Segoe UI", 10), bg=THEME['bg_light'],
                                     fg=THEME['success'])
        self.status_label.pack()
        self.object_count_label = tk.Label(status_frame, text="📦 0 אובייקטים",
                                           font=("Segoe UI", 9), bg=THEME['bg_light'],
                                           fg=THEME['text_dim'])
        self.object_count_label.pack()

    # =============================================
    # VOICE + TEXT INPUT
    # =============================================
    def _create_voice_section(self):
        frame = tk.Frame(self.root, bg=THEME['bg'], padx=15, pady=5)
        frame.grid(row=1, column=0, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        # BIG Microphone Button
        self.mic_button = tk.Button(frame, text="🎤", font=("Segoe UI", 28),
                                    bg=THEME['mic_ready'], fg="white",
                                    width=3, height=1, relief="flat", cursor="hand2",
                                    activebackground="#3BC96A",
                                    command=self.toggle_recording)
        self.mic_button.grid(row=0, column=0, padx=(0, 12), pady=5)

        # Text input
        input_frame = tk.Frame(frame, bg=THEME['card'], padx=3, pady=3)
        input_frame.grid(row=0, column=1, sticky="ew", pady=5)
        input_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = tk.Entry(input_frame, font=("Segoe UI", 15),
                                      bg=THEME['card'], fg=THEME['text'],
                                      insertbackground=THEME['text'], relief="flat",
                                      border=0)
        self.command_entry.grid(row=0, column=0, sticky="ew", padx=10, ipady=10)
        self.command_entry.insert(0, "כתוב כאן מה לבנות...")
        self.command_entry.bind("<FocusIn>", self._on_entry_focus)
        self.command_entry.bind("<FocusOut>", self._on_entry_unfocus)
        self.command_entry.bind("<Return>", lambda e: self.send_text_command())
        self.command_entry.configure(fg=THEME['text_dim'])

        # Send button
        send_btn = tk.Button(input_frame, text="שלח ➤", font=("Segoe UI", 13, "bold"),
                             bg=THEME['accent_pink'], fg="white", relief="flat",
                             cursor="hand2", padx=20, pady=8,
                             activebackground="#FF5585",
                             command=self.send_text_command)
        send_btn.grid(row=0, column=1, padx=5, pady=3)

        # Modify bar (smart logic)
        modify_frame = tk.Frame(frame, bg=THEME['bg'])
        modify_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(3, 0))
        tk.Label(modify_frame, text="🔧 שנה:", font=("Segoe UI", 9),
                 bg=THEME['bg'], fg=THEME['text_dim']).pack(side="left", padx=(0, 5))

        for action in MODIFY_ACTIONS:
            btn = tk.Button(modify_frame, text=f"{action['icon']} {action['label']}",
                            font=("Segoe UI", 9), bg=THEME['card'],
                            fg=THEME['text'], relief="flat", cursor="hand2", padx=8, pady=2,
                            activebackground=THEME['card_hover'],
                            command=lambda a=action: self._modify_last_object(a))
            btn.pack(side="left", padx=2)

    # =============================================
    # QUICK BUILD BAR
    # =============================================
    def _create_quick_build_bar(self):
        outer = tk.Frame(self.root, bg=THEME['bg'], padx=15)
        outer.grid(row=2, column=0, sticky="ew", pady=(5, 5))
        outer.grid_columnconfigure(0, weight=1)

        # Title
        title_row = tk.Frame(outer, bg=THEME['bg'])
        title_row.pack(fill="x")
        tk.Label(title_row, text="⚡ בנייה מהירה", font=("Segoe UI", 12, "bold"),
                 bg=THEME['bg'], fg=THEME['text']).pack(side="left")
        # Clean world button
        tk.Button(title_row, text="🧹 נקה עולם", font=("Segoe UI", 9),
                  bg=THEME['card'], fg=THEME['accent_red'], relief="flat",
                  cursor="hand2", padx=10, activebackground=THEME['card_hover'],
                  command=lambda: self.execute_command("נקה את העולם")).pack(side="right")

        # Row 1 - Common objects
        btn_frame = tk.Frame(outer, bg=THEME['bg'])
        btn_frame.pack(fill="x", pady=(5, 2))

        for item in QUICK_BUILDS:
            btn = tk.Button(btn_frame, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Row 2 - More objects
        btn_frame2 = tk.Frame(outer, bg=THEME['bg'])
        btn_frame2.pack(fill="x", pady=(0, 2))

        for item in QUICK_BUILDS_2:
            btn = tk.Button(btn_frame2, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Row 3 - NEW v4.0 objects (animals, food, space, music)
        btn_frame3 = tk.Frame(outer, bg=THEME['bg'])
        btn_frame3.pack(fill="x", pady=(0, 2))

        for item in QUICK_BUILDS_3:
            btn = tk.Button(btn_frame3, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Row 4 - NEW v5.0 Interactive & Action objects
        btn_frame4 = tk.Frame(outer, bg=THEME['bg'])
        btn_frame4.pack(fill="x", pady=(0, 2))

        tk.Label(btn_frame4, text="⚡", font=("Segoe UI", 10),
                 bg=THEME['bg'], fg=THEME['accent_orange']).pack(side="left", padx=(0, 2))

        for item in QUICK_BUILDS_4:
            btn = tk.Button(btn_frame4, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Row 5 - NEW v6.0 NPCs & Weather
        btn_frame5 = tk.Frame(outer, bg=THEME['bg'])
        btn_frame5.pack(fill="x", pady=(0, 2))

        tk.Label(btn_frame5, text="🎭", font=("Segoe UI", 10),
                 bg=THEME['bg'], fg=THEME['accent_purple']).pack(side="left", padx=(0, 2))

        for item in QUICK_BUILDS_5:
            btn = tk.Button(btn_frame5, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Row 6 - NEW v8.0 BEHAVIORS & LOGIC
        logic_title = tk.Frame(outer, bg=THEME['bg'])
        logic_title.pack(fill="x", pady=(8, 2))
        tk.Label(logic_title, text="🧠 לוגיקה והתנהגויות", font=("Segoe UI", 12, "bold"),
                 bg=THEME['bg'], fg=THEME['accent_green']).pack(side="left")
        tk.Label(logic_title, text="(סמן אובייקט ולחץ)", font=("Segoe UI", 9),
                 bg=THEME['bg'], fg=THEME['text_dim']).pack(side="left", padx=(10, 0))

        # Movement behaviors
        logic_frame1 = tk.Frame(outer, bg=THEME['bg'])
        logic_frame1.pack(fill="x", pady=(0, 2))
        tk.Label(logic_frame1, text="🏃", font=("Segoe UI", 10),
                 bg=THEME['bg'], fg=THEME['accent_green']).pack(side="left", padx=(0, 2))

        logic_buttons_1 = [
            {"icon": "🏃", "label": "ריצה", "cmd": "תוסיף ריצה לנבחר", "color": THEME['accent_green']},
            {"icon": "👣", "label": "עקוב", "cmd": "תוסיף עקיבה אחרי שחקן", "color": THEME['accent_blue']},
            {"icon": "🔄", "label": "סיור", "cmd": "תוסיף סיור", "color": THEME['accent_cyan']},
            {"icon": "⬆️", "label": "קפיצה", "cmd": "תוסיף קפיצה", "color": THEME['accent_yellow']},
            {"icon": "🕊️", "label": "עפיפה", "cmd": "תוסיף עפיפה", "color": THEME['accent_purple']},
            {"icon": "🚗", "label": "נהיגה", "cmd": "תוסיף נהיגה למכונית", "color": THEME['accent_orange']},
        ]
        for item in logic_buttons_1:
            btn = tk.Button(logic_frame1, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Interaction behaviors
        logic_frame2 = tk.Frame(outer, bg=THEME['bg'])
        logic_frame2.pack(fill="x", pady=(0, 2))
        tk.Label(logic_frame2, text="🖱️", font=("Segoe UI", 10),
                 bg=THEME['bg'], fg=THEME['accent_orange']).pack(side="left", padx=(0, 2))

        logic_buttons_2 = [
            {"icon": "🚪", "label": "דלת", "cmd": "תוסיף דלת שנפתחת בלחיצה", "color": THEME['accent_orange']},
            {"icon": "🪙", "label": "מטבע", "cmd": "תוסיף מטבע לאיסוף", "color": THEME['accent_yellow']},
            {"icon": "💥", "label": "נזק", "cmd": "תוסיף נזק בנגיעה", "color": THEME['accent_red']},
            {"icon": "💚", "label": "ריפוי", "cmd": "תוסיף ריפוי בנגיעה", "color": THEME['accent_green']},
            {"icon": "🌀", "label": "טלפורט", "cmd": "תוסיף טלפורט", "color": THEME['accent_purple']},
            {"icon": "🤸", "label": "טרמפולינה", "cmd": "תוסיף טרמפולינה קופצנית", "color": THEME['accent_cyan']},
            {"icon": "💣", "label": "פיצוץ", "cmd": "תוסיף פיצוץ בנגיעה", "color": THEME['accent_red']},
        ]
        for item in logic_buttons_2:
            btn = tk.Button(logic_frame2, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # NPC & Game Systems
        logic_frame3 = tk.Frame(outer, bg=THEME['bg'])
        logic_frame3.pack(fill="x", pady=(0, 2))
        tk.Label(logic_frame3, text="🎮", font=("Segoe UI", 10),
                 bg=THEME['bg'], fg=THEME['accent_pink']).pack(side="left", padx=(0, 2))

        logic_buttons_3 = [
            {"icon": "💬", "label": "NPC מדבר", "cmd": "תוסיף דמות שמדברת", "color": THEME['accent_blue']},
            {"icon": "⚔️", "label": "אויב", "cmd": "תוסיף אויב שתוקף", "color": THEME['accent_red']},
            {"icon": "❤️", "label": "חיים", "cmd": "תוסיף מערכת חיים", "color": THEME['accent_pink']},
            {"icon": "🪙", "label": "כסף", "cmd": "תוסיף מערכת מטבעות", "color": THEME['accent_yellow']},
            {"icon": "🏁", "label": "מירוץ", "cmd": "תוסיף מירוץ", "color": THEME['accent_green']},
            {"icon": "🏳️", "label": "צ'קפוינט", "cmd": "תוסיף צ'קפוינט", "color": THEME['accent_cyan']},
            {"icon": "⏱️", "label": "טיימר", "cmd": "תוסיף טיימר", "color": THEME['accent_orange']},
        ]
        for item in logic_buttons_3:
            btn = tk.Button(logic_frame3, text=f"{item['icon']}\n{item['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=item['color'], fg="white",
                            width=7, height=2, relief="flat", cursor="hand2",
                            activebackground=THEME['card_hover'],
                            command=lambda c=item['cmd']: self.execute_command(c))
            btn.pack(side="left", padx=2, pady=1)

        # Utility buttons row: undo, save, clear weather
        util_frame = tk.Frame(outer, bg=THEME['bg'])
        util_frame.pack(fill="x", pady=(3, 0))
        tk.Button(util_frame, text="↩️ בטל", font=("Segoe UI", 9, "bold"),
                  bg=THEME['card'], fg=THEME['accent_yellow'], relief="flat",
                  cursor="hand2", padx=10,
                  command=lambda: self.execute_command("בטל")).pack(side="left", padx=2)
        tk.Button(util_frame, text="💾 שמור עולם", font=("Segoe UI", 9, "bold"),
                  bg=THEME['card'], fg=THEME['accent_green'], relief="flat",
                  cursor="hand2", padx=10,
                  command=lambda: self.execute_command("שמור עולם")).pack(side="left", padx=2)
        tk.Button(util_frame, text="☀️ נקה מזג אוויר", font=("Segoe UI", 9, "bold"),
                  bg=THEME['card'], fg=THEME['accent_cyan'], relief="flat",
                  cursor="hand2", padx=10,
                  command=lambda: self.execute_command("נקה מזג אוויר")).pack(side="left", padx=2)
        tk.Button(util_frame, text="📡 סרוק משחק", font=("Segoe UI", 9, "bold"),
                  bg=THEME['card'], fg=THEME['accent_purple'], relief="flat",
                  cursor="hand2", padx=10,
                  command=lambda: self.execute_command("סרוק את המשחק")).pack(side="left", padx=2)

        # AI Chat row
        ai_frame = tk.Frame(outer, bg=THEME['bg'])
        ai_frame.pack(fill="x", pady=(5, 0))

        tk.Label(ai_frame, text="🤖 AI Chat:", font=("Segoe UI", 10, "bold"),
                 bg=THEME['bg'], fg=THEME['accent_purple']).pack(side="left", padx=(0, 5))

        self.ai_entry = tk.Entry(ai_frame, font=("Segoe UI", 10),
                                 bg=THEME['card'], fg=THEME['text'],
                                 insertbackground=THEME['text'],
                                 relief="flat", width=40)
        self.ai_entry.pack(side="left", fill="x", expand=True, padx=2)
        self.ai_entry.insert(0, "תשנה את הסקריפט של...")
        self.ai_entry.bind("<FocusIn>", lambda e: self._on_ai_focus(e))
        self.ai_entry.bind("<Return>", lambda e: self._on_ai_send())

        tk.Button(ai_frame, text="🚀 שלח", font=("Segoe UI", 10, "bold"),
                  bg=THEME['accent_purple'], fg="white", relief="flat",
                  cursor="hand2", padx=12,
                  command=self._on_ai_send).pack(side="left", padx=2)

    def _on_ai_focus(self, event):
        """Clear placeholder text on focus."""
        if self.ai_entry.get() == "תשנה את הסקריפט של...":
            self.ai_entry.delete(0, tk.END)

    def _on_ai_send(self):
        """Send AI Chat command."""
        text = self.ai_entry.get().strip()
        if text and text != "תשנה את הסקריפט של...":
            self.ai_entry.delete(0, tk.END)
            self.log(f"🤖 AI Chat: {text}", "info")
            self.execute_command(text)

    # =============================================
    # HELP GUIDE
    # =============================================
    def _show_help_guide(self):
        """Show comprehensive help/guide window."""
        guide = tk.Toplevel(self.root)
        guide.title("📖 מדריך Voice Creator v8.0")
        guide.configure(bg=THEME['bg'])
        guide.geometry("700x700")
        guide.minsize(600, 500)

        # Title
        tk.Label(guide, text="📖 איך להשתמש ב-Voice Creator",
                 font=("Segoe UI", 20, "bold"), bg=THEME['bg'],
                 fg=THEME['accent_yellow']).pack(pady=(15, 5))
        tk.Label(guide, text="פשוט תדבר או תכתוב בעברית - רובי יבנה הכל!",
                 font=("Segoe UI", 12), bg=THEME['bg'],
                 fg=THEME['text_dim']).pack(pady=(0, 10))

        # Scrollable content
        canvas = tk.Canvas(guide, bg=THEME['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(guide, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=THEME['bg'])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=15)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        guide.protocol("WM_DELETE_WINDOW", lambda: (canvas.unbind_all("<MouseWheel>"), guide.destroy()))

        def section(title, icon, color):
            f = tk.Frame(scroll_frame, bg=THEME['bg'])
            f.pack(fill="x", pady=(12, 2), padx=5)
            tk.Label(f, text=f"{icon} {title}", font=("Segoe UI", 14, "bold"),
                     bg=THEME['bg'], fg=color, anchor="w").pack(fill="x")
            return f

        def item(parent, text, color=THEME['text']):
            tk.Label(parent, text=text, font=("Segoe UI", 11),
                     bg=THEME['bg'], fg=color, anchor="w",
                     wraplength=620, justify="right").pack(fill="x", padx=(20, 0), pady=1)

        def card(parent, title, examples, color):
            c = tk.Frame(parent, bg=THEME['card'], padx=10, pady=8)
            c.pack(fill="x", padx=15, pady=3)
            tk.Label(c, text=title, font=("Segoe UI", 11, "bold"),
                     bg=THEME['card'], fg=color, anchor="w").pack(fill="x")
            for ex in examples:
                tk.Label(c, text=f'  "{ex}"', font=("Segoe UI", 10),
                         bg=THEME['card'], fg=THEME['text_dim'], anchor="w").pack(fill="x")

        # === Section 1: Getting Started ===
        s = section("התחלה מהירה", "🚀", THEME['accent_green'])
        item(s, "1. לחץ על 🎤 (מיקרופון) ודבר בעברית")
        item(s, "2. או כתוב פקודה בשדה הטקסט ולחץ Enter")
        item(s, "3. או לחץ על כפתור מהיר (בית, עץ, מכונית...)")
        item(s, "4. רובי יבנה את מה שביקשת ב-Roblox Studio!")

        # === Section 2: Basic Commands ===
        s = section("פקודות בסיסיות - בנייה", "🏗️", THEME['accent_blue'])
        card(s, "בנה אובייקטים:", [
            "בנה בית", "בנה עץ", "בנה מכונית",
            "בנה מגדל", "בנה גשר", "בנה טירה",
            "בנה חללית", "בנה עוגה", "בנה כלב",
        ], THEME['accent_blue'])
        card(s, "פקודות קצרות (בלי 'בנה'):", [
            "בית!", "עץ!", "מכונית!", "מטבע!", "שומר!",
        ], THEME['accent_cyan'])
        card(s, "עולמות שלמים:", [
            "בנה כפר עם בתים, עצים, וכביש",
            "בנה פארק שעשועים עם מגלשות ונדנדות",
            "בנה עיר עם בניינים ומכוניות",
        ], THEME['accent_purple'])

        # === Section 3: Interactive Objects ===
        s = section("אובייקטים אינטראקטיביים", "⚡", THEME['accent_orange'])
        card(s, "עם סקריפטים עובדים:", [
            "בנה מכונית  ← אפשר לשבת ולנהוג! 🚗",
            "בנה בית  ← דלת שנפתחת + תאורה פנימית! 🏠",
            "בנה מטבע  ← מסתובב + נותן נקודות! 🪙",
            "בנה טרמפולינה  ← קופצים גבוה! 🤸",
            "בנה לבה  ← מזיק למי שנוגע! 🌋",
            "בנה טלפורט  ← מעביר למקום אחר! 🌀",
            "בנה מדורה  ← אש + אור + עשן! 🔥",
        ], THEME['accent_orange'])

        # === Section 4: NPCs ===
        s = section("דמויות NPC", "🎭", THEME['accent_purple'])
        card(s, "דמויות חיות:", [
            "בנה שומר  ← מסייר הלוך וחזור! 💂",
            "בנה אויב  ← מזיק למי שנוגע! 👹",
            "בנה חבר  ← מנופף ידיים! 🧑",
        ], THEME['accent_purple'])

        # === Section 5: Weather ===
        s = section("מזג אוויר ותאורה", "🌦️", THEME['accent_cyan'])
        card(s, "אפקטים מדהימים:", [
            "בנה גשם  ← עננים + טיפות + ערפל! 🌧️",
            "בנה שלג  ← פתיתי שלג + אווירה חורפית! ❄️",
            "בנה לילה  ← חושך + כוכבים + ירח! 🌙",
            "בנה שקיעה  ← שמיים כתומים + זוהר! 🌅",
            "בנה ערפל  ← ראות מוגבלת + מסתורין! 🌫️",
        ], THEME['accent_cyan'])

        # === Section 6: Mini-games ===
        s = section("מיני-משחקים", "🏆", THEME['accent_yellow'])
        card(s, "משחקים שלמים:", [
            "בנה משחק מטבעות  ← אסוף מטבעות + לידרבורד! 🪙",
            "בנה מירוץ  ← מסלול + בוסטים + קו סיום! 🏁",
            "בנה אובי  ← מסלול מכשולים! 🏃",
        ], THEME['accent_yellow'])

        # === Section 7: AI Chat ===
        s = section("AI Chat - שינוי סקריפטים", "🤖", THEME['accent_purple'])
        item(s, "כתוב בשורת ה-AI Chat למטה כדי לשנות דברים במשחק:")
        card(s, "דוגמאות:", [
            "תשנה את המכונית שתהיה מהירה יותר",
            "תוסיף סקריפט שהבית נותן נקודות",
            "שנה את הצבע של השומר לירוק",
            "תעשה שהמטבעות שווים 50 נקודות",
            "תגרום לכל האובייקטים להסתובב",
        ], THEME['accent_purple'])

        # === Section 8: Utility Commands ===
        s = section("פקודות שירות", "🛠️", THEME['text'])
        card(s, "ניהול העולם:", [
            "בטל / חזור  ← מבטל את הפעולה האחרונה",
            "שמור עולם  ← שומר את כל מה שבנית",
            "טען עולם  ← טוען עולם שנשמר",
            "נקה מזג אוויר  ← מחזיר ליום רגיל",
            "סרוק את המשחק  ← AI סורק מה יש במשחק",
        ], THEME['text'])
        card(s, "עוד פקודות:", [
            "שפר / שדרג  ← משפר את הבנייה האחרונה",
            "עוד / עוד אחד  ← בונה עוד אחד כמו האחרון",
            "הגדל / הקטן  ← משנה גודל",
            "מחק  ← מוחק נבחרים",
        ], THEME['text_dim'])

        # === Section 9: Tips ===
        s = section("טיפים", "💡", THEME['accent_yellow'])
        item(s, "• אפשר לשלב אובייקטים: 'בנה בית, עצים, ומכונית'")
        item(s, "• אפשר לבקש עולמות: 'בנה כפר עם בתים ועצים'")
        item(s, "• המכונית עובדת! תשב בה ותנהג!")
        item(s, "• הדלת בבית עובדת! לחץ עליה לפתוח!")
        item(s, "• ה-AI Chat יכול לשנות כל דבר במשחק!")
        item(s, "• הכפתורים המהירים עובדים גם בקול!")

        # === Setup ===
        s = section("התקנה", "⚙️", THEME['text_dim'])
        item(s, "1. שמור את VoiceCreator.lua בתיקייה:")
        item(s, "   %LOCALAPPDATA%\\Roblox\\Plugins\\", THEME['accent_cyan'])
        item(s, "2. פתח Roblox Studio ולחץ על Voice Creator בToolbar")
        item(s, "3. הפעל את האפליקציה: python src/kids_interface.py")
        item(s, "4. (אופציונלי) הגדר OPENROUTER_API_KEY לAI Chat")

    # =============================================
    # TABBED GAME TEMPLATES
    # =============================================
    def _create_tabbed_games(self):
        outer = tk.Frame(self.root, bg=THEME['bg'], padx=15)
        outer.grid(row=3, column=0, sticky="nsew", pady=(0, 5))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Tab bar
        tab_bar = tk.Frame(outer, bg=THEME['bg'])
        tab_bar.pack(fill="x", pady=(0, 5))
        tk.Label(tab_bar, text="🎮 משחקים מוכנים", font=("Segoe UI", 12, "bold"),
                 bg=THEME['bg'], fg=THEME['text']).pack(side="left", padx=(0, 15))

        for cat_key, cat_data in GAME_CATEGORIES.items():
            btn = tk.Button(tab_bar, text=f"{cat_data['icon']} {cat_data['label']}",
                            font=("Segoe UI", 10, "bold"),
                            bg=THEME['card'] if cat_key != self.current_tab else cat_data['color'],
                            fg="white", relief="flat", cursor="hand2", padx=12, pady=4,
                            activebackground=cat_data['color'],
                            command=lambda k=cat_key: self._switch_tab(k))
            btn.pack(side="left", padx=3)
            self.tab_buttons[cat_key] = btn

        # Game content area
        self.games_container = tk.Frame(outer, bg=THEME['bg'])
        self.games_container.pack(fill="both", expand=True)

        # Create all tab frames (hidden by default)
        for cat_key, cat_data in GAME_CATEGORIES.items():
            frame = tk.Frame(self.games_container, bg=THEME['bg'])
            self.tab_frames[cat_key] = frame

            col = 0
            for game_name, game_data in cat_data['games'].items():
                game_btn = tk.Frame(frame, bg=THEME['card'], padx=10, pady=8, cursor="hand2")
                game_btn.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
                frame.grid_columnconfigure(col, weight=1)

                icon_lbl = tk.Label(game_btn, text=game_data['icon'], font=("Segoe UI", 36),
                                    bg=THEME['card'], fg=THEME['text'])
                icon_lbl.pack(pady=(5, 2))
                name_lbl = tk.Label(game_btn, text=game_name, font=("Segoe UI", 11, "bold"),
                                    bg=THEME['card'], fg=THEME['text'])
                name_lbl.pack(pady=(0, 5))

                # Click handler
                for widget in [game_btn, icon_lbl, name_lbl]:
                    widget.bind("<Button-1>", lambda e, n=game_name, d=game_data: self.create_game(n, d))
                    widget.bind("<Enter>", lambda e, f=game_btn: f.configure(bg=THEME['card_hover']))
                    widget.bind("<Leave>", lambda e, f=game_btn: f.configure(bg=THEME['card']))

                col += 1

        # Show first tab
        self._switch_tab(self.current_tab)

    def _switch_tab(self, tab_key: str):
        """Switch between game category tabs"""
        self.current_tab = tab_key

        # Update tab button colors
        for key, btn in self.tab_buttons.items():
            if key == tab_key:
                btn.configure(bg=GAME_CATEGORIES[key]['color'])
            else:
                btn.configure(bg=THEME['card'])

        # Show/hide frames
        for key, frame in self.tab_frames.items():
            if key == tab_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # =============================================
    # LOG PANEL (compact at bottom)
    # =============================================
    def _create_log_panel(self):
        outer = tk.Frame(self.root, bg=THEME['bg_light'], padx=15, pady=5)
        outer.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))
        outer.grid_columnconfigure(0, weight=1)

        # Header row
        header = tk.Frame(outer, bg=THEME['bg_light'])
        header.pack(fill="x")
        tk.Label(header, text="📋 לוג", font=("Segoe UI", 10, "bold"),
                 bg=THEME['bg_light'], fg=THEME['text_dim']).pack(side="left")

        # Toggle expand/collapse
        self.log_expanded = False
        self.toggle_log_btn = tk.Button(header, text="▲ הרחב", font=("Segoe UI", 8),
                                         bg=THEME['bg_light'], fg=THEME['text_dim'],
                                         relief="flat", cursor="hand2",
                                         command=self._toggle_log)
        self.toggle_log_btn.pack(side="right")

        tk.Button(header, text="🗑️", font=("Segoe UI", 8),
                  bg=THEME['bg_light'], fg=THEME['text_dim'], relief="flat",
                  cursor="hand2", command=self.clear_log).pack(side="right", padx=5)

        # Log text (compact by default)
        self.log_text = scrolledtext.ScrolledText(outer, font=("Consolas", 9),
                                                   bg=THEME['bg'], fg=THEME['text'],
                                                   relief="flat", state='disabled',
                                                   wrap='word', height=3)
        self.log_text.pack(fill="x", pady=(3, 0))

    def _toggle_log(self):
        """Toggle log panel height"""
        self.log_expanded = not self.log_expanded
        if self.log_expanded:
            self.log_text.configure(height=10)
            self.toggle_log_btn.configure(text="▼ כווץ")
        else:
            self.log_text.configure(height=3)
            self.toggle_log_btn.configure(text="▲ הרחב")

    # =============================================
    # INPUT HELPERS
    # =============================================
    def _on_entry_focus(self, event):
        if self.command_entry.get() == "כתוב כאן מה לבנות...":
            self.command_entry.delete(0, 'end')
            self.command_entry.configure(fg=THEME['text'])

    def _on_entry_unfocus(self, event):
        if not self.command_entry.get().strip():
            self.command_entry.insert(0, "כתוב כאן מה לבנות...")
            self.command_entry.configure(fg=THEME['text_dim'])

    # =============================================
    # ACTIONS
    # =============================================
    def clear_log(self):
        if self.log_text:
            self.log_text.configure(state='normal')
            self.log_text.delete(1.0, 'end')
            self.log_text.configure(state='disabled')

    def send_text_command(self):
        if not self.command_entry:
            return
        text = self.command_entry.get().strip()
        if text and text != "כתוב כאן מה לבנות...":
            self.command_entry.delete(0, 'end')
            self.execute_command(text)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.mic_button.configure(bg=THEME['mic_recording'], text="⏹️")
        self.log("מקליט... דבר עכשיו!", "command")
        self.bot_say("מקשיב לך...", "listening")
        threading.Thread(target=self._record_and_execute, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        self.mic_button.configure(bg=THEME['mic_ready'], text="🎤")

    def _record_and_execute(self):
        """Record audio and execute with improved Whisper"""
        try:
            import sounddevice as sd
            import numpy as np
            from openai import OpenAI
            import tempfile
            import wave

            sample_rate = 44100
            duration = 5  # 5 seconds for more time to speak

            self.log("מקליט 5 שניות... דבר!", "info")
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate,
                                channels=1, dtype=np.int16)
            sd.wait()

            # Check if audio has content (not silence)
            audio_level = np.abs(audio_data).mean()
            if audio_level < 50:
                self.log("לא שמעתי כלום, נסה שוב", "warning")
                self.bot_say("לא שמעתי, נסה שוב", "error")
                return

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
                with wave.open(temp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())

            self.log("ממיר לטקסט...", "info")
            self.bot_say_random("thinking")
            client = OpenAI()
            with open(temp_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="he",
                    prompt=WHISPER_HEBREW_VOCAB,
                )

            text = transcript.text.strip()
            os.unlink(temp_path)

            if text:
                self.log(f"שמעתי: \"{text}\"", "command")
                self.execute_command(text)
            else:
                self.log("לא הצלחתי להבין", "warning")
                self.bot_say("לא הבנתי, נסה שוב", "error")

        except ImportError as e:
            self.log(f"חסרה ספרייה: {e}", "error")
            self.bot_say("צריך להתקין ספריות קול", "error")
        except Exception as e:
            self.log(f"שגיאה: {e}", "error")
            self.bot_say("משהו לא עבד, ננסה שוב", "error")
        finally:
            self.root.after(0, self.stop_recording)

    def execute_command(self, text: str):
        """Execute a build command with personality feedback"""
        self.log(f"פקודה: {text}", "command")
        self.bot_say_random("thinking")

        def _execute():
            try:
                result = self.controller.execute_voice_command(text)

                if 'understood' in result:
                    self.log(f"הבנתי: {result['understood']}", "info")

                if result.get('success'):
                    msg = result.get('message', 'בוצע!')
                    method = result.get('method', '')
                    self.log(f"{msg} [{method}]" if method else msg, "success")
                    understood = result.get('understood', text)

                    # Use world_success mood for compound builds
                    if method == 'world_builder':
                        self.bot_say_random("world_success")
                    elif method == 'improve_context':
                        self.bot_say_random("improve")
                    else:
                        self.bot_say_random("success", understood)

                    self._update_object_count()

                    # Suggest what to build next after a short delay
                    threading.Thread(target=self._suggest_next, args=(understood,), daemon=True).start()

                elif result.get('not_a_command'):
                    self.bot_say("זו לא פקודת בנייה, נסה לבקש משהו לבנות", "happy")
                else:
                    error = result.get('error', 'שגיאה')
                    hint = result.get('hint', '')
                    self.log(f"{error}", "error")
                    if hint:
                        self.log(f"טיפ: {hint}", "info")
                    self.bot_say_random("error")
            except Exception as e:
                self.log(f"שגיאה: {e}", "error")
                self.bot_say_random("error")

        threading.Thread(target=_execute, daemon=True).start()

    def _suggest_next(self, built_object: str):
        """Suggest what to build next after a successful build"""
        import random
        import time
        time.sleep(4)  # Wait before suggesting

        # Find matching suggestions
        suggestions = BUILD_SUGGESTIONS.get("default")
        for key in BUILD_SUGGESTIONS:
            if key in built_object:
                suggestions = BUILD_SUGGESTIONS[key]
                break

        if suggestions:
            suggestion = random.choice(suggestions)
            self.bot_say_random("suggest", suggestion)
            self.log(f"💡 הצעה: מה עם {suggestion}?", "info")

    def _modify_last_object(self, action: dict):
        """Modify the last built object using smart logic"""
        # Get the last object from world state
        last_obj = None
        if hasattr(self.controller, 'world_state'):
            last_obj = self.controller.world_state.get_last_created()

        if last_obj:
            cmd = action['cmd'].replace("{object}", last_obj.name)
        else:
            cmd = action['cmd'].replace("{object}", "האובייקט האחרון")

        self.execute_command(cmd)

    def create_game(self, name: str, data: dict):
        """Create a game from template"""
        self.log(f"יוצר: {name} {data['icon']}", "build")
        self.bot_say(f"מכין {name}! זה ייקח רגע...", "thinking")
        self.execute_command(data['command'])

    def _update_object_count(self):
        """Update the object counter display"""
        if self.object_count_label and hasattr(self.controller, 'world_state'):
            count = len(self.controller.world_state.objects)
            self.root.after(0, lambda: self.object_count_label.configure(
                text=f"📦 {count} אובייקטים"))

    def run(self):
        if self.root:
            self.root.mainloop()


# =============================================
# MAIN
# =============================================
def main():
    print("=" * 50)
    print(" Voice Creator - Kids Edition v8.0 - Logic & Behaviors")
    print("=" * 50)

    start_server(port=8080)
    print("HTTP Server on http://127.0.0.1:8080")

    controller = DirectController(use_smart_agent=True)

    interface = KidsInterface(controller)
    window = interface.create_window()

    print("Ready!")
    interface.run()


if __name__ == "__main__":
    main()
