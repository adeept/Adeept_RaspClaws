#!/usr/bin/python
# -*- coding: UTF-8 -*-
# File name   : client.py
# Description : client  
# Website	 : www.adeept.com
# E-mail	  : support@adeept.com
# Author	  : Devin
# Date		: 2023/06/14

from socket import *
import sys
import time
import threading as thread
import tkinter as tk
import math
import json
import subprocess
try:
	import cv2
	import zmq
	import base64
	import numpy as np
except:
	print("Couldn't import OpenCV, you need to install it first.")

ip_stu=1		#Shows connection status
c_f_stu = 0
c_b_stu = 0
c_l_stu = 0
c_r_stu = 0
c_ls_stu= 0
c_rs_stu= 0
funcMode= 0
steadyMode = 0
TS_stu  = 0
DS_stu  = 0
tcpClicSock = ''
root = ''
stat = 0
ip_adr = ''
footage_socket = None

Switch_3 = 0
Switch_2 = 0
Switch_1 = 0
SmoothMode = 0
FV_Line = 0
FV_Start = 0
########>>>>>VIDEO<<<<<########
def RGB_to_Hex(r, g, b):
	return ('#'+str(hex(r))[-2:]+str(hex(g))[-2:]+str(hex(b))[-2:]).replace('x','0').upper()
def run_open():
    script_path = 'Footage-GUI.py'
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    print('stdout:', result.stdout)
    print('stderr:', result.stderr)
def video_thread():
	global footage_socket, font, frame_num, fps
	context = zmq.Context()
	footage_socket = context.socket(zmq.SUB)
	footage_socket.connect('tcp://%s:5555'%ip_adr)
	footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

	font = cv2.FONT_HERSHEY_SIMPLEX
	

	frame_num = 0
	fps = 0

def get_FPS():
	global frame_num, fps
	while 1:
		try:
			time.sleep(1)
			fps = frame_num
			frame_num = 0
		except:
			time.sleep(1)



fps_threading=thread.Thread(target=get_FPS)		 #Define a thread for FPV and OpenCV
fps_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
fps_threading.start()									 #Thread starts


########>>>>>VIDEO<<<<<########


def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
	newline=""
	str_num=str(new_num)
	with open("./ip.txt","r") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				line = initial+"%s" %(str_num)
			newline += line
	with open("./ip.txt","w") as f:
		f.writelines(newline)	#Call this function to replace data in '.txt' file


def num_import(initial):			#Call this function to import data from '.txt' file
	with open("./ip.txt") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				r=line
	begin=len(list(initial))
	snum=r[begin:]
	n=snum
	return n	


def call_forward(event):		 #When this function is called,client commands the car to move forward
	global c_f_stu
	if c_f_stu == 0:
		tcpClicSock.send(('forward').encode())
		c_f_stu=1


def call_back(event):			#When this function is called,client commands the car to move backward
	global c_b_stu 
	if c_b_stu == 0:
		tcpClicSock.send(('backward').encode())
		c_b_stu=1

def call_DS(event):
	global DS_stu
	tcpClicSock.send(('DS').encode())
	DS_stu = 0

def call_TS(event):
	global TS_stu
	tcpClicSock.send(('TS').encode())
	TS_stu = 0
def call_FB_stop(event):			#When this function is called,client commands the car to stop moving
	global c_f_stu,c_b_stu,c_l_stu,c_r_stu,c_ls_stu,c_rs_stu
	c_f_stu=0
	c_b_stu=0
	tcpClicSock.send(('DS').encode())


def call_Turn_stop(event):			#When this function is called,client commands the car to stop moving
	global c_f_stu,c_b_stu,c_l_stu,c_r_stu,c_ls_stu,c_rs_stu
	c_l_stu=0
	c_r_stu=0
	c_ls_stu=0
	c_rs_stu=0
	tcpClicSock.send(('TS').encode())


def call_Left(event):			#When this function is called,client commands the car to turn left
	global c_l_stu
	if c_l_stu == 0:
		tcpClicSock.send(('left').encode())
		c_l_stu=1


def call_Right(event):		   #When this function is called,client commands the car to turn right
	global c_r_stu
	if c_r_stu == 0:
		tcpClicSock.send(('right').encode())
		c_r_stu=1


def call_LeftSide(event):
	global c_ls_stu
	if c_ls_stu == 0:
		tcpClicSock.send(('leftside').encode())
		c_ls_stu=1


