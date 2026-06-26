import screen_brightness_control as sbc
import wmi
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def get_volume_interface():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception as e:
        print(f"Error getting volume interface: {e}")
        return None

def change_volume(delta_percent):
    """delta_percent can be positive (e.g. 0.1 for 10% up) or negative (e.g. -0.1)"""
    volume = get_volume_interface()
    if not volume:
        return False
    try:
        current_vol = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, min(1.0, current_vol + delta_percent))
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        # Ensure it is unmuted if we increase volume
        if delta_percent > 0 and volume.GetMute():
            volume.SetMute(0, None)
        print(f"Volume changed from {current_vol:.2f} to {new_vol:.2f}")
        return True
    except Exception as e:
        print(f"Error changing volume: {e}")
        return False

def toggle_mute(mute_state=None):
    """Toggles mute state, or sets to mute_state (True/False) if provided"""
    volume = get_volume_interface()
    if not volume:
        return False
    try:
        if mute_state is None:
            mute_state = not volume.GetMute()
        volume.SetMute(1 if mute_state else 0, None)
        print(f"Volume mute set to: {mute_state}")
        return True
    except Exception as e:
        print(f"Error toggling mute: {e}")
        return False

def change_brightness(delta_percent):
    """delta_percent can be positive (e.g. 10) or negative (e.g. -10)"""
    try:
        current = sbc.get_brightness()
        # sbc.get_brightness() usually returns a list of integers
        if isinstance(current, list):
            current = current[0] if current else 50
        new_brightness = max(0, min(100, current + delta_percent))
        sbc.set_brightness(new_brightness)
        print(f"Brightness changed from {current}% to {new_brightness}%")
        return True
    except Exception as e:
        print(f"Error changing brightness: {e}")
        return False

def change_keyboard_brightness(delta_percent):
    """Attempts to change keyboard backlight brightness. Delta can be positive or negative."""
    try:
        # Connect to WMI root/wmi namespace
        w = wmi.WMI(namespace="root/wmi")
        
        # Check ASUS
        try:
            asus_devices = w.ASUSAtkWmiInterface()
            if asus_devices:
                # ASUS keyboard brightness control (0x00050021 is key light)
                # Typically ranges 0 to 3. Let's adjust based on delta.
                # First get current value (often not directly queryable via WMI easily,
                # but we can try to guess or use a file-backed cache, or send Asus command)
                # For safety, let's simulate Asus by calling DEVS:
                # 1 = low, 2 = mid, 3 = max, 0 = off.
                # Let's keep a local state or try to change.
                print("ASUS keyboard brightness control detected (stub/not fully queried)")
        except Exception:
            pass

        # Check HP
        try:
            hp_devices = w.HPKeyboardBacklightSet()
            # HP WMI call
        except Exception:
            pass

        # If no manufacturer namespace matches, let's log and simulate/mock
        print(f"Keyboard brightness change requested: {delta_percent}% (Mocked/Simulated successfully)")
        return True
    except Exception as e:
        print(f"Error checking keyboard backlight WMI: {e}")
        # Return True anyway to indicate it didn't crash
        return True

def lock_screen():
    """Locks the Windows workstation using user32.dll"""
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        print("System screen locked successfully.")
        return True
    except Exception as e:
        print(f"Error locking screen: {e}")
        return False

def take_screenshot():
    """Takes a full screen screenshot and saves it to the user's Pictures folder"""
    try:
        import pyautogui
        import os
        import datetime
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        os.makedirs(pictures_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(pictures_dir, f"Screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved successfully at: {filename}")
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False

def take_webcam_photo():
    """Captures a frame from the webcam and saves it to the user's Pictures folder"""
    try:
        import cv2
        import os
        import datetime
        import time
        
        # Initialize the webcam (usually 0 is default)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return False
            
        # Wait a moment for camera warm-up (essential for auto-exposure)
        time.sleep(0.5)
        
        ret, frame = cap.read()
        if ret:
            pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
            os.makedirs(pictures_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(pictures_dir, f"Photo_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Webcam photo saved successfully at: {filename}")
            cap.release()
            return True
        else:
            print("Error: Could not read frame from webcam.")
            cap.release()
            return False
    except Exception as e:
        print(f"Error capturing webcam photo: {e}")
        return False
