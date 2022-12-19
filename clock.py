import board
import neopixel
import time
import RPi.GPIO as GPIO
import os


######## GLOBAL VARIABLES ########

# Set absolute amount of LEDs of the ring
absolute_led = int(60)

# Debugging on/off
debug_mode = False

# Show markers on/off
show_hour_marker = True
show_quarter_marker = True

# Set Hour Markers depending on LED count
hour_marker_0 = 0
hour_marker_1 = int(absolute_led / 12)
hour_marker_2 = int(2 * absolute_led / 12)
hour_marker_3 = int(3 * absolute_led / 12)
hour_marker_4 = int(4 * absolute_led / 12)
hour_marker_5 = int(5 * absolute_led / 12)
hour_marker_6 = int(6 * absolute_led / 12)
hour_marker_7 = int(7 * absolute_led / 12)
hour_marker_8 = int(8 * absolute_led / 12)
hour_marker_9 = int(9 * absolute_led / 12)
hour_marker_10 = int(10 * absolute_led / 12)
hour_marker_11 = int(11 * absolute_led / 12)

# Set Quarter Markers depending on LED count
quarter_marker_15 = int(absolute_led / 4)
quarter_marker_30 = int(2 * absolute_led / 4)
quarter_marker_45 = int(3 * absolute_led / 4)

# Set colors
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
cyan = (0, 255, 255)
blue = (0, 0, 255)
violett = (140, 0, 120)
quarter_marker = (70, 60, 60)
hour_marker = (7, 5, 5)
led_off = (0, 0, 0)
orange = (140, 55, 0)
bright_white = (255, 255, 255)

# Initialize NeoPixels
pixels = neopixel.NeoPixel(board.D18, absolute_led, bpp=3, brightness=0.5, auto_write=False, pixel_order="GRB")

# Initialize GPIOs für Buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

##################################


def get_current_time(param):
    # Return current seconds, minutes or hours
    if param == "hour":
        return int(time.strftime("%I"))
    elif param == "minute":
        return int(time.strftime("%M"))
    elif param == "second":
        return int(time.strftime("%S"))


def init_clock():
    # Initialize the clock
    pixel_hours, pixel_minutes, pixel_seconds = get_time()

    # Clear all pixels
    pixels.fill((0, 0, 0))

    # Set marker pixels
    pixels[hour_marker_0] = orange
    if show_quarter_marker:
        # Make the quarter marker brighter than the hour marker
        pixels[quarter_marker_15] = quarter_marker
        pixels[quarter_marker_30] = quarter_marker
        pixels[quarter_marker_45] = quarter_marker
    elif show_hour_marker and not show_quarter_marker:
        # Make the quarter marker and the hour marker to the same brightness
        pixels[quarter_marker_15] = hour_marker
        pixels[quarter_marker_30] = hour_marker
        pixels[quarter_marker_45] = hour_marker

    if show_hour_marker:
        pixels[hour_marker_1] = hour_marker
        pixels[hour_marker_2] = hour_marker
        pixels[hour_marker_4] = hour_marker
        pixels[hour_marker_5] = hour_marker
        pixels[hour_marker_7] = hour_marker
        pixels[hour_marker_8] = hour_marker
        pixels[hour_marker_10] = hour_marker
        pixels[hour_marker_11] = hour_marker

    # Set pixels for second, minute and hour
    if pixel_seconds == pixel_hours and pixel_seconds == pixel_minutes:
        pixels[pixel_seconds] = bright_white
    elif pixel_hours == pixel_minutes:
        pixels[pixel_minutes] = cyan
        pixels[pixel_seconds] = red
    else:
        pixels[pixel_hours] = green
        pixels[pixel_minutes] = blue
        pixels[pixel_seconds] = red

    pixels.show()


def get_time():
    # Get current local time
    #global second

    hour = get_current_time("hour")
    if hour == 12:
        hour = 0
    minute = get_current_time("minute")
    second = get_current_time("second")

    pixel_hours = int((hour * absolute_led / 12) + ((absolute_led / 12) * minute / 60))
    pixel_minutes = int(minute * absolute_led / 60)
    pixel_seconds = int(second * absolute_led / 60)

    return pixel_hours, pixel_minutes, pixel_seconds


