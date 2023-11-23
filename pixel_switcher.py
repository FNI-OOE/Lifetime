from arduino_relay_com import ArduinoRelayCom

class PixelSwitcher:

    def __init__(self, port):
        self.relay = ArduinoRelayCom(port)

    def turn_off(self):
        return self.relay.turn_all_off()

    def turn_on_pixel(self, pixel_number):
        self.turn_off()
        if pixel_number in [1,2,3]:
            self.relay.turn_on_pin(pixel_number)
            self.relay.turn_on_pin(7)
            state = self.relay.turn_on_pin(8)
        elif pixel_number in [4,5,6]:
            self.relay.turn_on_pin(pixel_number)
            self.relay.turn_on_pin(9)
            state = self.relay.turn_on_pin(10)
        return state

    def close(self):
        self.turn_off()
        self.relay.close()
    
if __name__ == "__main__":
    pass
    # ps = PixelSwitcher("COM4")