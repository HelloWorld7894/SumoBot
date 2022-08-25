from Start import Startup
from time import sleep

#Picamera
from picamera.array import PiRGBArray
from picamera import PiCamera  #kinda unused ngl

import lib.Camera as Camera
import lib.Control as Control #library for camera algorithms
import lib.Peripheals as Peripheals #library for laser_ranger, accelerometer and line sensors
from lib.Mapping import *

from lib.Multithreading import Thread_Inherit #Running this script in more threads

#Image modification libs
import cv2
import numpy as np


#System libs
import sys
import os
import RPi.GPIO as GPIO
import random

#functions

#happens when robot touches lines
def EscapeFront():
    Bridge.Forward(7) #7cm escape

    #this is such a stupid way of decision making #TODO: rework!
    choice = random.randint(0, 1)
    if choice == 1:
        Bridge.Right(6, "forward")
    else:
        Bridge.Left(6, "forward")

def EscapeBack():
    Bridge.Backward(7)
    
    #same here
    choice = random.randint(0, 1)
    if choice == 1:
        Bridge.Right(6, "backward")
    else:
        Bridge.Left(6, "backward")

def ToFsetup(Ranger):
    print("ToF started")
    Ranger.start_ranging(Control.SHORT_RANGE)

def ToFstop(Ranger):
    print("ToF closed")
    Ranger.stop_ranging()
    Ranger.close()

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

        #ToF setup
        ToFsetup(Laser_Ranger)

        print("START")

        #Camera data extraction
        for frame in Cam.capture_continuous(rawCapture, format="bgr", use_video_port = True):
            rawCapture.truncate(0)
            rawCapture.seek(0)

            for i in Control.FRONT:
                if GPIO.input(i) == 1:
                    EscapeBack()
            for i in Control.BACK:
                if GPIO.input(i) == 1:
                    EscapeFront()

            if GPIO.input(12) == GPIO.LOW:
                print("Exit")
                ToFstop(Laser_Ranger)
                exit(1)

            #image conversion
            full_image = frame.array
            
            #Multithreading setup
            Thread1 = Thread_Inherit(target=Camera.LBdetection, args=(full_image, ))
            Thread2 = Thread_Inherit(target=Peripheals.Get_data, args=(Laser_Ranger, Accel, Line, ))
            
            #start
            Thread1.start()
            Thread2.start()

            #Getting output
            ApproxPos, Boundaries = Thread1.join() #TODO: finish
            Data = Thread2.join()

            Thread1.kill()
            Thread2.kill()

            #ApproxPos, Boundaries = Camera.LBdetection(full_image)
            #Data = Peripheals.Get_data(Laser_Ranger, Accel, Line)

            print(ApproxPos, Boundaries)

            #check if rotation was invoked
            if Control.LastRotation:
                #Charge
                if len(Boundaries) == 0:
                    #5cm
                    Bridge.Forward(5)
                else:
                    #Controlling charge by boundaries
                    if Boundaries[0] <= 60:
                        Dist = Control.DegreesToDist * 45
                        Bridge.Right(Dist)
                    elif 60 > Boundaries[0] <= 120:
                        Dist = Control.DegreesToDist * 90
                        Bridge.Right(Dist)
                    elif 120 > Boundaries[0] <= 180:
                        Dist = Control.DegreesToDist * 90
                        Bridge.Left(Dist)
                    else:
                        Dist = Control.DegreesToDist * 45
                        Bridge.Left(Dist)

                    Bridge.Forward(Boundaries[1] / 32)
                Control.LastRotation = False

            #checking distance
            dist_dev = Peripheals.std_dist - Data[2][0]
            if abs(dist_dev) > 0.75 and dist_dev > 0: #in case that laser ranger would range off track
                #object detected
                Degrees_center = Control.Degrees - 90
                Dist = Control.DegreesToDist * abs(Degrees_center)
                if Degrees_center > 0:
                    #turn right
                    Bridge.Right(Dist, "forward")
                else:
                    #turn left
                    Bridge.Left(Dist, "forward")

                servo.Rotate(90)
                
                Control.LastRotation = True

            else:
                if len(ApproxPos) != 0:
                    #Camera centering
                    DegreeChange = Camera.CameraCenter(ApproxPos)
                    NewDegrees = Control.Degrees + DegreeChange
                    Control.Servo.Rotate(servo, NewDegrees)

                else:
                    #Camera random centering
                    angle = random.randint(0, 180)
                    Control.Servo.Rotate(servo, angle)
            
"""
INIT
"""

Cam, Laser_Ranger, Accel, Line, Bridge, servo = Startup() #Retrieving sensor objects
Start_Button = Button
Start_Button.Setup()

while True:
    pass #Very weird, i know, but its for initial loop