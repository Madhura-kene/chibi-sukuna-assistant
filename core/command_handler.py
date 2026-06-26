import datetime
import webbrowser
from core import system_control
from core import app_manager

def handle_command(text):
    """
    Parses the command text and routes it to the correct action.
    Returns a tuple of (response_template, voice_parameters) or a string response.
    """
    text_clean = text.lower().strip()
    
    # 1. Custom Keywords from config.json
    import json
    import os
    config_path = r"C:\Users\Madhura\z\asistant sukuna\config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                custom_keywords = config.get("custom_keywords", {})
                for kw, ans in custom_keywords.items():
                    if kw.lower().strip() in text_clean:
                        return "custom_voice", ans
        except Exception as e:
            print(f"[Command] Error loading custom keywords: {e}")

    # 2. Take Note Command
    if "take note" in text_clean or "start taking notes" in text_clean or "make a note" in text_clean:
        return "voice_take_note", None
    
    # 3. Time query
    if "time" in text_clean or "what time is it" in text_clean:
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        # Strip leading zero from hour if any
        if time_str.startswith("0"):
            time_str = time_str[1:]
        return "voice_time", time_str
        
    # 4. Brightness controls
    if "brightness up" in text_clean or "brighter" in text_clean or "brighten" in text_clean or "increase brightness" in text_clean or "turn up the brightness" in text_clean or "turn up brightness" in text_clean:
        system_control.change_brightness(10)
        return "voice_brightness_up", None
        
    if "brightness down" in text_clean or "dimmer" in text_clean or "dim" in text_clean or "decrease brightness" in text_clean or "turn down the brightness" in text_clean or "turn down brightness" in text_clean or "dimmer the brightness" in text_clean or "dinner" in text_clean or "dinner the brightness" in text_clean or "dinner brightness" in text_clean:
        system_control.change_brightness(-10)
        return "voice_brightness_down", None
        
    # 5. Volume controls
    if "volume up" in text_clean or "louder" in text_clean or "increase volume" in text_clean or "turn up the volume" in text_clean or "turn up volume" in text_clean or "turn the volume up" in text_clean:
        system_control.change_volume(0.1) # 10%
        return "voice_volume_up", None
        
    if "volume down" in text_clean or "quieter" in text_clean or "decrease volume" in text_clean or "turn down the volume" in text_clean or "turn down volume" in text_clean or "turn the volume down" in text_clean:
        system_control.change_volume(-0.1) # 10%
        return "voice_volume_down", None
        
    if "mute" in text_clean or "silence" in text_clean:
        system_control.toggle_mute(True)
        return "voice_mute", None
        
    if "unmute" in text_clean:
        system_control.toggle_mute(False)
        return "voice_volume_up", None
        
    # 6. Keyboard brightness controls
    if "keyboard brightness up" in text_clean or "keyboard light up" in text_clean or "keyboard up" in text_clean or "keyboard brighter" in text_clean or "lit" in text_clean or "turn up backlight" in text_clean:
        system_control.change_keyboard_brightness(10)
        return "voice_keyboard_up", None
        
    if "keyboard brightness down" in text_clean or "keyboard light down" in text_clean or "keyboard down" in text_clean or "keyboard dimmer" in text_clean or "turn off the backlight" in text_clean or "turn off backlight" in text_clean:
        system_control.change_keyboard_brightness(-10)
        return "voice_keyboard_down", None
        
    # 7. Open App
    if "open" in text_clean:
        # Extract app name after "open"
        parts = text_clean.split("open", 1)
        if len(parts) > 1:
            app_name = parts[1].strip()
            success, resolved_name = app_manager.launch_app(app_name)
            if success:
                return "voice_open_app", resolved_name
            else:
                return "voice_app_not_found", app_name
                
    # 8. Close App
    if "close" in text_clean:
        # Extract app name after "close"
        parts = text_clean.split("close", 1)
        if len(parts) > 1:
            app_name = parts[1].strip()
            success = app_manager.close_app(app_name)
            if success:
                return "voice_close_app", app_name.capitalize()
            else:
                return "voice_app_not_found", app_name
                
    # 9. Google Search
    if "search" in text_clean or "google" in text_clean:
        if "search" in text_clean:
            parts = text_clean.split("search", 1)
        else:
            parts = text_clean.split("google", 1)
        if len(parts) > 1:
            query = parts[1].strip()
            import os
            # Try to force chrome if possible, otherwise use default browser
            try:
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                chrome_path_x86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
                    webbrowser.get('chrome').open(f"https://www.google.com/search?q={query}")
                elif os.path.exists(chrome_path_x86):
                    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path_x86))
                    webbrowser.get('chrome').open(f"https://www.google.com/search?q={query}")
                else:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
            except Exception:
                webbrowser.open(f"https://www.google.com/search?q={query}")
            return "voice_search", query
            
    # 9.5 Lock Screen / Sleep
    if "sleep" in text_clean or "lock screen" in text_clean or "lock the screen" in text_clean or "lock my screen" in text_clean:
        system_control.lock_screen()
        return "voice_sleep", None
            
    # 9.6 Screenshot
    if "screenshot" in text_clean or "take screenshot" in text_clean or "take a screenshot" in text_clean:
        return "voice_screenshot", None
            
    # 9.7 Battery percentage query
    if "battery" in text_clean or "how much battery" in text_clean or "battery level" in text_clean:
        import psutil
        try:
            battery = psutil.sensors_battery()
            percent = battery.percent if battery else 100
        except Exception:
            percent = 100
        return "voice_battery", str(percent)
            
    # 9.8 Good morning greeting
    if "good morning" in text_clean:
        return "voice_good_morning", None
            
    # 9.9 Good night greeting
    if "good night" in text_clean:
        return "voice_good_night", None
            
    # 9.95 Thanks response
    if "thanks" in text_clean or "thank you" in text_clean:
        return "voice_thanks", None
            
    # 9.96 Who are you query
    if "who are you" in text_clean or "identify yourself" in text_clean:
        return "voice_who_are_you", None
            
    # 9.97 Who am i query
    if "who am i" in text_clean or "my name" in text_clean:
        return "voice_who_am_i", None
            
    # 9.98 Camera command
    if "camera" in text_clean or "open camera" in text_clean or "turn on camera" in text_clean or "turn on the camera" in text_clean:
        import subprocess
        try:
            subprocess.Popen("start microsoft.windows.camera:", shell=True)
        except Exception:
            pass
        return "voice_camera", None
            
    # 9.99 Webcam photo command
    if "take photo" in text_clean or "take a photo" in text_clean or "capture photo" in text_clean or "snap a photo" in text_clean:
        system_control.take_webcam_photo()
        return "voice_take_photo", None
            
    # 10. Unrecognized
    return "voice_not_understood", None
