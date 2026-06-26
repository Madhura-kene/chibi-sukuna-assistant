import sys
import os
import threading
from PyQt5 import QtWidgets, QtCore
from ui.chibi_window import ChibiWindow
from core.voice_listener import VoiceListenerThread
from core import command_handler

class SukunaAssistantApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        
        # Root directory
        self.root_dir = r"C:\Users\Madhura\z\asistant sukuna"
        self.assets_dir = os.path.join(self.root_dir, "assets")
        
        # Create UI
        self.window = ChibiWindow(self.assets_dir)
        
        # Start Voice Listener
        self.listener = VoiceListenerThread(
            on_state_change=self.handle_state_change,
            on_command_executed=self.handle_command_executed
        )
        self.listener.start()
        
    def handle_state_change(self, state, msg):
        self.window.state_changed_signal.emit(state, msg or "")
        if state == "Listening" and msg and msg.startswith("Woke Up"):
            if "Hey Sukuna" in msg:
                self.window.speak_trigger("voice_hey_sukuna")
            else:
                self.window.speak_trigger("voice_wake")

    def handle_command_executed(self, command_text):
        if not command_text:
            self.window.state_changed_signal.emit("Idle", "Dismiss")
            return
            
        # Change state to Speaking
        self.window.state_changed_signal.emit("Speaking", None)
        
        # Execute voice response and actions in background thread
        def ollama_task():
            # Check local command handler first
            local_trigger, local_arg = command_handler.handle_command(command_text)
            
            if local_trigger == "voice_take_note":
                print("[Main] Note-taking command triggered. Launching Notepad.")
                from core import app_manager
                app_manager.launch_app("notepad")
                self.listener.note_mode = True
                self.window.speak_trigger("voice_take_note")
            elif local_trigger == "custom_voice":
                print(f"[Main] Custom keyword triggered: '{command_text}' -> '{local_arg}'")
                self.window.speak_trigger("custom_voice", raw_text=local_arg)
            elif local_trigger == "voice_screenshot":
                print("[Main] Screenshot command triggered. Capturing cleanly...")
                self.window.screenshot_signal.emit()
                self.window.speak_trigger("voice_screenshot")
            elif local_trigger != "voice_not_understood":
                print(f"[Main] Executed local command: {local_trigger} (arg: {local_arg})")
                self.window.speak_trigger(local_trigger, local_arg)
            else:
                # Route to local Ollama (Qwen 2.5)
                from core import ollama_client
                print(f"[Main] Querying local Ollama model for: '{command_text}'")
                
                speak_text = ollama_client.query_sukuna_llm(command_text)
                
                if speak_text:
                    self.window.speak_trigger("dynamic_voice", raw_text=speak_text)
                else:
                    self.window.speak_trigger("voice_not_understood")
            
        threading.Thread(target=ollama_task, daemon=True).start()

    def exec(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    print("Starting Sukuna Chibi Laptop Assistant with local Ollama integration...")
    assistant = SukunaAssistantApp()
    assistant.exec()
