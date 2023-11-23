import numpy as np
import pyvisa as visa
import matplotlib.pyplot as plt
import time
import pandas as pd
import math

# GP: script is in early test phase, still messy, some comments might be misleading or some lines not working as intended (23-11-13)
# Define the USB device identifier (VISA resource string)
resource_string = 'USB::0x0957::0x4118::MY61150002::0::INSTR'

# Set the desired voltage and current ranges
voltage_range = 2
current_range = '1uA'
measurement_interval = 3  # Time interval between measurements (in seconds)
measurement_duration = 200  # Total measurement duration (in seconds)
NPLC = 100

OLEDIstart = 1e-6
OLEDIend = 1e-3
npoints = math.floor(measurement_duration/measurement_interval)
Drive_current = np.logspace(np.log10(OLEDIstart), np.log10(OLEDIend), npoints)

# EQE stuff
Calibrations = pd.read_csv('Calibrations.txt', sep='\t')
Spectrum = pd.read_csv('Spectra\\DMeCzIPN Yb.txt', sep='\t')
Calibrations = pd.merge(Calibrations, Spectrum, on='Wavelength', how='outer').fillna(0)
pixel_area = (2 * 0.001)**2  # (mm / 1000)^2 = m^2
distance_OLED_PD = 20 / 100  # cm / 100 = m
r_PD = 0.005 # m


try:
    # Create a VISA resource manager and open a connection to the instrument
    rm = visa.ResourceManager()
    instrument = rm.open_resource(resource_string, timeout=measurement_interval*2000)

    # Photodiode part
    instrument.write(f"SOUR:VOLT:RANG R{voltage_range}V, (@1)")
    instrument.write(f"SOUR:CURR:RANG R{current_range}, (@1)")
    # instrument.write(f"SOUR:CURR:LIM {current_range}, (@1)")
    instrument.write(f"SENSe:CURRent:NPLCycles {NPLC}, (@1)")
    instrument.write("SOUR:VOLT 0V, (@1)")
    instrument.write("OUTP ON, (@1)")  # Turn on the output

    # OLED part
    instrument.write(f"SOUR:VOLT:RANG R20V, (@2)")
    instrument.write(f"SOUR:CURR:RANG R1mA, (@2)")
    instrument.write(f"SOUR:VOLT:LIM 12V, (@2)")
    instrument.write("SOUR:CURR 0mA, (@2)")
    instrument.write("OUTP ON, (@2)")  # Turn on the output

    # Initialize time and data lists for plotting
    times = []
    current_values = []
    dark_current = []
    luminance_values = []

    print("Measurusing dark current")
    for idx in range(3):
        dark_current.append(float(instrument.query("MEAS:CURR? (@1)")))
        time.sleep(measurement_interval)
    print(f"Dark current = {dark_current}")
    dark_current = np.mean(dark_current)
    print(f"Dark current = {dark_current}")

    # Create a real-time updating plot
    plt.ion()  # Turn on interactive mode
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("PD current (A)")
    ax1.set_xlim(0, measurement_duration)
    # ax.legend()
    ax2.set_xlabel("Oled current (A)")
    ax2.set_ylabel("PD current (A)")
    ax3.set_xlabel("Oled current (A)")
    ax3.set_ylabel("Luminance (cd/m^2)")

    start_time = time.time()
    for idx in range(npoints):
    # while (time.time() - start_time) < measurement_duration:

        instrument.write(f"SOUR:CURR {Drive_current[idx]}, (@2)")
        # time.sleep(0.1)

        # Query the instrument for the current value
        current = float(instrument.query("MEAS:CURR? (@1)")) - dark_current
        print(f"Current = {current}")
        voltage = float(instrument.query("MEAS:VOLT? (@1)"))
        print(f"Voltage = {voltage}")

        # Append data to the lists
        current_values.append(current)
        times.append(time.time() - start_time)
        lum = (683 * current * np.sum(Calibrations['Spectrum']*Calibrations['Photopic interpolated']) / 3.14 / pixel_area
               / np.sum(Calibrations['Spectrum']*Calibrations['PD interpolated'])) / math.sin(math.atan(r_PD/distance_OLED_PD)) ** 2
        luminance_values.append(lum)

        # Update the plot
        ax1.clear()
        ax1.plot(times, current_values, label="Current vs. Time")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("PD current (A)")
        ax1.relim()
        ax1.autoscale_view()
        # ax.legend()

        ax2.clear()
        ax2.plot(Drive_current[:idx+1], current_values, label="Responsivity plot")
        ax2.set_xlabel("Oled current (A)")
        ax2.set_ylabel("PD current (A)")
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.grid(True)
        ax2.relim()
        ax2.autoscale_view()

        ax3.clear()
        ax3.plot(Drive_current[:idx + 1], luminance_values, label="Luminance plot")
        ax3.set_xlabel("Oled current (A)")
        ax3.set_ylabel("Luminance (cd/m^2)")
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        ax3.grid(True)
        ax3.relim()
        ax3.autoscale_view()

        plt.pause(0.01)

        # Sleep for the measurement interval
        time.sleep(0.1)

    print("Measurements done")
    # Turn off the output after measurement is done
    instrument.write("OUTP OFF, (@1)")
    instrument.write("OUTP OFF, (@2)")

    # Close the connection to the instrument
    instrument.close()

except visa.VisaIOError as e:
    print(f"An error occurred: {e}")

finally:
    # Close the VISA resource manager
    rm.close()

# Save results to txt
data = {
    'OLED current': Drive_current,
    'time': times,
    'PD current': current_values,
    'Luminance': luminance_values
}

# Create a DataFrame using the dictionary
df = pd.DataFrame(data)

# Save the DataFrame as a text file with tab separation
df.to_csv('output.txt', sep='\t', index=False)

# Keep the plot open until manually closed by the user
plt.ioff()
plt.show()
