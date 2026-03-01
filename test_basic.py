"""
Roblox Voice Creator - Basic Tests
===================================
בדיקות בסיסיות לפני הרצת האפליקציה.

הרצה:
    python test_basic.py
"""

import sys
import os
from typing import Tuple, List


class Colors:
    """צבעים לפלט"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """הדפסת כותרת"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.RESET}\n")


def print_result(name: str, success: bool, message: str = ""):
    """הדפסת תוצאה"""
    if success:
        status = f"{Colors.GREEN}[PASS]{Colors.RESET}"
    else:
        status = f"{Colors.RED}[FAIL]{Colors.RESET}"

    try:
        print(f"  {status}  {name}")
        if message:
            print(f"         {Colors.YELLOW}{message}{Colors.RESET}")
    except UnicodeEncodeError:
        # Fallback for terminals that don't support colors
        print(f"  {'[PASS]' if success else '[FAIL]'}  {name}")
        if message:
            print(f"         {message}")


def test_python_version() -> Tuple[bool, str]:
    """בדיקת גרסת Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"נדרש Python 3.9+, נמצא {version.major}.{version.minor}"


def test_import_anthropic() -> Tuple[bool, str]:
    """בדיקת ספריית Anthropic"""
    try:
        import anthropic
        return True, f"גרסה: {anthropic.__version__}"
    except ImportError:
        return False, "pip install anthropic"


def test_import_openai() -> Tuple[bool, str]:
    """בדיקת ספריית OpenAI"""
    try:
        import openai
        return True, f"גרסה: {openai.__version__}"
    except ImportError:
        return False, "pip install openai"


def test_import_pyaudio() -> Tuple[bool, str]:
    """בדיקת ספריית PyAudio"""
    try:
        import pyaudio
        return True, "PyAudio זמין"
    except ImportError:
        return False, "pip install pyaudio (או: pipwin install pyaudio)"


def test_import_sounddevice() -> Tuple[bool, str]:
    """בדיקת ספריית sounddevice (חלופה ל-PyAudio)"""
    try:
        import sounddevice
        return True, f"גרסה: {sounddevice.__version__}"
    except ImportError:
        return False, "pip install sounddevice"


def test_import_pyautogui() -> Tuple[bool, str]:
    """בדיקת ספריית pyautogui"""
    try:
        import pyautogui
        return True, "pyautogui זמין"
    except ImportError:
        return False, "pip install pyautogui"


def test_import_pillow() -> Tuple[bool, str]:
    """בדיקת ספריית Pillow"""
    try:
        from PIL import Image
        import PIL
        return True, f"גרסה: {PIL.__version__}"
    except ImportError:
        return False, "pip install Pillow"


def test_import_numpy() -> Tuple[bool, str]:
    """בדיקת ספריית numpy"""
    try:
        import numpy
        return True, f"גרסה: {numpy.__version__}"
    except ImportError:
        return False, "pip install numpy"


def test_import_dotenv() -> Tuple[bool, str]:
    """בדיקת ספריית python-dotenv"""
    try:
        import dotenv
        return True, "python-dotenv זמין"
    except ImportError:
        return False, "pip install python-dotenv"


def test_tkinter() -> Tuple[bool, str]:
    """בדיקת tkinter"""
    try:
        import tkinter
        return True, f"גרסה: {tkinter.TkVersion}"
    except ImportError:
        return False, "tkinter לא מותקן (בדרך כלל מגיע עם Python)"


def test_env_file() -> Tuple[bool, str]:
    """בדיקת קובץ .env"""
    if os.path.exists(".env"):
        return True, "קובץ .env קיים"
    elif os.path.exists(".env.example"):
        return False, "העתק .env.example ל-.env והוסף את המפתחות"
    else:
        return False, "קובץ .env לא נמצא"


def test_openai_key() -> Tuple[bool, str]:
    """בדיקת OPENAI_API_KEY"""
    from dotenv import load_dotenv
    load_dotenv()

    key = os.getenv("OPENAI_API_KEY")
    if key and key.startswith("sk-") and len(key) > 20:
        return True, f"מפתח תקין ({key[:8]}...)"
    elif key:
        return False, "מפתח לא תקין - צריך להתחיל ב-sk-"
    else:
        return False, "OPENAI_API_KEY לא מוגדר ב-.env"


def test_openrouter_key() -> Tuple[bool, str]:
    """בדיקת OPENROUTER_API_KEY או ANTHROPIC_API_KEY"""
    from dotenv import load_dotenv
    load_dotenv()

    # בדיקת OpenRouter תחילה
    or_key = os.getenv("OPENROUTER_API_KEY")
    if or_key and or_key.startswith("sk-or-") and len(or_key) > 20:
        return True, f"OpenRouter תקין ({or_key[:12]}...)"

    # בדיקת Anthropic ישיר
    ant_key = os.getenv("ANTHROPIC_API_KEY")
    if ant_key and ant_key.startswith("sk-ant-") and len(ant_key) > 20:
        return True, f"Anthropic תקין ({ant_key[:12]}...)"

    # אם שניהם לא קיימים
    if or_key:
        return False, "OPENROUTER_API_KEY לא תקין - צריך להתחיל ב-sk-or-"
    elif ant_key:
        return False, "ANTHROPIC_API_KEY לא תקין - צריך להתחיל ב-sk-ant-"
    else:
        return False, "חסר OPENROUTER_API_KEY או ANTHROPIC_API_KEY"


def test_microphone() -> Tuple[bool, str]:
    """בדיקת מיקרופון"""
    try:
        import pyaudio
        audio = pyaudio.PyAudio()

        # חיפוש מיקרופון
        mic_count = 0
        default_mic = None

        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                mic_count += 1
                if default_mic is None:
                    default_mic = info['name']

        audio.terminate()

        if mic_count > 0:
            return True, f"נמצאו {mic_count} מיקרופונים, ברירת מחדל: {default_mic[:30]}..."
        else:
            return False, "לא נמצאו מיקרופונים"

    except Exception as e:
        return False, f"שגיאה בבדיקת מיקרופון: {e}"


def test_roblox_studio() -> Tuple[bool, str]:
    """בדיקה אם Roblox Studio מותקן"""
    import subprocess
    import platform

    if platform.system() == "Windows":
        # חיפוש ב-Windows
        possible_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Roblox"),
            os.path.expandvars(r"%PROGRAMFILES%\Roblox"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                # חיפוש RobloxStudioBeta.exe
                for root, dirs, files in os.walk(path):
                    if "RobloxStudioBeta.exe" in files:
                        return True, f"נמצא ב: {root}"

        # ניסיון לחפש בתהליכים
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq RobloxStudioBeta.exe"],
                capture_output=True,
                text=True
            )
            if "RobloxStudioBeta.exe" in result.stdout:
                return True, "Roblox Studio רץ כרגע!"
        except:
            pass

        return False, "Roblox Studio לא נמצא - נא להתקין מ-roblox.com/create"

    elif platform.system() == "Darwin":  # macOS
        if os.path.exists("/Applications/RobloxStudio.app"):
            return True, "נמצא ב-/Applications"
        return False, "Roblox Studio לא נמצא - נא להתקין"

    else:
        return False, "מערכת הפעלה לא נתמכת"


def test_screen_capture() -> Tuple[bool, str]:
    """בדיקת צילום מסך"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        width, height = screenshot.size
        return True, f"רזולוציה: {width}x{height}"
    except Exception as e:
        return False, f"שגיאה: {e}"


