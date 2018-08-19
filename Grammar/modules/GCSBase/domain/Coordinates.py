class Coordinates:
    def __init__(self, x: int, y: int, *args):
        self.x = x
        self.y = y

    def __str__(self):
        return '[{0}][{1}]'.format(self.x, self.y)

    @staticmethod
    def fromJson(coordinate):
        if coordinate is not None:
            return Coordinates(coordinate['x'], coordinate['y'])
        return None
