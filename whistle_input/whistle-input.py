import sounddevice as sd
import numpy as np
from pynput.keyboard import Key, Controller
from time import sleep

CHUNK_SIZE = 4096
RATE = 44100
CHANNELS = 1
VOLUME_THRESHOLD = -50.0
SLOPE_THRESHOLD = 50.0
SLOPE_THRESHOLD_MAX = 120.0

# print info about audio devices
print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

# let user select audio device
input_device = int(input("\nSelect input device: "))

keyboard = Controller()
buffer = []
dedupe = 5
state = None

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

# Compute the slope over the most recent values
# polyfit calculates a line (y = mx + b) through
# all points and we simply extract the slope
def get_slope():
    if len(buffer) < 5:
        return 0

    y = np.array(buffer)
    x = np.arange(len(y))
    slope = np.polyfit(x, y, 1)[0]
    return slope

# audio callback to safe data
def audio_callback(indata, frames, time, status):
    global buffer
    global dedupe
    global state

    if status:
        print(status)

    data = indata[:, 0]  # mono

    volume = calc_volume(data)
    if volume < VOLUME_THRESHOLD:
        buffer.clear()
        dedupe = 5
        return

    pitch = detect_pitch(data, RATE)
    if len(buffer) < 1 or pitch != buffer[-1] or dedupe < 1:
        buffer.append(pitch)
        del buffer[:-5]
        dedupe = 5
    else:
        dedupe -= 1

    slope = get_slope()

    if state is None:
        if SLOPE_THRESHOLD < slope < SLOPE_THRESHOLD_MAX:
            keyboard.press(Key.up)
            keyboard.release(Key.up)
            print("Detected UP chirp")
            state = 1
        if -SLOPE_THRESHOLD_MAX < slope < -SLOPE_THRESHOLD:
            keyboard.press(Key.down)
            keyboard.release(Key.down)
            print("Detected DOWN chirp")
            state = -1
    elif state == 1 and abs(slope) < 8:
        state = None
    elif state == -1 and abs(slope) < 8:
        state = None

# open audio input stream
stream = sd.InputStream(
    device=input_device,
    channels=CHANNELS,
    samplerate=RATE,
    blocksize=CHUNK_SIZE,
    callback=audio_callback,
    latency='low'
)

# continously capture and plot audio signal
with stream:
    print("\nNow listening for chirps (Ctrl+C to stop)")
    while True:
        sleep(0.01)
