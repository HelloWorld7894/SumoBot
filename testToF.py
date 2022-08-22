from lib.Control import *
from time import sleep
import RPi.GPIO as GPIO

servoX, servoY = Servo.Setup()
Servo.Start(servoX)
Servo.Start(servoY)

DutyX, DutyY = 0, 0

ToF = Laser_Ranger.sensor
sleep(1)
ToF.start_ranging(SHORT_RANGE)

"""
try:
    while True:
        DutyX = 90
        Servo.Rotate(servoX, DutyX)

        distance = ToF.get_distance()
        sleep(0.1)
        print(distance)

except KeyboardInterrupt:
        ToF.stop_ranging()
"""

ToF.stop_ranging()

DutyX = 45
Servo.Rotate(servoX, DutyX)