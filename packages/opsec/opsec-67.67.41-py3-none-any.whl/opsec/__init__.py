# opsec/__init__.py

import time
import sys
import random

__version__ = "0.0.1337"
__author__ = "SkidSec™"
__all__ = [
    "init",
    "hide_ip",
    "scrub_discord",
    "spoof_mac",
    "wipe_hwid",
    "report_status",
    "enable_military_mode",
    "burn_logs",
    "encrypt_brain",
    "clear_temp_folder",
    "install_ransomware_as_cover",
    "run"
]

def _loading_bar(task, seconds=2):
    sys.stdout.write(f"[opsec] {task.ljust(30)} [")
    sys.stdout.flush()
    for _ in range(20):
        sys.stdout.write("#")
        sys.stdout.flush()
        time.sleep(seconds / 20)
    sys.stdout.write("] ✅\n")
    sys.stdout.flush()

def init():
    print("[opsec] Initializing...")

def hide_ip():
    _loading_bar("Hiding IP")
    print(" - IP changed to 127.0.0.1 YEAH FUCK YOU JJSPLOIT IP LOGGER")

def scrub_discord():
    _loading_bar("Cleaning Discord dms with ekittens")

def spoof_mac():
    _loading_bar("Spoofing MAC Address")
    print(" - MAC now FA:KE:69:69:69:69")

def wipe_hwid():
    _loading_bar("Wiping HWID")
    print(" - Ur BIOS is bricked :skull:")

def enable_military_mode():
    _loading_bar("Enabling Military-Grade Mode")
    print(" - idek bro")

def burn_logs():
    _loading_bar("Deleting Logs")
    print(" - ur entire appdata is wiped ngl")

def encrypt_brain():
    _loading_bar("encrypting niggalink brain")

def clear_temp_folder():
    _loading_bar("Clearing TEMP Folder")
    print(" - deleted 241 rats from ur %tmp%")

def install_ransomware_as_cover():
    _loading_bar("Deploying Fake Ransomware")

def report_status():
    print("\n[opsec] FINAL STATUS REPORT:")
    print(" - Yea ggs ur detected :sob:")

def run():
    print("[opsec] Running OPSEC...\n")
    time.sleep(1)
    
    init()
    time.sleep(0.5)
    hide_ip()
    time.sleep(0.5)
    scrub_discord()
    time.sleep(0.5)
    spoof_mac()
    time.sleep(0.5)
    wipe_hwid()
    time.sleep(0.5)
    enable_military_mode()
    time.sleep(0.5)
    burn_logs()
    time.sleep(0.5)
    encrypt_brain()
    time.sleep(0.5)
    clear_temp_folder()
    time.sleep(0.5)
    install_ransomware_as_cover()
    time.sleep(0.5)
    report_status()
    print("[opsec] Protocol complete.\n")
