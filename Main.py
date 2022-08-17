from Start import Startup
from time import sleep

#Picamera
from picamera.array import PiRGBArray
from picamera import PiCamera  #kinda unused ngl
import lib.Camera as Camera #library for camera algorithms

#Image modification libs
import cv2
import numpy

#System libs
import sys
import os
import RPi.GPIO as GPIO

#GPIO event button
class Button:
    Iter = 0
    Switch = False

    def Setup():
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(12, GPIO.RISING, callback=Button.ButtonCallback)
    
    def ButtonCallback(channel):
        sleep(0.2)
        print("Invoked start button")

        rawCapture = PiRGBArray(Cam, size = (640, 480))
        sleep(0.1)

        print("START")

        #Camera data extraction
        for frame in Cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):

            if GPIO.input(12) == GPIO.LOW:
                print("Exit")
                exit(1)

            image = frame.array
            rawCapture.truncate(0)
            rawCapture.seek(0)

            cv2.imshow("Frame", image)
            cv2.waitKey(1)

"""
INIT
"""
Cam, ToF, Accel, Line, Bridge, servos = Startup() #Retrieving sensor objects
Start_Button = Button
Start_Button.Setup()

while True:
    pass #Very weird, i know, but its for initial loop