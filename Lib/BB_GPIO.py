import  Adafruit_BBIO.GPIO as gp
# Table Translation

table = { 49: 'P9_23', 60: 'P9_12', 117: 'P9_25', 115: 'P9_27', 112: 'P9_30', 20: 'P9_41' ,
          66: 'P8_7' , 69: 'P8_9' , 45: 'P8_11' , 47: 'P8_15' , 27: 'P8_17' , 67: 'P8_8' , 
          68: 'P8_10' , 44: 'P8_12' , 26: 'P8_14' , 46: 'P8_16' , 65: 'P8_18' , 61: 'P8_26'}


class GPIO:
    def __init__(self,port_num,state):
        bank = port_num//32
        offset = port_num % 32
        self.port_num = port_num
        self.f_string = "GPIO" + str(bank) + "_" + str(offset)
        if state:
            
            gp.setup(self.f_string, gp.OUT)
            self.dir = 1
        else:
           
            gp.setup(table[port_num], gp.IN)
            self.dir = 0

    def on(self):
        gp.output(self.f_string,gp.HIGH)
    def off(self):
        gp.output(self.f_string,gp.LOW)

    def read(self):
        if not self.dir:
            return gp.input(self.f_string)
        else:
            return -1

    def reset(self):
            gp.cleanup()

    def detect_event(self):
        return gp.event_detected(table[self.port_num])


    def add_event(self,edge):
        if edge == "falling":
            gp.add_event_detect(table[self.port_num], gp.FALLING)
        else:
            gp.add_event_detect(table[self.port_num], gp.RISING)

        

