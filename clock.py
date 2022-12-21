""" Neo Pixel LED Clock Module """

import os
import time
import board
import neopixel
import RPi.GPIO as GPIO


######## GLOBAL VARIABLES ########

# Set absolute amount of LEDs of the ring
ABSOLUTE_LED = int(60)

# Debugging on/off
DEBUG_MODE = True

# Show markers on/off
SHOW_HOUR_MARKER = True
SHOW_QUARTER_MARKER = True

# Set Hour Markers depending on LED count
HOUR_MARKER_0 = 0
HOUR_MARKER_1 = int(ABSOLUTE_LED / 12)
HOUR_MARKER_2 = int(2 * ABSOLUTE_LED / 12)
HOUR_MARKER_3 = int(3 * ABSOLUTE_LED / 12)
HOUR_MARKER_4 = int(4 * ABSOLUTE_LED / 12)
HOUR_MARKER_5 = int(5 * ABSOLUTE_LED / 12)
HOUR_MARKER_6 = int(6 * ABSOLUTE_LED / 12)
HOUR_MARKER_7 = int(7 * ABSOLUTE_LED / 12)
HOUR_MARKER_8 = int(8 * ABSOLUTE_LED / 12)
HOUR_MARKER_9 = int(9 * ABSOLUTE_LED / 12)
HOUR_MARKER_10 = int(10 * ABSOLUTE_LED / 12)
HOUR_MARKER_11 = int(11 * ABSOLUTE_LED / 12)

# Set Quarter Markers depending on LED count
QUARTER_MARKER_15 = int(ABSOLUTE_LED / 4)
QUARTER_MARKER_30 = int(2 * ABSOLUTE_LED / 4)
QUARTER_MARKER_45 = int(3 * ABSOLUTE_LED / 4)

# Set colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
VIOLET = (140, 0, 120)
QUARTER_MARKER = (70, 60, 60)
HOUR_MARKER = (7, 5, 5)
LED_OFF = (0, 0, 0)
ORANGE = (140, 55, 0)
BRIGHT_WHITE = (255, 255, 255)

# Initialize NeoPixels
pixels = neopixel.NeoPixel(board.D18, ABSOLUTE_LED, bpp=3, brightness=0.5, auto_write=False,
                           pixel_order="GRB")

# Initialize GPIOs für Buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

##################################


def get_current_time(param):
    """ Return current seconds, minutes or hours """
    if param == "hour":
        return int(time.strftime("%I"))
    if param == "minute":
        return int(time.strftime("%M"))
    if param == "second":
        return int(time.strftime("%S"))

    return None


def init_clock():
    """ Initialize the clock """
    led_hours, led_minutes, led_seconds = get_time()

    # Clear all pixels
    pixels.fill((0, 0, 0))

    # Set marker pixels
    pixels[HOUR_MARKER_0] = ORANGE
    if SHOW_QUARTER_MARKER:
        # Make the quarter marker brighter than the hour marker
        pixels[QUARTER_MARKER_15] = QUARTER_MARKER
        pixels[QUARTER_MARKER_30] = QUARTER_MARKER
        pixels[QUARTER_MARKER_45] = QUARTER_MARKER
    elif SHOW_HOUR_MARKER and not SHOW_QUARTER_MARKER:
        # Make the quarter marker and the hour marker to the same brightness
        pixels[QUARTER_MARKER_15] = HOUR_MARKER
        pixels[QUARTER_MARKER_30] = HOUR_MARKER
        pixels[QUARTER_MARKER_45] = HOUR_MARKER

    if SHOW_HOUR_MARKER:
        pixels[HOUR_MARKER_1] = HOUR_MARKER
        pixels[HOUR_MARKER_2] = HOUR_MARKER
        pixels[HOUR_MARKER_4] = HOUR_MARKER
        pixels[HOUR_MARKER_5] = HOUR_MARKER
        pixels[HOUR_MARKER_7] = HOUR_MARKER
        pixels[HOUR_MARKER_8] = HOUR_MARKER
        pixels[HOUR_MARKER_10] = HOUR_MARKER
        pixels[HOUR_MARKER_11] = HOUR_MARKER

    # Set pixels for second, minute and hour
    if led_seconds == led_hours and led_seconds == led_minutes:
        pixels[led_seconds] = BRIGHT_WHITE
    elif led_hours == led_minutes:
        pixels[led_minutes] = CYAN
        pixels[led_seconds] = RED
    else:
        pixels[led_hours] = GREEN
        pixels[led_minutes] = BLUE
        pixels[led_seconds] = RED

    pixels.show()


