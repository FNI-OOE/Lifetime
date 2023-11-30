from U2722A import SMU
from pixel_switcher import PixelSwitcher
import time

SMU = SMU()
PS = PixelSwitcher("COM12")
SMU.connect()
# SMU.setup_PD(channel=1, NPLC=100)
SMU.setup_OLED()
# SMU.output_on(channels = [SMU.PD_channel])
# res = SMU.measure_PD_current()
# print(res)
# dark_current = SMU.measure_dark_current(npoints=3)
# print(dark_current)
# print(res-dark_current)
PS.turn_on_pixel(6)
SMU.set_OLED_current(1e-3)
SMU.output_on([SMU.OLED_channel])
time.sleep(3)
PS.close()
SMU.disconnect()