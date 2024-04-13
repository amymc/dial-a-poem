# https://github.com/amymc/push-a-poem/blob/master/pressure.mp3

import vlc
import random
import time
import RPi.GPIO as GPIO

track_names = ["vajra-kisses", "pressure", "cemetery-hill"]

def play_random_track():
    randTrack = random.choice(track_names)
    # print(randTrack)
    print("https://github.com/amymc/push-a-poem/blob/master/% s.mp3?raw=true" % (randTrack))
    p = vlc.MediaPlayer(randTrack)
    p.play()

    while True:
        pass

BUTTON_PIN = 16
GPIO.setmode(GPIO.BCM)  
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

try:
    while True:
        time.sleep(0.1)
        if (GPIO.input(BUTTON_PIN) == GPIO.LOW) and (button_pressed is False):
            print("button pressed")
            button_pressed = True
            play_random_track()
        elif (GPIO.input(BUTTON_PIN) == GPIO.HIGH):
            button_pressed = False
except KeyboardInterrupt:
    GPIO.cleanup()

# play_random_track()