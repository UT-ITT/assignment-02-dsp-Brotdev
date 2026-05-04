import pyglet
from pyglet import window, shapes
from pyglet.gl import glClearColor
from pyglet.math import Mat4, Vec3, Vec2
import sounddevice as sd
import random

from karaoke.utils import setup_tracks, calc_volume, detect_pitch, convert_to_midi
from karaoke.cursor import Cursor
from karaoke.note import Note

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CHUNK_SIZE = 2048
RATE = 44100
CHANNELS = 1

win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
glClearColor(1.0, 1.0, 1.0, 1.0)

tracks = setup_tracks(win)
cursor = Cursor()
notes = []

score = 0
scoreL = pyglet.text.Label('0', font_name='Times New Roman', font_size=36, x=win.width//2, y=win.height-20, anchor_x='center', anchor_y='top', color=(0, 0, 0))
gameover = False
gameoverL = pyglet.text.Label('Press R to restart', font_name='Times New Roman', font_size=36, x=win.width//2, y=win.height//2, anchor_x='center', anchor_y='center', color=(0, 0, 0))

print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

# let user select audio device
input_device = int(input("\nSelect input device: "))
midi = -1

def audio_callback(indata, frames, time, status):
    global midi
    if status:
        print(status)

    data = indata[:, 0]  # mono

    volume = calc_volume(data)
    if volume < -46:
        midi = -1
        return

    pitch = detect_pitch(data, RATE)
    midi = convert_to_midi(pitch) % 12

# open audio input stream
stream = sd.InputStream(
    device=input_device,
    channels=CHANNELS,
    samplerate=RATE,
    blocksize=CHUNK_SIZE,
    callback=audio_callback,
    latency='low'
)

@win.event
def on_draw():
    win.clear()
    tracks.draw()
    
    for note in notes:
        note.draw()

    cursor.draw(win, midi)
    scoreL.draw()

    if gameover:
        gameoverL.draw()

@win.event       
def on_key_press(symbol, modifiers):
    global gameover
    global score
    global timer
    if symbol == window.key.R:
        timer = 0
        score = 0
        scoreL.text = str(score)
        notes.clear()
        gameover = False

timer = 0.0
def update(delta: float) -> None:
    global gameover
    global timer
    global score
    global scoreL
    if gameover: return

    timer += delta

    for note in notes.copy():
        note.update(delta)

        if note.is_hit(midi):
            score += 1
            scoreL.text = str(score)
            notes.remove(note)
        elif note.is_gameover():
            gameover = True

    if timer > 2.0:
        notes.append(Note(random.randint(0, 11), win))
        timer -= 2.0

pyglet.clock.schedule_interval(update, 1.0/60.0)

with stream:
    pyglet.app.run()
