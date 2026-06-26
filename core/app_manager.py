import os
import subprocess
import psutil
import webbrowser

# Map of common app names to their launch commands or protocols
COMMON_APPS = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "spotify": "spotify",
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "explorer": "explorer",
    "file explorer": "explorer",
    "discord": "discord",
    "steam": "steam",
    "vlc": "vlc",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt"
}

def launch_app(app_name):
    """Launches an application by name. Returns (success_bool, clean_app_name)"""
    app_name_lower = app_name.lower().strip()
    
    # Check direct mapping
    cmd = COMMON_APPS.get(app_name_lower, app_name_lower)
    
    # Try launching using subprocess
    try:
        # Spotify has a custom protocol which is very reliable
        if app_name_lower == "spotify":
            webbrowser.open("spotify:")
            return True, "Spotify"
            
        # Run start command via shell to let Windows resolve it
        # using shell=True allows launching system apps like calc, notepad, chrome if in path
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, cmd.capitalize()
    except Exception as e:
        print(f"Error launching {app_name}: {e}")
        return False, app_name

def close_app(app_name):
    """Closes an application by looking for processes matching the name. Returns success_bool"""
    app_name_lower = app_name.lower().strip()
    
    # Resolve common process names if mapped
    # For example, if they say "chrome", the process is "chrome.exe"
    process_targets = [app_name_lower]
    if app_name_lower == "google chrome" or app_name_lower == "chrome":
        process_targets = ["chrome.exe", "chrome"]
    elif app_name_lower == "spotify":
        process_targets = ["spotify.exe", "spotify"]
    elif app_name_lower == "notepad":
        process_targets = ["notepad.exe", "notepad"]
    elif app_name_lower == "calculator":
        process_targets = ["calculator.exe", "calc.exe", "calculatorApp.exe", "calculator"]
    
    closed_any = False
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            if name and any(t in name.lower() for t in process_targets):
                proc.terminate()
                closed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
            
    return closed_any
