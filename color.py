import colorsys


class Color:
    def __init__(self, rgb):
        self.rgb = rgb
        self.hsv = colorsys.rgb_to_hsv(self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255)

    @staticmethod
    def _to_rgb(h, s, v):
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)

    def with_brightness(self, brightness):
        return self._to_rgb(self.hsv[0], self.hsv[1], brightness)

    def get_brightness(self):
        return self.hsv[2]

    @classmethod
    def black(cls):
        return Color((0, 0, 0))
