


import Adafruit_BBIO.UART as uart_bus
import serial

import time

import sys

class ESP8266:

    def __init__(self, esp_uart):
        self.uart = esp_uart
        #self.uart.query("AT+RESTORE\r\n")
        self.uart.query("AT+RST\r\n") ## Reset the ESP8266
        self.uart.query("AT+CWMODE=1\r\n") ## Send the ESP's "WiFi Mode" to client by default
        #self.uart.query("AT+CIPMUX=0\r\n")
        #self.uart.query("AT+CIPMODE=1\r\n")

    ## Connect the ESP8266 to a network given WiFi credentials
    def connect(self,ssid, password):
        self.uart.query("AT+CWJAP_CUR=\"" + ssid + "\",\"" + password + "\"\r\n")
        #return self.uart.readData()

    def list_network(self):
        self.uart.query("AT+CWLAP\r\n")
    def restore(self):
        self.uart.query("AT+RESTORE\r\n")

    ## Disconnect from current network
    def disconnect(self):
        self.uart.query("AT+CWQAP\r\n")
        #return self.uart.readData()

    ## Opens a TCP/UDP connection
    def open(self,protocol):
        #addr = self.uart.sendData("AT+CIPSTATUS=\"addr\"\r\n")
        #port = self.uart.sendData("AT+CIPSTATUS=\"port\"\r\n")
        name = "Aiden"
        addr = "10.0.0.72"#/?name=" + name
        port = "5000"
        if protocol == "TCP":
            self.uart.query("AT+CIPSTART=\"TCP\",\"10.0.0.72\",\"6000\"\r\n")
            #self.uart.query("AT+CIPSTART=\"TCP\",\"" + addr + "\",\"" + port + "\"\r\n")
            
        elif protocol == "UDP":
            self.uart.query("AT+CIPSTART=\"UDP\",\"" + addr + "\",\"" + port + "\"\r\n")
            #return self.uart.readData()

    ## Closes current TCP/UDP connection
    def close(self):
        self.uart.sendData("AT+CIPCLOSE\r\n")
        return self.uart.readData()

    ## Get the current connection status
    def status(self):
        self.uart.query("AT+CIPSTATUS\r\n")
        #return self.uart.readData()

    ## Get the current IP address of the ESP8266
    def localIP(self):
        stdio = self.uart.query("AT+CIFSR\r\n")
        return stdio

    ## Transmit data
    def send(self,data):
        length = sys.getsizeof(data)
        self.uart.sendData("AT+CIPSEND=" + str(length))
        self.uart.query(">" + data)
        #return self.uart.readData()
    
    ## Do something as proof of concept that there's a wifi connection to something over the internet
    def doSomething():
        pass

class UART:
    def __init__(self,uart_num,baud=9600):
        fstring = "UART" + str(uart_num)
        uart_bus.setup(fstring)
        device = "/dev/ttyO" + str(uart_num)
        self.ser = serial.Serial(device, baud,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

    def sendData(self,write_data): # on success return 0 else return 1
        if self.ser.isOpen():
            self.ser.write(str.encode(write_data))
            return 0
        else:
            return 1

    def readData(self):
        return self.ser.readline()
        
    def query(self,cmd,my_str=""):
        self.ser.write(str.encode(cmd))
        exhaust = False
        time.sleep(1)
        x = []
        while(True):
            if self.ser.in_waiting:
                line = self.ser.readline()
                time.sleep(0.1)
                x.append(line)
                exhaust = True
                if line == b'OK\r\n':
                    break
                
            else:
                continue

        return x

    def open(self):
        self.ser.close()
        self.ser.open()

    def close(self):
        self.ser.close()

    def cleanup(self):
        uart_bus.cleanup()
        
