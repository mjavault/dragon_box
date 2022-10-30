from led_strip import LedStrip


class Event:
    GPIO = 0
    SOUND = 1
    LEDS = 2

    def __init__(self, time, action, data):
        self.time = time
        self.action = action
        self.data = data

    @staticmethod
    def parse(line):
        try:
            if not line.startswith("#") and len(line.strip()) > 0:
                fields = list(map(lambda x: x.strip(), line.split(",")))
                time = float(fields[0])
                action = Event._parse_action(fields[1])
                if action == Event.GPIO:
                    data = {
                        'device': fields[2],
                        'value': fields[3] == "True",
                    }
                elif action == Event.SOUND:
                    data = {
                        'file': fields[2],
                        'resync': fields[3] == "True",
                    }
                elif action == Event.LEDS:
                    mode = Event._parse_leds_mode(fields[2])
                    data = {
                        'mode': mode,
                        'color': Event._parse_color(fields[3])
                    }
                else:
                    data = {}
                return Event(time, action, data)
        except Exception as e:
            print("Invalid line in animation: [{0}] -> {1}".format(line, e))
            return None

    @staticmethod
    def _parse_action(s):
        # Support both int and text notation
        try:
            action = int(s)
        except ValueError:
            if s == "GPIO":
                action = Event.GPIO
            elif s == "SOUND":
                action = Event.SOUND
            elif s == "LEDS":
                action = Event.LEDS
            else:
                raise Exception("Invalid action: {0}".format(s))
        return action

    @staticmethod
    def _parse_leds_mode(s):
        # Support both int and text notation
        try:
            mode = int(s)
        except ValueError:
            if s == "MODE_OFF":
                mode = LedStrip.MODE_OFF
            elif s == "MODE_ON":
                mode = LedStrip.MODE_ON
            elif s == "MODE_FLICKER":
                mode = LedStrip.MODE_FLICKER
            elif s == "MODE_RAINBOW":
                mode = LedStrip.MODE_RAINBOW
            else:
                raise Exception("Invalid LEDs mode: {0}".format(s))
        return mode

    @staticmethod
    def _parse_color(s):
        try:
            return tuple(map(lambda x: int(x.strip()), s.split("/")))
        except Exception:
            raise
