import os
import sys
import time
import json
import platform
import hashlib
import requests
import psutil

CHECK_INTERVAL = 1800  # 30 minutes
API_ENDPOINT = "http://localhost:8000/api/report"  # Change as needed

def get_machine_id():
    # Cross-platform unique machine id
    if platform.system() == "Windows":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        return value
    elif platform.system() == "Darwin":
        return os.popen("ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { print $3; }'").read().strip().strip('"')
    else:
        return open('/etc/machine-id').read().strip()

def check_disk_encryption():
    if platform.system() == "Windows":
        # Check BitLocker status
        try:
            import subprocess
            output = subprocess.check_output('manage-bde -status', shell=True).decode()
            return "Fully Encrypted" in output
        except Exception:
            return False
    elif platform.system() == "Darwin":
        try:
            output = os.popen("fdesetup status").read()
            return "FileVault is On" in output
        except Exception:
            return False
    else:
        # Linux: check LUKS
        try:
            output = os.popen("lsblk -o NAME,TYPE,MOUNTPOINT | grep 'crypt'").read()
            return bool(output.strip())
        except Exception:
            return False

def check_os_update_status():
    if platform.system() == "Windows":
        try:
            import subprocess
            output = subprocess.check_output('powershell -Command "Get-WindowsUpdateLog"', shell=True)
            # For demo, just return True (implement actual check as needed)
            return True
        except Exception:
            return False
    elif platform.system() == "Darwin":
        try:
            output = os.popen("softwareupdate -l").read()
            return "No new software available" in output
        except Exception:
            return False
    else:
        try:
            output = os.popen("apt list --upgradable 2>/dev/null | grep -v Listing").read()
            return not bool(output.strip())
        except Exception:
            return False

def check_antivirus_status():
    if platform.system() == "Windows":
        try:
            import win32com.client
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            obj = wmi.ConnectServer(".", "root\\SecurityCenter2")
            av_products = obj.ExecQuery("Select * from AntiVirusProduct")
            return any(av.displayName for av in av_products)
        except Exception:
            return False
    elif platform.system() == "Darwin":
        # macOS: check for common AV processes
        av_processes = ["symantec", "sophos", "avast", "mcafee", "bitdefender"]
        for proc in psutil.process_iter(['name']):
            if any(av in proc.info['name'].lower() for av in av_processes):
                return True
        return False
    else:
        # Linux: check for clamav or similar
        for proc in psutil.process_iter(['name']):
            if "clamd" in proc.info['name'].lower():
                return True
        return False

def check_sleep_settings():
    if platform.system() == "Windows":
        try:
            import subprocess
            output = subprocess.check_output('powercfg -query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE', shell=True).decode()
            # Parse output for timeout (in seconds)
            for line in output.splitlines():
                if "Power Setting Index" in line:
                    seconds = int(line.split()[-1], 16)
                    return seconds <= 600
            return False
        except Exception:
            return False
    elif platform.system() == "Darwin":
        try:
            output = os.popen("pmset -g | grep sleep").read()
            for line in output.splitlines():
                if "sleep" in line:
                    minutes = int(line.split()[-1])
                    return minutes <= 10
            return False
        except Exception:
            return False
    else:
        try:
            output = os.popen("gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout").read()
            seconds = int(output.strip())
            return seconds <= 600
        except Exception:
            return False

def collect_data():
    return {
        "machine_id": get_machine_id(),
        "os": platform.system(),
        "os_version": platform.version(),
        "disk_encryption": check_disk_encryption(),
        "os_update": check_os_update_status(),
        "antivirus": check_antivirus_status(),
        "sleep_setting_ok": check_sleep_settings(),
        "timestamp": int(time.time())
    }

def hash_data(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def main():
    last_hash = None
    while True:
        data = collect_data()
        current_hash = hash_data(data)
        if current_hash != last_hash:
            try:
                resp = requests.post(API_ENDPOINT, json=data, timeout=10)
                print(f"Reported: {resp.status_code}")
            except Exception as e:
                print(f"Failed to report: {e}")
            last_hash = current_hash
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()