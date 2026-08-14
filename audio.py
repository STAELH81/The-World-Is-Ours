"""Effets sonores et musique procéduraux (aucun fichier audio requis)."""

import array
import math
import pygame


class AudioManager:
    def __init__(self, volume=0.7):
        self.volume = max(0.0, min(1.0, volume))
        self.enabled = True
        self.music_name = None
        self.music = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
            pygame.mixer.set_num_channels(12)
        except pygame.error:
            self.enabled = False
            return

        try:
            self.sounds = {
                "click": self._tone(620, 40, 0.28, decay=True),
                "recruit": self._tone(520, 90, 0.32, sweep=180, decay=True),
                "build": self._tone(340, 120, 0.34, sweep=80, decay=True),
                "move": self._tone(240, 70, 0.22, decay=True),
                "battle": self._noise(140, 0.4),
                "ranged": self._tone(980, 60, 0.28, sweep=-320, decay=True),
                "turn": self._tone(392, 110, 0.3, sweep=80, decay=True),
                "victory": self._chord([523, 659, 784], 320),
                "defeat": self._tone(110, 280, 0.4, sweep=-40, decay=True),
                "embark": self._tone(220, 140, 0.3, sweep=90, decay=True),
            }
            self.tracks = {
                "menu": self._music_loop([196, 247, 294, 247, 220, 196, 165, 196], 0.12),
                "game": self._music_loop([147, 196, 220, 196, 175, 147, 131, 147], 0.09),
            }
        except pygame.error:
            self.enabled = False
            self.sounds = {}
            self.tracks = {}

    def _tone(self, frequency, duration_ms, volume=0.4, sweep=0, decay=False):
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        amplitude = int(32767 * volume)
        samples = array.array("h")
        for i in range(n_samples):
            t = i / n_samples
            freq = frequency + sweep * t
            env = (1.0 - t) if decay else 1.0
            env *= min(1.0, i / 80.0)
            val = math.sin(2 * math.pi * freq * i / sample_rate)
            samples.append(int(amplitude * env * val))
        return pygame.mixer.Sound(buffer=samples)

    def _noise(self, duration_ms, volume=0.35):
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        amplitude = int(32767 * volume)
        samples = array.array("h")
        seed = 12345
        for i in range(n_samples):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            noise = ((seed >> 16) / 32768.0) * 2 - 1
            env = 1.0 - (i / n_samples)
            rumble = math.sin(2 * math.pi * 70 * i / sample_rate)
            samples.append(int(amplitude * env * (noise * 0.55 + rumble * 0.45)))
        return pygame.mixer.Sound(buffer=samples)

    def _chord(self, frequencies, duration_ms, volume=0.32):
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        amplitude = int(32767 * volume) / max(1, len(frequencies))
        buf = []
        for i in range(n_samples):
            t = i / n_samples
            env = (1.0 - t) ** 0.6
            val = sum(math.sin(2 * math.pi * f * i / sample_rate) for f in frequencies)
            buf.append(int(amplitude * env * val))
        return pygame.mixer.Sound(buffer=array.array("h", buf))

    def _music_loop(self, notes, volume):
        sample_rate = 22050
        note_samples = int(sample_rate * 0.28)
        samples = array.array("h")
        amplitude = int(32767 * volume)
        for freq in notes:
            for i in range(note_samples):
                t = i / note_samples
                env = min(t * 8, 1.0, (1.0 - t) * 4)
                val = math.sin(2 * math.pi * freq * i / sample_rate)
                val += 0.35 * math.sin(2 * math.pi * (freq * 0.5) * i / sample_rate)
                samples.append(int(amplitude * env * val * 0.7))
        return pygame.mixer.Sound(buffer=samples)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.music:
            try:
                self.music.set_volume(self.volume * 0.45)
            except pygame.error:
                pass

    def play(self, name):
        if not self.enabled or self.volume <= 0:
            return
        sound = self.sounds.get(name)
        if not sound:
            return
        try:
            sound.set_volume(self.volume)
            sound.play()
        except pygame.error:
            pass

    def play_music(self, name):
        if not self.enabled or name == self.music_name:
            return
        try:
            if self.music:
                self.music.stop()
            self.music = self.tracks.get(name)
            self.music_name = name
            if self.music and self.volume > 0:
                self.music.set_volume(self.volume * 0.45)
                self.music.play(loops=-1)
        except pygame.error:
            self.music = None
            self.music_name = None

    def stop_music(self):
        try:
            if self.music:
                self.music.stop()
        except pygame.error:
            pass
        self.music = None
        self.music_name = None
