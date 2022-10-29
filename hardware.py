import time
from collections import deque
from threading import Thread

import pygame
from gpiozero import LED
from gpiozero import MotionSensor

from event import Event
from led_strip import LedStrip

COLOR_ALERT = (0, 255, 0)
COLOR_FLICKER = (255, 70, 0)


class Hardware:
    ANIMATION_SEQUENCE = [
        Event(0.00, Event.SOUND, {'file': 'audio/wolf.ogg', 'resync': True}),
        Event(0.00, Event.LEDS, {'mode': LedStrip.MODE_ON, 'color': COLOR_ALERT}),
        # 1st bark
        Event(0.55, Event.GPIO, {'device': 'fog', 'value': 'on'}),
        Event(0.55, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(0.65, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(0.80, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(1.00, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(1.16, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(1.36, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(1.56, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(1.76, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(1.95, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(2.15, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(2.15, Event.GPIO, {'device': 'fog', 'value': 'off'}),
        # growls
        Event(2.85, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(2.95, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(3.05, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(3.15, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(3.25, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(3.35, Event.GPIO, {'device': 'box', 'value': 'off'}),
        # 2nd (large) bark
        Event(4.95, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(5.00, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(5.10, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(5.15, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(5.28, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(5.52, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(5.52, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(5.72, Event.GPIO, {'device': 'box', 'value': 'off'}),
        # 3rd bark
        Event(5.85, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(6.00, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        # 4th bark
        Event(7.58, Event.GPIO, {'device': 'fog', 'value': 'on'}),
        Event(7.58, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(7.88, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(8.50, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(8.70, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(8.90, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(9.10, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(9.30, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(9.50, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(9.50, Event.GPIO, {'device': 'fog', 'value': 'off'}),
        # last bark
        Event(9.90, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(10.00, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(10.14, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(10.30, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        # growls
        Event(11.95, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(12.15, Event.GPIO, {'device': 'box', 'value': 'off'}),
        # end
        Event(19.00, Event.LEDS, {'mode': LedStrip.MODE_FLICKER, 'color': COLOR_FLICKER}),
    ]

    ANIMATION_SEQUENCE_OLD = [
        Event(0.0, Event.LEDS, {'mode': LedStrip.MODE_ON, 'color': COLOR_ALERT}),
        Event(0.0, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(0.2, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(0.2, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(0.4, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(1.0, Event.GPIO, {'device': 'lid', 'value': 'on'}),
        Event(1.2, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(2.0, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(2.2, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(2.4, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(2.6, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(2.8, Event.GPIO, {'device': 'box', 'value': 'on'}),
        Event(3.0, Event.GPIO, {'device': 'box', 'value': 'off'}),
        Event(4.0, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(6.0, Event.GPIO, {'device': 'lid', 'value': 'off'}),
        Event(7.0, Event.LEDS, {'mode': LedStrip.MODE_FLICKER, 'color': COLOR_FLICKER}),
    ]
    BACKGROUND_SOUNDTRACK = 'audio/background.ogg'

    def __init__(self):
        self._running = False
        self._thread = None
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

    def start(self):
        self._running = True
        self.pir.when_motion = self._alert
        self.pir.when_no_motion = self._rearmed
        self.leds.set_mode(LedStrip.MODE_FLICKER, COLOR_FLICKER)
        self.leds.start()
        # background soundtrack
        pygame.mixer.init(buffer=512)
        pygame.mixer.music.load(self.BACKGROUND_SOUNDTRACK)
        self._start_background_music()

    def _start_background_music(self):
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
            gpio = self.fog
        if gpio is not None:
            if on:
                gpio.on()
            else:
                gpio.off()

    def _alert(self):
        print("Motion detected")
        if self._motion_enabled:
            self.play_sequence(self.ANIMATION_SEQUENCE)
        else:
            print("... motion is disabled")

    def _rearmed(self):
        print("Rearmed")

    def _run_sequence(self, sequence):
        print("Sequence started")
        try:
            queue = deque(sequence)
            start_time = time.time()
            while queue:
                e = queue.popleft()
                delay = e.time - (time.time() - start_time)
                if delay > 0:
                    time.sleep(delay)
                if e.action == Event.GPIO:
                    self.set_gpio(e.data['device'], e.data['value'] == 'on')
                elif e.action == Event.SOUND:
                    sound = pygame.mixer.Sound(e.data['file'])
                    sound.play()
                    if e.data['resync']:
                        # resynchronize the loop time with moment the audio file started playing
                        start_time = time.time() - e.time
                elif e.action == Event.LEDS:
                    self.leds.set_mode(e.data['mode'], e.data['color'])
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
