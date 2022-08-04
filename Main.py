from Start import Startup
from time import sleep

#Picamera
from picamera.array import PiRGBArray
from picamera import PiCamera  #kinda unused ngl

#Image modification libs
import cv2
import numpy

#System libs
import sys
import os
import RPi.GPIO as GPIO

#GPIO event button
class Button:
    Switch = False

    def Setup():
        GPIO.setup(12, GPIO.IN)
        GPIO.add_event_detect(12, GPIO.RISING, callback=Button.ButtonCallback)
    
    def ButtonCallback(channel):
        sleep(0.2)

        if Button.Switch: 
            Button.Switch = False
            os.execv(sys.executable, ["python"] + [sys.argv[0]]) #restart the program and wait for initial switch
        else: 
            Button.Switch = True

def Run(Cam, ToF, Accel, Line, Bridge, servos):
    
    #Camera data extraction
    rawCapture = PiRGBArray(Cam, size = (640, 480))
    sleep(0.1)

    print("START")

    for frame in Cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):
        image = frame.array

        cv2.imshow("Frame", image)
        cv2.waitKey(1)
    
"""
INIT
"""
Cam, ToF, Accel, Line, Bridge, servos = Startup() #Retrieving sensor objects
Start_Button = Button
Start_Button.Setup()

while True:
    if Start_Button.Switch == True:
        #START
        Run(Cam, ToF, Accel, Line, Bridge, servos)