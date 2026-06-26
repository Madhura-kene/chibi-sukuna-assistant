import os
import asyncio
import edge_tts
import winsound
import requests

# Mapping of voice triggers to their spoken scripts for reference
VOICE_SCRIPTS = {
    "voice_wake": "You called?",
    "voice_hey_sukuna": "what is it",
    "voice_time": "It's {0}... don't waste it.",
    "voice_open_app": "Fine. Opening... {0}",
    "voice_close_app": "Gone. As it should be.",
    "voice_search": "Searching... {0} ...pathetic that you need my help for this.",
    "voice_brightness_up": "yes ofcourse you blind peasant",
    "voice_brightness_down": "are you sure because you are blind but okay",
    "voice_volume_up": "why are you deff",
    "voice_volume_down": "arent you deaf.",
    "voice_mute": "Silenced.",
    "voice_keyboard_up": "yes brighter then your future",
    "voice_keyboard_down": "are you sure baby",
    "voice_not_understood": "Say that again. Clearly.",
    "voice_app_not_found": "That doesn't exist. Pathetic.",
    "voice_grabbed": "Don't touch me.",
    "voice_take_note": "suree . peasant .",
    "voice_sleep": "Finally. Some peacefrom you",
    "voice_screenshot": "okay babygirl.if that is what you want.",
    "voice_battery": "{0} percent. Don't drain more",
    "voice_good_morning": "You're still alive. Boring.",
    "voice_good_night": "Finally. Go away.",
    "voice_thanks": "Don't thank me. It's beneath you.",
    "voice_who_are_you": "The strongest. Obviously.",
    "voice_who_am_i": "kaiu . or should i say , mine.",
    "voice_camera": "yes ofcourse beautiful",
    "voice_take_photo": "sure ."
}

async def _generate_audio_async(text, filepath):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-10%", pitch="-5Hz")
    await communicate.save(filepath)

def generate_voice_audio(text, filepath):
    # 1. Try Zen Voice Forge
    try:
        url = "http://127.0.0.1:8000/v1/synthesis"
        headers = {
            "Authorization": "Bearer vf_sk_dev_local",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "output_format": "mp3",
            "parameters": {
                "emotion": "neutral"
            }
        }
        response = requests.post(url, json=payload, headers=headers, timeout=3)
        if response.status_code == 201:
            data = response.json()
            audio_url = data.get("audio_url")
            if audio_url:
                audio_res = requests.get(audio_url, headers=headers, timeout=3)
                if audio_res.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(audio_res.content)
                    print(f"[TTS] Successfully generated audio using Zen Voice Forge for: \"{text}\"")
                    return True
        print(f"[TTS] Zen Voice Forge returned status {response.status_code}. Falling back to edge-tts.")
    except Exception as e:
        print(f"[TTS] Zen Voice Forge connection failed ({e}). Falling back to edge-tts.")

    # 2. Fallback to edge-tts
    try:
        # Run in a clean asyncio loop to avoid event loop conflicts in threads
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_audio_async(text, filepath))
        loop.close()
        return True
    except Exception as e:
        print(f"[TTS] Error generating audio with edge-tts fallback: {e}")
        return False

def get_voice_file(trigger, format_arg=None, raw_text=None):
    """
    Generates the voice response associated with a trigger or raw_text.
    Returns the absolute path to the generated MP3 file, or None if failed.
    """
    if raw_text:
        script = raw_text
    else:
        script = VOICE_SCRIPTS.get(trigger, "")
        if format_arg:
            script = script.format(format_arg)
            
    print(f"\n[SUKUNA VOICE]: \"{script}\"")
    
    audio_dir = r"C:\Users\Madhura\z\asistant sukuna\assets\audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    # Avoid dynamic file access conflicts by appending a simple counter or checking existence
    # Since only one voice plays at a time, we can alternate between two dynamic files
    if raw_text or format_arg:
        # Toggle between two filenames to prevent file locking issues
        import time
        suffix = int(time.time()) % 2
        voice_file = os.path.join(audio_dir, f"dynamic_voice_{suffix}.mp3")
    else:
        voice_file = os.path.join(audio_dir, f"{trigger}.mp3")
        
    if raw_text or format_arg or not os.path.exists(voice_file):
        if os.path.exists(voice_file):
            try:
                os.remove(voice_file)
            except Exception:
                pass
        success = generate_voice_audio(script, voice_file)
        if not success:
            return None
            
    return voice_file
