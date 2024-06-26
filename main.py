#!/usr/bin/env python3
import math
import random
import re
import time
from datetime import datetime, timedelta

import vlc
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

audio_process = vlc.MediaPlayer()

audio_mode = AudioMode.POEMS
track_map = get_tracks()

DOUBLE_TAP_TIMEOUT = 200

# This regex is copied from the flask WTF form validation.
url_regex = re.compile(
    r"^[a-z]+://" r"(?P<host>[^\/\?:]+)" r"(?P<port>:[0-9]+)?" r"(?P<path>\/.*?)?" r"(?P<query>\?.*)?$"
)


def start_counting():
    """Called when the dialler starts rotating back to its starting position."""
    global on_hook, counting

    if on_hook:
        return

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
    global dialling_count
    # Reset to 1, which means we will start continuously counting again.
    # If we reset to 0 we block unnecessarily incrementing and checking for a potential play.
    dialling_count = 1

    terminate_running_subprocess()


def get_digit_for_count():
    """Returns the digit that was dialled. We do not zero offset. If you dial 1 you get 1!"""
    global count
    digit = math.ceil((count - 5) / 20.6)

    if digit == 10:
        digit = 0

    return digit


def play_dialled_number():
    global audio_mode, digit_buffer, audio_process

    if not digit_buffer:
        return

    combined_digits = "".join(digit_buffer)
    tracks_for_audio_mode = track_map.get(audio_mode, AudioMode.POEMS)
    track = tracks_for_audio_mode.get(combined_digits, random.choice(list(tracks_for_audio_mode.values())))

    digit_buffer = []

    # Could we just do track.endswith(".mp3") instead? Are there URLs that end in .mp3?
    if url_regex.match(track):
        audio_process.set_mrl(track)
        # Alternatively, use requests to first download and then play the audio:
        # if response.headers["Content-Type"] != "audio/mpeg":
        #     return
        #
        # with tempfile.NamedTemporaryFile() as f:
        #     f.write(response.content)
        #     audio_process.set_mrl(f.name)
        #     audio_process.play()
    else:
        audio_process.set_mrl(AUDIO_DIR / audio_mode / track)
    audio_process.play()


def start_listening():
    """Called when you take the phone off the hook."""
    global audio_mode, digit_buffer, on_hook, audio_process
    on_hook = False
    digit_buffer = []

    audio_process.set_mrl(AUDIO_DIR / audio_mode / "off-hook.mp3")
    audio_process.play()


def stop_listening():
    """Called when you replace the phone on the hook."""
    global counting, count, dialling_count, on_hook

    on_hook = True
    dialling_count = 0
    counting = False
    count = 0
    reset_dialling_count()
    handle_hook_double_tap()


def handle_hook_double_tap():
    """Checks if the hook has been replaced twice in rapid succession. If so, toggle between poem and joke modes."""
    global audio_mode, on_hook_count

    print(f"{on_hook_count=}")

    if on_hook_count == 0:
        # Hook just replaced, allow incrementing count in main loop
        on_hook_count = 1
    elif 30 < on_hook_count < DOUBLE_TAP_TIMEOUT:
        # 'Double-tapped' phone back on hook
        on_hook_count = 0
        audio_mode = toggle_audio_mode(audio_mode)


def run_main_loop(observer):
    global count, counting, dialling_count, on_hook_count

    hook_trigger = Button(26)

    # Used to manually detect lifting/hanging up the phone.
    # This is necessary because there is some sort of weird lock that happens when hanging up with a background
    # subprocess.
    # With the built-in event detection, the hang-up is not detected and the CPU usage goes to 100%
    # (while there is an active background mp3 subprocess).
    lifted_hook = False
    time_since_lifted_off = 0
    time_since_hung_up = 0

    try:
        while True:
            if not lifted_hook and hook_trigger.is_pressed:
                time_since_hung_up = 0
                time_since_lifted_off += 1
            elif lifted_hook and not hook_trigger.is_pressed:
                time_since_lifted_off = 0
                time_since_hung_up += 1

            if not lifted_hook and time_since_lifted_off > 30:
                start_listening()
                lifted_hook = True

            if lifted_hook and time_since_hung_up > 30:
                stop_listening()
                lifted_hook = False

            if counting:
                count += 1

            if dialling_count > 0:
                dialling_count += 1

            if dialling_count > 400:
                dialling_count = 0
                play_dialled_number()

            # The phone was taken off the hook, start counting how long it has been.
            if on_hook_count > 0:
                on_hook_count += 1

            if on_hook_count > DOUBLE_TAP_TIMEOUT:
                # We have not replaced the hook for a while, stop counting
                on_hook_count = 0

            time.sleep(0.005)
    finally:
        terminate_running_subprocess()

        observer.stop()
        observer.join()


def terminate_running_subprocess():
    global audio_process

    if audio_process.is_playing():
        audio_process.stop()


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
