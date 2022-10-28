import time
from collections import deque
from threading import Thread

from gpiozero import LED
from gpiozero import MotionSensor

from event import Event
from led_strip import LedStrip

COLOR_ALERT = (0, 255, 0)
COLOR_FLICKER = (255, 70, 0)


class Hardware:
    def __init__(self):
        # Motion sensor
        self.pir = MotionSensor(4)
        self.alarm = False
        # Valves actuators
        self.valve1 = LED(21)
        self.valve2 = LED(27)
        # Fog actuators
        self.fog = LED(26)
        # Led strip
        self.leds = LedStrip()

    def start(self):
        self.pir.when_motion = self._alert
        self.pir.when_no_motion = self._rearmed
        self.leds.set_mode(LedStrip.MODE_FLICKER, COLOR_FLICKER)
        self.leds.start()

    def stop(self):
        pass  # TODO

    def _alert(self):
        self.alarm = True
        print("Motion detected")
        # Play the alarm sequence
        sequence = [
            Event(0.0, Event.LEDS, {'mode': LedStrip.MODE_ON, 'color': COLOR_ALERT}),
            Event(0.0, Event.GPIO, {'device': 'valve1', 'value': 'on'}),
            Event(0.2, Event.GPIO, {'device': 'valve1', 'value': 'off'}),
            Event(0.2, Event.GPIO, {'device': 'valve2', 'value': 'on'}),
            Event(0.4, Event.GPIO, {'device': 'valve2', 'value': 'off'}),
            Event(1.0, Event.GPIO, {'device': 'valve2', 'value': 'on'}),
            Event(1.2, Event.GPIO, {'device': 'valve2', 'value': 'off'}),
            Event(5.0, Event.LEDS, {'mode': LedStrip.MODE_FLICKER, 'color': COLOR_FLICKER}),
        ]
        thread = Thread(target=self._run_sequence, args=(sequence,), daemon=True)
        thread.start()

    def _rearmed(self):
        self.alarm = False
        print("Rearmed")

    def _run_sequence(self, sequence):
        print("Sequence started")
        queue = deque(sequence)
        start_time = time.time()
        while queue:
            e = queue.popleft()
            delay = e.time - (time.time() - start_time)
            if delay > 0:
                time.sleep(delay)
            last_event_time = e.time
            if e.action == Event.GPIO:
                gpio = None
                if e.data['device'] == 'valve1':
                    gpio = self.valve1
                elif e.data['device'] == 'valve2':
                    gpio = self.valve2
                elif e.data['device'] == 'fog':
                    gpio = self.fog
                if gpio is not None:
                    if e.data['value'] == 'on':
                        gpio.on()
                    else:
                        gpio.off()
            elif e.action == Event.SOUND:
                pass
            elif e.action == Event.LEDS:
                self.leds.set_mode(e.data['mode'], e.data['color'])
        print("Sequence complete")
