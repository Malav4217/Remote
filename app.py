from flask import Flask, render_template_string, send_from_directory
from flask_socketio import SocketIO
import pyautogui
import os
import ctypes
import socket
from zeroconf import ServiceInfo, Zeroconf

# DPI awareness for high-res monitors
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="manifest" href="/manifest.json">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Master Remote Ultra</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        :root {
            --bg: #050505;
            --glass: rgba(255, 255, 255, 0.06);
            --border: rgba(255, 255, 255, 0.1);
            --accent-red: #ff4757;
            --accent-green: #2ed573;
            --accent-blue: #1e90ff;
            --accent-orange: #ffa502;
            --accent-win: #0078d7;
        }

        body {
            background-color: var(--bg);
            color: #efefef;
            margin: 0;
            font-family: -apple-system, system-ui, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            user-select: none;
        }

        .header {
            display: flex;
            justify-content: space-between;
            padding: 25px 25px 5px 25px;
        }

        .icon-btn {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--glass);
            border: 1px solid var(--border);
        }

        .icon-btn svg { width: 24px; height: 24px; fill: none; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
        .mute-btn svg { stroke: var(--accent-blue); }
        .win-btn svg { fill: var(--accent-win); width: 22px; height: 22px; }
        .power-btn svg { stroke: var(--accent-red); }

        #trackpad {
            position: relative;
            flex: 1.2;
            margin: 15px 20px;
            background: linear-gradient(145deg, #0d0d0d, #050505);
            border: 1px solid var(--border);
            border-radius: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255, 255, 255, 0.05);
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }

        .vol-zone-hint {
            position: absolute;
            right: 10px;
            height: 60%;
            width: 4px;
            background: var(--accent-blue);
            border-radius: 2px;
            opacity: 0.1;
        }

        .controls-container {
            flex: 1.6;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 30px;
        }

        .kb-bar {
            width: 80%;
            background: var(--glass);
            border: 1px solid var(--border);
            padding: 14px;
            border-radius: 20px;
            text-align: center;
            color: var(--accent-orange);
            font-weight: bold;
            margin-bottom: 25px;
        }

        .wheel-outer {
            position: relative;
            width: 240px;
            height: 240px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: repeat(3, 1fr);
            gap: 8px;
        }

        .d-btn {
            background: var(--glass);
            border: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.1s ease;
            font-size: 1.2rem;
        }

        .d-btn:active { transform: scale(0.92); background: rgba(255, 255, 255, 0.15); }

        .up { grid-column: 2; grid-row: 1; border-radius: 50% 50% 10px 10px; color: var(--accent-blue); }
        .down { grid-column: 2; grid-row: 3; border-radius: 10px 10px 50% 50%; color: var(--accent-blue); }
        .left { grid-column: 1; grid-row: 2; border-radius: 50% 10px 10px 50%; color: var(--accent-green); }
        .right { grid-column: 3; grid-row: 2; border-radius: 10px 50% 50% 10px; color: var(--accent-green); }

        .center-cell {
            grid-column: 2;
            grid-row: 2;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .play-pause {
            width: 85px;
            height: 85px;
            background: #111;
            border: 2px solid var(--border);
            border-radius: 50%;
            color: white;
            font-size: 1.6rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }

        #kb-overlay {
            position: fixed;
            top: -100px;
            left: 0;
            width: 100%;
            background: #121212;
            border-bottom: 2px solid var(--accent-orange);
            transition: top 0.3s ease;
            padding: 10px 15px;
            box-sizing: border-box;
            z-index: 1000;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        #kb-overlay.active { top: 0; }

        #kb-input {
            flex: 1;
            background: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            color: white;
            outline: none;
            font-size: 1rem;
        }

        .kb-action-btn { padding: 10px 15px; border-radius: 8px; border: none; font-weight: bold; color: white; }
        .send-btn { background: var(--accent-orange); }
        .cancel-btn { background: #333; }
    </style>
</head>
<body>

    <div class="header">
        <div class="icon-btn mute-btn" onclick="sendCmd('volumemute')">
            <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
                <line x1="23" y1="9" x2="17" y2="15"></line>
                <line x1="17" y1="9" x2="23" y2="15"></line>
            </svg>
        </div>
        <div class="icon-btn win-btn" onclick="sendCmd('win')">
            <svg viewBox="0 0 88 88" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 12.402l35.687-4.86.016 34.423-35.703.202zm35.687 33.474l-.016 34.373-35.671-4.887V46.101zM40.522 6.942L87.994 0v41.134l-47.472.336zm47.472 39.462v41.531l-47.472-6.756-.016-34.498z"/>
            </svg>
        </div>
        <div class="icon-btn power-btn" onclick="confirmShutdown()">
            <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path><line x1="12" y1="2" x2="12" y2="12"></line>
            </svg>
        </div>
    </div>

    <div id="kb-overlay">
        <button class="kb-action-btn cancel-btn" onclick="toggleKB(false)">✕</button>
        <input type="text" id="kb-input" placeholder="Type to PC..." autocomplete="off">
        <button class="kb-action-btn send-btn" onclick="submitText()">SEND</button>
    </div>

    <div id="trackpad">
        <div class="vol-zone-hint"></div>
        <svg viewBox="0 0 24 24" style="width: 50px; height: 50px; opacity: 0.2; stroke: white; fill: none; stroke-width: 1.5;">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
        </svg>
    </div>

    <div class="controls-container">
        <div class="kb-bar" onclick="toggleKB(true)">⌨ TYPE TEXT</div>
        
        <div class="wheel-outer">
            <div class="d-btn up" onclick="sendCmd('up')">▲</div>
            <div class="d-btn down" onclick="sendCmd('down')">▼</div>
            <div class="d-btn left" onclick="sendCmd('left')">◀</div>
            <div class="d-btn right" onclick="sendCmd('right')">▶</div>
            
            <div class="center-cell">
                <div class="play-pause" onclick="sendCmd('space')">⏯</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        const trackpad = document.getElementById('trackpad');
        const overlay = document.getElementById('kb-overlay');
        const input = document.getElementById('kb-input');
        
        const SENSITIVITY = 4.0;
        let lastX = 0, lastY = 0, moved = false;
        let isScrolling = false;
        let isVolumeSwiping = false;

        // Helper for Haptic Feedback
        function haptic(ms = 20) {
            if (navigator.vibrate) {
                navigator.vibrate(ms);
            }
        }

        function sendCmd(name) { 
            haptic(30); 
            socket.emit('cmd', name); 
        }

        function toggleKB(show) {
            haptic(15);
            if(show) { 
                overlay.classList.add('active'); 
                setTimeout(() => input.focus(), 300); 
            } else { 
                overlay.classList.remove('active'); 
                input.value = ""; 
                input.blur(); 
            }
        }

        function submitText() { 
            if(input.value) { 
                haptic(40);
                socket.emit('type_text', input.value); 
                toggleKB(false); 
            } 
        }

        input.addEventListener("keypress", (e) => { if (e.key === "Enter") submitText(); });

        function confirmShutdown() { 
            haptic(100);
            if(confirm("Shutdown PC?")) sendCmd('shutdown_now'); 
        }

        trackpad.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            const rect = trackpad.getBoundingClientRect();
            const xPercent = (touch.clientX - rect.left) / rect.width;

            if (xPercent > 0.85) {
                isVolumeSwiping = true;
                haptic(10); 
            } else if (e.touches.length === 2) {
                isScrolling = true;
            } else {
                isVolumeSwiping = false;
                isScrolling = false;
            }
            
            lastX = touch.clientX;
            lastY = touch.clientY;
            moved = false;
        });

        trackpad.addEventListener('touchmove', (e) => {
            e.preventDefault();
            moved = true;
            const touch = e.touches[0];
            const dy = touch.clientY - lastY;

            if (isVolumeSwiping) {
                if (Math.abs(dy) > 12) {
                    haptic(5); 
                    socket.emit('cmd', dy > 0 ? 'volumedown' : 'volumeup');
                    lastY = touch.clientY;
                }
            } else if (isScrolling && e.touches.length === 2) {
                if (Math.abs(dy) > 5) {
                    socket.emit('scroll', { dy: dy > 0 ? 1 : -1 });
                    lastY = touch.clientY;
                }
            } else {
                const dx = (touch.clientX - lastX) * SENSITIVITY;
                const dy_mouse = (touch.clientY - lastY) * SENSITIVITY;
                socket.emit('mouse_move', { dx, dy: dy_mouse });
                lastX = touch.clientX;
                lastY = touch.clientY;
            }
        }, { passive: false });

        trackpad.addEventListener('touchend', (e) => {
            if (!moved) {
                haptic(35);
                socket.emit('cmd', 'click');
            }
            isVolumeSwiping = false;
            isScrolling = false;
        });
        
        document.addEventListener('touchstart', function() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(() => {});
            }
        }, { once: true });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

@socketio.on('mouse_move')
def handle_mouse(data):
    pyautogui.moveRel(data['dx'], data['dy'])

@socketio.on('scroll')
def handle_scroll(data):
    pyautogui.scroll(data['dy'] * 120)

@socketio.on('type_text')
def handle_type(text):
    pyautogui.typewrite(text)
    pyautogui.press('enter')

@socketio.on('cmd')
def handle_command(cmd):
    if cmd == 'click': pyautogui.click()
    elif cmd == 'win': pyautogui.press('win')
    elif cmd == 'shutdown_now': os.system("shutdown /s /t 1")
    else: pyautogui.press(cmd)

def broadcast_service(ip):
    desc = {'version': '1.0'}
    info = ServiceInfo(
        "_http._tcp.local.",
        "MalavRemote._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=5000,
        properties=desc,
        server="pc.local.",
    )
    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    return zeroconf

# In your __main__ block:
if __name__ == '__main__':
    local_ip = socket.gethostbyname(socket.gethostname())
    zc = broadcast_service(local_ip)
    print(f"Broadcasting as http://pc.local:5000")
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        zc.unregister_all_services()