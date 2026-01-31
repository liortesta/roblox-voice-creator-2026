"""
Roblox Voice Creator - Voice Engine
====================================
מנוע זיהוי קול באמצעות OpenAI Whisper.
תומך בעברית ומותאם לדיבור של ילדים.
"""

import os
import wave
import tempfile
import threading
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time


class RecordingState(Enum):
    """מצבי הקלטה"""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class TranscriptionResult:
    """תוצאת זיהוי קול"""
    text: str                    # הטקסט שזוהה
    language: str                # השפה שזוהתה
    confidence: float            # רמת ביטחון
    duration: float              # אורך ההקלטה בשניות
    success: bool                # האם הצליח
    error: Optional[str] = None  # הודעת שגיאה אם נכשל


class VoiceEngine:
    """
    מנוע זיהוי קול עם OpenAI Whisper.

    השימוש:
    ```python
    engine = VoiceEngine(api_key="sk-...")
    engine.start_recording()
    # ... הילד מדבר ...
    result = engine.stop_and_transcribe()
    print(result.text)  # "תוסיף קוביה כחולה"
    ```
    """

    def __init__(
        self,
        api_key: str = None,
        language: str = "he",
        on_state_change: Optional[Callable[[RecordingState], None]] = None,
        on_volume_change: Optional[Callable[[float], None]] = None
    ):
        """
        אתחול מנוע הקול.

        Args:
            api_key: מפתח API של OpenAI (אם לא סופק, יקרא מ-OPENAI_API_KEY)
            language: שפת ברירת מחדל (he = עברית)
            on_state_change: callback לשינוי מצב
            on_volume_change: callback לשינוי עוצמת קול (למד ויזואלי)
        """
        # קבלת מפתח מסביבה אם לא סופק
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("נדרש OpenAI API key - הגדר OPENAI_API_KEY או העבר כפרמטר")

        self.language = language
        self.on_state_change = on_state_change or (lambda x: None)
        self.on_volume_change = on_volume_change or (lambda x: None)

        self.state = RecordingState.IDLE
        self._recording = False
        self._audio_frames = []
        self._stream = None
        self._audio = None

        # הגדרות הקלטה
        self.sample_rate = 16000  # Whisper עובד הכי טוב עם 16kHz
        self.channels = 1        # מונו
        self.chunk_size = 1024   # גודל chunk

        # אתחול OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("נא להתקין: pip install openai")

    def _set_state(self, state: RecordingState):
        """עדכון מצב והודעה ל-callback."""
        self.state = state
        self.on_state_change(state)

    def start_recording(self) -> bool:
        """
        התחלת הקלטה.

        Returns:
            True אם ההקלטה התחילה בהצלחה
        """
        if self._recording:
            return False

        try:
            import pyaudio

            self._audio = pyaudio.PyAudio()
            self._audio_frames = []
            self._recording = True

            # פתיחת stream
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )

            self._set_state(RecordingState.RECORDING)
            self._stream.start_stream()
            return True

        except ImportError:
            raise ImportError("נא להתקין: pip install pyaudio")
        except Exception as e:
            self._set_state(RecordingState.ERROR)
            print(f"שגיאה בהתחלת הקלטה: {e}")
            return False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback לקבלת אודיו."""
        import pyaudio

        if self._recording:
            self._audio_frames.append(in_data)

            # חישוב עוצמת קול למד ויזואלי
            import struct
            data = struct.unpack(f'{len(in_data)//2}h', in_data)
            volume = max(abs(min(data)), abs(max(data))) / 32768.0
            self.on_volume_change(volume)

        return (in_data, pyaudio.paContinue if self._recording else pyaudio.paComplete)

    def stop_recording(self) -> bytes:
        """
        עצירת הקלטה והחזרת האודיו.

        Returns:
            נתוני האודיו כ-bytes
        """
        if not self._recording:
            return b''

        self._recording = False

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        if self._audio:
            self._audio.terminate()
            self._audio = None

        # המרה ל-bytes
        audio_data = b''.join(self._audio_frames)
        self._audio_frames = []

        return audio_data

    def stop_and_transcribe(self) -> TranscriptionResult:
        """
        עצירת הקלטה וזיהוי הטקסט.

        Returns:
            TranscriptionResult עם הטקסט שזוהה
        """
        self._set_state(RecordingState.PROCESSING)

        audio_data = self.stop_recording()

        if not audio_data:
            self._set_state(RecordingState.IDLE)
            return TranscriptionResult(
                text="",
                language=self.language,
                confidence=0,
                duration=0,
                success=False,
                error="לא נקלט אודיו"
            )

        # שמירה לקובץ זמני
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                with wave.open(f, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data)

            # חישוב משך ההקלטה
            duration = len(audio_data) / (self.sample_rate * 2)  # 16-bit = 2 bytes

            # שליחה ל-Whisper
            result = self._transcribe_file(temp_path, duration)

            # מחיקת הקובץ הזמני
            os.unlink(temp_path)

            self._set_state(RecordingState.IDLE)
            return result

        except Exception as e:
            self._set_state(RecordingState.ERROR)
            return TranscriptionResult(
                text="",
                language=self.language,
                confidence=0,
                duration=0,
                success=False,
                error=str(e)
            )

    def _transcribe_file(self, file_path: str, duration: float) -> TranscriptionResult:
        """
        זיהוי קול מקובץ.

        Args:
            file_path: נתיב לקובץ האודיו
            duration: משך ההקלטה

        Returns:
            TranscriptionResult
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.language,
                    response_format="verbose_json"
                )

            # עיבוד התשובה
            text = response.text.strip()
            detected_language = getattr(response, 'language', self.language)

            # Whisper לא מחזיר confidence ישירות, אבל אפשר להעריך לפי אורך
            confidence = 0.9 if len(text) > 3 else 0.5

            return TranscriptionResult(
                text=text,
                language=detected_language,
                confidence=confidence,
                duration=duration,
                success=True
            )

        except Exception as e:
            return TranscriptionResult(
                text="",
                language=self.language,
                confidence=0,
                duration=duration,
                success=False,
                error=str(e)
            )

    def transcribe_audio_bytes(self, audio_data: bytes) -> TranscriptionResult:
        """
        זיהוי קול מ-bytes ישירות.
        שימושי אם יש לך אודיו ממקור אחר.

        Args:
            audio_data: נתוני האודיו

        Returns:
            TranscriptionResult
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            with wave.open(f, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)

        duration = len(audio_data) / (self.sample_rate * 2)
        result = self._transcribe_file(temp_path, duration)
        os.unlink(temp_path)
        return result

    def is_recording(self) -> bool:
        """האם כרגע מקליט?"""
        return self._recording

    def get_state(self) -> RecordingState:
        """החזרת המצב הנוכחי."""
        return self.state


class SimpleVoiceRecorder:
    """
    גרסה פשוטה יותר להקלטת קול ללא callbacks.
    טובה לבדיקות ולשימוש פשוט.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sample_rate = 16000
        self.channels = 1

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("נא להתקין: pip install openai")

    def record_and_transcribe(self, duration_seconds: float = 5.0) -> str:
        """
        הקלטה למשך זמן קבוע וזיהוי.

        Args:
            duration_seconds: משך ההקלטה בשניות

        Returns:
            הטקסט שזוהה
        """
        try:
            import pyaudio

            audio = pyaudio.PyAudio()
            frames = []

            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=1024
            )

            print(f"מקליט למשך {duration_seconds} שניות...")

            for _ in range(int(self.sample_rate / 1024 * duration_seconds)):
                data = stream.read(1024)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()

            print("מעבד...")

            # שמירה לקובץ זמני
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                with wave.open(f, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(frames))

            # זיהוי
            with open(temp_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="he"
                )

            os.unlink(temp_path)
            return response.text.strip()

        except ImportError:
            raise ImportError("נא להתקין: pip install pyaudio")
        except Exception as e:
            return f"שגיאה: {e}"


# שימוש לדוגמה
if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("נא להגדיר OPENAI_API_KEY")
        exit(1)

    # בדיקה פשוטה
    recorder = SimpleVoiceRecorder(api_key)
    text = recorder.record_and_transcribe(3.0)
    print(f"זוהה: {text}")
