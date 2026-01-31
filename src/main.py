"""
Roblox Voice Creator - Main Application
========================================
נקודת הכניסה הראשית לאפליקציה.
מחברת את כל הרכיבים: GUI, Voice Engine, Claude Controller.

שימוש:
    python main.py

או עם פרמטרים:
    python main.py --debug
    python main.py --test-voice
    python main.py --test-controller
"""

import os
import sys
import io
import asyncio
import argparse
import threading
from typing import Optional
from dotenv import load_dotenv

# תיקון encoding ל-Windows - חייב להיות לפני כל הדפסה
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# טעינת משתני סביבה
load_dotenv()

# הוספת התיקייה הנוכחית ל-path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import VoiceCreatorGUI, AppState
from voice_engine import VoiceEngine, RecordingState
from claude_controller import RobloxController


class RobloxVoiceCreatorApp:
    """
    האפליקציה הראשית - מחברת את כל הרכיבים.

    זרימת העבודה:
    1. המשתמש לוחץ על הכפתור
    2. VoiceEngine מקליט ומזהה את הקול
    3. RobloxController מבצע את הפעולה ב-Roblox Studio
    4. GUI מציג את התוצאות
    """

    def __init__(self, debug: bool = False):
        """
        אתחול האפליקציה.

        Args:
            debug: מצב דיבוג עם הדפסות נוספות
        """
        self.debug = debug

        # קבלת מפתחות API
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        # אתחול רכיבים
        self.gui: Optional[VoiceCreatorGUI] = None
        self.voice_engine: Optional[VoiceEngine] = None
        self.controller: Optional[RobloxController] = None

        # Event loop לפעולות async
        self.loop = asyncio.new_event_loop()

    def _log(self, message: str, level: str = "info"):
        """לוג פנימי - תמיד מדפיס לקונסול."""
        # תמיד הדפס לקונסול עם flush מיידי!
        print(f"[{level.upper()}] {message}", flush=True)
        if self.gui:
            self.gui.add_log(message, level)

    def _validate_api_keys(self) -> bool:
        """בדיקת תקינות מפתחות API."""
        errors = []

        if not self.openai_key:
            errors.append("חסר OPENAI_API_KEY (לזיהוי קול)")

        if not self.anthropic_key:
            errors.append("חסר ANTHROPIC_API_KEY (לשליטה על Roblox עם Computer Use)")

        if errors:
            error_msg = "שגיאת הגדרות:\n" + "\n".join(errors)
            error_msg += "\n\nנא ליצור קובץ .env עם המפתחות."
            if self.gui:
                self.gui.show_error(error_msg)
            else:
                print(error_msg)
            return False

        return True

    def _init_components(self) -> bool:
        """אתחול כל הרכיבים."""
        try:
            # Voice Engine
            self._log("מאתחל מנוע קול...")
            self.voice_engine = VoiceEngine(
                api_key=self.openai_key,
                language="he",
                on_state_change=self._on_voice_state_change,
                on_volume_change=self._on_volume_change
            )

            # Claude Controller (Anthropic Direct with Computer Use)
            self._log("מאתחל בקר Roblox עם Computer Use...")
            self.controller = RobloxController(
                api_key=self.anthropic_key,
                on_status_update=lambda s: self._log(s, "info"),
                on_action=lambda a: self._log(a, "action")
            )

            self._log("כל הרכיבים מוכנים!", "success")
            return True

        except Exception as e:
            self._log(f"שגיאה באתחול: {e}", "error")
            if self.gui:
                self.gui.show_error(f"שגיאה באתחול:\n{e}")
            return False

    def _on_voice_state_change(self, state: RecordingState):
        """טיפול בשינוי מצב הקלטה."""
        if self.gui:
            if state == RecordingState.RECORDING:
                self.gui.set_state(AppState.RECORDING)
            elif state == RecordingState.PROCESSING:
                self.gui.set_state(AppState.PROCESSING)
            elif state == RecordingState.ERROR:
                self.gui.set_state(AppState.ERROR)

    def _on_volume_change(self, level: float):
        """עדכון מד עוצמת קול."""
        if self.gui:
            self.gui.update_volume(level)

    def _on_start_recording(self):
        """טיפול בהתחלת הקלטה."""
        self._log("התחלתי להקליט... דבר עכשיו!", "info")
        if self.voice_engine:
            self.voice_engine.start_recording()

    def _on_stop_recording(self):
        """טיפול בעצירת הקלטה."""
        self._log("עוצר הקלטה ומעבד...", "info")

        # הרצה ב-thread נפרד כדי לא לחסום את ה-GUI
        thread = threading.Thread(target=self._process_recording)
        thread.daemon = True
        thread.start()

    def _process_recording(self):
        """עיבוד ההקלטה וביצוע הפעולה."""
        try:
            # זיהוי קול
            result = self.voice_engine.stop_and_transcribe()

            if not result.success:
                self._log(f"שגיאה בזיהוי קול: {result.error}", "error")
                if self.gui:
                    self.gui.root.after(0, lambda: self.gui.set_state(AppState.ERROR))
                return

            text = result.text
            self._log(f"זיהיתי: {text}", "success")

            if self.gui:
                self.gui.root.after(0, lambda: self.gui.set_transcription(text))
                self.gui.root.after(0, lambda: self.gui.set_state(AppState.EXECUTING))

            # ביצוע הפעולה
            self._log("מבצע את הפעולה ב-Roblox Studio...", "action")

            # הרצת הפעולה האסינכרונית
            asyncio.set_event_loop(self.loop)
            execute_result = self.loop.run_until_complete(
                self.controller.execute_command(text)
            )

            if execute_result["success"]:
                message = execute_result.get("message", "הפעולה בוצעה בהצלחה!")
                self._log(message, "success")
            else:
                error = execute_result.get("error", "שגיאה לא ידועה")
                self._log(f"שגיאה: {error}", "error")

            # חזרה למצב מוכן
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.set_state(AppState.READY))

        except Exception as e:
            self._log(f"שגיאה: {e}", "error")
            if self.gui:
                self.gui.root.after(0, lambda: self.gui.set_state(AppState.ERROR))

    def run(self):
        """הרצת האפליקציה."""
        # יצירת GUI
        self.gui = VoiceCreatorGUI(
            on_start_recording=self._on_start_recording,
            on_stop_recording=self._on_stop_recording
        )
        self.gui.create_window()

        # בדיקת מפתחות
        if not self._validate_api_keys():
            return

        # אתחול רכיבים
        if not self._init_components():
            return

        # הרצה
        self._log("מוכן! לחץ על הכפתור ודבר.", "success")
        self.gui.run()

    def cleanup(self):
        """ניקוי משאבים."""
        if self.loop:
            try:
                if not self.loop.is_running():
                    self.loop.close()
            except Exception:
                pass  # התעלם משגיאות סגירה


