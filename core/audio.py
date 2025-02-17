# core/audio.py
import pygame
import os
import random

class AudioManager:
    """Manages audio playback for the game."""

    def __init__(self, config):
        """Initializes the AudioManager with settings from the config."""
        self.config = config
        self.initialized = False  # Flag to track initialization
        if self.config["audio"]["enabled"]:
            try:
                pygame.mixer.init()
                pygame.mixer.music.set_volume(self.config["audio"]["music_volume"])
                self.initialized = True
            except pygame.error as e:
                print(f"Error initializing Pygame mixer: {e}")
                # Consider setting a flag to disable audio if initialization fails

    def play_sound(self, sound_file):
        """Plays a sound effect. Handles sound pools and missing files."""
        if self.initialized:
            try:
                if isinstance(sound_file, list):
                    sound_file = random.choice(sound_file)

                sound_path = os.path.join("assets", "sound", sound_file)
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(self.config["audio"]["sfx_volume"])
                sound.play()
            except FileNotFoundError:
                print(f"SoundFX: {sound_file}")
            except pygame.error as e:
                print(f"Error playing sound: {e}")
            except TypeError as e:
                print(f"Type error. Check config file for audio_cue definition: {e}")

    def play_music(self, music_file):
        """Plays background music. Handles missing files."""
        if self.initialized:
            try:
                music_path = os.path.join("assets", "music", music_file)
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
            except FileNotFoundError:
                print(f"Soundtrack: {music_file}") # Corrected output
            except pygame.error as e:
                print(f"Error playing music: {e}") # Keep Pygame error message
            except TypeError as e:
                print(f"Type error. Check your config file for a music path: {e}")


    def stop_music(self):
        """Stops the background music."""
        if self.initialized:
            pygame.mixer.music.stop()