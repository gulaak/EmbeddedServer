import Adafruit_BBIO.ADC as analog

class ADC:
    def __init__(self,adc_num):
        analog.setup()
        self.pin = adc_num

    def read(self):
        return analog.read(self.pin)