def test_src_files() -> Tuple[bool, str]:
    """בדיקת קבצי המקור"""
    required_files = [
        "src/main.py",
        "src/gui.py",
        "src/voice_engine.py",
        "src/claude_controller.py",
    ]

    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)

    if not missing:
        return True, "כל הקבצים קיימים"
    else:
        return False, f"חסרים: {', '.join(missing)}"


def test_command_parsing() -> Tuple[bool, str]:
    """בדיקת פירוש פקודות"""
    try:
        sys.path.insert(0, "src")
        from claude_controller import RobloxController

        # יצירת controller ללא API key (רק לבדיקת פירוש)
        controller = RobloxController.__new__(RobloxController)
        controller.COLORS_MAP = RobloxController.COLORS_MAP
        controller.SHAPES_MAP = RobloxController.SHAPES_MAP
        controller.SIZES_MAP = RobloxController.SIZES_MAP
        controller.COMMAND_KEYWORDS = RobloxController.COMMAND_KEYWORDS

        # בדיקת פקודות
        test_cases = [
            ("תוסיף קוביה כחולה", "create", "Block"),
            ("תצבע באדום", "color", None),
            ("תגדיל", "resize", None),
        ]

        passed = 0
        for text, expected_action, expected_target in test_cases:
            parsed = controller._parse_command(text)
            if parsed.action == expected_action:
                passed += 1

        return True, f"עבר {passed}/{len(test_cases)} בדיקות פירוש"

    except Exception as e:
        return False, f"שגיאה: {e}"


