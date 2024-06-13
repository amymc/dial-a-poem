#!/usr/bin/env python3
import math
import random
import subprocess
import time
from datetime import datetime, timedelta

from gpiozero import Button
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from audio_mode import AudioMode, toggle_audio_mode, TOGGLE_MODE_DIALLING_NUMBER
from utils import AUDIO_DIR, get_tracks

# Used to determine the number dialled. Once the rotary dial is released, this starts incrementing until the dial
# stops rotating. We map from this count to the digit in `get_digit_for_count`.
count = 0
counting = False

# Used to check the delay between dialling digits.  Each time we dial a new digit, we reset this count.
# If the delay is long enough (e.g. it has been a while since we last dialled a digit) we combine all
# dialled digits into a single number.
dialling_count = 0
digit_buffer = []

p = None  # The process that handles playing the mp3

audio_mode = AudioMode.POEMS
track_map = get_tracks()


def start_counting():
    """Called when the dialler starts rotating back to its starting position."""
    global counting

    reset_dialling_count()
    counting = True


def stop_counting():
    """Called when the dialler finishes rotating back to its starting position."""
    global count, counting

    if not counting:
        return

    digit = get_digit_for_count()
    # Convert to strings so that we can have leading / trailing zeros
    digit_buffer.append(str(digit))

    reset_dialling_count()
    counting = False
    count = 0


def reset_dialling_count():
    global dialling_count, p
    # Reset to 1, which means we will start continuously counting again.
    # If we reset to 0 we block unnecessarily incrementing and checking for a potential play.
    dialling_count = 1

    if p and p.poll() is None:
        p.terminate()


def get_digit_for_count():
    """Returns the digit that was dialled. We do not zero offset. If you dial 1 you get 1!"""
    global count
    digit = math.ceil((count - 5) / 21.8)

    if digit == 10:
        digit = 0

    return digit


def play_dialled_number():
    global audio_mode, digit_buffer, p

    if not digit_buffer:
        return

    combined_digits = "".join(digit_buffer)
    digit_buffer = []

    if combined_digits == str(TOGGLE_MODE_DIALLING_NUMBER):
        audio_mode = toggle_audio_mode(audio_mode)
        return

    tracks_for_audio_mode = track_map.get(audio_mode, AudioMode.POEMS)
    track = tracks_for_audio_mode.get(combined_digits, random.choice(list(tracks_for_audio_mode.values())))

    p = subprocess.Popen(["mpg123", AUDIO_DIR / audio_mode / track])


def run_main_loop(observer):
    global count, counting, dialling_count, p

    try:
        while True:
            if counting:
                count += 1

            if dialling_count > 0:
                dialling_count += 1

            if dialling_count > 400:
                dialling_count = 0
                play_dialled_number()

            time.sleep(0.005)
    finally:
        if p and p.poll() is None:
            p.terminate()

        observer.stop()
        observer.join()


def main():
    stop_dial_trigger = Button(17)  # White
    count_trigger = Button(23)  # Blue

    stop_dial_trigger.when_deactivated = stop_counting
    stop_dial_trigger.when_activated = reset_dialling_count
    count_trigger.when_deactivated = start_counting

    observer = Observer()
    event_handler = FileChangedHandler()
    observer.schedule(event_handler, str(AUDIO_DIR), recursive=False)
    observer.start()

    run_main_loop(observer)


class FileChangedHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = datetime.now()

    def on_modified(self, event: FileSystemEvent) -> None:
        # Only take action when the track-list is modified, not when new audio is saved to the directory
        if event.is_directory:
            return

        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return

        # Allow some time for the file to be written to disk
        time.sleep(1)
        self.last_modified = datetime.now()

        global track_map
        track_map = get_tracks()


if __name__ == "__main__":
    main()
