import socketio
import threading
import os
import sys
import subprocess
import signal
import time
import psutil

socket_map = {}


sio = socketio.Client()
sio.connect("http://10.0.0.128:5000")

gpio_reset = """
    import Adafruit_BBIO.GPIO as GPIO
    GPIO.cleanup()

"""

uart_reset = """

    import Adafruit_BBIO.UART as UART
    UART.cleanup()
"""

pwm_reset = """
    import Adafruit_BBIO.PWM as PWM
    PWM.cleanup()

"""



  #  while(True):
  #      time.sleep(5)
  #      cpu = psutil.cpu_percent()
  #      print(cpu)
  #


def background_thread():
    while(True):
        time.sleep(5)
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        sio.emit('update stats', [cpu,mem.total,mem.available,mem.percent])


if __name__ == "__main__":
    thread = threading.Thread(target=background_thread)
    thread.start() # run new thread to handle program 


def run_program(data,ID,resources):
    #print("I received data", data)
    res = subprocess.Popen([sys.executable, '-u', '-c',data],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    idx = 0
    try:
        if socket_map[ID]:
            socket_map[ID].append(res.pid)
            idx = len(socket_map[ID]) 
    except:
        socket_map[ID] = [res.pid]
        idx = 1    
    

    #print(socket_map[ID])   
    #idx = len(socket_map[ID])
    while(True):
        std_out = res.stdout.readline()
        if std_out == '' and res.poll() is not None:
            break
        if std_out:
            #print(std_out)
            sio.emit('std out', [std_out,ID])
    if res.poll() > 0:
        print("Error")
        sio.emit('compile error', [res.stderr.read(),ID,resources]) 
    else:

        sio.emit('release beaglebone', [data,ID,resources])


    try:
        socket_map[ID]
        socket_map[ID].pop(idx-1)
    except:
        pass
    #std_out, std_error = res.communicate()
    #std_error_str = std_error.decode('utf-8')
    #if len(std_error_str) > 0:
    #    sio.emit('compile error',[std_error,ID])
    #else:
    #    sio.emit('std out', [std_out.decode('utf-8'),ID]) # return stdout of process back to the requesting client
    



@sio.on("send program")
def on_file(data, ID, resources):
    #print("Received")
    thread = threading.Thread(target=run_program, args=(data,ID,resources,),daemon=True)
    thread.start() # run new thread to handle program 
    

@sio.on("stop program")
def on_end(ID):
    print(socket_map[ID])
    for pid in socket_map[ID]:
        if pid > 0:
            os.kill(pid, signal.SIGTERM) #kill process (send stdout back to client)
    del socket_map[ID]


@sio.on("reset")
def on_reset(idx):
    program = ""
    if (idx == 0):
        program = gpio_reset
    elif (idx == 1):
        program = uart_reset
    elif (idx == 2):
        program = pwm_reset

    
    res = subprocess.Popen([sys.executable,'-c',program],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)

    stdout, stderr = res.communicate() #block till done


