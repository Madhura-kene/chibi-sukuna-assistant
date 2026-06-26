import threading
import time
import speech_recognition as sr

WAKE_WORDS = ["sukuna", "sakuna", "tsukuna", "sukna", "sukun", "secular", "sukanya", "shukula", "hakuna", "suguna", "sugna", "shukla"]

class VoiceListenerThread(threading.Thread):
    def __init__(self, on_state_change, on_command_executed):
        super().__init__()
        self.daemon = True
        self.on_state_change = on_state_change  # Callback for UI state change
        self.on_command_executed = on_command_executed  # Callback for execution output
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200 # Set a lower initial threshold for better sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.running = True
        self.note_mode = False
        
    def run(self):
        print("[VoiceListener] Calibrating microphone...")
        try:
            mic = sr.Microphone()
        except Exception as e:
            print(f"[VoiceListener] Error initializing microphone: {e}")
            self.on_state_change("Error", "No microphone detected")
            return

        with mic as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Cap maximum calibrated energy threshold to prevent microphone desensitization in noisy rooms
                if self.recognizer.energy_threshold > 350:
                    self.recognizer.energy_threshold = 300
                print(f"[VoiceListener] Calibration complete. Energy threshold: {self.recognizer.energy_threshold}")
            except Exception as e:
                print(f"[VoiceListener] Calibration error: {e}")

            while self.running:
                try:
                    # Note Taking Mode Intercept
                    if self.note_mode:
                        self.on_state_change("Listening", "Note Mode")
                        print("[VoiceListener] [Note Mode] Listening for notes...")
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                        try:
                            transcription = self.recognizer.recognize_google(audio).strip()
                            print(f"[VoiceListener] [Note Mode] Heard: '{transcription}'")
                            
                            # Check stop words
                            if transcription.lower().strip() in ["stop note", "stop taking notes", "exit", "done", "stop", "exit note"]:
                                print("[VoiceListener] [Note Mode] Stopping note mode.")
                                self.note_mode = False
                                self.on_state_change("Idle", "Dismiss")
                                continue
                                
                            # Type into active window (Notepad)
                            import pyautogui
                            pyautogui.write(transcription + " ")
                        except sr.UnknownValueError:
                            continue
                        except Exception as note_err:
                            print(f"[VoiceListener] [Note Mode] Error typing: {note_err}")
                        continue

                    self.on_state_change("Idle", None)
                    print("[VoiceListener] Listening for wake word 'Sukuna'...")
                    
                    # Listen for wake word (short phrase limit)
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=4)
                    
                    try:
                        # Perform Google STT
                        transcription = self.recognizer.recognize_google(audio).lower().strip()
                        print(f"[VoiceListener] Heard: '{transcription}'")
                        
                        # Find if any wake word matches
                        detected_wake = None
                        for w in WAKE_WORDS:
                            if w in transcription:
                                detected_wake = w
                                break
                                
                        if detected_wake:
                            self.on_state_change("Listening", None)
                            
                            # Check if command was spoken in the same breath
                            parts = transcription.split(detected_wake, 1)
                            command = parts[1].strip() if len(parts) > 1 else ""
                            
                            if command:
                                print(f"[VoiceListener] Extracted command: '{command}'")
                                self.on_state_change("Processing", None)
                                self.on_command_executed(command)
                            else:
                                # Wake word only, listen for command next
                                print(f"[VoiceListener] Wake word ({detected_wake}) detected. Listening for command...")
                                if "hey" in transcription:
                                    self.on_state_change("Listening", "Woke Up: Hey Sukuna")
                                else:
                                    self.on_state_change("Listening", "Woke Up")
                                
                                # Wait and listen for the actual command
                                try:
                                    cmd_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                                    self.on_state_change("Processing", None)
                                    cmd_transcription = self.recognizer.recognize_google(cmd_audio).lower().strip()
                                    print(f"[VoiceListener] Heard command: '{cmd_transcription}'")
                                    self.on_command_executed(cmd_transcription)
                                except sr.WaitTimeoutError:
                                    print("[VoiceListener] Command timeout.")
                                    self.on_state_change("Error", "Timeout")
                                    self.on_command_executed("")
                                except Exception as cmd_err:
                                    print(f"[VoiceListener] Command listening error: {cmd_err}")
                                    self.on_state_change("Error", "Error")
                                    self.on_command_executed("")
                                    
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as re:
                        print(f"[VoiceListener] Google Speech Recognition service error: {re}")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"[VoiceListener] Loop error: {e}")
                    time.sleep(1)

    def stop(self):
        self.running = False
