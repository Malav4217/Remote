<p align="center">
  <img src="https://placehold.co/1200x400/0f172a/ffffff?text=Remote" alt="Remote Banner" width="850">
</p>


## Project Motivation

While numerous remote-control applications exist in the market, many are burdened with intrusive advertisements or require premium subscriptions for essential features such as low-latency input and haptic feedback. This tool was engineered as a lightweight, privacy-focused, and entirely free solution tailored to specific developer requirements.

---

## Technical Features

- **Zero-Configuration Discovery**: Utilizes mDNS (Zeroconf) to allow connection via `http://pc.local:5000`, eliminating the need for static IP addresses.
- **High-DPI Awareness**: Custom Windows API integration ensures mouse precision is maintained across 4K and other high-resolution displays.
- **Real-Time Haptic Feedback**: Integrated vibration feedback for clicks, scrolls, and volume adjustments.
- **Progressive Web App (PWA) Support**: Configured via `manifest.json` to allow installation as a standalone, full-screen mobile application.

---

## Installation and Setup

### 1. Requirements

- **Python 3.11+** installed on Windows.
- Required Python libraries: `flask`, `flask-socketio`, `pyautogui`, `zeroconf`.

### 2. Dependency Installation

Run the following command in your terminal:

```bash
pip install flask flask-socketio pyautogui zeroconf
```
### 3. File Organization

Ensure `app.py`, `manifest.json`, and `run_remote.vbs` are placed in the same project directory.

---

## Automated Background Startup

To ensure the remote server is available immediately upon login without a persistent terminal window, use the included VBScript.

### Step 1: Configure the VBScript

Open `run_remote.vbs` and update the directory path to match your local installation:

```vbscript
Set WshShell = CreateObject("WScript.Shell")

' REPLACE THE PATH BELOW with your actual folder location
WshShell.CurrentDirectory = "C:\Users\Your_Path\remote" 

WshShell.Run "pythonw app.py", 0
Set WshShell = Nothing
```
### Step 2: Configure Windows Startup

1. Press `Win + R`, type `shell:startup`, and press Enter.
2. Create a shortcut of your `run_remote.vbs` file.
3. Move the shortcut into the Startup folder.
4. The server will now launch silently in the background whenever you log in.

---

## Mobile Implementation

To achieve a native application experience on a mobile device:

1. Connect the mobile device to the same Wi-Fi network as the PC.
2. Open the mobile browser and navigate to `http://pc.local:5000`.
3. Select **"Add to Home Screen"** from the browser menu.
4. Launch the application from the home screen for a full-screen interface.

---
## Project Screenshots

<p align="center">
  <img src="https://github.com/Malav4217/Remote/blob/main/screenshot.png" alt="Master Remote Ultra PC and Mobile Views" width="800">
</p>

---
## Tech Stack
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

---

## Developed By

**Malav Patel**
