"""
Agent Memory System - מערכת זיכרון לסוכנים
===========================================
מערכת זיכרון משותפת שמאפשרת לסוכנים לזכור:
- היסטוריית שיחות
- אובייקטים שנוצרו
- העדפות משתמש
- הקשרים בין אובייקטים
"""

import json
import time
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class MemoryType(Enum):
    """סוגי זיכרונות."""
    CONVERSATION = "conversation"     # שיחה
    CREATION = "creation"             # יצירת אובייקט
    MODIFICATION = "modification"     # שינוי אובייקט
    USER_PREFERENCE = "preference"    # העדפת משתמש
    GAME_CONFIG = "game_config"       # הגדרות משחק
    RELATIONSHIP = "relationship"     # יחס בין אובייקטים
    ERROR = "error"                   # שגיאה
    SUCCESS = "success"               # הצלחה


@dataclass
class Memory:
    """זיכרון בודד."""
    id: str
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    importance: float = 1.0  # 0-10, כמה חשוב הזיכרון

    def to_dict(self) -> dict:
        d = asdict(self)
        d['memory_type'] = self.memory_type.value
        return d

    @staticmethod
    def from_dict(d: dict) -> 'Memory':
        d['memory_type'] = MemoryType(d['memory_type'])
        return Memory(**d)


