import pyglet
from pyglet import graphics, shapes

class Note:

    def __init__(self, track, win):
        spacing = win.height / 12

        self.speed = 80
        self.pos = win.width
        self.track = track
        self.shape = shapes.Rectangle(self.pos, self.track * spacing, 20, spacing, color = (32, 32, 32))

    def is_hit(self, midi):
        return abs(self.track - midi) < 1.0 and self.pos < 20.0

    def is_gameover(self):
        return self.pos < 0.0

    def update(self, delta):
        self.pos -= self.speed * delta
        self.shape.x = self.pos

    def draw(self):
        self.shape.draw()

