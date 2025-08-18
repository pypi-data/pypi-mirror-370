import winreg
import ctypes
import sys

def request_admin():
    """Attempt to relaunch the script as administrator."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def restore_uac():
    """Restore UAC settings to re-enable prompts with detailed logs."""
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        print("[*] Opening registry key...")
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            # Restore default UAC settings
            print("[*] Restoring 'ConsentPromptBehaviorAdmin' to default (5)...")
            winreg.SetValueEx(reg_key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 5)
            print("[+] 'ConsentPromptBehaviorAdmin' set to 5 (Prompt for consent).")

            print("[*] Restoring 'EnableLUA' to default (1)...")
            winreg.SetValueEx(reg_key, "EnableLUA", 0, winreg.REG_DWORD, 1)
            print("[+] 'EnableLUA' set to 1 (UAC enabled).")

        print("[*] UAC settings restored. A system restart may be required for changes to take effect.")
    except PermissionError:
        print("[-] Access denied. Please run this script as Administrator.")
    except Exception as e:
        print(f"[-] Failed to restore UAC settings: {e}")

if __name__ == "__main__":
    print("[*] Checking administrator privileges...")
    if not request_admin():
        sys.exit("[-] Failed to elevate privileges. Exiting.")

    print("[*] Starting UAC restoration process...")
    restore_uac()
    print("[*] UAC restoration process completed.")
