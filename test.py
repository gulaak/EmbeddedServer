



from BB_Serial import UART

import time

bus = UART(1)

bus.open()

while(True):
    bus.send(str.encode("AT+BAUD?"))
    time.sleep(1)
    print(bus.read(10))
    time.sleep(1)






