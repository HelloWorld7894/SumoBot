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

    """
    PENDING TESTING
    #ServoY = Servo(19)
    #ServoX = Servo(26)

    #ServoY.Start()
    #ServoX.Start()
    sleep(0.2)


    #test rotation
    #ServoY.Rotate(90)
    #ServoX.Rotate(90)
    #sleep(0.5)

    #ServoY.CleanRotation()
    #ServoX.CleanRotation()

    #ServoY.Stop()
    #ServoX.Stop()
    """
    DetectionTest(Cam, ToF, Accel, Line)

def DetectionTest(Camera, ToF, Accel, Line):
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
    Accel_data1, Gyro_data1 = Accel.read_data_all()
    


if __name__ == "__main__":
    Startup()