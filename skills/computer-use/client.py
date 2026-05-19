#!/usr/bin/env python3
"""Computer Use agent for Windows - screenshot, click, type via SSH"""
import sys, json, base64, io, os, time

try:
    import mss
    import mss.tools
    import pyautogui
except ImportError as e:
    print(json.dumps({"error": f"ImportError: {e}"}))
    sys.exit(1)

# Safety: pyautogui fail-safe - move mouse to corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

OUTPUT_DIR = os.path.expanduser(r"~\.openclaw\computer-use\outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def screenshot():
    """Take a screenshot, return base64 PNG"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        img = sct.grab(monitor)
        png = mss.tools.to_png(img.rgb, img.size)
        buf = io.BytesIO()
        buf.write(png)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

def click(x: int, y: int, button: str = "left", clicks: int = 1):
    """Click at coordinates"""
    pyautogui.click(x, y, button=button, clicks=clicks)
    return {"ok": True, "x": x, "y": y, "button": button}

def double_click(x: int, y: int):
    """Double click at coordinates"""
    pyautogui.doubleClick(x, y)
    return {"ok": True, "x": x, "y": y}

def type_text(text: str, interval: float = 0.05):
    """Type text"""
    pyautogui.typewrite(text, interval=interval)
    return {"ok": True, "text": text}

def press_keys(keys: str):
    """Press key combination like 'ctrl+c'"""
    pyautogui.hotkey(*keys.split('+'))
    return {"ok": True, "keys": keys}

def move_mouse(x: int, y: int, duration: float = 0.2):
    """Move mouse smoothly"""
    pyautogui.moveTo(x, y, duration=duration)
    return {"ok": True, "x": x, "y": y}

def scroll(amount: int, x: int = None, y: int = None):
    """Scroll at position or current"""
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.05)
    pyautogui.scroll(amount)
    return {"ok": True, "amount": amount}

def screen_size():
    """Get screen resolution"""
    return {"width": pyautogui.size()[0], "height": pyautogui.size()[1]}

def mouse_position():
    """Get current mouse position"""
    pos = pyautogui.position()
    return {"x": pos[0], "y": pos[1]}

COMMANDS = {
    "screenshot": screenshot,
    "click": click,
    "double_click": double_click,
    "type": type_text,
    "press": press_keys,
    "move": move_mouse,
    "scroll": scroll,
    "screen_size": screen_size,
    "mouse_pos": mouse_position,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: computer_use.py <command> [args...]", "commands": list(COMMANDS.keys())}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(json.dumps({"error": f"Unknown command: {cmd}", "available": list(COMMANDS.keys())}))
        sys.exit(1)
    
    try:
        if cmd == "screenshot":
            result = screenshot()
            # Truncate for JSON output - only show first 50 chars
            print(json.dumps({"screenshot_base64": result[:50] + "...", "full_length": len(result)}))
        elif cmd == "click":
            result = click(int(sys.argv[2]), int(sys.argv[3]), 
                          button=sys.argv[4] if len(sys.argv) > 4 else "left")
            print(json.dumps(result))
        elif cmd == "double_click":
            result = double_click(int(sys.argv[2]), int(sys.argv[3]))
            print(json.dumps(result))
        elif cmd == "type":
            result = type_text(" ".join(sys.argv[2:]))
            print(json.dumps(result))
        elif cmd == "press":
            result = press_keys(sys.argv[2])
            print(json.dumps(result))
        elif cmd == "move":
            result = move_mouse(int(sys.argv[2]), int(sys.argv[3]))
            print(json.dumps(result))
        elif cmd == "scroll":
            result = scroll(int(sys.argv[2]))
            print(json.dumps(result))
        elif cmd == "screen_size":
            result = screen_size()
            print(json.dumps(result))
        elif cmd == "mouse_pos":
            result = mouse_position()
            print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
