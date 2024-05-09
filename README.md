<a href='http://www.recurse.com' title='Made with love at the Recurse Center'><img src='https://cloud.githubusercontent.com/assets/2883345/11325206/336ea5f4-9150-11e5-9e90-d86ad31993d8.png' height='20px'/></a>

Recreation of John Giorno’s Dial-A-Poem </br>
https://www.moma.org/magazine/articles/884

Made at Recurse Center with [@joshestein](https://github.com/joshestein)

Person dials a number, a corresponding poem is selected based on the number dialed and that's played through the speaker in the phone handset.

We used a combination of [this tutorial video](https://www.youtube.com/watch?v=JChn7tV_qBk) and [this wiring diagram](https://www.telephonecollectors.info/index.php/browse/wiring-diagrams/western-electric/500-series-wall-telephones/2186-500-series-wall-telephones-554a-tl/file) to figure out how to connect the phone to the pi.</br>
Orginally we had the button connected to GPIO 18 as per the video but we later changed it to 17 because the amplifier wiring also uses GPIO 18 and it's not possible to use one pin for both input and output.

To determine which number was dialed we measured the time from the release of the dial until it had returned to it's original position.
  - We knew when it was released because at that point we could see on the oscilloscope the signal on one of the pins (`count_trigger`) dropped to zero.
  - We knew it was back to the original position because at that point the signal on the other pin (`button`) dropped to zero.
  - We figured out the time range for each dial just by dialing each number a bunch of times and logging the count.

We had to use the lite version of the raspberry pi OS because the amplifier doesn't work on the full version. </br>
(See 2nd warning message here - https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-usage)
</br>
</br>

Docs etc.
- amplifier wiring info </br>
  https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-wiring
- diagram of raspberry pi gpio pens </br>
  https://www.raspberrypi-spy.co.uk/2014/07/raspberry-pi-b-gpio-header-details-and-pinout/
- rotary phone wiring diagram </br>
  https://www.telephonecollectors.info/index.php/browse/wiring-diagrams/western-electric/500-series-wall-telephones/2186-500-series-wall-telephones-554a-tl/file </br>
  (full library of US rotary wiring diagrams - https://www.telephonecollectors.info/index.php/browse/wiring-diagrams)
- video on how to connect a rotary dial to a raspberry pi </br>
  https://www.youtube.com/watch?v=JChn7tV_qBk
- orignal audio recording used </br>
  https://www.youtube.com/watch?v=_21D3TE7YQk
