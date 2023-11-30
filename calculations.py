import pandas as pd
import time
import numpy as np
import math
import os
import matplotlib.pyplot as plt

class Calculations:
    def __init__(self):
        self.reset_data()

    def reset_data(self):
        self.time_values = []
        self.voltage_values = []
        self.current_values = []
        self.luminance_values = []
        self.relative_luminance =[]
        self.start_luminance = None
        self.start_time = None
        
    def get_calibration(self, path='C:\\Users\\VUTMI\\Desktop\\LIFEsetupodalykai\\Lifetime\\', material=None):
        self.calibration = pd.read_csv(f'{path}Calibrations.txt', sep='\t')
        self.spectrum = pd.read_csv(f'{path}Spectra\\{material}.txt', sep='\t')
        self.calibrations = pd.merge(self.calibration, self.spectrum, on='Wavelength', how='outer').fillna(0)
        return self.calibrations
        
    def calculate_luminance(self, current, pixel_area, distance_OLED_PD, r_PD=0.005):
        lum = (683 * current * np.sum(self.calibrations['Spectrum']*self.calibrations['Photopic interpolated']) / 3.14 / pixel_area
               / np.sum(self.calibrations['Spectrum']*self.calibrations['PD interpolated'])) / math.sin(math.atan(r_PD/distance_OLED_PD)) ** 2
        if self.start_luminance is None:
            self.start_luminance = lum
            print(f"Start luminance = {self.start_luminance}")
            print("Warning about upcoming user warning: since first time point is 0, it is normal to get logscale errors.")
        self.relative_luminance.append(lum/self.start_luminance)
        return lum
        
    def get_time(self):
        if self.start_time is None:
            self.start_time = time.time()
        elapsed_time = time.time() - self.start_time
        return elapsed_time 
    
    def form_output(self):
        self.data = {
            'time': self.time_values,
            'PD current': self.current_values,
            'Luminance': self.luminance_values,
            'Relative Brightness': self.relative_luminance,
            'OLED voltage': self.voltage_values
        }
        self.data = pd.DataFrame(self.data)
        
    def save_file(self, save_path, device_name, pixel, OLED_current):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self.data.to_csv(os.path.join(save_path, f'{device_name} p{pixel} {OLED_current}A {self.start_luminance}nits.txt'), sep='\t', index=False)
        print("Results saved")

    def make_plots(self, title="Pixel 1"):
        # Create a real-time updating plot
        plt.ion()  # Turn on interactive mode
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1)
        self.fig.suptitle(title, fontsize=16)
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Luminance (cd/m^2)")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Luminance (cd/m^2)")
        self.ax3.set_xlabel("Time (s)")
        self.ax3.set_ylabel("Luminance (cd/m^2)")
    
    def update_plots(self):
        self.ax1.clear()
        self.ax1.plot(self.time_values, self.luminance_values)
        # self.ax1.set_xlabel("Time (s)")
        # self.ax1.set_ylabel("Luminance (cd/m^2)")
        self.ax1.grid(True)
        self.ax1.relim()
        self.ax1.autoscale_view()

        self.ax2.clear()
        self.ax2.plot(self.time_values, self.luminance_values)
        # self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Luminance (cd/m^2)")
        self.ax2.set_xscale('log')
        self.ax2.grid(True)
        self.ax2.relim()
        self.ax2.autoscale_view()

        self.ax3.clear()
        self.ax3.plot(self.time_values, self.luminance_values)
        self.ax3.set_xlabel("Time (s)")
        # self.ax3.set_ylabel("Luminance (cd/m^2)")
        self.ax3.set_xscale('log')
        self.ax3.set_yscale('log')
        self.ax3.grid(True)
        self.ax3.relim()
        self.ax3.autoscale_view()

        plt.pause(0.1)
        time.sleep(0.1)

        