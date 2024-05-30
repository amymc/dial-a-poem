#!/usr/bin/env python3

import math
import subprocess
import time
from gpiozero import Button
from pathlib import Path

from utils import get_tracks

count = 0
counting = False
dialling_count = 0
digit_buffer = []
on_hook = True
p = None

track_map = get_tracks()
TRACK_DIR = Path(__file__).resolve().parent / "tracks"


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


def get_digit_for_count():
    """Returns the digit that was dialled. We do not zero offset. If you dial 1 you get 1!"""
    global count
    index = math.ceil((count - 5) / 21.8)

    if index == 10:
        index = 0

    return index


def play_dialled_number():
    global dialling_count, digit_buffer, p

    if not digit_buffer:
        return

    combined_digits = "".join(digit_buffer)
    track = track_map.get(combined_digits, "geography")

    # Reset to zero to prevent further incrementing until we start dialling again
    dialling_count = 0
    digit_buffer = []

    p = subprocess.Popen(["mpg123", f"{TRACK_DIR / track}.mp3"])


def start_listening():
    """Called when you take the phone off the hook."""
    global digit_buffer, on_hook, p
    on_hook = False
    digit_buffer = []

    p = subprocess.Popen(["mpg123", f"{TRACK_DIR / 'off-hook'}.mp3"])


def stop_listening():
    """Called when you replace the phone on the hook."""
    global dialling_count, on_hook, p

    on_hook = True
    dialling_count = 0
    stop_counting()

    if p and p.poll() is None:
        p.terminate()


def reset_dialling_count():
    global dialling_count, p
    # Reset to 1, which means we will start continuously counting again.
    # If we reset to 0 we block unnecessarily incrementing and checking for a potential play.
    dialling_count = 1

    if p and p.poll() is None:
        p.terminate()


def main():
    global count, counting, dialling_count, p

    stop_dial_trigger = Button(17)  # White
    count_trigger = Button(23)  # Blue
    hook_trigger = Button(26)

    # These are kinda backwards. When you lift the phone off the hook the button is pressed.
    hook_trigger.when_pressed = start_listening
    hook_trigger.when_released = stop_listening

    stop_dial_trigger.when_deactivated = stop_counting
    stop_dial_trigger.when_activated = reset_dialling_count
    count_trigger.when_deactivated = start_counting

    try:
        while True:
            if on_hook:
                continue

            if counting:
                count += 1

            if dialling_count > 0:
                dialling_count += 1

            if dialling_count > 400:
                play_dialled_number()

            time.sleep(0.005)
    except KeyboardInterrupt:
        if p and p.poll() is None:
            p.terminate()


if __name__ == "__main__":
    main()
