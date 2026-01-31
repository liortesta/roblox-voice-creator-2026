"""
HTTP Command Server for Roblox Voice Creator
=============================================
שרת HTTP פשוט שה-Plugin ב-Roblox יכול לתשאל.

Python שולח פקודות לשרת, Roblox שואל כל שנייה אם יש פקודה חדשה.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)  # מאפשר ל-Roblox לגשת

# תור הפקודות
pending_command = None
command_lock = threading.Lock()


@app.route('/health', methods=['GET'])
def health():
    """בדיקת תקינות."""
    return jsonify({"status": "ok", "time": time.time()})


@app.route('/command', methods=['GET'])
def get_command():
    """Roblox שואל אם יש פקודה חדשה."""
    global pending_command
    with command_lock:
        if pending_command:
            cmd = pending_command
            pending_command = None  # נקה אחרי קריאה
            return jsonify({"hasCommand": True, "command": cmd})
        return jsonify({"hasCommand": False})


@app.route('/command', methods=['POST'])
def set_command():
    """Python שולח פקודה חדשה."""
    global pending_command
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "Missing command"}), 400

    with command_lock:
        pending_command = data['command']

    return jsonify({"success": True, "command": data['command']})


def start_server(port=8080, on_status=None):
    """הפעלת השרת ב-thread נפרד."""
    if on_status:
        on_status(f"מפעיל שרת HTTP על פורט {port}...")

    def run():
        # כבה לוגים של Flask
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run, daemon=True)
    server_thread.start()

    # חכה שהשרת יעלה
    time.sleep(0.5)

    if on_status:
        on_status(f"שרת HTTP פעיל על http://127.0.0.1:{port}")

    return server_thread


def send_command(lua_code: str, port=8080) -> bool:
    """שליחת פקודה לשרת."""
    import requests
    try:
        response = requests.post(
            f"http://127.0.0.1:{port}/command",
            json={"command": lua_code},
            timeout=2
        )
        return response.status_code == 200
    except Exception as e:
        print(f"שגיאה בשליחה: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Command Server for Roblox Voice Creator")
    print("=" * 50)
    print()
    print("Endpoints:")
    print("  GET  /health  - בדיקת תקינות")
    print("  GET  /command - Roblox שואל אם יש פקודה")
    print("  POST /command - Python שולח פקודה")
    print()

    # הפעל ישירות (לא ב-thread)
    app.run(host='127.0.0.1', port=8080, debug=True)
