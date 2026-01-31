"""
Roblox Voice Creator - גרסה פשוטה ומהירה!
==========================================
משתמש ב-HTTP Server לתקשורת עם Plugin ב-Roblox Studio.
הרבה יותר מהיר ואמין!

שימוש:
    python main_simple.py
"""

import os
import sys
import io
import tkinter as tk
from tkinter import ttk
import threading
from dotenv import load_dotenv

# תיקון encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voice_engine import VoiceEngine
from direct_controller import DirectRobloxController
from command_server import start_server


class SimpleVoiceApp:
    """אפליקציה פשוטה לשליטה קולית ב-Roblox."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Roblox Voice Creator")
        self.root.geometry("400x500")
        self.root.configure(bg="#2b2b2b")

        # רכיבים
        self.voice_engine = None
        self.controller = None
        self.is_recording = False

        self._setup_ui()
        self._init_components()

    def _setup_ui(self):
        """בניית הממשק."""
        # כותרת
        title = tk.Label(
            self.root,
            text="Roblox Voice Creator",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        title.pack(pady=20)

        # סטטוס
        self.status_label = tk.Label(
            self.root,
            text="מאתחל...",
            font=("Arial", 14),
            fg="#00ff00",
            bg="#2b2b2b"
        )
        self.status_label.pack(pady=10)

        # כפתור הקלטה
        self.record_btn = tk.Button(
            self.root,
            text="לחץ ודבר",
            font=("Arial", 24, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=3,
            command=self._toggle_recording
        )
        self.record_btn.pack(pady=30)

        # תיבת לוג
        log_frame = tk.Frame(self.root, bg="#2b2b2b")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.log_text = tk.Text(
            log_frame,
            height=10,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # הוראות
        instructions = tk.Label(
            self.root,
            text="פקודות: תוסיף קוביה, תצבע באדום, תגדיל, תמחק",
            font=("Arial", 10),
            fg="#888888",
            bg="#2b2b2b"
        )
        instructions.pack(pady=10)

    def _log(self, message: str, level: str = "info"):
        """הוספת הודעה ללוג."""
        print(f"[{level.upper()}] {message}", flush=True)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def _set_status(self, text: str):
        """עדכון סטטוס."""
        self.status_label.config(text=text)
        self._log(text)

    def _init_components(self):
        """אתחול הרכיבים."""
        try:
            # HTTP Server
            start_server(port=8080, on_status=self._log)
            self._log("שרת HTTP פעיל על פורט 8080")

            # Voice Engine
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self._set_status("חסר OPENAI_API_KEY!")
                return

            self.voice_engine = VoiceEngine(api_key=api_key)
            self._log("מנוע קול מוכן")

            # Direct Controller
            self.controller = DirectRobloxController(on_status=self._log)
            self._log("בקר Roblox מוכן")

            self._set_status("מוכן! הפעל Plugin ב-Roblox ולחץ על הכפתור.")

        except Exception as e:
            self._set_status(f"שגיאה: {e}")

    def _toggle_recording(self):
        """התחלה/עצירת הקלטה."""
        if not self.voice_engine:
            self._set_status("מנוע קול לא מוכן!")
            return

        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """התחלת הקלטה."""
        self.is_recording = True
        self.record_btn.config(bg="#f44336", text="מקליט...")
        self._set_status("מקליט... דבר עכשיו!")

        # הקלטה בthread נפרד
        threading.Thread(target=self._record_thread, daemon=True).start()

    def _record_thread(self):
        """Thread הקלטה."""
        try:
            self.voice_engine.start_recording()
        except Exception as e:
            self._log(f"שגיאה בהקלטה: {e}", "error")

    def _stop_recording(self):
        """עצירת הקלטה ועיבוד."""
        self.is_recording = False
        self.record_btn.config(bg="#4CAF50", text="לחץ ודבר")
        self._set_status("מעבד...")

        # עצירה ועיבוד בthread נפרד
        threading.Thread(target=self._process_thread, daemon=True).start()

    def _process_thread(self):
        """Thread עיבוד."""
        try:
            # קבל את הטקסט
            result = self.voice_engine.stop_and_transcribe()

            # חלץ את הטקסט מהתוצאה
            if hasattr(result, 'text'):
                text = result.text
            else:
                text = result

            if not text:
                self._set_status("לא שמעתי כלום")
                return

            self._log(f"זיהיתי: {text}")

            # בצע את הפקודה
            result = self.controller.execute_voice_command(text)

            if result.get("success"):
                self._set_status(result.get("message", "בוצע!"))
            else:
                self._set_status(result.get("error", "נכשל"))

        except Exception as e:
            self._log(f"שגיאה: {e}", "error")
            self._set_status("שגיאה בעיבוד")

    def run(self):
        """הפעלת האפליקציה."""
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("Roblox Voice Creator - HTTP Server Edition")
    print("=" * 50)
    print()
    print("הוראות:")
    print("1. פתח Roblox Studio")
    print("2. לחץ על כפתור Voice Creator ב-Toolbar להפעלת ה-Plugin")
    print("3. לחץ על הכפתור ודבר!")
    print()

    app = SimpleVoiceApp()
    app.run()
