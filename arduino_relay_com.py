import serial
import time


class ArduinoRelayCom:

    def __init__(self, port='COM3'):
        self.arduino = serial.Serial(port=port,   baudrate=9600, timeout=2)
        time.sleep(3)
        print("Connected to Arduino")

    def write_read(self, x:str) -> str:
        self.write(x)
        time.sleep(0.05)
        data = self.read_data()
        return data
    
    def write(self, x:str) -> None:
        self.arduino.write(bytes(str(x), 'utf-8'))
    
    def read_data(self) -> str:
        # time_start = time.time()
        data = self.arduino.readline().decode('utf-8').strip()
        # print(time.time() - time_start)
        # print(f"Read first time: {data}")
        # Wait for additional data if the first read was empty
        while not data:
            time.sleep(0.1)
            data = self.arduino.readline().decode('utf-8').strip()
            print("waiting for data")
        if len(data) == 0:
            print("No data received")
        if "Pin States:" in data:
            data = self.parse_pin_states(data)
        return data

    def parse_pin_states(self, data):
        pin_states = data.replace('\r\n','').split(':')[1].split(',')
        pin_states.pop(-1)
        return [not bool(int(x)) for x in pin_states] 

    def turn_all_on(self):
        return self.write_read("0;0")

    def turn_all_off(self):
        return self.write_read("0;1")

    def turn_on_pin(self, pin, get_return=True):
        resp = None
        if get_return:
            resp = self.write_read(f"{pin};0")
        else:
            self.write(f"{pin};0")
        return resp

    def turn_off_pin(self, pin, get_return=True):
        resp = None
        if get_return:
            resp = self.write_read(f"{pin};1")
        else:
            self.write(f"{pin};1")
        return resp

    def get_pin_states(self) -> str:
        return self.write_read("99;0")
    
    def close(self):
        self.arduino.close()

if __name__ == "__main__":
    pass
    # relay = ArduinoRelayCom('COM12')
    # print(relay.get_pin_states())
    # time.sleep(2)
    # relay.turn_on_pin(4)
    # time.sleep(1)
    # relay.turn_all_off()
    #
    # relay.close()

