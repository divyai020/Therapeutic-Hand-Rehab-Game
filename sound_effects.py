"""
Natural sound synthesis for Hand Rehab Game.
Generates calming, pleasant feedback tones using NumPy arrays directly.
Designed to feel calming, acoustic, and therapeutic.
"""

import pygame
import numpy as np

class SoundManager:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.sounds = {}
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self._generate_natural_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio notice: {e}. Running visual-only.")
            self.enabled = False

    def _create_stereo(self, wave_mono):
        int16_mono = (np.clip(wave_mono, -1.0, 1.0) * 16384).astype(np.int16)
        stereo = np.ascontiguousarray(np.column_stack((int16_mono, int16_mono)))
        return pygame.sndarray.make_sound(stereo)

    def _generate_natural_sounds(self):
        sr = self.sample_rate
        
        # 1. Warm Wooden Marimba Note on Grab (F#4, 370Hz + subtle harmonic, warm wooden decay)
        dur_grab = 0.14
        t_g = np.linspace(0, dur_grab, int(sr * dur_grab), False)
        env_g = np.exp(-t_g * 24)
        wave_g = (0.75 * np.sin(2 * np.pi * 370.0 * t_g) + 
                  0.25 * np.sin(2 * np.pi * 740.0 * t_g)) * env_g * 0.45
        self.sounds['grab'] = self._create_stereo(wave_g)

        # 2. Ceramic Wind Chime on Success (E5 + B5 harmonic, peaceful resonance)
        dur_succ = 0.35
        t_s = np.linspace(0, dur_succ, int(sr * dur_succ), False)
        env_s = np.exp(-t_s * 7)
        wave_s = (0.55 * np.sin(2 * np.pi * 659.25 * t_s) + 
                  0.35 * np.sin(2 * np.pi * 987.77 * t_s) +
                  0.15 * np.sin(2 * np.pi * 1318.5 * t_s)) * env_s * 0.40
        self.sounds['success'] = self._create_stereo(wave_s)

        # 3. Soft Water Drop Tone on Reset (Gentle pitch-glide down)
        dur_res = 0.12
        t_r = np.linspace(0, dur_res, int(sr * dur_res), False)
        freq_r = np.linspace(340, 240, len(t_r))
        env_r = np.exp(-t_r * 20)
        wave_r = np.sin(2 * np.pi * freq_r * t_r) * env_r * 0.30
        self.sounds['reset'] = self._create_stereo(wave_r)

        # 4. Harmonious Ceramic Bell Flourish on Session Completion
        dur_comp = 0.70
        t_c = np.linspace(0, dur_comp, int(sr * dur_comp), False)
        env_c = np.exp(-t_c * 3.5)
        wave_c = (0.35 * np.sin(2 * np.pi * 523.25 * t_c) +  # C5
                  0.30 * np.sin(2 * np.pi * 659.25 * t_c) +  # E5
                  0.25 * np.sin(2 * np.pi * 783.99 * t_c) +  # G5
                  0.20 * np.sin(2 * np.pi * 1046.5 * t_c)) * env_c * 0.50
        self.sounds['complete'] = self._create_stereo(wave_c)

    def play(self, name):
        if not self.enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