def call_RightSide(event):
	global c_rs_stu
	if c_rs_stu == 0:
		tcpClicSock.send(('rightside').encode())
		c_rs_stu=1


def call_headup(event):
	tcpClicSock.send(('up').encode())


def call_headdown(event):
	tcpClicSock.send(('down').encode())


def call_headleft(event):
	tcpClicSock.send(('lookleft').encode())


def call_headright(event):
	tcpClicSock.send(('lookright').encode())
 
def call_LRstop(event):
	tcpClicSock.send(('LRstop').encode())
 
def call_UDstop(event):
	tcpClicSock.send(('UDstop').encode())

def call_headhome(event):
	tcpClicSock.send(('home').encode())


def call_steady(event):
	global steadyMode
	if steadyMode == 0:
		tcpClicSock.send(('steadyCamera').encode())
		steadyMode = 1
	else:
		tcpClicSock.send(('steadyCameraOff').encode())
		steadyMode = 0


def call_FindColor(event):
	global funcMode
	if funcMode == 0:
		tcpClicSock.send(('findColor').encode())
		funcMode = 1
	else:
		tcpClicSock.send(('stopCV').encode())
		funcMode = 0


def call_WatchDog(event):
	global funcMode
	if funcMode == 0:
		tcpClicSock.send(('motionGet').encode())
		funcMode = 1
	else:
		tcpClicSock.send(('stopCV').encode())
		funcMode = 0


def call_Smooth(event):
	global SmoothMode
	if SmoothMode == 0:
		tcpClicSock.send(('slow').encode())
		SmoothMode = 1
	else:
		tcpClicSock.send(('fast').encode())
		SmoothMode = 0
def call_Police(event):
	global funcMode
	if funcMode == 0:
		tcpClicSock.send(('police').encode())
		funcMode = 1
	else:
		tcpClicSock.send(('policeOff').encode())
		funcMode = 0

def call_Switch_1(event):
	if Switch_1 == 0:
		tcpClicSock.send(('Switch_1_on').encode())
	else:
		tcpClicSock.send(('Switch_1_off').encode())


def call_Switch_2(event):
	if Switch_2 == 0:
		tcpClicSock.send(('Switch_2_on').encode())
	else:
		tcpClicSock.send(('Switch_2_off').encode())


def call_Switch_3(event):
	if Switch_3 == 0:
		tcpClicSock.send(('Switch_3_on').encode())
	else:
		tcpClicSock.send(('Switch_3_off').encode())


def all_btn_red():
	Btn_Steady.config(bg='#FF6D00', fg='#000000')
	Btn_FindColor.config(bg='#FF6D00', fg='#000000')
	Btn_WatchDog.config(bg='#FF6D00', fg='#000000')
	Btn_Smooth.config(bg='#FF6D00', fg='#000000')
	Btn_Police.config(bg='#FF6D00', fg='#000000')


def all_btn_normal():
	Btn_Steady.config(bg=color_btn, fg=color_text)
	Btn_FindColor.config(bg=color_btn, fg=color_text)
	Btn_WatchDog.config(bg=color_btn, fg=color_text)
	Btn_Smooth.config(bg=color_btn, fg=color_text)
	Btn_Police.config(bg=color_btn, fg=color_text)


