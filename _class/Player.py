class Player:
    def __init__(self, x, y, velocity, color):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.color = color

    def move(self, x, y):
        self.x = x
        self.y = y