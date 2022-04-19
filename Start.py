#local imports
from lib.Control import *
import Main

#other imports
import picamera
import picamera.array

def Startup():
    #Peripheals init

    Accel = Accelerometer(0x68)
    Accel.MPU_init()
    sleep(1)
    #Accel object is also Gyro

    Cam = Camera.camera

    ToF = Laser_Ranger.sensor
    sleep(1)
    ToF.start_ranging(MEDIUM_RANGE) #TODO: Dodělat i pro více range!

    Line = Line_Sensor
    Line.Setup()

    Start_Button = Button
    Start_Button.Setup()

    Bridge = H_Bridge
    Bridge.Setup()

    ServoY = Servo(19)
    ServoX = Servo(26)

    #test rotation
    #ServoY.Rotate(90)
    #ServoX.Rotate(90)

    DetectionTest(Cam, ToF, Accel, Line)

def DetectionTest(Camera, ToF, Accel, Line):
    #Cam test
    with picamera.array.PiRGBArray(Camera) as output:
        Camera.capture(output, "rgb")
        print(output)


if __name__ == "__main__":
    Startup()