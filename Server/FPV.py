#!/usr/bin/env/python
# File name   : FPV.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date		  : 2025/04/16

import time
import threading
import cv2
import zmq
import base64
import picamera2
import libcamera
from picamera2 import Picamera2, Preview
import io
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import argparse
import imutils
from collections import deque
import psutil
import os
import PID
import Kalman_Filter as Kalman_filter
import datetime
import Move as move
import Switch as switch
import numpy as np
import RPIservo

pid = PID.PID()
pid.SetKp(0.5)
pid.SetKd(0)
pid.SetKi(0)
Y_lock = 0
X_lock = 0
tor	= 17
FindColorMode = 0
WatchDogMode  = 0
UltraData = 3

#2
CVrun = 1
FindLineMode = 0
linePos_1 = 440
linePos_2 = 380
lineColorSet = 255
findLineError = 20
Threshold = 80 
findLineMove = 1
tracking_servo_status = 0
FLCV_Status = 0

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

hflip = 0  # Video flip horizontally: 0 or 1
vflip = 0  # Video vertical flip: 0/1
picam2 = Picamera2()
preview_config = picam2.preview_configuration
preview_config.size = (640, 480)
preview_config.format = 'RGB888'  # 'XRGB8888', 'XBGR8888', 'RGB888', 'BGR888', 'YUV420'
preview_config.transform = libcamera.Transform(hflip=hflip, vflip=vflip)
preview_config.colour_space = libcamera.ColorSpace.Sycc()
preview_config.buffer_count = 4
preview_config.queue = True

if not picam2.is_open:
    raise RuntimeError('Could not start camera.')
try:
    picam2.start()
except Exception as e:
    print(f"\033[38;5;1mError:\033[0m\n{e}")
    print("\nPlease check whether the camera is connected well, and disable the \"legacy camera driver\" on raspi-config")


modeText = 'Select your mode, ARM or PT?'

scGear = RPIservo.ServoCtrl()
scGear.moveInit()
scGear.start()

Dv = -1 #Directional variable
CVRun = 1
turn_speed = 15
tracking_servo_left = None
tracking_servo_left_mark = 0
tracking_servo_right_mark = 0
servo_left_stop = 0
servo_right_stop = 0
def map(input, in_min,in_max,out_min,out_max):
    return (input-in_min)/(in_max-out_min)*(out_max-out_min)+out_min
def findLineCtrl(posInput, setCenter):#2
	if posInput: 
		if posInput > 480:
			move.commandInput('right')
			pass
		elif posInput < 180:
			move.commandInput('left')
			pass
		else: 
			move.commandInput('forward')
			pass
	else:
		pass