def connection_thread():
	global funcMode, Switch_3, Switch_2, Switch_1, SmoothMode,steadyMode
	while 1:
		car_info = (tcpClicSock.recv(BUFSIZ)).decode()
		if not car_info:
			continue
		elif 'findColor' in car_info:
			funcMode = 1
			SmoothMode = 1
			Btn_FindColor.config(bg='#FF6D00', fg='#000000')

		elif 'steadyCamera' == car_info:
			steadyMode = 1
			SmoothMode = 1
			Btn_Steady.config(bg='#FF6D00', fg='#000000')

		elif 'steadyCameraOff' == car_info:
			steadyMode = 0
			SmoothMode = 0
			Btn_Steady.config(bg=color_btn, fg=color_text)

		elif 'motionGet' in car_info:
			funcMode = 1
			SmoothMode = 1
			Btn_WatchDog.config(bg='#FF6D00', fg='#000000')
   
		elif 'slow' in car_info:
			funcMode = 1
			SmoothMode = 1
			Btn_Smooth.config(bg='#FF6D00', fg='#000000')
		elif 'fast' in car_info:
			funcMode = 0
			SmoothMode = 0
			Btn_Smooth.config(bg=color_btn, fg=color_text)
		elif 'police' == car_info:
			funcMode = 1
			SmoothMode = 1
			Btn_Police.config(bg='#FF6D00', fg='#000000')

		elif 'policeOff' == car_info:
			funcMode = 0
			SmoothMode = 0
			Btn_Police.config(bg=color_btn, fg=color_text)

		elif 'Switch_3_on' in car_info:
			Switch_3 = 1
			Btn_Switch_3.config(bg='#4CAF50')

		elif 'Switch_2_on' in car_info:
			Switch_2 = 1
			Btn_Switch_2.config(bg='#4CAF50')

		elif 'Switch_1_on' in car_info:
			Switch_1 = 1
			Btn_Switch_1.config(bg='#4CAF50')

		elif 'Switch_3_off' in car_info:
			Switch_3 = 0
			Btn_Switch_3.config(bg=color_btn)

		elif 'Switch_2_off' in car_info:
			Switch_2 = 0
			Btn_Switch_2.config(bg=color_btn)

		elif 'Switch_1_off' in car_info:
			Switch_1 = 0
			Btn_Switch_1.config(bg=color_btn)

		elif 'CVFL' in car_info:
			FV_Start = 1


		elif 'stopCV' in car_info:
			SmoothMode = 0
			funcMode = 0
			Btn_FindColor.config(bg=color_btn, fg=color_text)
			Btn_WatchDog.config(bg=color_btn, fg=color_text)

		print(car_info)


def Info_receive():
	global CPU_TEP,CPU_USE,RAM_USE
	HOST = ''
	INFO_PORT = 2256							#Define port serial 
	ADDR = (HOST, INFO_PORT)
	InfoSock = socket(AF_INET, SOCK_STREAM)
	InfoSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	InfoSock.bind(ADDR)
	InfoSock.listen(5)					  #Start server,waiting for client
	InfoSock, addr = InfoSock.accept()
	print('Info connected')
	while 1:
		try:
			info_data = ''
			info_data = str(InfoSock.recv(BUFSIZ).decode())
			info_get = info_data.split()
			CPU_TEP,CPU_USE,RAM_USE= info_get
			#print('cpu_tem:%s\ncpu_use:%s\nram_use:%s'%(CPU_TEP,CPU_USE,RAM_USE))
			CPU_TEP_lab.config(text='CPU Temp: %s℃'%CPU_TEP)
			CPU_USE_lab.config(text='CPU Usage: %s'%CPU_USE)
			RAM_lab.config(text='RAM Usage: %s'%RAM_USE)
		except:
			pass


def socket_connect():	 #Call this function to connect with the server
	global ADDR,tcpClicSock,BUFSIZ,ip_stu,ipaddr,ip_adr
	ip_adr=E1.get()	   #Get the IP address from Entry

	if ip_adr == '':	  #If no input IP address in Entry,import a default IP
		ip_adr=num_import('IP:')
		l_ip_4.config(text='Connecting')
		l_ip_4.config(bg='#FF8F00')
		l_ip_5.config(text='Default:%s'%ip_adr)
		pass
	
	SERVER_IP = ip_adr
	SERVER_PORT = 10223   #Define port serial 
	BUFSIZ = 1024		 #Define buffer size
	ADDR = (SERVER_IP, SERVER_PORT)
	tcpClicSock = socket(AF_INET, SOCK_STREAM) #Set connection value for socket

	for i in range (1,6): #Try 5 times if disconnected
		#try:
		if ip_stu == 1:
			print("Connecting to server @ %s:%d..." %(SERVER_IP, SERVER_PORT))
			print("Connecting")
			tcpClicSock.connect(ADDR)		#Connection with the server
		
			print("Connected")
		
			l_ip_5.config(text='IP:%s'%ip_adr)
			l_ip_4.config(text='Connected')
			l_ip_4.config(bg='#558B2F')

			replace_num('IP:',ip_adr)
			E1.config(state='disabled')	  #Disable the Entry
			Btn14.config(state='disabled')   #Disable the Entry
			
			ip_stu=0						 #'0' means connected

			connection_threading=thread.Thread(target=connection_thread)		 #Define a thread for FPV and OpenCV
			connection_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
			connection_threading.start()									 #Thread starts
			
			video_threading=thread.Thread(target=run_open)		 
			video_threading.setDaemon(True)							 
			video_threading.start()									 


			info_threading=thread.Thread(target=Info_receive)		 #Define a thread for FPV and OpenCV
			info_threading.setDaemon(True)							 #'True' means it is a front thread,it would close when the mainloop() closes
			info_threading.start()									 #Thread starts


			break
		else:
			print("Cannot connecting to server,try it latter!")
			l_ip_4.config(text='Try %d/5 time(s)'%i)
			l_ip_4.config(bg='#EF6C00')
			print('Try %d/5 time(s)'%i)
			ip_stu=1
			time.sleep(1)
			continue

	if ip_stu == 1:
		l_ip_4.config(text='Disconnected')
		l_ip_4.config(bg='#F44336')


