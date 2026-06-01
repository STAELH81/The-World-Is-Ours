"""Effets sonores procéduraux (aucun fichier audio requis)."""

import array
import math
import pygame


class AudioManager:
    def __init__(self, volume=0.7):
        self.volume = max(0.0, min(1.0, volume))
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error:
            self.enabled = False
            return

        self.sounds = {
            "click": self._tone(520, 45, 0.35),
            "recruit": self._tone(660, 80, 0.4),
            "build": self._tone(440, 100, 0.45),
            "move": self._tone(300, 60, 0.3),
            "battle": self._tone(180, 140, 0.55),
            "ranged": self._tone(900, 70, 0.35),
            "turn": self._tone(350, 90, 0.4),
            "victory": self._chord([523, 659, 784], 220),
            "defeat": self._tone(120, 260, 0.5),
        }

    def _tone(self, frequency, duration_ms, volume=0.4):
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        amplitude = int(32767 * volume)
        samples = array.array(
            "h",
            (
                int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                for i in range(n_samples)
            ),
        )
        return pygame.mixer.Sound(buffer=samples)

    def _chord(self, frequencies, duration_ms, volume=0.35):
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        amplitude = int(32767 * volume) / max(1, len(frequencies))
        buf = []
        for i in range(n_samples):
            val = sum(
                math.sin(2 * math.pi * f * i / sample_rate) for f in frequencies
            )
            buf.append(int(amplitude * val))
        return pygame.mixer.Sound(buffer=array.array("h", buf))

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))

    def play(self, name):
        if not self.enabled or self.volume <= 0:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(self.volume)
            sound.play()
