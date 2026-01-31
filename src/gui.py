"""
Roblox Voice Creator - GUI
===========================
ממשק משתמש גרפי ידידותי לילדים.
כפתור גדול וצבעוני "לחץ ודבר" עם פידבק ויזואלי.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import threading
from enum import Enum
import datetime
import os


class AppState(Enum):
    """מצבי האפליקציה"""
    READY = "ready"           # מוכן להקלטה
    RECORDING = "recording"   # מקליט
    PROCESSING = "processing" # מעבד
    EXECUTING = "executing"   # מבצע פעולה ברובלוקס
    ERROR = "error"           # שגיאה


class VoiceCreatorGUI:
    """
    ממשק גרפי ראשי לאפליקציה.

    מאפיינים:
    - כפתור גדול וצבעוני "לחץ ודבר"
    - מד עוצמת קול
    - תצוגת טקסט של מה שזוהה
    - לוג פעולות
    - רשימת פקודות לדוגמה
    """

    # צבעים ידידותיים לילדים
    COLORS = {
        "bg": "#1a1a2e",           # רקע כהה
        "primary": "#4ade80",       # ירוק בהיר
        "secondary": "#60a5fa",     # כחול בהיר
        "accent": "#f472b6",        # ורוד
        "warning": "#fbbf24",       # צהוב
        "error": "#ef4444",         # אדום
        "text": "#ffffff",          # לבן
        "text_secondary": "#94a3b8", # אפור
        "button_ready": "#22c55e",   # ירוק - מוכן
        "button_recording": "#ef4444", # אדום - מקליט
        "button_processing": "#f59e0b", # כתום - מעבד
    }

    def __init__(
        self,
        on_start_recording: Optional[Callable[[], None]] = None,
        on_stop_recording: Optional[Callable[[], None]] = None,
        title: str = "Roblox Voice Creator"
    ):
        """
        אתחול הממשק.

        Args:
            on_start_recording: callback כשמתחילים הקלטה
            on_stop_recording: callback כשמפסיקים הקלטה
            title: כותרת החלון
        """
        self.on_start_recording = on_start_recording or (lambda: None)
        self.on_stop_recording = on_stop_recording or (lambda: None)

        self.state = AppState.READY
        self.root = None
        self.main_button = None
        self.status_label = None
        self.transcription_label = None
        self.log_text = None
        self.volume_canvas = None
        self.volume_bar = None

    def create_window(self) -> tk.Tk:
        """יצירת החלון הראשי."""
        self.root = tk.Tk()
        self.root.title("Roblox Voice Creator")
        self.root.geometry("600x700")
        self.root.configure(bg=self.COLORS["bg"])
        self.root.resizable(True, True)

        # מרכוז החלון
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self._create_widgets()
        return self.root

    def _create_widgets(self):
        """יצירת כל הווידג'טים."""

        # כותרת
        title_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text="Roblox Voice Creator",
            font=("Segoe UI", 28, "bold"),
            fg=self.COLORS["primary"],
            bg=self.COLORS["bg"]
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="דבר ובנה משחקים!",
            font=("Segoe UI", 14),
            fg=self.COLORS["text_secondary"],
            bg=self.COLORS["bg"]
        )
        subtitle_label.pack()

        # כפתור ראשי - גדול וצבעוני
        button_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        button_frame.pack(pady=30)

        self.main_button = tk.Button(
            button_frame,
            text="לחץ ודבר",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg=self.COLORS["button_ready"],
            activebackground=self.COLORS["button_recording"],
            activeforeground="white",
            width=15,
            height=3,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_button_click
        )
        self.main_button.pack()

        # סטטוס
        self.status_label = tk.Label(
            self.root,
            text="לחץ על הכפתור ואמור מה אתה רוצה לבנות!",
            font=("Segoe UI", 12),
            fg=self.COLORS["text_secondary"],
            bg=self.COLORS["bg"]
        )
        self.status_label.pack(pady=10)

        # מד עוצמת קול
        volume_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        volume_frame.pack(pady=10)

        tk.Label(
            volume_frame,
            text="עוצמת קול:",
            font=("Segoe UI", 10),
            fg=self.COLORS["text_secondary"],
            bg=self.COLORS["bg"]
        ).pack(side=tk.LEFT, padx=5)

        self.volume_canvas = tk.Canvas(
            volume_frame,
            width=200,
            height=20,
            bg=self.COLORS["bg"],
            highlightthickness=0
        )
        self.volume_canvas.pack(side=tk.LEFT)

        # רקע של המד
        self.volume_canvas.create_rectangle(0, 0, 200, 20, fill="#333", outline="")
        # הבר עצמו
        self.volume_bar = self.volume_canvas.create_rectangle(0, 0, 0, 20, fill=self.COLORS["primary"], outline="")

        # תצוגת טקסט שזוהה
        transcription_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        transcription_frame.pack(pady=20, padx=30, fill=tk.X)

        tk.Label(
            transcription_frame,
            text="מה אמרת:",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLORS["secondary"],
            bg=self.COLORS["bg"]
        ).pack(anchor=tk.W)

        self.transcription_label = tk.Label(
            transcription_frame,
            text="...",
            font=("Segoe UI", 14),
            fg=self.COLORS["text"],
            bg="#2a2a4a",
            wraplength=500,
            justify=tk.CENTER,
            pady=15,
            padx=15
        )
        self.transcription_label.pack(fill=tk.X)

        # לוג פעולות
        log_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        log_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

        tk.Label(
            log_frame,
            text="מה קורה:",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg"]
        ).pack(anchor=tk.W)

        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 10),
            fg=self.COLORS["text"],
            bg="#2a2a4a",
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar ללוג
        scrollbar = ttk.Scrollbar(self.log_text, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # כפתור העתקת לוגים
        buttons_frame = tk.Frame(log_frame, bg=self.COLORS["bg"])
        buttons_frame.pack(fill=tk.X, pady=5)

        self.copy_button = tk.Button(
            buttons_frame,
            text="[Copy Logs]",
            font=("Segoe UI", 9),
            bg="#3498DB",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._copy_logs
        )
        self.copy_button.pack(side=tk.LEFT, padx=2)

        self.clear_button = tk.Button(
            buttons_frame,
            text="[Clear]",
            font=("Segoe UI", 9),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_log
        )
        self.clear_button.pack(side=tk.LEFT, padx=2)

        self.open_log_button = tk.Button(
            buttons_frame,
            text="[Open Log File]",
            font=("Segoe UI", 9),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._open_log_file
        )
        self.open_log_button.pack(side=tk.LEFT, padx=2)

        # פקודות לדוגמה
        examples_frame = tk.Frame(self.root, bg=self.COLORS["bg"])
        examples_frame.pack(pady=10, padx=30, fill=tk.X)

        tk.Label(
            examples_frame,
            text="דוגמאות למה שאפשר להגיד:",
            font=("Segoe UI", 10, "bold"),
            fg=self.COLORS["warning"],
            bg=self.COLORS["bg"]
        ).pack(anchor=tk.W)

        examples = [
            '"תוסיף קוביה כחולה"',
            '"תעשה שהדמות תרוץ מהר"',
            '"תגדיל את הקוביה"',
            '"תריץ את המשחק"'
        ]

        examples_text = "  |  ".join(examples)
        tk.Label(
            examples_frame,
            text=examples_text,
            font=("Segoe UI", 9),
            fg=self.COLORS["text_secondary"],
            bg=self.COLORS["bg"],
            wraplength=550
        ).pack(anchor=tk.W)

    def _on_button_click(self):
        """טיפול בלחיצה על הכפתור הראשי."""
        if self.state == AppState.READY:
            self._start_recording()
        elif self.state == AppState.RECORDING:
            self._stop_recording()

    def _start_recording(self):
        """התחלת הקלטה."""
        self.set_state(AppState.RECORDING)
        self.on_start_recording()

    def _stop_recording(self):
        """עצירת הקלטה."""
        self.set_state(AppState.PROCESSING)
        self.on_stop_recording()

    def set_state(self, state: AppState):
        """
        שינוי מצב האפליקציה ועדכון הממשק.

        Args:
            state: המצב החדש
        """
        self.state = state

        if self.root is None:
            return

        if state == AppState.READY:
            self.main_button.configure(
                text="לחץ ודבר",
                bg=self.COLORS["button_ready"],
                state=tk.NORMAL
            )
            self.status_label.configure(text="לחץ על הכפתור ואמור מה אתה רוצה לבנות!")
            # החזר את החלון למרכז המסך
            try:
                self.root.deiconify()
                self.root.lift()
                # החזר לגודל ומיקום מקורי (מרכז המסך)
                self.root.geometry("500x700")
                self.root.update_idletasks()
                x = (self.root.winfo_screenwidth() - 500) // 2
                y = (self.root.winfo_screenheight() - 700) // 2
                self.root.geometry(f"500x700+{x}+{y}")
            except:
                pass

        elif state == AppState.RECORDING:
            self.main_button.configure(
                text="מקליט... לחץ לסיום",
                bg=self.COLORS["button_recording"],
                state=tk.NORMAL
            )
            self.status_label.configure(text="מקשיב... דבר עכשיו!")

        elif state == AppState.PROCESSING:
            self.main_button.configure(
                text="מעבד...",
                bg=self.COLORS["button_processing"],
                state=tk.DISABLED
            )
            self.status_label.configure(text="מנסה להבין מה אמרת...")

        elif state == AppState.EXECUTING:
            self.main_button.configure(
                text="מבצע...",
                bg=self.COLORS["secondary"],
                state=tk.DISABLED
            )
            self.status_label.configure(text="עובד על זה ב-Roblox Studio! אל תזיז את העכבר!")
            # שים את החלון במסך שני/שלישי כדי לא להפריע
            try:
                # X=2000 יעביר למסך השני (אם יש)
                # אם אין מסך שני - יהיה בקצה הימני של המסך הראשי
                self.root.geometry("400x600+2000+100")
                self.root.attributes('-topmost', False)  # לא תמיד למעלה
            except:
                pass

        elif state == AppState.ERROR:
            self.main_button.configure(
                text="לחץ לנסות שוב",
                bg=self.COLORS["error"],
                state=tk.NORMAL
            )
            self.status_label.configure(text="אופס! משהו השתבש. נסה שוב!")

        self.root.update()

    def update_volume(self, level: float):
        """
        עדכון מד עוצמת הקול.

        Args:
            level: רמת העוצמה (0-1)
        """
        if self.volume_canvas and self.volume_bar:
            width = int(level * 200)
            self.volume_canvas.coords(self.volume_bar, 0, 0, width, 20)

            # שינוי צבע לפי עוצמה
            if level < 0.3:
                color = self.COLORS["primary"]
            elif level < 0.7:
                color = self.COLORS["warning"]
            else:
                color = self.COLORS["error"]
            self.volume_canvas.itemconfig(self.volume_bar, fill=color)

    def set_transcription(self, text: str):
        """
        הצגת הטקסט שזוהה.

        Args:
            text: הטקסט שזוהה מהקול
        """
        if self.transcription_label:
            self.transcription_label.configure(text=text if text else "...")

    def add_log(self, message: str, level: str = "info"):
        """
        הוספת הודעה ללוג.

        Args:
            message: ההודעה
            level: רמת ההודעה (info/success/warning/error)
        """
        if self.log_text is None:
            return

        # בחירת אייקון (ASCII בלבד - תואם Windows)
        icons = {
            "info": "[INFO]",
            "success": "[OK]",
            "warning": "[WARN]",
            "error": "[ERR]",
            "action": "[ACT]"
        }
        icon = icons.get(level, "[*]")

        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{icon} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

        # שמירה לקובץ לוג
        self._save_to_log_file(f"{icon} {message}")

    def clear_log(self):
        """ניקוי הלוג."""
        if self.log_text:
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.configure(state=tk.DISABLED)

    def show_error(self, message: str):
        """
        הצגת הודעת שגיאה.

        Args:
            message: הודעת השגיאה
        """
        messagebox.showerror("שגיאה", message)

    def show_success(self, message: str):
        """
        הצגת הודעת הצלחה.

        Args:
            message: הודעת ההצלחה
        """
        messagebox.showinfo("הצלחה!", message)

    def run(self):
        """הרצת האפליקציה."""
        if self.root is None:
            self.create_window()
        self.root.mainloop()

    def _copy_logs(self):
        """העתקת כל הלוגים ל-clipboard."""
        if self.log_text:
            logs = self.log_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(logs)
            self.status_label.configure(text="Logs copied to clipboard!", fg="#27AE60")
            # החזרת הסטטוס אחרי 2 שניות
            self.root.after(2000, lambda: self.status_label.configure(
                text="Click the button and say what you want to build!",
                fg=self.COLORS["text_secondary"]
            ))

    def _save_to_log_file(self, message: str):
        """שמירת הודעה לקובץ לוג."""
        try:
            log_file = "roblox_voice_creator.log"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass  # התעלם משגיאות שמירה

    def _open_log_file(self):
        """פתיחת קובץ הלוג."""
        log_file = "roblox_voice_creator.log"
        if os.path.exists(log_file):
            os.startfile(log_file)  # Windows
        else:
            self.status_label.configure(text="No log file yet", fg=self.COLORS["warning"])

    def destroy(self):
        """סגירת האפליקציה."""
        if self.root:
            self.root.destroy()


class LoadingWindow:
    """חלון טעינה פשוט."""

    def __init__(self, message: str = "טוען..."):
        self.root = tk.Toplevel()
        self.root.title("")
        self.root.geometry("300x100")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # ללא כותרת

        # מרכוז
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 150
        y = (self.root.winfo_screenheight() // 2) - 50
        self.root.geometry(f'+{x}+{y}')

        tk.Label(
            self.root,
            text=message,
            font=("Segoe UI", 14),
            fg="white",
            bg="#1a1a2e"
        ).pack(expand=True)

    def update_message(self, message: str):
        """עדכון ההודעה."""
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(text=message)

    def close(self):
        """סגירה."""
        self.root.destroy()


# דוגמה לשימוש
if __name__ == "__main__":
    def on_start():
        print("Recording started!")
        gui.add_log("התחלתי להקליט", "info")

    def on_stop():
        print("Recording stopped!")
        gui.add_log("עצרתי להקליט", "info")
        gui.set_transcription("תוסיף קוביה כחולה")
        gui.add_log("זיהיתי: תוסיף קוביה כחולה", "success")

        # סימולציה של עיבוד
        gui.root.after(1000, lambda: gui.set_state(AppState.EXECUTING))
        gui.root.after(1000, lambda: gui.add_log("יוצר קוביה...", "action"))
        gui.root.after(2000, lambda: gui.add_log("צובע בכחול...", "action"))
        gui.root.after(3000, lambda: gui.add_log("הקוביה הכחולה נוצרה!", "success"))
        gui.root.after(3000, lambda: gui.set_state(AppState.READY))

    gui = VoiceCreatorGUI(
        on_start_recording=on_start,
        on_stop_recording=on_stop
    )
    gui.run()
