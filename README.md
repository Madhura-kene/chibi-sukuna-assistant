# Sukuna Chibi Desktop Assistant

Created by: https://github.com/Madhura-kene

A lightweight desktop chibi Sukuna assistant for Windows featuring voice commands, an animated sprite overlay, and local text-to-speech (TTS) responses.

GitHub Repository: https://github.com/Madhura-kene/chibi-sukuna-assistant

## Key Features

- Transparent Chibi Sprite: A frameless, transparent PyQt5 window overlay positioned at the bottom right corner of the screen. Supports dragging, custom scaling, and corner snapping.
- Animated Lip-Syncing: Mouth animations automatically synchronize with speech playback by selecting mouth frames based on real-time audio amplitude.
- Local Voice Control: Background microphone listener with phonetic wake word detection (supporting variations like Sukuna, Suguna, and Sakuna).
- System and App Control: Direct system actions (volume, screen brightness, keyboard backlight, system lock, Google Search in Chrome, and taking screenshots).
- Note Dictation Mode: Saying "take note" or "make a note" launches Notepad and writes down everything you speak until you say a stop word.
- Custom Voice Scripting: Configurable voice replies for specific trigger keywords.

## Voice Commands and Responses

### Wake Words
- "Sukuna" or "Suguna" (normal wake): "You called?"
- "Hey Sukuna" or "Hey Suguna": "what is it"

### System Actions
- Mouse Click and Hold (Dragging): "Don't touch me."
- "what time is it" / "time": "It's [TIME]... don't waste it."
- "open [app]": "Fine. Opening... [APP]"
- "close [app]": "Gone. As it should be."
- "search [query]" / "google [query]": Opens Chrome and searches Google. Sukuna says: "Searching... [QUERY] ...pathetic that you need my help for this."
- "brightness up" / "brighter" / "turn up the brightness": "yes ofcourse you blind peasant"
- "brightness down" / "dimmer" / "turn down the brightness" / "dinner the brightness": "are you sure because you are blind but okay"
- "volume up" / "louder" / "turn the volume up": "why are you deff"
- "volume down" / "quieter" / "turn the volume down": "arent you deaf."
- "mute" / "silence": "Silenced."
- "unmute": "why are you deff" (unmutes system volume)
- "lit" / "keyboard brighter" / "turn up backlight": "yes brighter then your future"
- "keyboard down" / "keyboard dimmer" / "turn off the backlight": "are you sure baby"
- "sleep" / "lock screen": Locks the Windows workstation and says "Finally. Some peacefrom you"
- "screenshot" / "take a screenshot": Hides the chibi window temporarily, takes a full screenshot saved to your Pictures folder, and says: "okay babygirl.if that is what you want."
- "camera" / "open camera" / "turn on camera": Opens the Windows Camera application and says: "yes ofcourse beautiful"
- "take photo" / "take a photo" / "capture photo": Captures a picture from your webcam silently in the background, saves it to your Pictures folder, and says: "sure ."
- "battery" / "how much battery": "[BATTERY_LEVEL] percent. Don't drain more"

### Greetings and Questions
- "good morning": "You're still alive. Boring."
- "good night": "Finally. Go away."
- "thanks" / "thank you": "Don't thank me. It's beneath you."
- "who are you": "The strongest. Obviously."
- "who am i": "kaiu . or should i say , mine."

## Error Triggers
- Command not understood: "Say that again. Clearly."
- Application not found: "That doesn't exist. Pathetic."

## Project Structure

- main.py: Main entry point initializing the PyQt5 application, tray icon, and background listener thread.
- config.json: Configures mouth positions, scale, rotation, and supports adding custom keyword-answer pairs.
- core/
  - voice_listener.py: Background thread listening to the microphone for wake words and commands.
  - command_handler.py: Routes spoken commands to system actions and returns correct response triggers.
  - system_control.py: Handles system calls for volume, brightness, keyboard backlight, locking, and screenshots.
  - app_manager.py: Launches system apps and closes running processes.
- ui/
  - chibi_window.py: Transparent PyQt5 widget managing the sprite displays, dragging, signals, and mouth overlay.
  - animator.py: Analyzes speech audio files to animate lip sync frames.
- tts/
  - voice_player.py: Connects to local Zen Voice Forge server or falls back to Microsoft edge-tts to prepare spoken audio.

## Installation

1. Install Python 3.8 or higher on Windows.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up a local TTS server (Zen Voice Forge or use the built-in Microsoft edge-tts fallback).
4. Run the assistant:
   ```bash
   python main.py
   ```

## Calibration Mode
If you need to align the mouth overlay position:
1. Right-click the system tray icon and select "Toggle Mouth Calibration".
2. Use the arrow keys (or Shift + Arrow Keys for larger steps) to align the mouth preview.
3. Save the calibration to config.json by turning off calibration mode or pressing Enter.
