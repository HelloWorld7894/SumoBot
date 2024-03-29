#local imports
from lib.Control import *

#other imports
from picamera import PiCamera
import picamera.array
from time import sleep

def Startup():
    #Peripheals init

    Accel = Accelerometer(0x68)
    Accel.MPU_init()
    sleep(1)
    #Accel object is also Gyro

    Cam = Camera.camera
    Cam.rotation = 180
    Cam.resolution = (640, 480)
    Cam.framerate = 32

    ToF = Laser_Ranger.sensor
    sleep(1)
    


    Line = Line_Sensor
    Line.Setup()

    Bridge = H_Bridge
    Bridge.Setup()

    servo1 = Servo.Setup()
    Servo.Start(servo1)
    #Servo.Start(servo2)

    DetectionTest(ToF, Accel, servo1)

    return Cam, ToF, Accel, Line, Bridge, servo1

def DetectionTest(ToF, Accel, servo):
    #Cam test
    #with picamera.array.PiRGBArray(Camera) as output:
    #    Camera.capture(output, "rgb")
    #    if len(output.array) == 0:
    #        print("ERROR getting data from camera: PER_INIT")
    #        exit(2)
    #print("Picamera test passed...")

    #Time of flight sensor
    Dist = []
    Ranges = [SHORT_RANGE, MEDIUM_RANGE, LONG_RANGE]

    for T_Range in Ranges:
        ToF.start_ranging(T_Range)
        Dist.append(ToF.get_distance())
        ToF.stop_ranging()
        sleep(1)

    for D in Dist:
        if D < 0:
            print("ERROR getting data from ToF: PER_INIT")
            exit(2)
    print("ToF test passed...")
    
    #accelerometer and gyro
    Accel_data, Gyro_data = Accel.read_data_all()
    if None in Accel_data and None in Gyro_data:
        print("ERROR getting data from Accelerometer and Gyrom: PER_INIT")
        exit(1)
    print("Accelerometer and Gyro test passed...")

    #Simple servo test
    Servo.Rotate(servo, 80)
    Servo.Rotate(servo, 90)