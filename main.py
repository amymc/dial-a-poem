#!/usr/bin/env python3

import math
import subprocess
import time
from pathlib import Path

from gpiozero import Button

count = 0
counting = False
on_hook = True
p = None

track_map = {
    0: "vajra-kisses",
    1: "pressure",
    2: "cemetery-hill",
    3: "green-automobile",
    4: "mushroom-haiku",
    5: "excerpt-from-i-remember",
    6: "poems",
    7: "the-sonnets",
    8: "how-the-sestina-yawn-works",
    9: "geography",
}


def start_counting():
    global on_hook, counting

    if on_hook:
        return

    counting = True


def stop_counting():
    global count, counting, on_hook

    if on_hook or not counting:
        return

    digit = get_digit_for_count()

    counting = False
    count = 0


def get_digit_for_count():
    global count
    index = math.ceil((count - 5) / 21.8) - 1
    return index


def play_dialled_number(digit):
    global p

    if digit in track_map:
        track = track_map[digit]
    else:
        track = track_map[0]

    if p:
        p.terminate()

    parent = Path(__file__).resolve().parent
    p = subprocess.Popen(["mpg123", f"{parent / 'tracks' / track}.mp3"])


def start_listening():
    global on_hook
    on_hook = False


def stop_listening():
    global on_hook, p

    on_hook = True
    stop_counting(False)

    if p and p.poll() is None:
        p.terminate()


def main():
    global count, counting, p

    stop_dial_trigger = Button(17)  # White
    count_trigger = Button(23)  # Blue
    hook_trigger = Button(26)

    # These are kinda backwards. When you lift the phone off the hook the button is pressed.
    hook_trigger.when_pressed = start_listening
    hook_trigger.when_released = stop_listening

    stop_dial_trigger.when_deactivated = stop_counting
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