class AgentMemory:
    """
    מערכת זיכרון לסוכנים - מאפשרת לזכור היסטוריה ולשתף מידע.
    """

    def __init__(self, storage_path: str = None, on_status=None):
        """
        אתחול מערכת הזיכרון.

        Args:
            storage_path: נתיב לקובץ שמירה
            on_status: פונקציה לעדכוני סטטוס
        """
        self.on_status = on_status or (lambda x: print(f"[Memory] {x}"))

        # קבע נתיב שמירה
        if storage_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            storage_path = os.path.join(project_root, "data", "agent_memory.json")
        self.storage_path = storage_path

        # ודא שהתיקייה קיימת
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # אתחל מבני נתונים
        self.memories: List[Memory] = []
        self.memory_counter = 0

        # אינדקסים לחיפוש מהיר
        self._by_type: Dict[MemoryType, List[Memory]] = {}
        self._by_object: Dict[str, List[Memory]] = {}  # אובייקט -> זיכרונות קשורים

        # העדפות משתמש
        self.user_preferences: Dict[str, Any] = {
            "favorite_colors": [],
            "preferred_style": None,
            "common_objects": [],
            "language_level": "kids",  # kids / advanced
        }

        # הקשר נוכחי
        self.current_context: Dict[str, Any] = {
            "current_project": None,
            "last_objects": [],
            "session_start": time.time(),
        }

        # נסה לטעון מקובץ
        self._load_if_exists()

    def _generate_id(self) -> str:
        """יצירת מזהה ייחודי."""
        self.memory_counter += 1
        return f"mem_{self.memory_counter}_{int(time.time())}"

    def add_memory(self, memory_type: MemoryType, content: str,
                   metadata: Dict[str, Any] = None,
                   importance: float = 1.0) -> Memory:
        """
        הוספת זיכרון חדש.

        Args:
            memory_type: סוג הזיכרון
            content: תוכן הזיכרון
            metadata: מטאדאטה נוספת
            importance: חשיבות (0-10)

        Returns:
            הזיכרון שנוצר
        """
        memory = Memory(
            id=self._generate_id(),
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            importance=importance
        )

        self.memories.append(memory)

        # עדכן אינדקסים
        if memory_type not in self._by_type:
            self._by_type[memory_type] = []
        self._by_type[memory_type].append(memory)

        # אם יש אובייקט קשור
        if metadata and "object_id" in metadata:
            obj_id = metadata["object_id"]
            if obj_id not in self._by_object:
                self._by_object[obj_id] = []
            self._by_object[obj_id].append(memory)

        return memory

    def remember_conversation(self, user_message: str, assistant_response: str,
                              objects_created: List[str] = None) -> Memory:
        """
        זכור שיחה.

        Args:
            user_message: הודעת המשתמש
            assistant_response: תגובת הסוכן
            objects_created: אובייקטים שנוצרו
        """
        return self.add_memory(
            MemoryType.CONVERSATION,
            f"משתמש: {user_message}\nתגובה: {assistant_response}",
            metadata={
                "user_message": user_message,
                "assistant_response": assistant_response,
                "objects_created": objects_created or []
            }
        )

    def remember_creation(self, object_name: str, object_type: str,
                          position: Tuple[float, float, float],
                          properties: Dict[str, Any] = None) -> Memory:
        """
        זכור יצירת אובייקט.

        Args:
            object_name: שם האובייקט
            object_type: סוג האובייקט
            position: מיקום
            properties: מאפיינים
        """
        content = f"נוצר {object_name} (סוג: {object_type}) במיקום {position}"

        memory = self.add_memory(
            MemoryType.CREATION,
            content,
            metadata={
                "object_name": object_name,
                "object_type": object_type,
                "position": position,
                "properties": properties or {}
            },
            importance=5.0
        )

        # עדכן רשימת אובייקטים אחרונים
        self.current_context["last_objects"].append(object_name)
        if len(self.current_context["last_objects"]) > 10:
            self.current_context["last_objects"] = self.current_context["last_objects"][-10:]

        return memory

    def remember_user_preference(self, preference_type: str, value: Any) -> Memory:
        """
        זכור העדפת משתמש.

        Args:
            preference_type: סוג ההעדפה
            value: הערך
        """
        self.user_preferences[preference_type] = value

        return self.add_memory(
            MemoryType.USER_PREFERENCE,
            f"העדפה: {preference_type} = {value}",
            metadata={"preference_type": preference_type, "value": value},
            importance=7.0
        )

    def remember_game_config(self, game_type: str, config: Dict[str, Any]) -> Memory:
        """
        זכור הגדרות משחק.

        Args:
            game_type: סוג המשחק
            config: ההגדרות
        """
        return self.add_memory(
            MemoryType.GAME_CONFIG,
            f"משחק {game_type} עם הגדרות: {config}",
            metadata={"game_type": game_type, "config": config},
            importance=8.0
        )

    def remember_relationship(self, obj1_name: str, obj2_name: str,
                              relation: str) -> Memory:
        """
        זכור יחס בין אובייקטים.

        Args:
            obj1_name: שם אובייקט 1
            obj2_name: שם אובייקט 2
            relation: סוג היחס
        """
        return self.add_memory(
            MemoryType.RELATIONSHIP,
            f"{obj1_name} {relation} {obj2_name}",
            metadata={
                "object1": obj1_name,
                "object2": obj2_name,
                "relation": relation
            },
            importance=3.0
        )

    def get_recent_memories(self, count: int = 10,
                            memory_type: MemoryType = None) -> List[Memory]:
        """
        קבלת זיכרונות אחרונים.

        Args:
            count: כמות מקסימלית
            memory_type: סנן לפי סוג

        Returns:
            רשימת זיכרונות
        """
        if memory_type:
            memories = self._by_type.get(memory_type, [])
        else:
            memories = self.memories

        # מיין לפי זמן (החדש ביותר קודם)
        sorted_memories = sorted(memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:count]

    def get_important_memories(self, min_importance: float = 5.0) -> List[Memory]:
        """
        קבלת זיכרונות חשובים.

        Args:
            min_importance: סף חשיבות מינימלי

        Returns:
            רשימת זיכרונות
        """
        return [m for m in self.memories if m.importance >= min_importance]

    def get_memories_for_object(self, object_name: str) -> List[Memory]:
        """
        קבלת זיכרונות הקשורים לאובייקט.

        Args:
            object_name: שם האובייקט

        Returns:
            רשימת זיכרונות
        """
        result = []
        for memory in self.memories:
            if object_name.lower() in memory.content.lower():
                result.append(memory)
        return result

    def search_memories(self, query: str) -> List[Memory]:
        """
        חיפוש בזיכרונות.

        Args:
            query: מחרוזת חיפוש

        Returns:
            רשימת זיכרונות
        """
        query_lower = query.lower()
        return [m for m in self.memories if query_lower in m.content.lower()]

    def get_context_for_agents(self) -> str:
        """
        יצירת הקשר לסוכנים.

        Returns:
            טקסט הקשר
        """
        lines = ["== הקשר מזיכרון =="]

        # העדפות משתמש
        if any(self.user_preferences.values()):
            lines.append("\nהעדפות משתמש:")
            if self.user_preferences.get("favorite_colors"):
                lines.append(f"  - צבעים אהובים: {', '.join(self.user_preferences['favorite_colors'])}")
            if self.user_preferences.get("preferred_style"):
                lines.append(f"  - סגנון מועדף: {self.user_preferences['preferred_style']}")
            if self.user_preferences.get("common_objects"):
                lines.append(f"  - אובייקטים נפוצים: {', '.join(self.user_preferences['common_objects'])}")

        # אובייקטים אחרונים
        if self.current_context.get("last_objects"):
            lines.append(f"\nאובייקטים אחרונים: {', '.join(self.current_context['last_objects'])}")

        # שיחות אחרונות
        recent_convos = self.get_recent_memories(3, MemoryType.CONVERSATION)
        if recent_convos:
            lines.append("\nשיחות אחרונות:")
            for conv in recent_convos:
                if "user_message" in conv.metadata:
                    lines.append(f"  - {conv.metadata['user_message'][:50]}...")

        # זיכרונות חשובים
        important = self.get_important_memories(7.0)[:5]
        if important:
            lines.append("\nזיכרונות חשובים:")
            for mem in important:
                lines.append(f"  - {mem.content[:50]}...")

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """
        קבלת סיכום הזיכרון.

        Returns:
            מילון סיכום
        """
        return {
            "total_memories": len(self.memories),
            "by_type": {t.value: len(mems) for t, mems in self._by_type.items()},
            "session_duration": time.time() - self.current_context.get("session_start", time.time()),
            "last_objects": self.current_context.get("last_objects", []),
            "user_preferences": self.user_preferences,
        }

    def learn_from_conversation(self, user_message: str):
        """
        למד מהשיחה - זהה העדפות וסגנון.

        Args:
            user_message: הודעת המשתמש
        """
        message_lower = user_message.lower()

        # זהה צבעים
        colors = ["אדום", "כחול", "ירוק", "צהוב", "כתום", "סגול", "ורוד", "לבן", "שחור"]
        for color in colors:
            if color in message_lower:
                if color not in self.user_preferences["favorite_colors"]:
                    self.user_preferences["favorite_colors"].append(color)
                    if len(self.user_preferences["favorite_colors"]) > 5:
                        self.user_preferences["favorite_colors"] = \
                            self.user_preferences["favorite_colors"][-5:]

        # זהה אובייקטים נפוצים
        common = ["בית", "עץ", "מכונית", "שולחן", "כיסא", "פרח", "כביש"]
        for obj in common:
            if obj in message_lower:
                if obj not in self.user_preferences["common_objects"]:
                    self.user_preferences["common_objects"].append(obj)
                    if len(self.user_preferences["common_objects"]) > 10:
                        self.user_preferences["common_objects"] = \
                            self.user_preferences["common_objects"][-10:]

    def save(self):
        """שמירה לקובץ."""
        data = {
            "memories": [m.to_dict() for m in self.memories],
            "counter": self.memory_counter,
            "user_preferences": self.user_preferences,
            "current_context": self.current_context,
        }

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.on_status(f"זיכרון נשמר: {len(self.memories)} זיכרונות")

    def _load_if_exists(self):
        """טעינה מקובץ אם קיים."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.memories = [Memory.from_dict(m) for m in data.get("memories", [])]
                self.memory_counter = data.get("counter", 0)
                self.user_preferences = data.get("user_preferences", self.user_preferences)

                # שחזר אינדקסים
                for memory in self.memories:
                    if memory.memory_type not in self._by_type:
                        self._by_type[memory.memory_type] = []
                    self._by_type[memory.memory_type].append(memory)

                self.on_status(f"נטענו {len(self.memories)} זיכרונות")
            except Exception as e:
                self.on_status(f"שגיאה בטעינת זיכרון: {e}")

    def clear(self):
        """ניקוי כל הזיכרונות."""
        self.memories.clear()
        self._by_type.clear()
        self._by_object.clear()
        self.memory_counter = 0
        self.on_status("הזיכרון נוקה")


class SharedAgentContext:
    """
    הקשר משותף לכל הסוכנים - סינגלטון.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.memory = AgentMemory()
        self.world_state = None  # יאותחל מבחוץ
        self.game_config = None  # הגדרות משחק נוכחיות
        self._initialized = True

    def set_world_state(self, world_state):
        """קביעת WorldState."""
        self.world_state = world_state

    def get_full_context(self) -> str:
        """
        קבלת הקשר מלא לסוכנים.

        Returns:
            טקסט הקשר המלא
        """
        parts = []

        # הקשר מזיכרון
        parts.append(self.memory.get_context_for_agents())

        # הקשר מעולם
        if self.world_state:
            parts.append("\n" + self.world_state.get_context_for_llm())

        # הגדרות משחק
        if self.game_config:
            parts.append(f"\nמשחק נוכחי: {self.game_config}")

        return "\n".join(parts)


# ========================================
# בדיקות
# ========================================

if __name__ == "__main__":
    print("בדיקת Agent Memory")
    print("=" * 40)

    memory = AgentMemory()

    # הוסף זיכרונות
    memory.remember_conversation(
        "תבנה לי בית כחול",
        "בניתי בית כחול במיקום (0, 5, 0)"
    )

    memory.remember_creation(
        "הבית הכחול",
        "building",
        (0, 5, 0),
        {"color": "blue", "size": "medium"}
    )

    memory.remember_user_preference("favorite_colors", ["כחול", "ירוק"])

    memory.remember_relationship("עץ", "בית", "ליד")

    # הדפס סיכום
    print("\nסיכום:")
    print(memory.get_summary())

    print("\nהקשר לסוכנים:")
    print(memory.get_context_for_agents())

    # שמור
    memory.save()
    print("\nנשמר בהצלחה!")
