
import threading
import logging
import sys
import warnings
import os
import time

warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message=r".*pkg_resources is deprecated as an API.*"
)

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

logger = logging.getLogger(__name__)

class HoloWave:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        super().__init__()
        if hasattr(self, "initialized"):
            return

        self._initComponents(parent)

        self.initialized = True

    def _initComponents(self, parent):
        self.parent = parent
        self._setDefaults()

    def _setDefaults(self):
        self.soundChannel   = getattr(self.parent, "soundChannel", 2) if self.parent else 2
        self.soundChoice    = getattr(self.parent, "soundChoice", 0) if self.parent else 0
        self.sounds         = getattr(self.parent, "sounds", {}) if self.parent else {}
        self._initMixer()

    def getProperty(self, propName):
        propMap = {
            # pygame mixer properties
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),
        }
        getter = propMap.get(propName)
        if getter:
            return getter()
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def setProperty(self, propName, value):
        propMap = {
            # pygame mixer properties
            "sounds":       lambda v: setattr(self, "sounds", v),
            "soundChannel": lambda v: setattr(self, "soundChannel", int(v)),
            "soundChoice":  lambda v: setattr(self, "soundChoice", int(v)),
        }
        setter = propMap.get(propName)
        if setter:
            setter(value)
        else:
            raise AttributeError(f"Unknown property: '{propName}'. Allowed: {list(propMap)}")

    def _soundFallback(self, freq: int = 350, duration: int = 500) -> None:
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(freq, duration)
        else:
            print('\a', end='', flush=True)

    # def getSound(self, key: int) -> None:
    #     try:
    #         soundFile = self.sounds.get(key)
    #     except AttributeError:
    #         logger.error("Sounds not initialized. Please set up sounds first.", exc_info=True)
    #         return
    #     if not soundFile:
    #         self._soundFallback()
    #         return
    #     try:
    #         self.waveChannel.play(pygame.mixer.Sound(soundFile))
    #         while self.isPlaying():
    #             time.sleep(0.1)
    #     except pygame.error:
    #         logger.error("Sound error", exc_info=True)
    def getSound(self, key: int) -> None:
        try:
            # prefer live parent mapping; fall back to local snapshot
            sounds = getattr(self.parent, "sounds", None) or self.sounds
            soundFile = sounds.get(key)
        except AttributeError:
            logger.error("Sounds not initialized. Please set up sounds first.", exc_info=True)
            return

        if not soundFile:
            self._soundFallback()
            return
        try:
            self.waveChannel.play(pygame.mixer.Sound(soundFile))
            while self.isPlaying():
                time.sleep(0.1)
        except pygame.error:
            logger.error("Sound error", exc_info=True)


    def _initMixer(self) -> None:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                return
        if not hasattr(self, "speechChannel"):
            self.waveChannel = pygame.mixer.Channel(self.soundChannel)

    def isPlaying(self) -> bool:
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                self.waveChannel = pygame.mixer.Channel(self.soundChannel)
            except pygame.error as e:
                logger.error(f"Failed to initialize the mixer:", exc_info=True)
                return False
        return self.waveChannel.get_busy()
