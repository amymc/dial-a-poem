#!/usr/bin/env python3

import math
import subprocess
import time
from functools import partial
from pathlib import Path

from gpiozero import Button

count = 0
p = None
counting = False
on_hook = True

track_names = [
    "vajra-kisses",
    "pressure",
    "cemetery-hill",
    "green-automobile",
    "mushroom-haiku",
    "excerpt-from-i-remember",
    "poems",
    "the-sonnets",
    "how-the-sestina-yawn-works",
    "geography",
]


def start_counting():
    global on_hook, counting

    if on_hook:
        return

    counting = True


def stop_counting(play_audio: bool):
    global count, counting, on_hook

    if on_hook or not counting:
        return

    if play_audio:
        play_dialled_number(count)

    counting = False
    count = 0


def play_dialled_number(count):
    global p

    index = math.ceil((count - 5) / 21.8) - 1

    try:
        track = track_names[index]
    except IndexError:
        track = track_names[-1]

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

    if p:
        p.terminate()


def main():
    global count, counting, p

    stop_dial_trigger = Button(17)  # White
    count_trigger = Button(23)  # Blue
    hook_trigger = Button(26)

    # These are kinda backwards. When you lift the phone off the hook the button is pressed.
    hook_trigger.when_pressed = start_listening
    hook_trigger.when_released = stop_listening

    stop_dial_trigger.when_deactivated = partial(stop_counting, True)
    count_trigger.when_deactivated = start_counting

    try:
        while True:
            if on_hook:
                continue

            if counting:
                count += 1

            time.sleep(0.005)
    except KeyboardInterrupt:
        if p:
            p.terminate()


if __name__ == "__main__":
    main()
