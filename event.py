class Event:
    GPIO = 0
    SOUND = 1
    LEDS = 2

    def __init__(self, time, action, data):
        self.time = time
        self.action = action
        self.data = data
