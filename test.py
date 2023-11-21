from pixel_switcher import PixelSwitcher
import time

pixel = 5

PS = PixelSwitcher("COM3")
time.sleep(2)

PS.turn_on_pixel(pixel)
#
# time.sleep(2)
#
# PS.close()