def get_time():
    """ Get current local time """
    #global second

    hour = get_current_time("hour")
    if hour == 12:
        hour = 0
    minute = get_current_time("minute")
    second = get_current_time("second")

    led_hours = int((hour * ABSOLUTE_LED / 12) + ((ABSOLUTE_LED / 12) * minute / 60))
    led_minutes = int(minute * ABSOLUTE_LED / 60)
    led_seconds = int(second * ABSOLUTE_LED / 60)

    return led_hours, led_minutes, led_seconds


def switch_clock_mode(_channel):
    """ Switch between the different clock modes and set only quarter marker,
     only hour marker, quarter and hour marker or no marker """
    # global is necessary, because of a callback function in the GPIO
    global SHOW_HOUR_MARKER
    global SHOW_QUARTER_MARKER

    if SHOW_HOUR_MARKER and SHOW_QUARTER_MARKER:
        SHOW_QUARTER_MARKER = False
        SHOW_HOUR_MARKER = True
        if DEBUG_MODE:
            print("Clock mode changed - ClockMode 1")
    elif SHOW_HOUR_MARKER and not SHOW_QUARTER_MARKER:
        SHOW_HOUR_MARKER = False
        SHOW_QUARTER_MARKER = True
        if DEBUG_MODE:
            print("Clock mode changed - ClockMode 2")
    elif SHOW_QUARTER_MARKER and not SHOW_HOUR_MARKER:
        SHOW_QUARTER_MARKER = False
        SHOW_HOUR_MARKER = False
        if DEBUG_MODE:
            print("Clock mode changed - ClockMode 3")
    elif not SHOW_QUARTER_MARKER and not SHOW_HOUR_MARKER:
        SHOW_HOUR_MARKER = True
        SHOW_QUARTER_MARKER = True
        if DEBUG_MODE:
            print("Clock mode changed - ClockMode 4")

    init_clock()


