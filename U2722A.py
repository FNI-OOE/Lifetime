import pyvisa
import time
import numpy as np

class SMU:
    OLED_channel = None
    PD_channel = None
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.instrument = None
        
    def connect(self, resource_string='USB::0x0957::0x4118::MY61150002::0::INSTR', timeout=2000):
        try:
            print("Attempting connection to Keysight U2722A...")
            self.instrument = self.rm.open_resource(resource_string, timeout=int(timeout))
            print("Instrument identity: ", self.instrument.query('*IDN?'))
        except pyvisa.VisaIOError as e:
            print(f"Connection failed with error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
                      
    def setup_PD(self, channel=1, NPLC=100): 
        self.PD_channel = channel
        # Ranges should be as low as possible (2V, 1uA), because the output expected is much lower
        self.instrument.write(f"SOUR:VOLT:RANG R2V, (@{channel})")
        self.instrument.write(f"SOUR:CURR:RANG R1uA, (@{channel})")
        # NPLC should be high (~100 is ok), because the measurement is noisy otherwise.
        self.instrument.write(f"SENSe:CURRent:NPLCycles {NPLC}, (@{channel})")
        self.instrument.write(f"SOUR:VOLT 0V, (@{channel})")
        
    def setup_OLED(self, channel=2, voltage_limit=12): 
        self.OLED_channel = channel
        self.instrument.write(f"SOUR:VOLT:RANG R20V, (@{channel})")
        if 0 <= voltage_limit <= 20:
            self.instrument.write(f"SOUR:VOLT:LIM {voltage_limit}V, (@{channel})")
        else:
            print("Warning: invalid voltage limit for OLED")
            
        # self.OLED_current_range = None
        # self.OLED_current = None
        
    def measure_PD_current(self):
        result = self.instrument.query(f"MEAS:CURR? (@{self.PD_channel})")
        return float(result)
    
    def measure_OLED_voltage(self):
        result = self.instrument.query(f"MEAS:VOLT? (@{self.OLED_channel})")
        return float(result)
    
    def set_OLED_current(self, value):
        # Keysight should correctly set range based on value. Although it might not work.
        self.instrument.write(f"SOUR:CURR:RANG R{value}, (@{self.OLED_channel})")
        self.instrument.write(f"SOUR:CURR {value}, (@{self.OLED_channel})")
        
    def measure_dark_current(self, npoints=5):
        print("Measuring dark current")
        dark_current = []
        for idx in range(npoints):
            dark_current.append(self.measure_PD_current())
            time.sleep(2.5)
        print(f"Dark current = {dark_current}")
        dark_current = np.mean(dark_current)
        print(f"Dark current = {dark_current}")
        return dark_current

    def output_on(self, channels=[1,2]):
        for ch in channels:
            self.instrument.write(f"OUTP ON, (@{ch})")
            print(f"Channel {ch} turned on")
            
    def output_off(self, channels=[1,2]):
        for ch in channels:
            self.instrument.write(f"OUTP OFF, (@{ch})")
            print(f"Channel {ch} turned off")
    
    def disconnect(self):
        time.sleep(2)  # This is to allow for measurement completion in unplanned shutdowns. Not sure if necessary.
        self.output_off(channels=[self.OLED_channel, self.PD_channel])
        self.instrument.close()
        self.rm.close()
        print("Keysight U2722A disconnected")

