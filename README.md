# SUMMARY

This code is for building up a clock made of a NeoPixel Ring of a various amouont of LEDs. In my Example here I built it with 60 LEDs, but can also fit to a ring with 32, 24, 16 or 12 LEDs as well.

## Programming language / Software requirements

The clock is written in Python 3.7. Necessary installed Python modules are:
- Board
- Neopixel
- RPi.GPIO

The RasPi can have Raspian OS Lite or Full installed. The Script should only be installed as a startup script to let the clock run when the system boots up.

## Hardware requirements

The clock was built up with a RaspberryPi Zero W. But it can also be built up with differente Raspberry Pi's. To gather the correct time, it's neccessary to have either an internet connection or have a hardware clock connected to the RasPi.
Beneath the RasPi you will need a ring of NeoPixel LEDs. The amount of LEDs is adjustable within the definition of stativ variables. So it's compatible with many different amount of LEDs on a ring. The +/- of the LED ring is soldered to +5V0/Ground of the RasPi. Data line is soldered to GPIO18 of the RassPi.
Additionally two buttons are connected to change the clockmode and to shutdown the whole system. 
The cavbeling for all hardware can be seen in "Verkabelung.fzz".