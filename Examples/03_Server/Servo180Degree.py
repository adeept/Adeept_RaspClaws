#!/usr/bin/env/python3
# File name   : Servo180Degree.py
# Website     : www.Adeept.com
# Author      : Adeept
# Date        : 2025/04/8

from __future__ import division
import time
import RPi.GPIO as GPIO
import sys
import Adafruit_PCA9685


pwm = Adafruit_PCA9685.PCA9685(address=0x5F, busnum=1)
pwm.set_pwm_freq(50)


if __name__ == '__main__':
    channel = 0	# servo port number.
    while True:
        for i in range(0,420):
            pwm.set_pwm(channel, 0, (100+i))
            time.sleep(0.01)
        for i in range(0,420):
            pwm.set_pwm(channel, 0, (520-i))
            time.sleep(0.01)
