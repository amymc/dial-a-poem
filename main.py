#!/usr/bin/env python3
import math
import random
import subprocess
import time
from datetime import datetime, timedelta

from gpiozero import Button
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from audio_mode import AudioMode, toggle_audio_mode
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

on_hook = True

# Used to determine if we replaced the hook twice in quick succession (i.e. 'double-tapped' the hook).
# If so, we change the audio mode.
on_hook_count = 0

p = None  # The process that handles playing the mp3

audio_mode = AudioMode.POEMS
track_map = get_tracks()


def start_counting():
    """Called when the dialler starts rotating back to its starting position."""
    global on_hook, counting

    if on_hook:
        return

    reset_dialling_count()
    counting = True


def stop_counting():
    """Called when the dialler finishes rotating back to its starting position."""
    global count, counting, on_hook

    if on_hook or not counting:
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
    index = math.ceil((count - 5) / 21.8)

    if index == 10:
        index = 0

    return index


def play_dialled_number():
    global audio_mode, digit_buffer, p

    if not digit_buffer:
        return

    combined_digits = "".join(digit_buffer)
    tracks_for_audio_mode = track_map.get(audio_mode, AudioMode.POEMS)
    track = tracks_for_audio_mode.get(combined_digits, random.choice(list(tracks_for_audio_mode.values())))

    digit_buffer = []

    p = subprocess.Popen(["mpg123", AUDIO_DIR / audio_mode / track])


def start_listening():
    """Called when you take the phone off the hook."""
    global audio_mode, digit_buffer, on_hook, p
    on_hook = False
    digit_buffer = []

    p = subprocess.Popen(["mpg123", AUDIO_DIR / audio_mode / "off-hook.mp3"])


def stop_listening():
    """Called when you replace the phone on the hook."""
    global dialling_count, on_hook, p

    on_hook = True
    dialling_count = 0
    stop_counting()
    handle_hook_double_tap()

    if p and p.poll() is None:
        p.terminate()


def handle_hook_double_tap():
    """Checks if the hook has been replaced twice in rapid succession. If so, toggle between poem and joke modes."""
    global audio_mode, on_hook_count

    if on_hook_count == 0:
        # Hook just replaced, allow incrementing count in main loop
        on_hook_count = 1
    elif 30 < on_hook_count < 100:
        # 'Double-tapped' phone back on hook
        on_hook_count = 0
        audio_mode = toggle_audio_mode(audio_mode)


def run_main_loop(observer):
    global count, counting, dialling_count, on_hook_count, p

    try:
        while True:
            if counting:
                count += 1

            if dialling_count > 0:
                dialling_count += 1

            if dialling_count > 400:
                dialling_count = 0
                play_dialled_number()

            if on_hook_count > 0:
                on_hook_count += 1

            if on_hook_count > 100:
                # We have not replaced the hook for a while, stop counting
                on_hook_count = 0

            time.sleep(0.005)
    finally:
        if p and p.poll() is None:
            p.terminate()

        observer.stop()
        observer.join()


def main():
    stop_dial_trigger = Button(17)  # White
    count_trigger = Button(23)  # Blue
    hook_trigger = Button(26)

    # These are kinda backwards. When you lift the phone off the hook the button is pressed.
    hook_trigger.when_pressed = start_listening
    hook_trigger.when_released = stop_listening

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
