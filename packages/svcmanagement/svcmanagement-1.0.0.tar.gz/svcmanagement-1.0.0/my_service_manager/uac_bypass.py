import winreg
import ctypes
import sys

def request_admin():
    """Relaunch the script as administrator if not already."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def disable_uac():
    """Disable UAC settings by modifying the Windows registry."""
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        print("[*] Opening registry key for UAC settings...")

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            # Disable UAC prompts
            print("[*] Disabling 'ConsentPromptBehaviorAdmin'...")
            winreg.SetValueEx(reg_key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
            print("[+] 'ConsentPromptBehaviorAdmin' set to 0 (No prompt).")

            print("[*] Disabling 'EnableLUA'...")
            winreg.SetValueEx(reg_key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            print("[+] 'EnableLUA' set to 0 (UAC disabled).")

        print("[*] UAC settings have been disabled. A system restart is required for changes to take effect.")
    except PermissionError:
        print("[-] Access denied. Please run this script as Administrator.")
    except Exception as e:
        print(f"[-] Failed to disable UAC settings: {e}")

if __name__ == "__main__":
    print("[*] Checking administrator privileges...")
    if not request_admin():
        sys.exit("[-] Failed to elevate privileges. Exiting.")

    print("[*] Starting UAC disable process...")
    disable_uac()
    print("[*] UAC disable process completed.")
