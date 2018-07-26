class Coordinates:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return '[{0}][{1}]'.format(self.x, self.y)