def system_shutdown(_channel):
    """ Shutdown system """
    print("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
    pixels.deinit()
    os.system("sudo poweroff")
    time.sleep(1)


if __name__ == "__main__":
    #second = 0
    INIT = True

    init_clock()

    # Switch clock mode to show quarter marks or not
    GPIO.add_event_detect(23, GPIO.RISING, callback=switch_clock_mode, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(20, GPIO.RISING, callback=system_shutdown, bouncetime=400)

    while True:
        try:
            pixel_hours, pixel_minutes, pixel_seconds = get_time()

            if pixel_seconds == 0 and INIT:
                # Run init only once per minute
                init_clock()
                INIT = False

                if DEBUG_MODE:
                    print("INIT")

            # Define the pixel in front of the current pixel
            if pixel_seconds == 0:
                pixel_reverse = ABSOLUTE_LED - 1
            else:
                pixel_reverse = pixel_seconds - 1

            if pixel_seconds == ABSOLUTE_LED - 1:
                # Reset counter for Init
                INIT = True

            if pixel_seconds == pixel_hours and pixel_seconds == pixel_minutes:
                # If second, minute and hour are on the same pixel
                pixels[pixel_seconds] = BRIGHT_WHITE
                if pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = CYAN
                elif pixel_reverse == 0 and pixel_minutes > 0:
                    pixels[pixel_reverse] = ORANGE
                elif SHOW_QUARTER_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = QUARTER_MARKER
                elif not SHOW_QUARTER_MARKER and SHOW_HOUR_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = HOUR_MARKER
                elif SHOW_HOUR_MARKER and pixel_reverse in \
                        (HOUR_MARKER_1, HOUR_MARKER_2, HOUR_MARKER_4, HOUR_MARKER_5,
                         HOUR_MARKER_7, HOUR_MARKER_8, HOUR_MARKER_10, HOUR_MARKER_11):
                    pixels[pixel_reverse] = HOUR_MARKER
                else:
                    pixels[pixel_reverse] = LED_OFF

                if DEBUG_MODE:
                    print("SECOND/MINUTE/HOUR")
            elif pixel_seconds == pixel_minutes:
                # If second and minute are on the same pixel
                pixels[pixel_seconds] = VIOLET
                if pixel_reverse == pixel_hours:
                    pixels[pixel_reverse] = GREEN
                elif pixel_reverse == 0 and pixel_reverse != pixel_hours:
                    pixels[pixel_reverse] = ORANGE
                elif SHOW_QUARTER_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = QUARTER_MARKER
                elif not SHOW_QUARTER_MARKER and SHOW_HOUR_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = HOUR_MARKER
                elif SHOW_HOUR_MARKER and pixel_reverse in \
                        (HOUR_MARKER_1, HOUR_MARKER_2, HOUR_MARKER_4, HOUR_MARKER_5,
                         HOUR_MARKER_7, HOUR_MARKER_8, HOUR_MARKER_10, HOUR_MARKER_11):
                    pixels[pixel_reverse] = HOUR_MARKER
                else:
                    pixels[pixel_reverse] = LED_OFF

                if DEBUG_MODE:
                    print("MINUTE")
            elif pixel_seconds == pixel_hours:
                # If second and hour are on the same pixel
                pixels[pixel_seconds] = YELLOW
                if pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = BLUE
                elif pixel_reverse == 0 and pixel_reverse != pixel_minutes:
                    pixels[pixel_reverse] = ORANGE
                elif SHOW_QUARTER_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = QUARTER_MARKER
                elif not SHOW_QUARTER_MARKER and SHOW_HOUR_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = HOUR_MARKER
                elif SHOW_HOUR_MARKER and pixel_reverse in \
                        (HOUR_MARKER_1, HOUR_MARKER_2, HOUR_MARKER_4, HOUR_MARKER_5,
                         HOUR_MARKER_7, HOUR_MARKER_8, HOUR_MARKER_10, HOUR_MARKER_11):
                    pixels[pixel_reverse] = HOUR_MARKER
                else:
                    pixels[pixel_reverse] = LED_OFF

                if DEBUG_MODE:
                    print("HOUR")
            elif pixel_minutes == pixel_hours and pixel_seconds != pixel_minutes:
                # If minute and hour only are on the same pixel
                pixels[pixel_seconds] = RED
                if pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = CYAN
                elif pixel_reverse == 0 and pixel_reverse != pixel_minutes:
                    pixels[pixel_reverse] = ORANGE
                elif SHOW_QUARTER_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = QUARTER_MARKER
                elif not SHOW_QUARTER_MARKER and SHOW_HOUR_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = HOUR_MARKER
                elif SHOW_HOUR_MARKER and pixel_reverse in \
                        (HOUR_MARKER_1, HOUR_MARKER_2, HOUR_MARKER_4, HOUR_MARKER_5,
                         HOUR_MARKER_7, HOUR_MARKER_8, HOUR_MARKER_10, HOUR_MARKER_11):
                    pixels[pixel_reverse] = HOUR_MARKER
                else:
                    pixels[pixel_reverse] = LED_OFF

                if DEBUG_MODE:
                    print("MINUTE/HOUR")
            elif pixel_minutes == pixel_hours and pixel_reverse == pixel_minutes and \
                    pixel_reverse == pixel_hours:
                # If hour and minute are on the reverse pixel
                pixels[pixel_seconds] = RED
                pixels[pixel_reverse] = CYAN

                if DEBUG_MODE:
                    print("MINUTE_HOUR_REVERSE")
            elif pixel_reverse == pixel_minutes:
                # If only minute is on the reverse pixel
                pixels[pixel_seconds] = RED
                pixels[pixel_reverse] = BLUE

                if DEBUG_MODE:
                    print("MINUTE_REVERSE")
            elif pixel_reverse == pixel_hours:
                # If only hour is on the reverse pixel
                pixels[pixel_seconds] = RED
                pixels[pixel_reverse] = GREEN

                if DEBUG_MODE:
                    print("HOUR_REVERSE")
            else:
                # In any other case
                pixels[pixel_seconds] = RED
                if pixel_reverse == 0:
                    pixels[pixel_reverse] = ORANGE
                elif SHOW_QUARTER_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = QUARTER_MARKER
                elif not SHOW_QUARTER_MARKER and SHOW_HOUR_MARKER and pixel_reverse in \
                        (QUARTER_MARKER_15, QUARTER_MARKER_30, QUARTER_MARKER_45):
                    pixels[pixel_reverse] = HOUR_MARKER
                elif SHOW_HOUR_MARKER and pixel_reverse in \
                        (HOUR_MARKER_1, HOUR_MARKER_2, HOUR_MARKER_4, HOUR_MARKER_5,
                         HOUR_MARKER_7, HOUR_MARKER_8, HOUR_MARKER_10, HOUR_MARKER_11):
                    pixels[pixel_reverse] = HOUR_MARKER
                else:
                    pixels[pixel_reverse] = LED_OFF

                if DEBUG_MODE:
                    print("ELSE CASE")

            if pixels:
                pixels.show()
            time.sleep(0.05)

            #if pixel_seconds == 59:
            #    INIT = True
        except AttributeError:
            print("AttributeError")
            time.sleep(1)
        except KeyboardInterrupt:
            # Terminate the script and switch off all leds
            print("Press Ctrl-C to terminate while statement")
            pixels.deinit()
            break
