import os
from PyQt5.QtGui import QPixmap

class MouthAnimator:
    def __init__(self, sprites_dir):
        self.sprites_dir = sprites_dir
        self.mouth_pixmaps = {}
        self.load_mouth_sprites()
        
    def load_mouth_sprites(self):
        frames = {
            "closed": "mouth_closed.png",
            "smug": "mouth_smug.png",
            "half": "mouth_half.png",
            "open": "mouth_open.png"
        }
        for state, filename in frames.items():
            path = os.path.join(self.sprites_dir, filename)
            if os.path.exists(path):
                self.mouth_pixmaps[state] = QPixmap(path)
                print(f"[MouthAnimator] Loaded {state} from {filename}")
            else:
                print(f"[MouthAnimator] Warning: {filename} not found in {self.sprites_dir}")

    def get_mouth_frame(self, amplitude):
        """Maps volume amplitude (0-100) to the corresponding QPixmap"""
        if not self.mouth_pixmaps:
            return None
            
        if amplitude <= 10:
            return self.mouth_pixmaps.get("closed")
        elif amplitude <= 40:
            return self.mouth_pixmaps.get("smug")
        elif amplitude <= 75:
            return self.mouth_pixmaps.get("half")
        else:
            return self.mouth_pixmaps.get("open")
