from lib.Control import *
from time import sleep

"""
Accelerometer
"""

#Accel = Accelerometer(0x68)
#Accel.MPU_init()
#sleep(1)

#while True:
#    Accel.read_data_all()

"""
Picamera
"""

#Cam = Camera
#for frame in Cam.camera.capture_continuous(Cam.RawCapture, format="bgr", use_video_port=True):
    
#    Img = frame.array

"""
ToF
"""
#ToF = Laser_Ranger.sensor
#sleep(1)
#ToF.start_ranging(SHORT_RANGE)

#while True:
#    distance = ToF.get_distance()
#    sleep(0.1)

#rof.stop_ranging() #unreachable, but just showed how to stop ToF properly

"""
Line Sensor
"""

#Line = Line_Sensor
#Line.Setup()

#while True:
#    print(Line.GetLineData())

"""
Button
"""

#Start_Button = Button
#Start_Button.Setup()
#while True:
#    input = Start_Button.Check()

"""
H-Bridge
"""

#Bridge = H_Bridge
#Bridge.Setup()

#Bridge.Forward(2)
#Bridge.Backward(1)
#Bridge.Left(5, "forward")
#Bridge.Right(5, "forward")