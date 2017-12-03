# server stuff
# import simple_server as simpleSrvr
from simple_server import *
# motor control stuff
import motor_control as motorCtrl

# blossom control
import blossom_control as blossom
# blossom info
blossom_add = blossom.blossom_add
blossom_blinds = {'up':'fear2','down':'sad3'}

# GPIO setup
import RPi.GPIO as GPIO
# GPIO 4 (pin 7) goes up
gpio_up = 4
# GPIO 3 (pin 5) goes down
gpio_down = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_up,GPIO.IN)
GPIO.setup(gpio_down,GPIO.IN)

import firebase_control
from firebase_control import fb as gal9000

# threading
import threading

import SimpleHTTPServer
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse

port = 8000

class funHandler(BaseHTTPRequestHandler):
    # def do_GET(self, function, *args, **kwargs):
    def do_GET(self):
        print self.path
        self.send_response(200)
        move_blinds(self.path[1:])

# firebase functions
def gal9000_thread():
    while(1):
        try:
            if (GPIO.input(gpio_up)):
                move_blinds('up')
            elif (GPIO.input(gpio_down)):
                move_blinds('down')
        except KeyboardInterrupt:
            return

def gal9000_put(state):
    gal9000.put('blinds','state',state)

def gal9000_check():
    blinds_cmd = gal9000.get('blinds','cmd')
    blinds_state = gal9000.get('blinds','state')
    blossom_s = gal9000.get('blossom','s')
    blossom_idle = gal9000.get('blossom','idle')

    blossom.cmd_blossom(blossom_s, blossom_idle)

    # move blinds
    move_blinds(blinds_cmd)
    # erase commands
    gal9000.put('blinds','cmd','')

    return blinds_state

# motor functions
def check_motor_pos():
    load = motorCtrl.get_load(1)[0]
    if (load == -100):
        return 'down'
    elif (load == 100):
        return 'up'
    else:
        return 'mid'

def motor_move(speed):
    motorCtrl.move_wheel(1, speed)

def move_blinds(state):
    blossom.cmd_blossom(blossom_blinds[state])
    if (state == 'up'):
        motor_move(-1000)
        # gal9000_put('up')
    elif (state =='down'):
        motor_move(1000)
        # gal9000_put('down')
    elif (state == 'stop'):
        motor_move(0)
        return
    else:
        return
    gal9000.put('blinds','state',state)

# main
if __name__ == "__main__":

    # set function handler
    motorHandler = funHandler

    # init blinds state
    blinds_state = gal9000_check()

    # start threading
    t = threading.Thread(target=gal9000_thread)
    t.start()

    httpd = SocketServer.TCPServer(("", port), motorHandler)
    httpd.serve_forever()