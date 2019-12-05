#!/usr/bin/env/python
# File name   : appserver.py
# Production  : RaspClaws
# Website     : www.adeept.com
# Author      : William
# Date        : 2019/11/21

import socket
import threading
import time
import os
from rpi_ws281x import *
import LED
import move

LED = LED.LED()
LED.colorWipe(Color(0,64,255))

step_set = 1
speed_set = 100
DPI = 17

new_frame = 0
direction_command = 'no'
turn_command = 'no'
servo_command = 'no'

SmoothMode = 0
steadyMode = 0

def move_thread():
    global step_set
    stand_stu = 1
    while 1:
        if not steadyMode:
            if direction_command == 'forward' and turn_command == 'no':
                if SmoothMode:
                    move.dove(step_set,35,0.001,DPI,'no')
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
                else:
                    move.move(step_set, 35, 'no')
                    time.sleep(0.1)
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
            elif direction_command == 'backward' and turn_command == 'no':
                if SmoothMode:
                    move.dove(step_set,-35,0.001,DPI,'no')
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
                else:
                    move.move(step_set, -35, 'no')
                    time.sleep(0.1)
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
            else:
                pass

            if turn_command != 'no':
                if SmoothMode:
                    move.dove(step_set,35,0.001,DPI,turn_command)
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
                else:
                    move.move(step_set, 35, turn_command)
                    time.sleep(0.1)
                    step_set += 1
                    if step_set == 5:
                        step_set = 1
                    continue
            else:
                pass

            if turn_command == 'no' and direction_command == 'stand':
                move.stand()
                step_set = 1
            pass
        else:
            move.steady_X()
            move.steady()


class Servo_ctrl(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(Servo_ctrl, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()
            if servo_command == 'lookleft':
                move.look_left()
            elif servo_command == 'lookright':
                move.look_right()
            elif servo_command == 'up':
                move.look_up()
            elif servo_command == 'down':
                move.look_down()
            print('servo_move')
            time.sleep(0.03)

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


def app_ctrl():
    global servo_move
    app_HOST = ''
    app_PORT = 10123
    app_BUFSIZ = 1024
    app_ADDR = (app_HOST, app_PORT)

    servo_move = Servo_ctrl()
    servo_move.start()
    servo_move.pause()

    moving_threading=threading.Thread(target=move_thread)    #Define a thread for moving
    moving_threading.setDaemon(True)                         #'True' means it is a front thread,it would close when the mainloop() closes
    moving_threading.start()                                 #Thread starts

    def  ap_thread():
        os.system("sudo create_ap wlan0 eth0 Groovy 12345678")

    # def setup():
    #     move.setup()

    def appCommand(data_input):
        global direction_command, turn_command, SmoothMode, steadyMode, servo_command
        if data_input == 'forwardStart\n':
            direction_command = 'forward'

        elif data_input == 'backwardStart\n':
            direction_command = 'backward'

        elif data_input == 'leftStart\n':
            turn_command = 'left'

        elif data_input == 'rightStart\n':
            turn_command = 'right'

        elif 'forwardStop' in data_input:
            direction_command = 'stand'

        elif 'backwardStop' in data_input:
            direction_command = 'stand'

        elif 'leftStop' in data_input:
            turn_command = 'no'

        elif 'rightStop' in data_input:
            turn_command = 'no'

        if data_input == 'lookLeftStart\n':
            servo_command = 'lookleft'
            servo_move.resume()

        elif data_input == 'lookRightStart\n': 
            servo_command = 'lookright'
            servo_move.resume()

        elif data_input == 'downStart\n':
            servo_command = 'down'
            servo_move.resume()

        elif data_input == 'upStart\n':
            servo_command = 'up'
            servo_move.resume()

        elif 'lookLeftStop' in data_input:
            servo_move.pause()
            servo_command = 'no'
        elif 'lookRightStop' in data_input:
            servo_move.pause()
            servo_command = 'no'
        elif 'downStop' in data_input:
            servo_move.pause()
            servo_command = 'no'
        elif 'upStop' in data_input:
            servo_move.pause()
            servo_command = 'no'


        if data_input == 'aStart\n':
            if SmoothMode:
                SmoothMode = 0
            else:
                SmoothMode = 1

        elif data_input == 'bStart\n':
            if steadyMode:
                steadyMode = 0
            else:
                steadyMode = 1

        elif data_input == 'cStart\n':
            LED.colorWipe(Color(255,64,0))

        elif data_input == 'dStart\n':
            LED.colorWipe(Color(64,255,0))

        elif 'aStop' in data_input:
            pass
        elif 'bStop' in data_input:
            pass
        elif 'cStop' in data_input:
            pass
        elif 'dStop' in data_input:
            pass

        print(data_input)

    def appconnect():
        global AppCliSock, AppAddr
        try:
            s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("1.1.1.1",80))
            ipaddr_check=s.getsockname()[0]
            s.close()
            print(ipaddr_check)

            AppSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            AppSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            AppSerSock.bind(app_ADDR)
            AppSerSock.listen(5)
            print('waiting for App connection...')
            AppCliSock, AppAddr = AppSerSock.accept()
            print('...App connected from :', AppAddr)
        except:
            ap_threading=threading.Thread(target=ap_thread)       #Define a thread for AP Mode
            ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
            ap_threading.start()                                  #Thread starts

            LED.colorWipe(Color(0,16,50))
            time.sleep(1)
            LED.colorWipe(Color(0,16,100))
            time.sleep(1)
            LED.colorWipe(Color(0,16,150))
            time.sleep(1)
            LED.colorWipe(Color(0,16,200))
            time.sleep(1)
            LED.colorWipe(Color(0,16,255))
            time.sleep(1)
            LED.colorWipe(Color(35,255,35))

            AppSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            AppSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            AppSerSock.bind(app_ADDR)
            AppSerSock.listen(5)
            print('waiting for App connection...')
            AppCliSock, AppAddr = AppSerSock.accept()
            print('...App connected from :', AppAddr)

    appconnect()
    # setup()
    app_threading=threading.Thread(target=appconnect)         #Define a thread for app connection
    app_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
    app_threading.start()                                     #Thread starts

    while 1:
        data = ''
        data = str(AppCliSock.recv(app_BUFSIZ).decode())
        if not data:
            continue
        appCommand(data)
        pass

if __name__ == '__main__':
    app_ctrl()