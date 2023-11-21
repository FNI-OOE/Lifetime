import numpy as np
import pyvisa as visa
import matplotlib.pyplot as plt
import time
import pandas as pd
import math
import os
from pixel_switcher import PixelSwitcher

OLED_current = 1e-3
pixel = 5
NPLC = 100
pixel_area = (2 * 0.001)**2  # (mm / 1000)^2 = m^2
distance_OLED_PD = 10 / 100  # cm / 100 = m
spectrum = "DMeCzIPN Yb"
device_name = "test_sample"

resource_string = 'USB::0x0957::0x4118::MY61150002::0::INSTR'
PS = PixelSwitcher("COM3")
time.sleep(2)

# Set the desired voltage and current ranges
# voltage_range = 2
# current_range = '1uA'

# EQE stuff
Calibrations = pd.read_csv('Calibrations.txt', sep='\t')
Spectrum = pd.read_csv(f'Spectra\\{spectrum}.txt', sep='\t')
Calibrations = pd.merge(Calibrations, Spectrum, on='Wavelength', how='outer').fillna(0)
r_PD = 0.005  # m

try:
    # Create a VISA resource manager and open a connection to the instrument
    print("Attempting connection to Keysight...")
    rm = visa.ResourceManager()
    instrument = rm.open_resource(resource_string, timeout=10e3)
    PS.turn_on_pixel(pixel)
    time.sleep(2)

    # Photodiode part
    instrument.write(f"SOUR:VOLT:RANG R2V, (@1)")
    instrument.write(f"SOUR:CURR:RANG R1uA, (@1)")
    instrument.write(f"SENSe:CURRent:NPLCycles {NPLC}, (@1)")
    instrument.write("SOUR:VOLT 0V, (@1)")
    instrument.write("OUTP ON, (@1)")

    # OLED part
    instrument.write(f"SOUR:VOLT:RANG R20V, (@2)")
    instrument.write(f"SOUR:CURR:RANG R1mA, (@2)")
    instrument.write(f"SOUR:VOLT:LIM 12V, (@2)")
    instrument.write("SOUR:CURR 0mA, (@2)")
    instrument.write("OUTP ON, (@2)")

    # Initialize time and data lists for plotting
    times = []
    current_values = []
    dark_current = []
    luminance_values = []

    print("Measuring dark current")
    for idx in range(5):
        dark_current.append(float(instrument.query("MEAS:CURR? (@1)")))
        time.sleep(2.5)
    print(f"Dark current = {dark_current}")
    dark_current = np.mean(dark_current)
    print(f"Dark current = {dark_current}")

    # Create a real-time updating plot
    plt.ion()  # Turn on interactive mode
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Luminance (cd/m^2)")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Luminance (cd/m^2)")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Luminance (cd/m^2)")

    start_time = time.time()
    instrument.write(f"SOUR:CURR {OLED_current}, (@2)")
    start_luminance = []
    first_measurement = True
    measurement_done = False
    while not measurement_done:
        current = float(instrument.query("MEAS:CURR? (@1)")) - dark_current
        voltage = float(instrument.query("MEAS:VOLT? (@1)"))

        current_values.append(current)
        times.append(time.time() - start_time)
        lum = (683 * current * np.sum(Calibrations['Spectrum']*Calibrations['Photopic interpolated']) / 3.14 / pixel_area
               / np.sum(Calibrations['Spectrum']*Calibrations['PD interpolated'])) / math.sin(math.atan(r_PD/distance_OLED_PD)) ** 2
        luminance_values.append(lum)

        if first_measurement:
            start_luminance = lum
            first_measurement = False

        # Update the plot
        ax1.clear()
        ax1.plot(times, luminance_values)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Luminance (cd/m^2)")
        ax2.grid(True)
        ax1.relim()
        ax1.autoscale_view()

        ax2.clear()
        ax2.plot(times, luminance_values)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Luminance (cd/m^2)")
        ax2.set_xscale('log')
        ax2.grid(True)
        ax2.relim()
        ax2.autoscale_view()

        ax3.clear()
        ax3.plot(times, luminance_values)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Luminance (cd/m^2)")
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        ax3.grid(True)
        ax3.relim()
        ax3.autoscale_view()

        plt.pause(0.01)
        time.sleep(0.1)
        if lum < 0.45*start_luminance:
            measurement_done = True

    print("Measurements done")
    time.sleep(2)
    # # Turn off the output after measurement is done
    # instrument.write("OUTP OFF, (@1)")
    # instrument.write("OUTP OFF, (@2)")
    #
    # # Close the connection to the instrument
    # instrument.close()

except visa.VisaIOError as e:
    print(f"An error occurred: {e}")

finally:
    time.sleep(2)
    instrument.write("OUTP OFF, (@1)")
    instrument.write("OUTP OFF, (@2)")
    instrument.close()
    PS.close()
    rm.close()

# Save results to txt
data = {
    'time': times,
    'PD current': current_values,
    'Luminance': luminance_values
}

# Create a DataFrame using the dictionary
df = pd.DataFrame(data)

# Save the DataFrame as a text file with tab separation
if not os.path.exists('Lifetime measurements'):
    os.makedirs('Lifetime measurements')
df.to_csv(f'Lifetime measurements\\{device_name} p{pixel} {OLED_current}A '
          f'{start_luminance}nits.txt', sep='\t', index=False)

# Keep the plot open until manually closed by the user
plt.ioff()
plt.show()
