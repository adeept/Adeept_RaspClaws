#!/usr/bin/env/python3
# File name   : WebServer.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/04/16

import time
import threading
import os
import RPIservo
import Info as info
import Move as move
import RobotLight as robotLight
import Switch as switch
import socket
import Voltage
import asyncio
import websockets

import json
import app

batteryMonitor = Voltage.BatteryLevelMonitor()
batteryMonitor.start()

speed_set = 50
rad = 0.5
turnWiggle = 60
steady = 0
scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()



init_pwm0 = scGear.initPos[0]
init_pwm1 = scGear.initPos[1]
init_pwm2 = scGear.initPos[2]
init_pwm3 = scGear.initPos[3]
init_pwm4 = scGear.initPos[4]

init_pwm = []
for i in range(16):
	init_pwm.append(scGear.initPos[i])

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def servoPosInit():
	scGear.initConfig(2,init_pwm2,1)
	scGear.initConfig(1,init_pwm1,1)
	scGear.initConfig(0,init_pwm0,1)

def ap_thread():
	os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")

def functionSelect(command_input, response):
	global direction_command, turn_command, SmoothMode,steady

	if 'findColor' == command_input:
		flask_app.modeselect('findColor')

	elif 'motionGet' == command_input:
		flask_app.modeselect('watchDog')

	elif 'stopCV' == command_input:
		flask_app.modeselect('none')
		time.sleep(0.5)
		move.commandInput('no')
		move.commandInput('stand')

	elif 'fast' == command_input:
		move.commandInput(command_input)

	elif 'slow' == command_input:
		move.commandInput(command_input)

	elif 'police' == command_input:
		ws2812.police()

	elif 'policeOff' == command_input:
		ws2812.breath(70,70,255)

	elif 'steadyCamera' == command_input:
		move.commandInput(command_input)
		steady = 1

	elif 'steadyCameraOff' == command_input:
		move.commandInput(command_input)
		steady = 0

def switchCtrl(command_input, response):
	if 'Switch_1_on' in command_input:
		switch.switch(1,1)

	elif 'Switch_1_off' in command_input:
		switch.switch(1,0)

	elif 'Switch_2_on' in command_input:
		switch.switch(2,1)

	elif 'Switch_2_off' in command_input:
		switch.switch(2,0)

	elif 'Switch_3_on' in command_input:
		switch.switch(3,1)

	elif 'Switch_3_off' in command_input:
		switch.switch(3,0) 


def robotCtrl(command_input, response):
	global direction_command, turn_command
	if 'forward' == command_input:
		direction_command = 'forward'
		move.commandInput(direction_command)
	
	elif 'backward' == command_input:
		direction_command = 'backward'
		move.commandInput(direction_command)

	elif 'DS' in command_input:
		direction_command = 'stand'
		move.commandInput(direction_command)


	elif 'left' == command_input:
		turn_command = 'left'
		move.commandInput(turn_command)

	elif 'right' == command_input:
		turn_command = 'right'
		move.commandInput(turn_command)

	elif 'TS' in command_input:
		turn_command = 'no'
		move.commandInput(turn_command)


	elif 'lookleft' == command_input:
		scGear.singleServo(12, 1, 3)

	elif 'lookright' == command_input:
		scGear.singleServo(12,-1, 3)

	elif 'LRstop' in command_input:
		scGear.stopWiggle()


	elif 'up' == command_input:
		scGear.singleServo(13, 1, 3)

	elif 'down' == command_input:
		scGear.singleServo(13, -1, 3)

	elif 'UDstop' in command_input:
		scGear.stopWiggle()


