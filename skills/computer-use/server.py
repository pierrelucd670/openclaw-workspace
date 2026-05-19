#!/usr/bin/env python3
"""Computer Use HTTP Server - runs on Windows desktop session, listens on LAN"""
import json, base64, io, os, sys, time
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import mss, mss.tools, pyautogui
except ImportError as e:
    print(f"Missing module: {e}")
    sys.exit(1)

pyautogui.FAILSAFE = True
PORT = 9876

class ComputerUseHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # quiet
    
    def _json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def do_GET(self):
        path = self.path.rstrip("/")
        try:
            if path == "/screen_size":
                self._json({"width": pyautogui.size()[0], "height": pyautogui.size()[1]})
            elif path == "/mouse_pos":
                pos = pyautogui.position()
                self._json({"x": pos[0], "y": pos[1]})
            elif path == "/screenshot":
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    img = sct.grab(monitor)
                    png = mss.tools.to_png(img.rgb, img.size)
                    b64 = base64.b64encode(png).decode()
                    self._json({"screenshot_base64": b64, "width": monitor["width"], "height": monitor["height"]})
            elif path == "/health":
                self._json({"status": "ok", "host": os.environ.get("COMPUTERNAME", "?")})
            else:
                self._json({"error": "unknown endpoint", "available": ["/screenshot","/screen_size","/mouse_pos","/click","/type","/press","/scroll","/health"]}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        path = self.path.rstrip("/")
        try:
            if path == "/click":
                x, y = body["x"], body["y"]
                btn = body.get("button", "left")
                clicks = body.get("clicks", 1)
                pyautogui.click(x, y, button=btn, clicks=clicks)
                self._json({"ok": True, "action": "click", "x": x, "y": y})
            elif path == "/type":
                text = body["text"]
                interval = body.get("interval", 0.05)
                pyautogui.typewrite(text, interval=interval)
                self._json({"ok": True, "action": "type", "text": text})
            elif path == "/press":
                keys = body["keys"]
                pyautogui.hotkey(*keys.split("+"))
                self._json({"ok": True, "action": "press", "keys": keys})
            elif path == "/scroll":
                amount = body.get("amount", 3)
                x, y = body.get("x"), body.get("y")
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=0.05)
                pyautogui.scroll(amount)
                self._json({"ok": True, "action": "scroll", "amount": amount})
            elif path == "/move":
                x, y = body["x"], body["y"]
                dur = body.get("duration", 0.2)
                pyautogui.moveTo(x, y, duration=dur)
                self._json({"ok": True, "action": "move", "x": x, "y": y})
            else:
                self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

if __name__ == "__main__":
    print(f"🖥️  Computer Use Server")
    print(f"   http://{os.environ.get('COMPUTERNAME','localhost')}:{PORT}")
    print(f"   http://192.168.2.13:{PORT}")
    print(f"   Ctrl+C to stop")
    server = HTTPServer(("0.0.0.0", PORT), ComputerUseHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
