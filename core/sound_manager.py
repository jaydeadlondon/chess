import os
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class SoundManager:
    def __init__(self):
        self._sounds = {}
        self.enabled = True
        self.volume = 0.6
        self._loaded = False

    def load(self, sounds_dir="assets/sounds"):
        names = ["move", "capture", "check", "checkmate", "castle", "new_game"]
        for name in names:
            path = os.path.join(sounds_dir, f"{name}.wav")
            if os.path.exists(path):
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
                effect.setVolume(self.volume)
                self._sounds[name] = effect
        self._loaded = True

    def play(self, name):
        if not self.enabled or not self._loaded:
            return
        if name in self._sounds:
            s = self._sounds[name]
            try:
                s.play()
            except Exception:
                pass

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        for s in self._sounds.values():
            s.setVolume(self.volume)

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