def cvFindLine(frame_image):
    frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
    retval, frame_findline = cv2.threshold(frame_findline, Threshold, 255, cv2.THRESH_BINARY)
    frame_findline = cv2.erode(frame_findline, None, iterations=2)
    frame_findline = cv2.dilate(frame_findline, None, iterations=2)
    colorPos_1 = frame_findline[linePos_1]
    colorPos_2 = frame_findline[linePos_2]

    try:
        lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
        lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

        lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
        lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)

        if lineIndex_Pos1 != []:
            if abs(lineIndex_Pos1[0][-1] - lineIndex_Pos1[0][0]) > 500:
                print("Tracking color not found")
                findLineMove = 0
            else:
                findLineMove = 1
        elif lineIndex_Pos2 != []:
            if abs(lineIndex_Pos2[0][-1] - lineIndex_Pos2[0][0]) > 500:
                print("Tracking color not found")
                findLineMove = 0
            else:
                findLineMove = 1

        if lineColorCount_Pos1 == 0:
            lineColorCount_Pos1 = 1
        if lineColorCount_Pos2 == 0:
            lineColorCount_Pos2 = 1

        left_Pos1 = lineIndex_Pos1[0][1]
        right_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1 - 2]
        center_Pos1 = int((left_Pos1 + right_Pos1) / 2)

        left_Pos2 = lineIndex_Pos2[0][1]
        right_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2 - 2]
        center_Pos2 = int((left_Pos2 + right_Pos2) / 2)

        center = int((center_Pos1 + center_Pos2) / 2)
    except:
        center = None
        pass

    findLineCtrl(center, 320)

    try:
        if lineColorSet == 255:
            cv2.putText(frame_findline, ('Following White Line'), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 255, 128), 1,
                        cv2.LINE_AA)
        else:
            cv2.putText(frame_findline, ('Following Black Line'), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 255, 128), 1,
                        cv2.LINE_AA)	
		
        cv2.line(frame_findline, (left_Pos1, (linePos_1 + 30)), (left_Pos1, (linePos_1 - 30)), (255, 128, 64), 1)
        cv2.line(frame_findline, (right_Pos1, (linePos_1 + 30)), (right_Pos1, (linePos_1 - 30)), (64, 128, 255), 1)
        cv2.line(frame_findline, (0, linePos_1), (640, linePos_1), (255, 255, 64), 1)

        cv2.line(frame_findline, (left_Pos2, (linePos_2 + 30)), (left_Pos2, (linePos_2 - 30)), (255, 128, 64), 1)
        cv2.line(frame_findline, (right_Pos2, (linePos_2 + 30)), (right_Pos2, (linePos_2 - 30)), (64, 128, 255), 1)
        cv2.line(frame_findline, (0, linePos_2), (640, linePos_2), (255, 255, 64), 1)

        cv2.line(frame_findline, ((center - 20), int((linePos_1 + linePos_2) / 2)),
					((center + 20), int((linePos_1 + linePos_2) / 2)), (0, 0, 0), 1)
        cv2.line(frame_findline, ((center), int((linePos_1 + linePos_2) / 2 + 20)),
					((center), int((linePos_1 + linePos_2) / 2 - 20)), (0, 0, 0), 1)
    except:
        pass

    return frame_findline


