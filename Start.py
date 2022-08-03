#local imports
from lib.Control import *
import Main

#other imports
import picamera
import picamera.array
from time import sleep

def Startup():
    #Peripheals init

    Accel = Accelerometer(0x68)
    Accel.MPU_init()
    sleep(1)
    #Accel object is also Gyro

    Cam = Camera.camera

    ToF = Laser_Ranger.sensor
    sleep(1)
    


    Line = Line_Sensor
    Line.Setup()

    Start_Button = Button
    Start_Button.Setup()

    Bridge = H_Bridge
    Bridge.Setup()

    servo1, servo2 = Servo.Setup()
    Servo.Start(servo1)
    Servo.Start(servo2)

    DetectionTest(Cam, ToF, Accel, [servo1, servo2])

    return Cam, ToF, Accel, Line, Start_Button, Bridge, [servo1, servo2]

def DetectionTest(Camera, ToF, Accel, servos):
    #Cam test
    with picamera.array.PiRGBArray(Camera) as output:
        Camera.capture(output, "rgb")
        if len(output.array) == 0:
            print("ERROR getting data from camera: PER_INIT")
            exit(2)

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
    
    #accelerometer and gyro
    Accel_data, Gyro_data = Accel.read_data_all()
    if None in Accel_data and None in Gyro_data:
        print("ERROR getting data from Accelerometer and Gyrom: PER_INIT")
        exit(1)

    #Simple servo test
    Servo.Rotate(servos[1], 60)
    Servo.Rotate(servos[2], 60)

    Servo.Rotate(servos[1], 90)
    Servo.Rotate(servos[2], 90)