def connect(event):	   #Call this function to connect with the server
	if ip_stu == 1:
		sc=thread.Thread(target=socket_connect) #Define a thread for connection
		sc.setDaemon(True)					  #'True' means it is a front thread,it would close when the mainloop() closes
		sc.start()							  #Thread starts


def connect_click():	   #Call this function to connect with the server
	if ip_stu == 1:
		sc=thread.Thread(target=socket_connect) #Define a thread for connection
		sc.setDaemon(True)					  #'True' means it is a front thread,it would close when the mainloop() closes
		sc.start()							  #Thread starts



def EC_send(event):#z
		tcpClicSock.send(('setEC %s'%var_ec.get()).encode())
		time.sleep(0.03)


def EC_default(event):#z
	var_ec.set(0)
	tcpClicSock.send(('defEC').encode())


def scale_FL(x,y,w):#1
	global Btn_CVFL,FV_Line,FV_Start
	def lip1_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('CVFLL1 %s'%var_lip1.get()).encode())

	def lip2_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('CVFLL2 %s'%var_lip2.get()).encode())

	def err_send(event):
		time.sleep(0.03)
		tcpClicSock.send(('err %s'%var_err.get()).encode())



	def call_CVFL(event):
		global FV_Start
		if not FV_Start:
			tcpClicSock.send(('CVFL').encode())
			FV_Start = 1
		else:
			tcpClicSock.send(('stopCV').encode())
			FV_Start = 0
    

	def call_WB(event):
		global FV_Line
		if not FV_Line:
			tcpClicSock.send(('CVFLColorSet 0').encode())
			FV_Line = 1
		else:
			tcpClicSock.send(('CVFLColorSet 255').encode())
			FV_Line = 0

	Scale_lip1 = tk.Scale(root,label=None,
	from_=0,to=480,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_lip1,troughcolor='#212121',command=lip1_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_lip1.place(x=x,y=y)							#Define a Scale and put it in position

	Scale_lip2 = tk.Scale(root,label=None,
	from_=0,to=480,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_lip2,troughcolor='#212121',command=lip2_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_lip2.place(x=x,y=y+30)						#Define a Scale and put it in position

	Scale_err = tk.Scale(root,label=None,
	from_=0,to=200,orient=tk.HORIZONTAL,length=w,
	showvalue=1,tickinterval=None,resolution=1,variable=var_err,troughcolor='#212121',command=err_send,fg=color_text,bg=color_bg,highlightthickness=0)
	Scale_err.place(x=x,y=y+60)							#Define a Scale and put it in position

	canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
	canvas_cover.place(x=x,y=y+90)



	Btn_CVFL = tk.Button(root, width=23, text='CV FL',fg=color_text,bg='#212121',relief='ridge')
	Btn_CVFL.place(x=x+w+21,y=y+20)
	Btn_CVFL.bind('<ButtonPress-1>', call_CVFL)

	Btn_WB = tk.Button(root, width=23, text='LineColorSwitch',fg=color_text,bg='#212121',relief='ridge')
	Btn_WB.place(x=x+w+21,y=y+60)
	Btn_WB.bind('<ButtonPress-1>', call_WB)


def loop():					  #GUI
	global tcpClicSock,root,E1,connect,l_ip_4,l_ip_5,color_btn,color_text,Btn14,CPU_TEP_lab,CPU_USE_lab,RAM_lab,canvas_ultra,color_text,var_lip1,var_lip2,var_err,var_R,var_B,var_G,var_ec,Btn_Police,Btn_Steady,Btn_FindColor,Btn_WatchDog,Btn_Fun5,Btn_Fun6,Btn_Switch_1,Btn_Switch_2,Btn_Switch_3,Btn_Smooth,color_bg   #1 The value of tcpClicSock changes in the function loop(),would also changes in global so the other functions could use it.
	while True:
		color_bg='#000000'		#Set background color
		color_text='#E1F5FE'	  #Set text color
		color_btn='#0277BD'	   #Set button color
		color_line='#01579B'	  #Set line color
		color_can='#212121'	   #Set canvas color
		color_oval='#2196F3'	  #Set oval color
		target_color='#FF6D00'

		root = tk.Tk()			#Define a window named root
		root.title('Adeept RaspClaws')	  #Main window title
		root.geometry('565x680')  #1 Main window size, middle of the English letter x.
		root.config(bg=color_bg)  #Set the background color of root window
		try:
			logo =tk.PhotoImage(file = 'logo.png')		 #Define the picture of logo,but only supports '.png' and '.gif'
			l_logo=tk.Label(root,image = logo,bg=color_bg) #Set a label to show the logo picture
			l_logo.place(x=30,y=13)						#Place the Label in a right position
		except:
			pass

		CPU_TEP_lab=tk.Label(root,width=18,text='CPU Temp:',fg=color_text,bg='#212121')
		CPU_TEP_lab.place(x=400,y=15)						 #Define a Label and put it in position

		CPU_USE_lab=tk.Label(root,width=18,text='CPU Usage:',fg=color_text,bg='#212121')
		CPU_USE_lab.place(x=400,y=45)						 #Define a Label and put it in position

		RAM_lab=tk.Label(root,width=18,text='RAM Usage:',fg=color_text,bg='#212121')
		RAM_lab.place(x=400,y=75)						 #Define a Label and put it in position


		l_ip_4=tk.Label(root,width=18,text='Disconnected',fg=color_text,bg='#F44336')
		l_ip_4.place(x=400,y=110)						 #Define a Label and put it in position

		l_ip_5=tk.Label(root,width=18,text='Use default IP',fg=color_text,bg=color_btn)
		l_ip_5.place(x=400,y=145)						 #Define a Label and put it in position

		E1 = tk.Entry(root,show=None,width=16,bg="#37474F",fg='#eceff1')
		E1.place(x=180,y=40)							 #Define a Entry and put it in position

		l_ip_3=tk.Label(root,width=10,text='IP Address:',fg=color_text,bg='#000000')
		l_ip_3.place(x=175,y=15)						 #Define a Label and put it in position


		################################
		#canvas_rec=canvas_ultra.create_rectangle(0,0,340,30,fill = '#FFFFFF',width=0)
		#canvas_text=canvas_ultra.create_text((90,11),text='Ultrasonic Output: 0.75m',fill=color_text)
		################################
		Btn_Switch_1 = tk.Button(root, width=8, text='Port 1',fg=color_text,bg=color_btn,relief='ridge')
		Btn_Switch_2 = tk.Button(root, width=8, text='Port 2',fg=color_text,bg=color_btn,relief='ridge')
		Btn_Switch_3 = tk.Button(root, width=8, text='Port 3',fg=color_text,bg=color_btn,relief='ridge')

		Btn_Switch_1.place(x=30,y=265)
		Btn_Switch_2.place(x=100,y=265)
		Btn_Switch_3.place(x=170,y=265)

		Btn_Switch_1.bind('<ButtonPress-1>', call_Switch_1)
		Btn_Switch_2.bind('<ButtonPress-1>', call_Switch_2)
		Btn_Switch_3.bind('<ButtonPress-1>', call_Switch_3)

		Btn0 = tk.Button(root, width=8, text='Forward',fg=color_text,bg=color_btn,relief='ridge')
		Btn1 = tk.Button(root, width=8, text='Backward',fg=color_text,bg=color_btn,relief='ridge')
		Btn2 = tk.Button(root, width=8, text='Left',fg=color_text,bg=color_btn,relief='ridge')
		Btn3 = tk.Button(root, width=8, text='Right',fg=color_text,bg=color_btn,relief='ridge')



		Btn0.place(x=100,y=195)
		Btn1.place(x=100,y=230)
		Btn2.place(x=30,y=230)
		Btn3.place(x=170,y=230)

		Btn0.bind('<ButtonPress-1>', call_forward)
		Btn0.bind('<ButtonRelease-1>', call_DS)
		Btn1.bind('<ButtonPress-1>', call_back)
		Btn1.bind('<ButtonRelease-1>', call_DS)
		Btn2.bind('<ButtonPress-1>', call_Left)
		Btn2.bind('<ButtonRelease-1>', call_TS)
		Btn3.bind('<ButtonPress-1>', call_Right)
		Btn3.bind('<ButtonRelease-1>', call_TS)

		Btn0.bind('<ButtonRelease-1>', call_FB_stop)
		Btn1.bind('<ButtonRelease-1>', call_FB_stop)
		Btn2.bind('<ButtonRelease-1>', call_Turn_stop)
		Btn3.bind('<ButtonRelease-1>', call_Turn_stop)

		root.bind('<KeyPress-w>', call_forward) 
		root.bind('<KeyRelease-w>', call_DS) 
		root.bind('<KeyPress-a>', call_Left)
		root.bind('<KeyRelease-a>', call_TS)
		root.bind('<KeyPress-d>', call_Right)
		root.bind('<KeyRelease-d>', call_TS)
		root.bind('<KeyPress-s>', call_back)
		root.bind('<KeyRelease-s>', call_DS)

		root.bind('<KeyPress-q>', call_LeftSide)
		root.bind('<KeyPress-e>', call_RightSide)
		root.bind('<KeyRelease-q>', call_Turn_stop)
		root.bind('<KeyRelease-e>', call_Turn_stop)

		root.bind('<KeyRelease-w>', call_FB_stop)
		root.bind('<KeyRelease-a>', call_Turn_stop)
		root.bind('<KeyRelease-d>', call_Turn_stop)
		root.bind('<KeyRelease-s>', call_FB_stop)

		Btn_up = tk.Button(root, width=8, text='Up',fg=color_text,bg=color_btn,relief='ridge')
		Btn_down = tk.Button(root, width=8, text='Down',fg=color_text,bg=color_btn,relief='ridge')
		Btn_left = tk.Button(root, width=8, text='Left',fg=color_text,bg=color_btn,relief='ridge')
		Btn_right = tk.Button(root, width=8, text='Right',fg=color_text,bg=color_btn,relief='ridge')
		Btn_home = tk.Button(root, width=8, text='Home',fg=color_text,bg=color_btn,relief='ridge')
		Btn_up.place(x=400,y=195)
		Btn_down.place(x=400,y=265)
		Btn_left.place(x=330,y=230)
		Btn_right.place(x=470,y=230)
		Btn_home.place(x=400,y=230)
		root.bind('<KeyPress-i>', call_headup) 
		root.bind('<KeyRelease-i>', call_UDstop)
		root.bind('<KeyPress-k>', call_headdown)
		root.bind('<KeyRelease-k>', call_UDstop) 
		root.bind('<KeyPress-j>', call_headleft)
		root.bind('<KeyPress-l>', call_headright)
		root.bind('<KeyRelease-l>', call_LRstop)
		root.bind('<KeyRelease-j>', call_LRstop)
		Btn_up.bind('<ButtonPress-1>', call_headup)
		Btn_up.bind('<ButtonRelease-1>', call_UDstop)
		Btn_down.bind('<ButtonPress-1>', call_headdown)
		Btn_down.bind('<ButtonRelease-1>', call_UDstop)
		Btn_left.bind('<ButtonPress-1>', call_headleft)
		Btn_left.bind('<ButtonRelease-1>', call_LRstop)
		Btn_right.bind('<ButtonPress-1>', call_headright)
		Btn_right.bind('<ButtonRelease-1>', call_LRstop)
		Btn_home.bind('<ButtonPress-1>', call_headhome)

		Btn14= tk.Button(root, width=8,height=2, text='Connect',fg=color_text,bg=color_btn,command=connect_click,relief='ridge')
		Btn14.place(x=315,y=15)						  #Define a Button and put it in position

		root.bind('<Return>', connect)

		var_lip1 = tk.StringVar()#1
		var_lip1.set(440)
		var_lip2 = tk.StringVar()
		var_lip2.set(380)
		var_err = tk.StringVar()
		var_err.set(20)
  
		global canvas_show
		def R_send(event):
			canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
			time.sleep(0.03)


		def G_send(event):
			canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
			time.sleep(0.03)

		def B_send(event):
			canvas_show.config(bg = RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())))
			time.sleep(0.03)  

		def call_SET(event):
			r = int(var_R.get())
			g = int(var_G.get())
			b = int(var_B.get())

			data_str = f"{r}, {g}, {b}"
			message = f"{{'title': 'findColorSet', 'data': [{data_str}]}}"
			tcpClicSock.send(message.encode())
		var_R = tk.StringVar()
		var_R.set(80)

		Scale_R = tk.Scale(root,label=None,
		from_=0,to=255,orient=tk.HORIZONTAL,length=238,
		showvalue=1,tickinterval=None,resolution=1,variable=var_R,troughcolor='#F44336',command=R_send,fg=color_text,bg=color_bg,highlightthickness=0)
		Scale_R.place(x=30,y=330)							#Define a Scale and put it in position

		var_G = tk.StringVar()
		var_G.set(80)

		Scale_G = tk.Scale(root,label=None,
		from_=0,to=255,orient=tk.HORIZONTAL,length=238,
		showvalue=1,tickinterval=None,resolution=1,variable=var_G,troughcolor='#00E676',command=G_send,fg=color_text,bg=color_bg,highlightthickness=0)
		Scale_G.place(x=30,y=360)							#Define a Scale and put it in position

		var_B = tk.StringVar()
		var_B.set(80)

		Scale_B = tk.Scale(root,label=None,
		from_=0,to=255,orient=tk.HORIZONTAL,length=238,
		showvalue=1,tickinterval=None,resolution=1,variable=var_B,troughcolor='#448AFF',command=B_send,fg=color_text,bg=color_bg,highlightthickness=0)
		Scale_B.place(x=30,y=390)							#Define a Scale and put it in position
  
		canvas_cover=tk.Canvas(root,bg=color_bg,height=30,width=510,highlightthickness=0)
		canvas_cover.place(x=30,y=330+90)
		canvas_show=tk.Canvas(root,bg=RGB_to_Hex(int(var_R.get()), int(var_G.get()), int(var_B.get())),height=35,width=170,highlightthickness=0)
		canvas_show.place(x=238+30+21,y=330+15)


		Btn_WB = tk.Button(root, width=23, text='Color Set',fg=color_text,bg='#212121',relief='ridge')
		Btn_WB.place(x=30+238+21,y=330+60)
		Btn_WB.bind('<ButtonPress-1>', call_SET)
  
		var_ec = tk.StringVar() #Z start
		var_ec.set(0)			


		Btn_Steady = tk.Button(root, width=10, text='Steady',fg=color_text,bg=color_btn,relief='ridge')
		Btn_Steady.place(x=30,y=445)
		root.bind('<KeyPress-z>', call_steady)
		Btn_Steady.bind('<ButtonPress-1>', call_steady)

		Btn_FindColor = tk.Button(root, width=10, text='FindColor',fg=color_text,bg=color_btn,relief='ridge')
		Btn_FindColor.place(x=115,y=445)
		root.bind('<KeyPress-z>', call_FindColor)
		Btn_FindColor.bind('<ButtonPress-1>', call_FindColor)

		Btn_WatchDog = tk.Button(root, width=10, text='WatchDog',fg=color_text,bg=color_btn,relief='ridge')
		Btn_WatchDog.place(x=200,y=445)
		root.bind('<KeyPress-z>', call_WatchDog)
		Btn_WatchDog.bind('<ButtonPress-1>', call_WatchDog)

		Btn_Smooth = tk.Button(root, width=10, text='FAST/SLOW',fg=color_text,bg=color_btn,relief='ridge')
		Btn_Smooth.place(x=285,y=445)
		root.bind('<KeyPress-z>', call_Smooth)
		Btn_Smooth.bind('<ButtonPress-1>', call_Smooth)

		Btn_Police = tk.Button(root, width=10, text='Police',fg=color_text,bg=color_btn,relief='ridge')
		Btn_Police.place(x=370,y=445)
		root.bind('<KeyPress-z>', call_Police)
		Btn_Police.bind('<ButtonPress-1>', call_Police)


		scale_FL(30,490,315)#1

		global stat
		if stat==0:			  # Ensure the mainloop runs only once
			root.mainloop()  # Run the mainloop()
			stat=1		   # Change the value to '1' so the mainloop() would not run again.


if __name__ == '__main__':
	try:
		loop()				   # Load GUI
	except:
		tcpClicSock.close()		  # Close socket or it may not connect with the server again
		footage_socket.close()
		cv2.destroyAllWindows()
		pass