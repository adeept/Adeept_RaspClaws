#!/usr/bin/env/python
# File name   : server.py
# Description : main programe for RaspClaws
# Website     : www.adeept.com
# E-mail      : support@adeept.com
# Author      : William
# Date        : 2018/08/22

import socket
import time
import threading
import Move as move
import Adafruit_PCA9685
import argparse
import os
import FPV
import psutil
import Switch as switch
import RobotLight as robotLight
import ast
step_set = 1
speed_set = 100

new_frame = 0
direction_command = 'no'
turn_command = 'no'
pwm = Adafruit_PCA9685.PCA9685(address=0x5F, busnum=1)
pwm.set_pwm_freq(50)
rm = move.RobotM()
rm.start()
rm.pause()

SmoothMode = 0
steadyMode = 0


def  ap_thread():
    os.system("sudo create_ap wlan0 eth0 AdeeptCar 12345678")


def get_cpu_tempfunc():
    """ Return CPU temperature """
    result = 0
    mypath = "/sys/class/thermal/thermal_zone0/temp"
    with open(mypath, 'r') as mytmpfile:
        for line in mytmpfile:
            result = line

    result = float(result)/1000
    result = round(result, 1)
    return str(result)


def get_gpu_tempfunc():
    """ Return GPU temperature as a character string"""
    res = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    return res.replace("temp=", "")


def get_cpu_use():
    """ Return CPU usage using psutil"""
    cpu_cent = psutil.cpu_percent()
    return str(cpu_cent)


def get_ram_info():
    """ Return RAM usage using psutil """
    ram_cent = psutil.virtual_memory()[2]
    return str(ram_cent)


def get_swap_info():
    """ Return swap memory  usage using psutil """
    swap_cent = psutil.swap_memory()[3]
    return str(swap_cent)


def info_get():
    global cpu_t,cpu_u,gpu_t,ram_info
    while 1:
        cpu_t = get_cpu_tempfunc()
        cpu_u = get_cpu_use()
        ram_info = get_ram_info()
        time.sleep(3)




def info_send_client():
    SERVER_IP = addr[0]
    SERVER_PORT = 2256   #Define port serial 
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    Info_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Set connection value for socket
    Info_Socket.connect(SERVER_ADDR)
    print(SERVER_ADDR)
    while 1:
        try:
            Info_Socket.send((get_cpu_tempfunc()+' '+get_cpu_use()+' '+get_ram_info()).encode())
            time.sleep(1)
        except:
            pass


def FPV_thread():
    global fpv
    fpv=FPV.FPV()
    fpv.capture_thread(addr[0])