def configPWM(command_input, response):
    global steady
    if  steady == 0:
        if 'SiLeft' in command_input:
            numServo = int(command_input[7:])
            init_pwm[numServo] = init_pwm[numServo] - 2
            scGear.initConfig(numServo, init_pwm[numServo], 1)

        if 'SiRight' in command_input:
            numServo = int(command_input[8:])
            init_pwm[numServo] = init_pwm[numServo] + 2
            scGear.initConfig(numServo, init_pwm[numServo], 1)

        if 'PWMMS' in command_input:
            numServo = int(command_input[6:])
            init_pwm[numServo] = 300
            scGear.initConfig(numServo, init_pwm[numServo], 1)
  
        if 'PWMINIT' == command_input:
            for i in range(0,16):
                scGear.initConfig(i, init_pwm[i], 1)

        if 'PWMD' in command_input:
            for i in range(0,16):
                init_pwm[i] = 300
                scGear.initConfig(i, init_pwm[i], 1)

		
def wifi_check():
	try:
		s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		s.connect(("1.1.1.1",80))
		ipaddr_check=s.getsockname()[0]
		s.close()
		print(ipaddr_check)
	except:
		ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
		ap_threading.setDaemon(True)						  #'True' means it is a front thread,it would close when the mainloop() closes
		ap_threading.start()								  #Thread starts
		ws2812.set_all_led_color_data(0,16,50)
		ws2812.show()
		time.sleep(1)

async def check_permit(websocket):
	while True:
		recv_str = await websocket.recv()
		cred_dict = recv_str.split(":")
		if cred_dict[0] == "admin" and cred_dict[1] == "123456":
			response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
			await websocket.send(response_str)
			return True
		else:
			response_str = "sorry, the username or password is wrong, please submit again"
			await websocket.send(response_str)

async def recv_msg(websocket):
	global speed_set, modeSelect,steady
	direction_command = 'no'
	turn_command = 'no'

	while True: 
		response = {
			'status' : 'ok',
			'title' : '',
			'data' : None
		}

		data = ''
		data = await websocket.recv()
		try:
			data = json.loads(data)
		except Exception as e:
			print('not A JSON')

		if not data:
			continue

		if isinstance(data,str):
			robotCtrl(data, response)

			switchCtrl(data, response)

			functionSelect(data, response)

			configPWM(data, response)

			if 'get_info' == data:
				response['title'] = 'get_info'
				response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

			if 'wsB' in data:
				try:
					set_B=data.split()
					speed_set = int(set_B[1])
				except:
					pass

			elif 'CVFL' == data and steady == 0:
				flask_app.modeselect('findlineCV')

			elif 'CVFLColorSet' in data:
				color = int(data.split()[1])
				flask_app.camera.colorSet(color)

			elif 'CVFLL1' in data:
				pos = int(data.split()[1])
				flask_app.camera.linePosSet_1(pos)

			elif 'CVFLL2' in data:
				pos = int(data.split()[1])
				flask_app.camera.linePosSet_2(pos)

			elif 'CVFLSP' in data:
				err = int(data.split()[1])
				flask_app.camera.errorSet(err)


		elif(isinstance(data,dict)):
			if data['title'] == "findColorSet":
				color = data['data']
				flask_app.colorFindSet(color[0],color[1],color[2])

		print(data)
		response = json.dumps(response)
		await websocket.send(response)

async def main_logic(websocket, path):
	await check_permit(websocket)
	await recv_msg(websocket)

if __name__ == '__main__':
	switch.switchSetup()
	switch.set_all_switch_off()

	global flask_app
	flask_app = app.webapp()
	flask_app.startthread()

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
		wifi_check()
		try:				  #Start server,waiting for client
			start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
			asyncio.get_event_loop().run_until_complete(start_server)
			print('waiting for connection...')
			break
		except Exception as e:
			print(e)
			ws2812.set_all_led_color_data(0,0,0)
			ws2812.show()

		try:
			ws2812.set_all_led_color_data(0,80,255)
			ws2812.show()
		except:
			pass
	try:
		asyncio.get_event_loop().run_forever()
	except Exception as e:
		print(e)
		ws2812.set_all_led_color_data(0,0,0)
		ws2812.show()
		move.destroy()