def switch_clock_mode(channel):
    # Switch between the different clock modes and set only quarter marker, only hour marker, quarter and hour marker or no marker
    global show_hour_marker
    global show_quarter_marker

    if show_hour_marker and show_quarter_marker:
        show_quarter_marker = False
        show_hour_marker = True
        if debug_mode:
            print("Clock mode changed - ClockMode 1")
    elif show_hour_marker and not show_quarter_marker:
        show_hour_marker = False
        show_quarter_marker = True
        if debug_mode:
            print("Clock mode changed - ClockMode 2")
    elif show_quarter_marker and not show_hour_marker:
        show_quarter_marker = False
        show_hour_marker = False
        if debug_mode:
            print("Clock mode changed - ClockMode 3")
    elif not show_quarter_marker and not show_hour_marker:
        show_hour_marker = True
        show_quarter_marker = True
        if debug_mode:
            print("Clock mode changed - ClockMode 4")

    init_clock()


def system_shutdown(channel):
    # Shutdown system
    print("!!!! SYSTEM IS GOING TO SHUTDOWN !!!!")
    pixels.deinit()
    os.system("sudo poweroff")
    time.sleep(1)


if __name__ == "__main__":
    #second = 0
    init = True

    init_clock()

    # Switch clock mode to show quarter marks or not
    GPIO.add_event_detect(23, GPIO.RISING, callback=switch_clock_mode, bouncetime=400)

    # Shutdown the system
    GPIO.add_event_detect(20, GPIO.RISING, callback=system_shutdown, bouncetime=400)

    while True:
        try:
            pixel_hours, pixel_minutes, pixel_seconds = get_time()

            if pixel_seconds == 0 and init:
                # Run init only once per minute
                # new comment
                init_clock()
                init = False

                if debug_mode:
                    print("INIT")

            # Define the pixel in front of the current pixel
            if pixel_seconds == 0:
                pixel_reverse = absolute_led - 1
            else:
                pixel_reverse = pixel_seconds - 1

            if pixel_seconds == absolute_led - 1:
                # Reset counter for Init
                init = False

            if pixel_seconds == pixel_hours and pixel_seconds == pixel_minutes:
                # If second, minute and hour are on the same pixel
                pixels[pixel_seconds] = bright_white
                if show_quarter_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = quarter_marker
                elif not show_quarter_marker and show_hour_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = hour_marker
                elif show_hour_marker and \
                        (pixel_reverse == hour_marker_1 or
                         pixel_reverse == hour_marker_2 or
                         pixel_reverse == hour_marker_4 or
                         pixel_reverse == hour_marker_5 or
                         pixel_reverse == hour_marker_7 or
                         pixel_reverse == hour_marker_8 or
                         pixel_reverse == hour_marker_10 or
                         pixel_reverse == hour_marker_11):
                    pixels[pixel_reverse] = hour_marker
                elif pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = cyan
                elif pixel_reverse == 0 and pixel_minutes > 0:
                    pixels[pixel_reverse] = orange
                else:
                    pixels[pixel_reverse] = led_off

                if debug_mode:
                    print("SECOND/MINUTE/HOUR")
            elif pixel_seconds == pixel_minutes:
                # If second and minute are on the same pixel
                pixels[pixel_seconds] = violett
                if show_quarter_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = quarter_marker
                elif not show_quarter_marker and show_hour_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = hour_marker
                elif show_hour_marker and \
                        (pixel_reverse == hour_marker_1 or
                         pixel_reverse == hour_marker_2 or
                         pixel_reverse == hour_marker_4 or
                         pixel_reverse == hour_marker_5 or
                         pixel_reverse == hour_marker_7 or
                         pixel_reverse == hour_marker_8 or
                         pixel_reverse == hour_marker_10 or
                         pixel_reverse == hour_marker_11):
                    pixels[pixel_reverse] = hour_marker
                elif pixel_reverse == pixel_hours:
                    pixels[pixel_reverse] = green
                elif pixel_reverse == 0 and not pixel_reverse == pixel_hours:
                    pixels[pixel_reverse] = orange
                else:
                    pixels[pixel_reverse] = led_off

                if debug_mode:
                    print("MINUTE")
            elif pixel_seconds == pixel_hours:
                # If second and hour are on the same pixel
                pixels[pixel_seconds] = yellow
                if show_quarter_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = quarter_marker
                elif not show_quarter_marker and show_hour_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = hour_marker
                elif show_hour_marker and \
                        (pixel_reverse == hour_marker_1 or
                         pixel_reverse == hour_marker_2 or
                         pixel_reverse == hour_marker_4 or
                         pixel_reverse == hour_marker_5 or
                         pixel_reverse == hour_marker_7 or
                         pixel_reverse == hour_marker_8 or
                         pixel_reverse == hour_marker_10 or
                         pixel_reverse == hour_marker_11):
                    pixels[pixel_reverse] = hour_marker
                elif pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = blue
                elif pixel_reverse == 0 and not pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = orange
                else:
                    pixels[pixel_reverse] = led_off

                if debug_mode:
                    print("HOUR")
            elif pixel_minutes == pixel_hours and pixel_seconds != pixel_minutes:
                # If minute and hour only are on the same pixel
                pixels[pixel_seconds] = red
                if show_quarter_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = quarter_marker
                elif not show_quarter_marker and show_hour_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = hour_marker
                elif show_hour_marker and \
                        (pixel_reverse == hour_marker_1 or
                         pixel_reverse == hour_marker_2 or
                         pixel_reverse == hour_marker_4 or
                         pixel_reverse == hour_marker_5 or
                         pixel_reverse == hour_marker_7 or
                         pixel_reverse == hour_marker_8 or
                         pixel_reverse == hour_marker_10 or
                         pixel_reverse == hour_marker_11):
                    pixels[pixel_reverse] = hour_marker
                elif pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = cyan
                elif pixel_reverse == 0 and not pixel_reverse == pixel_minutes:
                    pixels[pixel_reverse] = orange
                else:
                    pixels[pixel_reverse] = led_off

                if debug_mode:
                    print("MINUTE/HOUR")
            elif pixel_minutes == pixel_hours and pixel_reverse == pixel_minutes and pixel_reverse == pixel_hours:
                # If hour and minute are on the reverse pixel
                pixels[pixel_seconds] = red
                pixels[pixel_reverse] = cyan

                if debug_mode:
                    print("MINUTE_HOUR_REVERSE")
            elif pixel_reverse == pixel_minutes:
                # If only minute is on the reverse pixel
                pixels[pixel_seconds] = red
                pixels[pixel_reverse] = blue

                if debug_mode:
                    print("MINUTE_REVERSE")
            elif pixel_reverse == pixel_hours:
                # If only hour is on the reverse pixel
                pixels[pixel_seconds] = red
                pixels[pixel_reverse] = green

                if debug_mode:
                    print("HOUR_REVERSE")
            else:
                # In any other case
                pixels[pixel_seconds] = red
                if show_quarter_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = quarter_marker
                elif not show_quarter_marker and show_hour_marker and \
                        (pixel_reverse == quarter_marker_15 or
                         pixel_reverse == quarter_marker_30 or
                         pixel_reverse == quarter_marker_45):
                    pixels[pixel_reverse] = hour_marker
                elif show_hour_marker and \
                        (pixel_reverse == hour_marker_1 or
                         pixel_reverse == hour_marker_2 or
                         pixel_reverse == hour_marker_4 or
                         pixel_reverse == hour_marker_5 or
                         pixel_reverse == hour_marker_7 or
                         pixel_reverse == hour_marker_8 or
                         pixel_reverse == hour_marker_10 or
                         pixel_reverse == hour_marker_11):
                    pixels[pixel_reverse] = hour_marker
                elif pixel_reverse == 0:
                    pixels[pixel_reverse] = orange
                else:
                    pixels[pixel_reverse] = led_off

            if pixels:
                pixels.show()
            time.sleep(0.05)
        except AttributeError:
            print("AttributeError")
            time.sleep(1)
        except KeyboardInterrupt:
            # Terminate the script and switch off all leds
            print("Press Ctrl-C to terminate while statement")
            pixels.deinit()
            break
