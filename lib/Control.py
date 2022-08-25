import RPi.GPIO as GPIO
from smbus2 import smbus2

from picamera import PiCamera
from picamera.array import PiRGBArray

import VL53L1X

from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#variables for servos
DEFAULT_POS = 7
MIN_POS = 3
MAX_POS = 12 
#conversion   
DegreesToDuty = 0.066666667 #12 / 180
DistInSec = 11.9 #1/8 obvodu otáčení robota ku 1 otáčce za 1 sekundu
DegreesToDist = 0.26 #by computations 90 degrees equals 23.4 cm -> 1 degree 0.26 cm
#variables
Degrees = 0
LastRotation = False

#MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

#VL53L1X distances
UNCHANGED = 0
SHORT_RANGE = 1
MEDIUM_RANGE = 2
LONG_RANGE = 3

#line sensor pins
FRONT = [21, 16] #removed middle pin 20 because my sensors are retarded
BACK = [7, 25] #same here for middle pin 8



#H bridge pins
A1 = 24
B1 = 23
A2 = 15
B2 = 18

class Accelerometer:
    def __init__(self, address): #address is 0x68
        self.address = address

    def MPU_init(self):
        self.bus = smbus2.SMBus(1)

        #write to sample rate register
        self.bus.write_byte_data(self.address, SMPLRT_DIV, 7)
	
	    #Write to power management register
        self.bus.write_byte_data(self.address, PWR_MGMT_1, 1)
	
	    #Write to Configuration register
        self.bus.write_byte_data(self.address, CONFIG, 0)
	
	    #Write to Gyro configuration register
        self.bus.write_byte_data(self.address, GYRO_CONFIG, 24)
	
	    #Write to interrupt enable register
        self.bus.write_byte_data(self.address, INT_ENABLE, 1)

    def read_raw_data(self, reg_address):
        high = self.bus.read_byte_data(self.address, reg_address)
        low = self.bus.read_byte_data(self.address, reg_address + 1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

    def read_data_all(self):
        acc_x = self.read_raw_data(ACCEL_XOUT_H)
        acc_y = self.read_raw_data(ACCEL_YOUT_H)
        acc_Z = self.read_raw_data(ACCEL_ZOUT_H)

        gyro_x = self.read_raw_data(GYRO_XOUT_H)
        gyro_y = self.read_raw_data(GYRO_YOUT_H)
        gyro_z = self.read_raw_data(GYRO_ZOUT_H)

        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_Z / 16384.0

        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        #print("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	
        sleep(0.5)
        return [Ax, Ay, Az], [Gx, Gy, Gz]

class Camera:
    camera = PiCamera() #TODO: this is also pretty much stupid, rewrite it



class Laser_Ranger:
    sensor = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
    sensor.open()



class Line_Sensor:
    def Setup():
        for pin in (FRONT + BACK):
            GPIO.setup(pin, GPIO.IN)
    def GetLineData():
        values = []

        for pin in (FRONT + BACK):
            values.append(GPIO.input(pin))
        
        return values



class H_Bridge:
    def Setup():

        GPIO.setup(A1, GPIO.OUT)
        GPIO.setup(B1, GPIO.OUT)

        GPIO.setup(A2, GPIO.OUT)
        GPIO.setup(B2, GPIO.OUT)

    def Stop():
        GPIO.output(A1, GPIO.LOW)
        GPIO.output(B1, GPIO.LOW)

        GPIO.output(A2, GPIO.LOW)
        GPIO.output(B2, GPIO.LOW)
        #GPIO.cleanup()


    def Forward(dist):

        GPIO.output(A1, GPIO.LOW)
        GPIO.output(B1, GPIO.HIGH)

        GPIO.output(A2, GPIO.LOW)
        GPIO.output(B2, GPIO.HIGH)
        sleep(dist / DistInSec)
        H_Bridge.Stop()
        

    def Backward(dist):
        
        GPIO.output(A1, GPIO.HIGH)
        GPIO.output(B1, GPIO.LOW)

        GPIO.output(A2, GPIO.HIGH)
        GPIO.output(B2, GPIO.LOW)
        sleep(dist / DistInSec)
        H_Bridge.Stop()

    def Left(dist, type):

        if type == "backward":
            GPIO.output(A1, GPIO.LOW)
            GPIO.output(B1, GPIO.HIGH)

            GPIO.output(A2, GPIO.LOW)
            GPIO.output(B2, GPIO.LOW)
        elif type == "forward":
            GPIO.output(A1, GPIO.HIGH)
            GPIO.output(B1, GPIO.LOW)

            GPIO.output(A2, GPIO.LOW)
            GPIO.output(B2, GPIO.LOW)

        sleep(dist / DistInSec)
        H_Bridge.Stop()

    def Right(dist, type):

        if type == "backward":
            GPIO.output(A1, GPIO.LOW)
            GPIO.output(B1, GPIO.LOW)

            GPIO.output(A2, GPIO.LOW)
            GPIO.output(B2, GPIO.HIGH)
        elif type == "forward":
            GPIO.output(A1, GPIO.LOW)
            GPIO.output(B1, GPIO.LOW)

            GPIO.output(A2, GPIO.HIGH)
            GPIO.output(B2, GPIO.LOW)

        sleep(dist / DistInSec)
        H_Bridge.Stop()

class Servo:

    def Setup():
        GPIO.setup(19, GPIO.OUT)
        GPIO.setup(26, GPIO.OUT)

        servo1 = GPIO.PWM(19, 50)
        #servo2 = GPIO.PWM(26, 50)

        return servo1#, servo2

    def Start(servo):
        servo.start(0)

    def Stop(servo):
        servo.stop()

    def Rotate(servo, angle):
        #could be implemented better but i dont care if it works
        Degrees = angle

        Duty = round(DegreesToDuty * angle)
        servo.ChangeDutyCycle(Duty)
        sleep(0.5)

        Servo.CleanRotation(servo)

    def CleanRotation(servo):
        servo.ChangeDutyCycle(5)
        sleep(2)

