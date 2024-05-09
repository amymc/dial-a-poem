#!/usr/bin/env python3

from gpiozero import Button
import math
import random
import time
import subprocess

button = Button(17)
count_trigger = Button(23)
count = 0
p = None
active = False

track_names = ["vajra-kisses", "pressure", "cemetery-hill", "green-automobile", "mushroom-haiku", "excerpt-from-i-remember", "poems", "the-sonnets", "how-the-sestina-yawn-works", "geography"]


def set_active():
    global active
    active = True


def print_dialled_number(count):
    global p

    index = math.ceil((count - 30) / 20)
    # index = min(len(track_names) - 1, index)
    track = track_names[index]

    # if count < 30:
    #     print('1')
    # elif count < 50:
    #     print('2')
    # elif count < 70:
    #     print('3')
    # elif count < 90:
    #     print('4')
    # elif count < 110:
    #     print('5')
    # elif count < 130:
    #     print('6')
    # elif count < 150:
    #     print('7')
    # elif count < 170:
    #     print('8')
    # elif count < 190:
    #     print('9')
    # else:
    #     print('0')

    if p:
        p.terminate()

    p = subprocess.Popen(["mpg123", f"{track}.mp3"])

def set_inactive():
    global count
    global active

    if not active:
        return

    print_dialled_number(count)
    active = False
    count = 0


def main():
    global count
    global active
    global p

    button.when_deactivated = set_inactive
    count_trigger.when_deactivated = set_active

    try:
        while True:
            if active:
                count += 1

            time.sleep(0.005)
    except KeyboardInterrupt:
        if p:
            p.terminate()


if __name__ == '__main__':
    main()