def run_all_tests() -> Tuple[int, int]:
    """הרצת כל הבדיקות"""
    tests = [
        ("Python Version", test_python_version),
        ("tkinter (GUI)", test_tkinter),
        ("anthropic", test_import_anthropic),
        ("openai", test_import_openai),
        ("PyAudio", test_import_pyaudio),
        ("sounddevice", test_import_sounddevice),
        ("pyautogui", test_import_pyautogui),
        ("Pillow", test_import_pillow),
        ("numpy", test_import_numpy),
        ("python-dotenv", test_import_dotenv),
    ]

    env_tests = [
        (".env File", test_env_file),
        ("OPENAI_API_KEY", test_openai_key),
        ("Claude API Key", test_openrouter_key),
    ]

    system_tests = [
        ("Microphone", test_microphone),
        ("Screen Capture", test_screen_capture),
        ("Roblox Studio", test_roblox_studio),
    ]

    project_tests = [
        ("Source Files", test_src_files),
        ("Command Parsing", test_command_parsing),
    ]

    passed = 0
    failed = 0

    # Libraries
    print_header("בדיקת ספריות")
    for name, test_func in tests:
        try:
            success, message = test_func()
            print_result(name, success, message)
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_result(name, False, str(e))
            failed += 1

    # Environment
    print_header("בדיקת סביבה")
    for name, test_func in env_tests:
        try:
            success, message = test_func()
            print_result(name, success, message)
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_result(name, False, str(e))
            failed += 1

    # System
    print_header("בדיקת מערכת")
    for name, test_func in system_tests:
        try:
            success, message = test_func()
            print_result(name, success, message)
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_result(name, False, str(e))
            failed += 1

    # Project
    print_header("בדיקת פרויקט")
    for name, test_func in project_tests:
        try:
            success, message = test_func()
            print_result(name, success, message)
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_result(name, False, str(e))
            failed += 1

    return passed, failed


def main():
    """Main"""
    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}   Roblox Voice Creator - System Check{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")

    passed, failed = run_all_tests()

    # Summary
    print_header("סיכום")
    total = passed + failed
    print(f"  {Colors.GREEN}עבר: {passed}{Colors.RESET}")
    print(f"  {Colors.RED}נכשל: {failed}{Colors.RESET}")
    print(f"  סה\"כ: {total}")

    try:
        if failed == 0:
            print(f"\n  {Colors.GREEN}{Colors.BOLD}All good! Run: python src/main.py{Colors.RESET}")
            return 0
        elif failed <= 3:
            print(f"\n  {Colors.YELLOW}{Colors.BOLD}Some issues, but might work{Colors.RESET}")
            return 1
        else:
            print(f"\n  {Colors.RED}{Colors.BOLD}Fix issues before running{Colors.RESET}")
            return 2
    except UnicodeEncodeError:
        if failed == 0:
            print("\n  All good! Run: python src/main.py")
            return 0
        elif failed <= 3:
            print("\n  Some issues, but might work")
            return 1
        else:
            print("\n  Fix issues before running")
            return 2


if __name__ == "__main__":
    sys.exit(main())
