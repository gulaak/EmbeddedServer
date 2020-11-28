import socketio
import threading
import os
import subprocess
import signal





sio = socketio.Client()

sio.connect("http://10.0.0.72:5000")

socket_map = {}

def run_program(data,ID):
    #print("I received data", data)
    res = subprocess.Popen(['python','-c',data],stdout=subprocess.PIPE)
    socket_map[ID] = res.pid
    stdout_resp = res.stdout.decode())
    if "Error" in stdout_resp:
        sio.emit('compile failed',ID)
    else:
        sio.emit('compile success',ID)
    
    sio.emit('stdout', stdout_resp) # return stdout of process back to the requesting client
    
@sio.event
def message(data):
    print("I received data")


@sio.on("send program")
def on_file(data, ID):
    thread = threading.Thread(target=run_program, args=(data,ID,))
    thread.start()


@sio.on("stop program")
def on_end(ID):
    os.kill(socket_map[ID], signal.SIGTERM) #kill process (send stdout back to client)

if __name__ == "__main__"