def test_voice_engine():
    """בדיקת מנוע הקול בלבד."""
    from voice_engine import SimpleVoiceRecorder

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("נא להגדיר OPENAI_API_KEY")
        return

    print("בדיקת מנוע קול...")
    print("מקליט למשך 5 שניות - דבר עכשיו!")

    recorder = SimpleVoiceRecorder(api_key)
    text = recorder.record_and_transcribe(5.0)
    print(f"\nזוהה: {text}")


def test_controller():
    """בדיקת הבקר בלבד (ללא Computer Use אמיתי)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("נא להגדיר ANTHROPIC_API_KEY")
        return

    print("בדיקת בקר Roblox...")

    controller = RobloxController(
        api_key=api_key,
        on_status_update=lambda s: print(f"[STATUS] {s}"),
        on_action=lambda a: print(f"[ACTION] {a}")
    )

    # בדיקת פירוש פקודות
    test_commands = [
        "תוסיף קוביה כחולה גדולה",
        "תעשה שהדמות תרוץ מהר",
        "תצבע באדום",
        "תגדיל את הכדור",
        "תריץ את המשחק",
    ]

    print("\nבדיקת פירוש פקודות:")
    print("-" * 50)

    for cmd in test_commands:
        parsed = controller._parse_command(cmd)
        print(f"\nפקודה: {cmd}")
        print(f"  סוג: {parsed.command_type.value}")
        print(f"  פעולה: {parsed.action}")
        print(f"  מטרה: {parsed.target}")
        print(f"  פרמטרים: {parsed.parameters}")
        print(f"  ביטחון: {parsed.confidence}")


def main():
    """נקודת כניסה ראשית."""
    parser = argparse.ArgumentParser(
        description="Roblox Voice Creator - יצירת משחקי Roblox בקול!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
דוגמאות:
  python main.py                  הרצה רגילה
  python main.py --debug          הרצה עם דיבוג
  python main.py --test-voice     בדיקת מנוע קול
  python main.py --test-controller בדיקת בקר Roblox
        """
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="מצב דיבוג עם הדפסות נוספות"
    )

    parser.add_argument(
        "--test-voice",
        action="store_true",
        help="בדיקת מנוע הקול בלבד"
    )

    parser.add_argument(
        "--test-controller",
        action="store_true",
        help="בדיקת הבקר בלבד"
    )

    args = parser.parse_args()

    # טעינת משתני סביבה
    load_dotenv()

    if args.test_voice:
        test_voice_engine()
    elif args.test_controller:
        test_controller()
    else:
        app = RobloxVoiceCreatorApp(debug=args.debug)
        try:
            app.run()
        finally:
            app.cleanup()


if __name__ == "__main__":
    main()
