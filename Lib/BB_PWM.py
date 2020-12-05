import Adafruit_BBIO.PWM as pulse


class PWM:
    def __init__(self,pwm_num,duty_cycle=50,freq=2000,polarity=0):
        if pwm_num == "1A":
            self.pin = "P9_14"
        elif pwm_num == "1B":
            self.pin = "P9_16"

        elif pwm_num == "2A":
            self.pin = "P8_19"
        elif pwm_num == "2B":
            self.pin = "P8_13"

        pulse.start(self.pin,duty_cycle,freq,polarity)


    def set_duty(self,duty_cycle):
        pulse.set_duty_cycle(self.pin,duty_cycle)

    def set_frequency(self,freq):
        pulse.set_duty_cycle(self.pin,freq)

