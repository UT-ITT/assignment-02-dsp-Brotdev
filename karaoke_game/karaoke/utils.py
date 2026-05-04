from pyglet import graphics, shapes
import numpy as np
import math

tracks = []

def setup_tracks(win):
    batch = graphics.Batch()

    count = 12
    spacing = win.height / count

    for i in range(1, count):
        y = i * spacing
        tracks.append(shapes.Line(0, y, win.width, y, 2, color=(256, 256, 256), batch=batch))

    return batch

# Compute RMS of audio sample
# Then convert to db
# See: https://en.wikipedia.org/wiki/Decibel#Acoustics
def calc_volume(sample):
    rms = np.sqrt(np.mean(sample ** 2))
    return 20 * np.log10(rms + 1e-12)

# Detect the pitch using autocorrelation
# Do correlation, find the lag/peak,
# convert to frequency
def detect_pitch(sample, rate):
    sample = sample - np.mean(sample)
    corr = np.correlate(sample, sample, mode='full')
    corr = corr[len(corr)//2:]
    d = np.diff(corr)
    start = np.where(d > 0)[0][0]
    peak = np.argmax(corr[start:]) + start
    return rate / peak if peak != 0 else 0

# Converts a frequency to a midi note (float)
# https://caml.music.mcgill.ca/~gary/307/week1/node11.html
def convert_to_midi(freq):
    return 69 + 12 * math.log2(freq / 440)
