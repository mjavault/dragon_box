import os
import random
import time
from collections import deque
from threading import Thread

import pygame
from gpiozero import LED
from gpiozero import MotionSensor

from event import Event
from led_strip import LedStrip

COLOR_GREEN = (0, 255, 0)
COLOR_ORANGE = (255, 70, 0)


class Hardware:
    def __init__(self):
        self._running = False
        self._thread = None
        # Animations
        self._background_music = []
        self._animations = {}
        self._idle_animations = []
        self._load_animations()
        self._last_animation_time = time.time()
        # Motion sensor
        self.pir = MotionSensor(4)
        # Valves actuators
        self.box = LED(21)
        self.lid = LED(27)
        # Fog actuators
        self.fog = LED(26)
        # Led strip
        self.leds = LedStrip()
        # Default options
        self._motion_enabled = True
        self._music_enabled = True
        self._fog_enabled = True
        self._idle_enabled = True
        self._min_pause_time = 10.0  # seconds

    def start(self):
        self._running = True
        self.pir.when_motion = self._alert
        self.pir.when_no_motion = self._rearmed
        self.leds.set_mode(LedStrip.MODE_FLICKER, COLOR_ORANGE)
        self.leds.start()
        # background soundtrack
        pygame.mixer.init(buffer=512)
        self._start_background_music()
        # idle animations
        thread = Thread(target=self._watchdog, daemon=True)
        thread.start()

    def _load_animations(self, ambient_path="audio/ambient/", animations_path="audio/animations/"):
        # Load ambient music files
        for path in os.listdir(ambient_path):
            if path.endswith(".ogg"):
                self._background_music.append(os.path.join(ambient_path, path))
        print("{0} ambient music files loaded".format(len(self._background_music)))

        # Load animations
        for path in os.listdir(animations_path):
            if path.endswith(".txt"):
                category = None
                animation = []
                file = open(os.path.join(animations_path, path), 'r')
                for line in file.readlines():
                    if line.startswith("#!"):
                        category = line[2:].strip()
                    elif not line.startswith("#"):
                        e = Event.parse(line)
                        if e is not None:
                            animation.append(e)
                if category != "DISABLED":
                    self._animations[path] = animation
                    if category == "IDLE":
                        self._idle_animations.append(animation)
        print("{0} animations loaded".format(len(self._animations)))

    def _start_background_music(self):
        if len(self._background_music) > 0:
            pygame.mixer.music.load(random.choice(self._background_music))
            pygame.mixer.music.play(loops=-1)

    def _stop_background_music(self):
        pygame.mixer.music.stop()

    def stop(self):
        self._running = False

    def play_sequence(self, sequence):
        # Play the alarm sequence
        if self._thread is None:
            self._thread = Thread(target=self._run_sequence, args=(sequence,), daemon=True)
            self._thread.start()
        else:
            print("... previous sequence still running")

    def set_gpio(self, device, on):
        gpio = None
        if device == 'box':
            gpio = self.box
        elif device == 'lid':
            gpio = self.lid
        elif device == 'fog':
            if not on or self._fog_enabled:
                gpio = self.fog
        if gpio is not None:
            if on:
                gpio.on()
            else:
                gpio.off()

    def _alert(self):
        print("Motion detected")
        if self._motion_enabled:
            if time.time() - self._last_animation_time > self._min_pause_time:
                self.animate()
            else:
                print("... motion is paused")
        else:
            print("... motion is disabled")

    def _rearmed(self):
        print("Rearmed")

    def animate(self, name=None):
        if name is not None:
            animation = self._animations.get(name)
            if animation is not None:
                print("... playing animation {0}".format(name))
                self.play_sequence(animation)
            else:
                print("... animation {0} not found".format(name))
        elif len(self._animations) > 0:
            animation = random.choice(list(self._animations.items()))
            print("... playing animation {0} (random)".format(animation[0]))
            self.play_sequence(animation[1])
        else:
            print("... no animation available")

    def _run_sequence(self, sequence):
        print("Sequence started")
        try:
            # update the last animation time now, and then again once the animation is complete
            self._last_animation_time = time.time()
            # store led state
            leds_previous_mode = self.leds.mode
            leds_previous_color = self.leds.color.rgb
            # start animation
            queue = deque(sequence)
            start_time = time.time()
            while queue:
                e = queue.popleft()
                delay = e.time - (time.time() - start_time)
                if delay > 0:
                    time.sleep(delay)
                if e.action == Event.GPIO:
                    self.set_gpio(e.data['device'], e.data['value'])
                elif e.action == Event.SOUND:
                    sound = pygame.mixer.Sound(e.data['file'])
                    sound.play()
                    if e.data['resync']:
                        # resynchronize the loop time with moment the audio file started playing
                        start_time = time.time() - e.time
                elif e.action == Event.LEDS:
                    self.leds.set_mode(e.data['mode'], e.data['color'])
            # restore previous led state
            self.leds.set_mode(leds_previous_mode, leds_previous_color)
            self._last_animation_time = time.time()
        except Exception as e:
            print("Animation error: {0} - {1!r}".format(type(e).__name__, e))
        print("Sequence complete")
        self._thread = None

    def is_fog_enabled(self):
        return self._fog_enabled

    def set_fog_enabled(self, enabled):
        self._fog_enabled = enabled
        if not enabled:
            self.set_gpio("fog", False)

    def is_motion_enabled(self):
        return self._motion_enabled

    def set_motion_enabled(self, enabled):
        self._motion_enabled = enabled

    def is_idle_enabled(self):
        return self._idle_enabled

    def set_idle_enabled(self, enabled):
        self._idle_enabled = enabled

    def is_music_enabled(self):
        return self._music_enabled

    def set_music_enabled(self, enabled):
        if enabled and not self._music_enabled:
            print("Starting background music")
            self._start_background_music()
        elif not enabled and self._music_enabled:
            print("Stopping background music")
            self._stop_background_music()
        self._music_enabled = enabled

    def _watchdog(self):
        while self._running:
            if self._idle_enabled and len(self._idle_animations) > 0:
                if time.time() - self._last_animation_time > 5 * 60:
                    print("Idle triggered")
                    animation = random.choice(self._idle_animations)
                    self.play_sequence(animation)
            time.sleep(5.0)
