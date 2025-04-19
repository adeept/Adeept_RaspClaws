#!/usr/bin/env/python3
# File name   : camera_opencv.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/04/16
import os
import cv2
from base_camera import BaseCamera
import RPIservo
import numpy as np
import Move as move
import datetime
import Kalman_Filter as Kalman_filter
import PID
import time
import threading
import imutils
import picamera2
import libcamera
from picamera2 import Picamera2, Preview
import io
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
pid = PID.PID()
pid.SetKp(0.5)
pid.SetKd(0)
pid.SetKi(0)
vflip = 0
hflip = 0 
CVRun = 1
linePos_1 = 440
linePos_2 = 380
lineColorSet = 255
frameRender = 1
findLineError = 160
Threshold = 80 
colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

class CVThread(threading.Thread):
	font = cv2.FONT_HERSHEY_SIMPLEX

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
	tor = 27

	scGear = RPIservo.ServoCtrl()
	scGear.moveInit()


	def __init__(self, *args, **kwargs):
		self.CVThreading = 0
		self.CVMode = 'none'
		self.imgCV = None

		self.mov_x = None
		self.mov_y = None
		self.mov_w = None
		self.mov_h = None

		self.radius = 0
		self.box_x = None
		self.box_y = None
		self.drawing = 0

		self.findColorDetection = 0

		self.left_Pos1 = None
		self.right_Pos1 = None
		self.center_Pos1 = None

		self.left_Pos2 = None
		self.right_Pos2 = None
		self.center_Pos2 = None

		self.center = None

		super(CVThread, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()

		self.avg = None
		self.motionCounter = 0
		self.lastMovtionCaptured = datetime.datetime.now()
		self.frameDelta = None
		self.thresh = None
		self.cnts = None

	def mode(self, invar, imgInput):
		self.CVMode = invar
		self.imgCV = imgInput
		self.resume()

	def elementDraw(self,imgInput):
		if self.CVMode == 'none':
			pass

		elif self.CVMode == 'findColor':
			if self.findColorDetection:
				cv2.putText(imgInput,'Target Detected',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
				self.drawing = 1
			else:
				cv2.putText(imgInput,'Target Detecting',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
				self.drawing = 0

			if self.radius > 10 and self.drawing:
				cv2.rectangle(imgInput,(int(self.box_x-self.radius),int(self.box_y+self.radius)),(int(self.box_x+self.radius),int(self.box_y-self.radius)),(255,255,255),1)

		elif self.CVMode == 'findlineCV':
			if frameRender:
				imgInput = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
				retval_bw, imgInput =  cv2.threshold(imgInput, Threshold, 255, cv2.THRESH_BINARY)
				imgInput = cv2.erode(imgInput, None, iterations=2) 
				imgInput = cv2.dilate(imgInput, None, iterations=2) 
			try:
				if lineColorSet == 255:
					cv2.putText(imgInput,('Following White Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)
				else:
					cv2.putText(imgInput,('Following Black Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)
				imgInput=cv2.merge((imgInput.copy(),imgInput.copy(),imgInput.copy()))
				cv2.line(imgInput,(self.left_Pos1,(linePos_1+30)),(self.left_Pos1,(linePos_1-30)),(255,128,64),2)
				cv2.line(imgInput,(self.right_Pos1,(linePos_1+30)),(self.right_Pos1,(linePos_1-30)),(64,128,255),2)
				cv2.line(imgInput,(0,linePos_1),(640,linePos_1),(255,128,64),1)

				cv2.line(imgInput,(self.left_Pos2,(linePos_2+30)),(self.left_Pos2,(linePos_2-30)),(64,128,255),2)
				cv2.line(imgInput,(self.right_Pos2,(linePos_2+30)),(self.right_Pos2,(linePos_2-30)),(64,128,255),2)
				cv2.line(imgInput,(0,linePos_2),(640,linePos_2),(64,128,255),1)

				cv2.line(imgInput,((self.center-20),int((linePos_1+linePos_2)/2)),((self.center+20),int((linePos_1+linePos_2)/2)),(0,0,0),1)
				cv2.line(imgInput,((self.center),int((linePos_1+linePos_2)/2+20)),((self.center),int((linePos_1+linePos_2)/2-20)),(0,0,0),1)
			except:
				pass

		elif self.CVMode == 'watchDog':
			if self.drawing:
				cv2.rectangle(imgInput, (self.mov_x, self.mov_y), (self.mov_x + self.mov_w, self.mov_y + self.mov_h), (128, 255, 0), 1)

		return imgInput


	def watchDog(self, imgInput):
		timestamp = datetime.datetime.now()
		gray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		if self.avg is None:
			print("[INFO] starting background model...")
			self.avg = gray.copy().astype("float")
			return 'background model'

		cv2.accumulateWeighted(gray, self.avg, 0.5)
		self.frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))


		self.thresh = cv2.threshold(self.frameDelta, 5, 255,
			cv2.THRESH_BINARY)[1]
		self.thresh = cv2.dilate(self.thresh, None, iterations=2)
		self.cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		self.cnts = imutils.grab_contours(self.cnts)

		for c in self.cnts:
			if cv2.contourArea(c) < 5000:
				continue

			(self.mov_x, self.mov_y, self.mov_w, self.mov_h) = cv2.boundingRect(c)
			self.drawing = 1
			
			self.motionCounter += 1
			self.lastMovtionCaptured = timestamp
		self.pause()


	def findLineCtrl(self, posInput, setCenter):
		if posInput:
			if posInput > 480:
				move.commandInput('right')
				print('right')
				pass
			elif posInput <180:
				move.commandInput('left')
				print('left')
				pass
			else:
				move.commandInput('forward')
				print('forward')
				pass


	def findlineCV(self, frame_image):
		frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
		retval, frame_findline =  cv2.threshold(frame_findline, Threshold, 255, cv2.THRESH_BINARY)
		frame_findline = cv2.erode(frame_findline, None, iterations=2)
		frame_findline = cv2.dilate(frame_findline, None, iterations=2)
		colorPos_1 = frame_findline[linePos_1]
		colorPos_2 = frame_findline[linePos_2]
		try:
			lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
			lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

			lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
			lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)

			if lineIndex_Pos1 !=[]:
				if abs(lineIndex_Pos1[0][-1] - lineIndex_Pos1[0][0]) > 500:
					print("Tracking color not found")
					findLineMove = 0 
				else:
					findLineMove = 1
			elif lineIndex_Pos2!= []:
				if abs(lineIndex_Pos2[0][-1] - lineIndex_Pos2[0][0]) > 500:
					print("Tracking color not found")
					findLineMove = 0
				else:
					findLineMove = 1
			if lineColorCount_Pos1 == 0:
				lineColorCount_Pos1 = 1
			if lineColorCount_Pos2 == 0:
				lineColorCount_Pos2 = 1
			self.left_Pos1 = lineIndex_Pos1[0][1] 
			self.right_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1-2]   # 

			self.center_Pos1 = int((self.left_Pos1+self.right_Pos1)/2)

			self.left_Pos2 =  lineIndex_Pos2[0][1]
			self.right_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2-2]
			self.center_Pos2 = int((self.left_Pos2+self.right_Pos2)/2)

			self.center = int((self.center_Pos1+self.center_Pos2)/2)
		except:
			center = None
			pass

		self.findLineCtrl(self.center, 320)
		self.pause()


	def servoMove(ID, Dir, errorInput):
		if ID == 12:
			errorGenOut = CVThread.kalman_filter_X.kalman(errorInput)
			CVThread.P_anglePos += 0.15*(errorGenOut*Dir)*CVThread.cameraDiagonalW/CVThread.videoW

			if abs(errorInput) > CVThread.tor:
				CVThread.scGear.moveAngle(ID,CVThread.P_anglePos)
				CVThread.X_lock = 0
			else:
				CVThread.X_lock = 1
		elif ID == 13:
			errorGenOut = CVThread.kalman_filter_Y.kalman(errorInput)
			CVThread.T_anglePos += 0.15*(errorGenOut*Dir)*CVThread.cameraDiagonalH/CVThread.videoH

			if abs(errorInput) > CVThread.tor:
				CVThread.scGear.moveAngle(ID,CVThread.T_anglePos)
				CVThread.Y_lock = 0
			else:
				CVThread.Y_lock = 1
		else:
			print('No servoPort %d assigned.'%ID)


	def findColor(self, frame_image):
		hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, colorLower, colorUpper)#1
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		center = None
		if len(cnts) > 0:
			self.findColorDetection = 1
			c = max(cnts, key=cv2.contourArea)
			((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			X = int(self.box_x)
			Y = int(self.box_y)
			error_Y = 240 - Y
			error_X = 320 - X
			CVThread.servoMove(CVThread.P_servo, CVThread.P_direction, -error_X)
			CVThread.servoMove(CVThread.T_servo, CVThread.T_direction, -error_Y)

		else:
			self.findColorDetection = 0
		self.pause()


	def pause(self):
		self.__flag.clear()

	def resume(self):
		self.__flag.set()

	def run(self):
		while 1:
			self.__flag.wait()
			if self.CVMode == 'none':
				move.commandInput('stand')
				move.commandInput('no')
				continue
			elif self.CVMode == 'findColor':
				self.CVThreading = 1
				self.findColor(self.imgCV)
				self.CVThreading = 0
			elif self.CVMode == 'findlineCV':
				self.CVThreading = 1
				self.findlineCV(self.imgCV)
				self.CVThreading = 0
			elif self.CVMode == 'watchDog':
				self.CVThreading = 1
				self.watchDog(self.imgCV)
				self.CVThreading = 0
			pass


class Camera(BaseCamera):
    video_source = 0
    modeSelect = 'none'

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        HUE_1 = invarH + 15
        HUE_2 = invarH - 15
        if HUE_1 > 180:
            HUE_1 = 180
        if HUE_2 < 0:
            HUE_2 = 0

        SAT_1 = invarS + 150
        SAT_2 = invarS - 150
        if SAT_1 > 255:
            SAT_1 = 255
        if SAT_2 < 0:
            SAT_2 = 0

        VAL_1 = invarV + 150
        VAL_2 = invarV - 150
        if VAL_1 > 255:
            VAL_1 = 255
        if VAL_2 < 0:
            VAL_2 = 0

        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d' % (HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d' % (HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def linePosSet_1(self, invar):
        global linePos_1
        linePos_1 = invar

    def linePosSet_2(self, invar):
        global linePos_2
        linePos_2 = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    def Threshold(self, value):
        global Threshold
        Threshold = value

    def ThresholdOK(self):
        global Threshold
        return Threshold

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        global ImgIsNone, hflip, vflip
        picam2 = Picamera2()

        preview_config = picam2.preview_configuration
        preview_config.size = (640, 480)
        preview_config.format = 'RGB888'
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
            print("\nPlease check whether the camera is connected well,  \
                  and disable the \"legacy camera driver\" on raspi-config")

        cvt = CVThread()
        cvt.start()

        while True:
            start_time = time.time()
            img = picam2.capture_array()

            if img is None:
                if ImgIsNone == 0:
                    print("--------------------")
                    print("\033[31merror: Unable to read camera data.\033[0m")
                    print("Use the command: \033[34m'sudo killall python3'\033[0m. Close the self-starting program webServer.py")
                    print("Press the keyboard keys \033[34m'Ctrl + C'\033[0m multiple times to exit the current program.")
                    print("--------Ctrl+C quit-----------")
                    ImgIsNone = 1
                continue

            if Camera.modeSelect == 'none':
                cvt.pause()
            else:
                if not cvt.CVThreading:
                    cvt.mode(Camera.modeSelect, img)
                    cvt.resume()
                try:
                    img = cvt.elementDraw(img)
                except:
                    pass

            if cv2.imencode('.jpg', img)[0]:
                yield cv2.imencode('.jpg', img)[1].tobytes()