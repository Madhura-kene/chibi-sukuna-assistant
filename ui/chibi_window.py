import os
import json
import random
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from ui.animator import MouthAnimator
from tts import voice_player
import winsound

CONFIG_PATH = r"C:\Users\Madhura\z\asistant sukuna\config.json"

class ChibiWindow(QtWidgets.QWidget):
    # Signals for thread-safe UI updates
    state_changed_signal = QtCore.pyqtSignal(str, str)
    play_audio_signal = QtCore.pyqtSignal(str)
    screenshot_signal = QtCore.pyqtSignal()
    
    def __init__(self, assets_dir):
        super().__init__()
        self.assets_dir = assets_dir
        self.sprites_dir = os.path.join(assets_dir, "sprites")
        self.animator = MouthAnimator(self.sprites_dir)
        self.screenshot_signal.connect(self.execute_screenshot)
        
        # Load mouth calibration config
        self.mouth_x = 350
        self.mouth_y = 480
        self.target_width = 180 # Restore Sukuna size back to 180
        self.mouth_scale = 0.5 # Default mouth scale (smaller mouth)
        self.mouth_rotation = 0.0 # Default mouth rotation in degrees (clockwise)
        self.load_config()
        
        # Window attributes
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.SubWindow
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        # State variables
        self.app_state = "Idle"
        self.is_dragging = False
        self.drag_position = QtCore.QPoint()
        self.current_mouth_amplitude = 0
        self.calibration_mode = False
        
        # Load base sprites
        self.idle_pixmap = QtGui.QPixmap(os.path.join(self.sprites_dir, "sukuna_idle.png"))
        self.grabbed_pixmap = QtGui.QPixmap(os.path.join(self.sprites_dir, "sukuna_grabbed.png"))
        
        # Scaling settings
        self.scale_factor = self.target_width / self.idle_pixmap.width()
        self.target_height = int(self.idle_pixmap.height() * self.scale_factor)
        self.resize(self.target_width, self.target_height)
        
        # Initialize QtMultimedia Player for native playback
        self.media_player = QMediaPlayer(self)
        self.media_player.stateChanged.connect(self.handle_media_state_change)
        
        # Set up a QTimer to drive the mouth animation updates
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animate_mouth_step)
        
        # Setup system tray
        self.setup_tray()
        
        # Position in bottom-right
        self.snap_to_corner("bottom-right")
        
        # Connect signals
        self.state_changed_signal.connect(self.update_state)
        self.play_audio_signal.connect(self.play_audio_file)
        
        self.show()
        self.raise_()
        self.activateWindow()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                    self.mouth_x = config.get("mouth_x", self.mouth_x)
                    self.mouth_y = config.get("mouth_y", self.mouth_y)
                    self.target_width = config.get("width", self.target_width)
                    self.mouth_scale = config.get("mouth_scale", self.mouth_scale)
                    self.mouth_rotation = config.get("mouth_rotation", self.mouth_rotation)
                    print(f"[UI] Loaded config: mouth_x={self.mouth_x}, mouth_y={self.mouth_y}, width={self.target_width}, mouth_scale={self.mouth_scale}, mouth_rotation={self.mouth_rotation}")
            except Exception as e:
                print(f"[UI] Error loading config: {e}")

    def save_config(self):
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump({
                    "mouth_x": self.mouth_x, 
                    "mouth_y": self.mouth_y,
                    "width": self.target_width,
                    "mouth_scale": self.mouth_scale,
                    "mouth_rotation": self.mouth_rotation
                }, f, indent=4)
            print(f"[UI] Saved config: mouth_x={self.mouth_x}, mouth_y={self.mouth_y}, width={self.target_width}, mouth_scale={self.mouth_scale}, mouth_rotation={self.mouth_rotation}")
        except Exception as e:
            print(f"[UI] Error saving config: {e}")

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = os.path.join(self.sprites_dir, "mouth_closed.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QtGui.QIcon(icon_path))
        else:
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtGui.QColor("red"))
            self.tray_icon.setIcon(QtGui.QIcon(pixmap))
            
        tray_menu = QMenu()
        
        show_action = QAction("Show Sukuna", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide Sukuna", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        calib_action = QAction("Toggle Mouth Calibration", self)
        calib_action.setCheckable(True)
        calib_action.triggered.connect(self.toggle_calibration)
        tray_menu.addAction(calib_action)
        self.calib_action = calib_action
        
        quit_action = QAction("Quit Assistant", self)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_calibration(self):
        self.calibration_mode = not self.calibration_mode
        self.calib_action.setChecked(self.calibration_mode)
        if self.calibration_mode:
            print("[UI] Mouth Calibration Mode Active.")
        else:
            self.save_config()
        self.update()

    def update_state(self, state, msg):
        self.app_state = state
        print(f"[UI State] Changed to: {state} (msg: {msg})")
        
        # Stop any active voice on state changes except when speaking
        if state != "Speaking":
            self.media_player.stop()
            self.animation_timer.stop()
            self.current_mouth_amplitude = 0
            
        if state == "Listening" and msg and msg.startswith("Woke Up"):
            # Play activate beeps/sound
            self.play_sfx("sfx_activate")
        elif state == "Error" or (state == "Idle" and msg == "Dismiss"):
            self.play_sfx("sfx_dismiss")
            
        self.update()

    def play_sfx(self, sfx_name):
        # High pitch whoosh simulation fallbacks
        if sfx_name == "sfx_activate":
            winsound.Beep(880, 100)
            winsound.Beep(1200, 100)
        elif sfx_name == "sfx_dismiss":
            winsound.Beep(600, 100)
            winsound.Beep(400, 100)

    def speak_trigger(self, trigger, format_arg=None, raw_text=None):
        """Asynchronously prepares the voice file and plays it thread-safely"""
        def speak_task():
            filepath = voice_player.get_voice_file(trigger, format_arg, raw_text)
            if filepath:
                self.play_audio_signal.emit(filepath)
            else:
                # If generation failed, play a fallback beep
                winsound.Beep(180, 150)
                self.state_changed_signal.emit("Idle", "Dismiss")
                
        threading.Thread(target=speak_task, daemon=True).start()

    def execute_screenshot(self):
        """Hides the window, takes a screenshot, and restores the window."""
        self.hide()
        QtWidgets.QApplication.processEvents()
        
        def take_screenshot_delayed():
            from core import system_control
            system_control.take_screenshot()
            self.show()
            self.raise_()
            self.activateWindow()
            
        QtCore.QTimer.singleShot(250, take_screenshot_delayed)

    def play_audio_file(self, filepath):
        """Called on the main thread via signal to play speech"""
        # Stop any current playing media
        self.media_player.stop()
        self.animation_timer.stop()
        
        # Load and play the file
        url = QtCore.QUrl.fromLocalFile(filepath)
        content = QMediaContent(url)
        self.media_player.setMedia(content)
        self.media_player.play()
        
        # Start mouth animation timer (runs every 50ms)
        self.animation_timer.start(50)

    def handle_media_state_change(self, state):
        if state == QMediaPlayer.StoppedState:
            self.animation_timer.stop()
            self.current_mouth_amplitude = 0
            self.update()
            
            # Transition back to Idle if we finished speaking
            if self.app_state == "Speaking":
                self.app_state = "Idle"
                self.update_state("Idle", "Dismiss")

    def animate_mouth_step(self):
        """Simulates speech amplitude changes to animate the mouth"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            # Alternate randomly between open, half, and smug states
            self.current_mouth_amplitude = random.randint(15, 95)
        else:
            self.current_mouth_amplitude = 0
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        
        if self.app_state == "Grabbed" or self.is_dragging:
            base_pixmap = self.grabbed_pixmap
        else:
            base_pixmap = self.idle_pixmap
            
        dest_rect = QtCore.QRect(0, 0, self.target_width, self.target_height)
        painter.drawPixmap(dest_rect, base_pixmap)
        
        if not (self.app_state == "Grabbed" or self.is_dragging):
            if self.calibration_mode:
                mouth_pixmap = self.animator.get_mouth_frame(90) # Open mouth for preview
            else:
                mouth_pixmap = self.animator.get_mouth_frame(self.current_mouth_amplitude)
                
            if mouth_pixmap:
                sx = int(self.mouth_x * self.scale_factor)
                sy = int(self.mouth_y * self.scale_factor)
                sw = int(mouth_pixmap.width() * self.scale_factor * self.mouth_scale)
                sh = int(mouth_pixmap.height() * self.scale_factor * self.mouth_scale)
                
                # Rotate mouth overlay centered around its own center point
                painter.save()
                cx = sx + sw / 2.0
                cy = sy + sh / 2.0
                painter.translate(cx, cy)
                painter.rotate(self.mouth_rotation)
                painter.drawPixmap(QtCore.QRect(int(-sw / 2.0), int(-sh / 2.0), sw, sh), mouth_pixmap)
                painter.restore()
                
        if self.calibration_mode:
            painter.setPen(QtGui.QPen(QtGui.QColor("yellow"), 2, QtCore.Qt.DashLine))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)
        elif self.app_state == "Listening":
            painter.setPen(QtGui.QPen(QtGui.QColor(230, 20, 20, 200), 2))
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.app_state = "Grabbed"
            self.update()
            
            # Stop any playing audio instantly
            self.media_player.stop()
            self.animation_timer.stop()
            self.current_mouth_amplitude = 0
            
            # Annoyed response on grab (uses QMediaPlayer asynchronously)
            self.speak_trigger("voice_grabbed")
            
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            self.app_state = "Idle"
            self.snap_to_closest_corner()
            self.update()
            event.accept()

    def keyPressEvent(self, event):
        if self.calibration_mode:
            step = 10 if event.modifiers() & QtCore.Qt.ShiftModifier else 1
            if event.key() == QtCore.Qt.Key_Left:
                self.mouth_x -= step
            elif event.key() == QtCore.Qt.Key_Right:
                self.mouth_x += step
            elif event.key() == QtCore.Qt.Key_Up:
                self.mouth_y -= step
            elif event.key() == QtCore.Qt.Key_Down:
                self.mouth_y += step
            elif event.key() == QtCore.Qt.Key_BracketLeft:
                self.mouth_scale = max(0.1, self.mouth_scale - 0.05)
                print(f"[Calibration] mouth_scale={self.mouth_scale:.2f}")
            elif event.key() == QtCore.Qt.Key_BracketRight:
                self.mouth_scale = min(2.0, self.mouth_scale + 0.05)
                print(f"[Calibration] mouth_scale={self.mouth_scale:.2f}")
            elif event.key() == QtCore.Qt.Key_Comma:
                # Rotate Counter-Clockwise
                self.mouth_rotation -= 1.0 if not event.modifiers() & QtCore.Qt.ShiftModifier else 5.0
                print(f"[Calibration] mouth_rotation={self.mouth_rotation:.1f}°")
            elif event.key() == QtCore.Qt.Key_Period:
                # Rotate Clockwise
                self.mouth_rotation += 1.0 if not event.modifiers() & QtCore.Qt.ShiftModifier else 5.0
                print(f"[Calibration] mouth_rotation={self.mouth_rotation:.1f}°")
            elif event.key() == QtCore.Qt.Key_Return:
                self.toggle_calibration()
                
            print(f"[Calibration] mouth_x={self.mouth_x}, mouth_y={self.mouth_y}")
            self.update()
            event.accept()
        else:
            super().keyPressEvent(event)

    def snap_to_corner(self, corner):
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        margin = 30
        if corner == "top-left":
            self.move(margin, margin)
        elif corner == "top-right":
            self.move(screen.width() - self.width() - margin, margin)
        elif corner == "bottom-left":
            self.move(margin, screen.height() - self.height() - margin - 50)
        elif corner == "bottom-right":
            self.move(screen.width() - self.width() - margin, screen.height() - self.height() - margin - 50)

    def snap_to_closest_corner(self):
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        x, y = self.x(), self.y()
        
        corners = {
            "top-left": (30, 30),
            "top-right": (screen.width() - self.width() - 30, 30),
            "bottom-left": (30, screen.height() - self.height() - 80),
            "bottom-right": (screen.width() - self.width() - 30, screen.height() - self.height() - 80)
        }
        
        closest_corner = min(
            corners.keys(),
            key=lambda c: (x - corners[c][0])**2 + (y - corners[c][1])**2
        )
        self.move(*corners[closest_corner])
