# 🛡️ Artifact Zero bot

A comprehensive Python-based Telegram bot designed for remote system administration, security monitoring, and "Red Team" auditing on Windows machines. This tool allows you to monitor hardware status, control system power, audit security logs, and manage files remotely via a secure Telegram interface.

## ⚡ Key Features

### **1. Surveillance & Monitoring**
* **Desktop Spy (`/rec`):** Records 10 seconds of screen activity and uploads the video.
* **Webcam & Audio:** Snaps photos (`/cam`) and records voice/room audio (`/listen`).
* **Network Scanner (`/net`):** Scans the local network for connected devices.
* **Watchdogs:** Automatically alerts you if a **New USB Drive** is plugged in or if the system comes online.

### **2. System Control**
* **Remote Power:** Lock (`/lock`), Sleep (`/sleep`), or Shutdown (`/shutdown`) the PC.
* **Process Killer:** Terminate any running application (`/kill`).
* **App Blocker:** Permanently block specific apps from running (`/block`).

### **3. Data & File Management**
* **File Browser:** Navigate folders (`/cd`, `/ls`) and download files (`/get`) to your phone.
* **System Deep Scan:** View detailed OS info, Antivirus status, and Firewall rules (`/info`).

### **4. Advanced Auditing (Red Team)**
* **Keylogger:** Captures keystrokes in the background (`/keys`).
* **WiFi Extractor:** Retrieves saved WiFi passwords (`/wifi`).
* **Browser History:** Fetches recent browsing history (`/history`).
* **Persistence:** Installs itself to Windows Startup (`/install`).

---

## 🛠️ Installation & Setup

### **Prerequisites**
You need Python 3.8+ installed on the target machine.

1.  **Install Required Libraries:**
    Open your terminal or command prompt and run the following command to install all dependencies:
    ```bash
    pip install python-telegram-bot opencv-python pyaudio requests mss numpy pyttsx3 pynput
    ```

2.  **Configuration:**
    Open the script `app.py` in a text editor (like Notepad or VS Code) and edit the configuration section at the top:
    ```python
    BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Get this from @BotFather on Telegram
    ALLOWED_USER_ID = 123456789            # Get your ID from @userinfobot
    ```

3.  **Run the Bot:**
    Navigate to the folder containing the script and run:
    ```bash
    python app.py
    ```

---

## 🎮 Command Manual

### **Surveillance**
| Command | Description |
| :--- | :--- |
| `/rec` | Records 10 seconds of the screen and sends the video file. |
| `/cam` | Takes a silent photo using the webcam. |
| `/listen` | Records 5 seconds of audio from the microphone. |
| `/net` | Scans the local network for other devices (ARP scan). |
| `/status` | Shows the public IP address and physical location. |

### **Control & Power**
| Command | Description |
| :--- | :--- |
| `/lock` | Instantly locks the Windows workstation. |
| `/sleep` | Puts the computer to sleep/suspend mode. |
| `/shutdown`| Shuts down the PC in 5 seconds. |
| `/cancel` | Cancels a pending shutdown. |
| `/kill <app>` | Kills a specific process (e.g., `/kill chrome.exe`). |
| `/block <app>` | Blocks an app from running (e.g., `/block notepad.exe`). |
| `/unblock <app>`| Removes an app from the blocklist. |

### **File System**
| Command | Description |
| :--- | :--- |
| `/ls` | Lists files and folders in the current directory. |
| `/cd <folder>` | Changes directory (use `..` to go back one folder). |
| `/get <file>` | Downloads a specific file to your Telegram chat. |

### **Advanced / Auditing**
| Command | Description |
| :--- | :--- |
| `/keys` | Dumps the captured keystrokes log to the chat. |
| `/wifi` | Extracts and displays saved WiFi networks and passwords. |
| `/history` | Grabs the last 15 visited websites (Chrome). |
| `/info` | Displays detailed System, Antivirus, and Firewall info. |
| `/install` | Installs the bot to Windows Registry for auto-start. |
| `/exec <cmd>` | Runs a custom Windows shell command (e.g., `/exec ipconfig`). |

### **Miscellaneous**
| Command | Description |
| :--- | :--- |
| `/say <text>` | Makes the computer speak the text out loud using TTS. |

---

## ⚠️ Important Notes

1.  **Admin Rights:** Some features (like `/install`, `/wifi`, or `/shutdown`) often require the script to be run as **Administrator** to work correctly.
2.  **Privacy:** This tool is powerful. Only use it on devices you own or have explicit permission to manage.
3.  **Antivirus:** Because this bot uses features like keylogging and process killing, Windows Defender may flag it. You may need to add an exclusion for the folder where the bot is running.

---

## 🚀 How to Run on Startup (Manual Method)

Since registry persistence can be flagged by antivirus, here is the standard Windows method to make your bot start automatically when the computer turns on:

1.  Press **Windows Key + R** on your keyboard.
2.  Type `shell:startup` and hit **Enter**.
3.  A folder will open. **Copy and Paste** your `app.exe` (or a shortcut to `app.py`) into this folder.

Now, every time that computer restarts, Windows will automatically launch your bot in the background.

---

## 📋 Quick Reference Sheet

| Category | Command | Description | Usage Example |
| :--- | :--- | :--- | :--- |
| **📊 Health** | `/stats` | Shows real-time CPU load, RAM usage, and System Uptime. | `/stats` |
| **📊 Health** | `/disk` | Lists all hard drives and free/used storage space. | `/disk` |
| **👁️ Spy** | `/rec` | Records 10 seconds of screen activity and sends the video. | `/rec` |
| **👁️ Spy** | `/cam` | Takes a silent photo using the webcam. | `/cam` |
| **👁️ Spy** | `/listen` | Records 5 seconds of audio from the microphone. | `/listen` |
| **👁️ Spy** | `/net` | Scans the local network for other connected devices. | `/net` |
| **🔒 Control** | `/lock` | Instantly locks the Windows workstation. | `/lock` |
| **🔒 Control** | `/sleep` | Puts the computer into Sleep/Suspend mode. | `/sleep` |
| **🔒 Control** | `/shutdown`| Shuts down the PC in 5 seconds. | `/shutdown` |
| **🔒 Control** | `/kill` | Force closes a specific running program. | `/kill chrome.exe` |
| **🔒 Control** | `/block` | Adds an app to the Blacklist (auto-kills it if opened). | `/block notepad.exe` |
| **🔒 Control** | `/unblock` | Removes an app from the Blacklist. | `/unblock notepad.exe` |
| **📂 Files** | `/ls` | Lists files and folders in the current directory. | `/ls` |
| **📂 Files** | `/cd` | Changes the current directory. | `/cd Documents` |
| **📂 Files** | `/get` | Uploads a specific file to your Telegram. | `/get resume.pdf` |
| **🛠️ Admin** | `/info` | Shows Hostname, IP, OS Version, and Antivirus status. | `/info` |
| **🛠️ Admin** | `/exec` | Runs a Windows Command Prompt command. | `/exec ipconfig` |
| **🗣️ Misc** | `/say` | Makes the laptop speak text out loud (Robot Voice). | `/say Get out!` |

### **🚨 Automated Background Features**
*(These run automatically; no command required)*

| Feature Name | Trigger Event | Bot Action |
| :--- | :--- | :--- |
| **USB Watchdog** | A USB drive is plugged in. | Sends: `🚨 USB ALERT: New Drive E:\ detected` |
| **App Watchdog** | A blocked app is opened. | Kills app & Sends: `🛡️ Blocked App Killed` |
| **Login Alert** | The script starts/User logs in. | Sends: `🔔 System Online: Monitoring active` |