import random
import time
from threading import Thread

import adafruit_dotstar as dotstar
import board

from color import Color


class LedStrip:
    MODE_OFF = 0
    MODE_ON = 1
    MODE_FLICKER = 2
    MODE_RAINBOW = 3
    RAINBOW_COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (127, 255, 0), (0, 255, 0), (0, 255, 127),
                      (0, 255, 255), (0, 127, 255), (0, 0, 255), (127, 0, 255), (255, 0, 255), (255, 0, 127)]

    def __init__(self):
        self.led_count = 144
        self.dots = dotstar.DotStar(board.SCLK, board.MOSI, self.led_count, brightness=1.0, auto_write=False)
        self.mode = self.MODE_OFF
        self.color = Color.black()
        self._brightness = [0.0] * self.led_count  # used by the FLICKER mode
        self._color_index = 0  # used by the RAINBOW mode

    def start(self):
        thread = Thread(target=self._watchdog, daemon=True)
        thread.start()

    def set_mode(self, mode, rgb=None):
        self.mode = mode
        self.set_color(rgb)

    def set_color(self, rgb):
        if rgb is not None:
            self.color = Color(rgb)
            for i in range(len(self._brightness)):
                self._brightness[i] = self.color.get_brightness()

    def _write_color(self, color):
        for dot in range(self.led_count):
            self.dots[dot] = color.rgb
        self.dots.show()

    def _flicker(self, i):
        if random.randint(0, 1) == 0:
            self._brightness[i] = min(1.0, self._brightness[i] + 0.3)
        else:
            self._brightness[i] = max(0.0, self._brightness[i] - 0.3)
        return self.color.with_brightness(self._brightness[i])

    def _watchdog(self):
        while True:
            if self.mode == self.MODE_FLICKER:
                for i in range(self.led_count):
                    self.dots[i] = self._flicker(i)
                self.dots.show()
            elif self.mode == self.MODE_ON:
                self._write_color(self.color)
                time.sleep(.25)
            elif self.mode == self.MODE_RAINBOW:
                # Create a new color at position 0
                self.dots[0] = self.RAINBOW_COLORS[self._color_index]
                self._color_index = (self._color_index + 1) % len(self.RAINBOW_COLORS)
                # Move every color one step forward
                for i in range(self.led_count - 2, -1, -1):
                    self.dots[i + 1] = self.dots[i]
                    self.dots[i] = (0, 0, 0)
                self.dots.show()
                time.sleep(0.02)
            else:
                self._write_color((0, 0, 0))
                time.sleep(.25)
