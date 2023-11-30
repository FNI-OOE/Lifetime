from pixel_switcher import PixelSwitcher
from calculations import Calculations
from U2722A import SMU
import matplotlib.pyplot as plt
import time
# import pyvisa

# ******************** Settings ********************
OLED_name = "TEST"  #pavadinimas seivinimui, jei pavadinimas sutaps, saugos ant virsaus
pixels = [5, 6]  # [1, 2, 3, 4, 5, 6] gali buti bet kokia eile
OLED_currents = [1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4]  #A, turi atititikti pixeliu skaiciu seka
pixel_area = (2 * 0.001)**2  # (mm / 1000)^2 = m^2
distance_OLED_PD = 10 / 100  # cm / 100 = m
spectrum = "DMeCzIPN Yb"
device_name = "test_sample2"
save_path = f"C:\\Users\\VUTMI\\Desktop\\LIFEsetupodalykai\\test save\\{OLED_name}"
# **************************************************

PS = PixelSwitcher("COM12")
Calc = Calculations()
SMU = SMU()
time.sleep(2)  # delete after PixelSwitcher update
calibrations = Calc.get_calibration(path='C:\\Users\\VUTMI\\Desktop\\LIFEsetupodalykai\\Lifetime\\', material=spectrum)
SMU.configure(nplc=100, v_limit=12)

for i, pixel in enumerate(pixels):
    try:
        print(f"Measuring pixel {pixel}")
        PS.turn_on_pixel(pixel)
        dark_current = SMU.measure_dark_current()
        Calc.make_plots(title=f"Pixel {pixel}")
        SMU.set_OLED_current(OLED_currents[i])
        SMU.output_on(channels = [SMU.OLED_channel])
        measurement_done = False
        while not measurement_done:
            Calc.current_values.append(SMU.measure_PD_current() - dark_current)
            Calc.voltage_values.append(SMU.measure_OLED_voltage())
            Calc.time_values.append(Calc.get_time())
            Calc.luminance_values.append(Calc.calculate_luminance(Calc.current_values[-1], pixel_area=pixel_area, distance_OLED_PD=distance_OLED_PD))
            Calc.update_plots()
            if Calc.luminance_values[-1] < 0.45*Calc.start_luminance:
                measurement_done = True
                print(f"Final luminance = {Calc.luminance_values[-1]}")
        print(f"Measurements done for pixel {pixel}")
        SMU.output_off(channels=[SMU.OLED_channel])

    # except pyvisa.VisaIOError as e:
    #     print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Executes if keyboard aborted
        Calc.form_output()
        Calc.save_file(save_path=save_path, device_name=device_name, pixel=pixel, OLED_current=OLED_currents[i])
        PS.close()
        SMU.measure_PD_current()  # Seems to fix the issue of not disconnecting properly
        SMU.disconnect()

    Calc.form_output()
    Calc.save_file(save_path=save_path, device_name=device_name, pixel=pixel, OLED_current=OLED_currents[i])
    # Keep the plot open until manually closed by the user
    plt.ioff()
    plt.draw()
    Calc.reset_data()

PS.close()
SMU.measure_PD_current()  # Seems to fix the issue of not disconnecting properly
SMU.disconnect()
plt.show()