class FPV: 
	kalman_filter_X =  Kalman_filter.Kalman_filter(0.01,0.1)
	kalman_filter_Y =  Kalman_filter.Kalman_filter(0.01,0.1)
	P_direction = -1
	T_direction = -1
	P_servo = 12 
	T_servo = 13 
	P_anglePos = 0
	T_anglePos = 0
	cameraDiagonalW = 64
	cameraDiagonalH = 48
	videoW = 640
	videoH = 480
	Y_lock = 0
	X_lock = 0
	tor = 17
	def __init__(self):
		self.frame_num = 0
		self.fps = 0

	def SetIP(self,invar):
		self.IP = invar


	def FindColor(self,invar):
		global FindColorMode
		FindColorMode = invar
		if not FindColorMode:
			scGear.moveAngle(1,0)


	def WatchDog(self,invar):
		global WatchDogMode
		WatchDogMode = invar

	def FindLineMode(self,invar):
		global FindLineMode
		FindLineMode = invar


	def UltraData(self,invar):
		global UltraData
		UltraData = invar


	def colorFindSet(self, invarH, invarS, invarV):
		global colorUpper, colorLower
		HUE_1 = invarH + 100
		HUE_2 = invarH - 100
		if HUE_1 > 255:
			HUE_1 = 255
		if HUE_2 < 0:
			HUE_2 = 0
    
		SAT_1 = invarS + 100
		SAT_2 = invarS - 100
		if SAT_1 > 255:
			SAT_1 = 255
		if SAT_2 < 0:
			SAT_2 = 0

		VAL_1 = invarV + 100
		VAL_2 = invarV - 100
		if VAL_1 > 255:
			VAL_1 = 255
		if VAL_2 < 0:
			VAL_2 = 0

		colorUpper = np.array([HUE_1, SAT_1, VAL_1])
		colorLower = np.array([HUE_2, SAT_2, VAL_2])
		print(colorUpper)
		print(colorLower)
   
	def servoMove(ID, Dir, errorInput):
		if ID == 12:
			errorGenOut = FPV.kalman_filter_X.kalman(errorInput)
			FPV.P_anglePos += 0.15*(errorGenOut*Dir)*FPV.cameraDiagonalW/FPV.videoW
			if abs(errorInput) > FPV.tor:
				scGear.moveAngle(ID,FPV.P_anglePos)
				FPV.X_lock = 0
			else:
				FPV.X_lock = 1
		if ID == 13:
			errorGenOut = FPV.kalman_filter_Y.kalman(errorInput)
			FPV.T_anglePos += 0.1*(errorGenOut*Dir)*FPV.cameraDiagonalH/FPV.videoH
			if abs(errorInput) > FPV.tor:
				scGear.moveAngle(ID,FPV.T_anglePos)
				FPV.Y_lock = 0
			else:
				FPV.Y_lock = 1

	def changeMode(self, textPut):
		global modeText
		modeText = textPut


	def capture_thread(self,IPinver):
		global frame_image, camera#Z
		ap = argparse.ArgumentParser()			#OpenCV initialization
		ap.add_argument("-b", "--buffer", type=int, default=64,
			help="max buffer size")
		args = vars(ap.parse_args())
		pts = deque(maxlen=args["buffer"])

		font = cv2.FONT_HERSHEY_SIMPLEX

		context = zmq.Context()
		footage_socket = context.socket(zmq.PAIR)
		print(IPinver)
		footage_socket.connect('tcp://%s:5555'%IPinver)

		avg = None
		motionCounter = 0

		lastMovtionCaptured = datetime.datetime.now()

		while True:
			frame_image = picam2.capture_array()
			timestamp = datetime.datetime.now()
			cv2.line(frame_image, (300, 240), (340, 240), (128, 255, 128), 1)
			cv2.line(frame_image, (320, 220), (320, 260), (128, 255, 128), 1)
			timestamp = datetime.datetime.now()
			
			if FindColorMode:
				####>>>OpenCV Start<<<####
				hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)
				mask = cv2.inRange(hsv, colorLower, colorUpper)#1
				mask = cv2.erode(mask, None, iterations=2)
				mask = cv2.dilate(mask, None, iterations=2)
				cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)[-2]
				center = None
				if len(cnts) > 0:
					cv2.putText(frame_image,'Target Detected',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)

					c = max(cnts, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)
					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					X = int(x)
					Y = int(y)
					if radius > 10:
						cv2.rectangle(frame_image,(int(x-radius),int(y+radius)),(int(x+radius),int(y-radius)),(255,255,255),1)

					error_Y = 240 - Y
					error_X = 320 - X
					FPV.servoMove(FPV.P_servo, FPV.P_direction, -error_X)
					FPV.servoMove(FPV.T_servo, FPV.T_direction, -error_Y)
				else:
					cv2.putText(frame_image,'Target Detecting',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)
				

			if WatchDogMode:
				gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
				gray = cv2.GaussianBlur(gray, (21, 21), 0)

				if avg is None:
					print("[INFO] starting background model...")
					avg = gray.copy().astype("float")
					continue

				cv2.accumulateWeighted(gray, avg, 0.5)
				frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
				thresh = cv2.threshold(frameDelta, 5, 255,
					cv2.THRESH_BINARY)[1]
				thresh = cv2.dilate(thresh, None, iterations=2)
				cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)
				cnts = imutils.grab_contours(cnts)
				for c in cnts:
					if cv2.contourArea(c) < 5000:
						continue
			 
					(x, y, w, h) = cv2.boundingRect(c)
					cv2.rectangle(frame_image, (x, y), (x + w, y + h), (128, 255, 0), 1)
					text = "Occupied"
					motionCounter += 1
					lastMovtionCaptured = timestamp
					switch.switch(1,1)
					switch.switch(2,1)
					switch.switch(3,1)

				if (timestamp - lastMovtionCaptured).seconds >= 0.5:
					switch.switch(1,0)
					switch.switch(2,0)
					switch.switch(3,0)

			if FindLineMode:
				frame_findline = cvFindLine(frame_image)
				encoded, buffer = cv2.imencode('.jpg', frame_findline)
			else:
				encoded, buffer = cv2.imencode('.jpg', frame_image)
			jpg_as_text = base64.b64encode(buffer)
			footage_socket.send(jpg_as_text)


if __name__ == '__main__':
	fpv=FPV()
	while 1:
		fpv.capture_thread('192.168.3.199')
		pass

