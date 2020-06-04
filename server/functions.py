#!/usr/bin/env python3
# File name   : servo.py
# Description : Control Functions
# Author	  : William
# Date		: 2020/03/17
import time
import RPi.GPIO as GPIO
import threading
from mpu6050 import mpu6050
import Adafruit_PCA9685
import os
import json
import Kalman_filter
import move
import RPIservo

scGear = RPIservo.ServoCtrl()

kalman_filter_X =  Kalman_filter.Kalman_filter(0.01,0.1)

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

MPU_connection = 1
try:
	sensor = mpu6050(0x68)
	print('mpu6050 connected, PT MODE ON')
except:
	MPU_connection = 0
	print('mpu6050 disconnected, ARM MODE ON')

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def num_import_int(initial):        #Call this function to import data from '.txt' file
	global r
	with open(thisPath+"/RPIservo.py") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				r=line
	begin=len(list(initial))
	snum=r[begin:]
	n=int(snum)
	return n

pwm0_direction = 1
pwm0_init = num_import_int('init_pwm0 = ')
pwm0_max  = 520
pwm0_min  = 100
pwm0_pos  = pwm0_init

pwm1_direction = 1
pwm1_init = num_import_int('init_pwm1 = ')
pwm1_max  = 520
pwm1_min  = 100
pwm1_pos  = pwm1_init

pwm2_direction = 1
pwm2_init = num_import_int('init_pwm2 = ')
pwm2_max  = 520
pwm2_min  = 100
pwm2_pos  = pwm2_init

def pwmGenOut(angleInput):
	return int(round(23/9*angleInput))


class Functions(threading.Thread):
	def __init__(self, *args, **kwargs):
		self.functionMode = 'none'
		self.steadyGoal = 0

		self.scanNum = 3
		self.scanList = [0,0,0]
		self.scanPos = 1
		self.scanDir = 1
		self.rangeKeep = 0.7
		self.scanRange = 100
		self.scanServo = 1
		self.turnServo = 2
		self.turnWiggle = 200

		super(Functions, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()


	def radarScan(self):
		global pwm0_pos
		scan_speed = 3
		result = []

		if pwm0_direction:
			pwm0_pos = pwm0_max
			pwm.set_pwm(12, 0, pwm0_pos)
			time.sleep(0.8)

			while pwm0_pos>pwm0_min:
				pwm0_pos-=scan_speed
				pwm.set_pwm(12, 0, pwm0_pos)
		else:
			pwm0_pos = pwm0_min
			pwm.set_pwm(12, 0, pwm0_pos)
			time.sleep(0.8)

			while pwm0_pos<pwm0_max:
				pwm0_pos+=scan_speed
				pwm.set_pwm(12, 0, pwm0_pos)
		pwm.set_pwm(12, 0, pwm0_init)
		return result


	def pause(self):
		self.functionMode = 'none'
		self.__flag.clear()


	def resume(self):
		self.__flag.set()


	def automatic(self):
		self.functionMode = 'Automatic'
		self.resume()


	def trackLine(self):
		self.functionMode = 'trackLine'
		self.resume()


	def keepDistance(self):
		self.functionMode = 'keepDistance'
		self.resume()


	def steady(self,goalPos):
		self.functionMode = 'Steady'
		self.steadyGoal = goalPos
		self.resume()


	def speech(self):
		self.functionMode = 'speechRecProcessing'
		self.resume()


	def trackLineProcessing(self):
		pass


	def automaticProcessing(self):
		print('automaticProcessing')
		pass


	def steadyProcessing(self):
		print('steadyProcessing')
		pass


	def speechRecProcessing(self):
		print('speechRecProcessing')
		pass


	def keepDisProcessing(self):
		print('keepDistanceProcessing')
		pass


	def functionGoing(self):
		if self.functionMode == 'none':
			self.pause()
		elif self.functionMode == 'Automatic':
			self.automaticProcessing()
		elif self.functionMode == 'Steady':
			self.steadyProcessing()
		elif self.functionMode == 'trackLine':
			self.trackLineProcessing()
		elif self.functionMode == 'speechRecProcessing':
			self.speechRecProcessing()
		elif self.functionMode == 'keepDistance':
			self.keepDisProcessing()


	def run(self):
		while 1:
			self.__flag.wait()
			self.functionGoing()
			pass


if __name__ == '__main__':
	pass
	# fuc=Functions()
	# fuc.radarScan()
	# fuc.start()
	# fuc.automatic()
	# # fuc.steady(300)
	# time.sleep(30)
	# fuc.pause()
	# time.sleep(1)
	# move.move(80, 'no', 'no', 0.5)