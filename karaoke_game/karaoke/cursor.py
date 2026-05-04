import pyglet
from pyglet import graphics, shapes

class Cursor:

    def __init__(self):
        self.shape = shapes.Triangle(
            0, 0,   # first vertex
            0, 0,   # second vertex
            0, 0,   # third vertex
            color=(255, 0, 0)  # RGB: red
        )

    def draw(self, win, midi):
        spacing = win.height / 12

        if midi >= 0:
            self.shape.color = (96, 96, 96)
        else:
            self.shape.color = (200, 200, 200)
            midi = 6

        self.shape.y = -spacing / 4 + midi * spacing
        self.shape.x2 = spacing / 2
        self.shape.y2 = midi * spacing
        self.shape.y3 = spacing / 4 + midi * spacing

        self.shape.draw()

