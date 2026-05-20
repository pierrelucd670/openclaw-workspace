#!/usr/bin/env python3
"""
Computer Use Server v2 — Windows 11 Remote Control
Adds /paste endpoint for reliable text input via clipboard.
"""
import http.server
import json
import base64
import io
import traceback
import pyautogui
import pyperclip
from mss import mss

PORT = 9876
pyautogui.FAILSAFE = False

def screenshot_base64():
    with mss() as sct:
        img = sct.grab(sct.monitors[1])
        png = io.BytesIO()
        import mss.tools
        mss.tools.to_png(img.rgb, img.size, output=png)
        return base64.b64encode(png.getvalue()).decode()

class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/health":
            self._send({"status": "ok", "host": "PEYO670-PC", "version": 2})
        elif self.path == "/screenshot":
            self._send({"screenshot_base64": screenshot_base64(), "width": 2560, "height": 1440})
        elif self.path == "/screen_size":
            self._send({"width": pyautogui.size().width, "height": pyautogui.size().height})
        elif self.path == "/mouse_pos":
            p = pyautogui.position()
            self._send({"x": p.x, "y": p.y})
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        
        try:
            if self.path == "/click":
                pyautogui.click(body.get("x"), body.get("y"), button=body.get("button", "left"))
                self._send({"ok": True, "action": "click", "x": body.get("x"), "y": body.get("y")})
            
            elif self.path == "/type":
                text = body.get("text", "")
                pyautogui.typewrite(text, interval=0.02)
                self._send({"ok": True, "action": "type", "text": text})
            
            elif self.path == "/paste":
                # NEW: Reliable clipboard paste
                text = body.get("text", "")
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                self._send({"ok": True, "action": "paste", "text": text[:100] + ("..." if len(text)>100 else "")})
            
            elif self.path == "/press":
                keys = body.get("keys", "")
                pyautogui.hotkey(*keys.split("+"))
                self._send({"ok": True, "action": "press", "keys": keys})
            
            elif self.path == "/scroll":
                pyautogui.scroll(body.get("amount", 3), body.get("x", None), body.get("y", None))
                self._send({"ok": True, "action": "scroll"})
            
            elif self.path == "/move":
                pyautogui.moveTo(body.get("x"), body.get("y"))
                self._send({"ok": True, "action": "move", "x": body.get("x"), "y": body.get("y")})
            
            else:
                self._send({"error": "not found"}, 404)
        except Exception as e:
            self._send({"ok": False, "error": str(e), "trace": traceback.format_exc()[:500]}, 500)

print(f"Computer Use Server v2 on port {PORT}")
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