def run():
    global direction_command, turn_command, SmoothMode, steadyMode
    info_threading=threading.Thread(target=info_send_client)   #Define a thread for communication
    info_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
    info_threading.start()                                     #Thread starts

    Y_pitch = 300
    Y_pitch_MAX = 600
    Y_pitch_MIN = 100

    while True: 
        data = ''
        data = str(tcpCliSock.recv(BUFSIZ).decode())
        if not data:
            continue
        elif 'forward' == data:
            direction_command = 'forward'
            move.commandInput(direction_command)
        elif 'backward' == data:
            direction_command = 'backward'
            move.commandInput(direction_command)
        elif 'DS' in data:
            direction_command = 'stand'
            move.commandInput(direction_command)

        elif 'left' == data:
            direction_command = 'left'
            move.commandInput(direction_command)
        elif 'right' == data:
            direction_command = 'right'
            move.commandInput(direction_command)
        elif 'TS' in data:
            direction_command = 'no'
            move.commandInput(direction_command)

        elif 'up' == data:
            move.look_up()
        elif 'down' == data:
            move.look_down()
        elif 'home' == data:
            move.home()

        elif 'lookleft' == data:
            move.look_left()
        elif 'lookright' == data:
            move.look_right()

        elif 'findColor' ==  data:
            fpv.FindColor(1)
            tcpCliSock.send(('findColor').encode())

        elif 'motionGet' in data:
            fpv.WatchDog(1)
            tcpCliSock.send(('motionGet').encode())

        elif 'steadyCamera' == data:
            move.commandInput(data)
            tcpCliSock.send(('steadyCamera').encode())
        elif 'steadyCameraOff' == data:
            move.commandInput(data)
            tcpCliSock.send(('steadyCameraOff').encode())

        elif 'stopCV' in data:
            fpv.FindColor(0)
            fpv.WatchDog(0)
            fpv.FindLineMode(0)
            tcpCliSock.send(('stopCV').encode())
            direction_command = 'stand'
            turn_command = 'no'
            move.commandInput('stand')
            move.commandInput('no')

        elif 'fast' in data:
            move.commandInput(data)
            tcpCliSock.send(('fast').encode())

        elif 'slow' in data:
            move.commandInput(data)
            tcpCliSock.send(('slow').encode())
        elif 'police' == data:
            ws2812.police()
            tcpCliSock.send(('police').encode())

        elif 'policeOff' == data:
            ws2812.breath(70,70,255)
            tcpCliSock.send(('policeOff').encode())

        elif 'Switch_1_on' in data:
            switch.switch(1,1)
            tcpCliSock.send(('Switch_1_on').encode())

        elif 'Switch_1_off' in data:
            switch.switch(1,0)
            tcpCliSock.send(('Switch_1_off').encode())

        elif 'Switch_2_on' in data:
            switch.switch(2,1)
            tcpCliSock.send(('Switch_2_on').encode())

        elif 'Switch_2_off' in data:
            switch.switch(2,0)
            tcpCliSock.send(('Switch_2_off').encode())

        elif 'Switch_3_on' in data:
            switch.switch(3,1)
            tcpCliSock.send(('Switch_3_on').encode())

        elif 'Switch_3_off' in data:
            switch.switch(3,0)
            tcpCliSock.send(('Switch_3_off').encode())

        elif 'CVFL' == data and steadyMode == 0:
            if not FPV.FindLineMode:
                FPV.FindLineMode = 1
                tcpCliSock.send(('CVFL_on').encode())

        elif 'CVFLColorSet 0' ==  data:
            FPV.lineColorSet = 0
            
        elif 'CVFLColorSet 255' ==  data:
            FPV.lineColorSet = 255

        elif 'CVFLL1' in data:
            try:
                set_lip1=data.split()
                lip1_set = int(set_lip1[1])
                FPV.linePos_1 = lip1_set
            except:
                pass

        elif 'CVFLL2' in data:
            try:
                set_lip2=data.split()
                lip2_set = int(set_lip2[1])
                FPV.linePos_2 = lip2_set
            except:
                pass

        elif 'findColorSet' in data:
            try:
                command_dict = ast.literal_eval(data)
                if 'data' in command_dict and len(command_dict['data']) == 3:
                    r, g, b = command_dict['data']
                    fpv.colorFindSet(r, g, b)
                    print(f"color: r={r}, g={g}, b={b}")
            except (SyntaxError, ValueError):
                print("The received string format is incorrect and cannot be parsed.")
        else:
            pass
        print(data)


def destory():
    move.clean_all()


if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()
    move.init_all()

    HOST = ''
    PORT = 10223                              #Define port serial 
    BUFSIZ = 1024                             #Define buffer size
    ADDR = (HOST, PORT)
    try:
        ws2812=robotLight.Adeept_SPI_LedPixel(16, 255)
        if ws2812.check_spi_state() != 0:
            ws2812.start()
            ws2812.breath(70,70,255)
        else:
            ws2812.led_close()
    except  KeyboardInterrupt:
        ws2812.led_close()
        pass
    while  1:
        try:
            s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("1.1.1.1",80))
            ipaddr_check=s.getsockname()[0]
            s.close()
            print(ipaddr_check)
        except:
            ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
            ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
            ap_threading.start()                                  #Thread starts

            ws2812.set_all_led_color_data(0,16,50)
            ws2812.show()
            time.sleep(1)
            ws2812.set_all_led_color_data(0,16,100)
            ws2812.show()
            time.sleep(1)
            ws2812.set_all_led_color_data(0,16,150)
            ws2812.show()
            time.sleep(1)
            ws2812.set_all_led_color_data(0,16,200)
            ws2812.show()
            time.sleep(1)
            ws2812.set_all_led_color_data(0,16,255)
            ws2812.show()
            time.sleep(1)
            ws2812.set_all_led_color_data(35,255,35)
            ws2812.show()

        try:
            tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcpSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            tcpSerSock.bind(ADDR)
            tcpSerSock.listen(5)                      #Start server,waiting for client
            print('waiting for connection...')
            tcpCliSock, addr = tcpSerSock.accept()
            print('...connected from :', addr)

            fps_threading=threading.Thread(target=FPV_thread)         #Define a thread for FPV and OpenCV
            fps_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
            fps_threading.start()                                     #Thread starts
            break
        except:
            pass

    try:
        ws2812.breath_status_set(0)
        ws2812.set_all_led_color_data(64,128,255)
        ws2812.show()
    except:
        pass
    run()   

