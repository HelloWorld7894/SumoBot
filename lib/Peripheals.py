from Control import *
import math

#some definitions
Angle = 70 #TODO: measure angle correctly
std_dist = 13 / math.cos(Angle)

def ToFsetup():
    ToF = Laser_Ranger.sensor
    ToF.start_ranging(SHORT_RANGE)
    return ToF

def Stop(Ranger_Object):
    Ranger_Object.stop_ranging()
    Ranger_Object.close()

def Get_data(Ranger_object, Accel, Line):
    #getting distance, acceleration, line

    #distance
    dist = Ranger_object.get_distance()

    horizontal_dist = math.cos(Angle) * dist

    #acceleration
    accel_data = Accel.read_data_all()
    
    #line
    line_data = Line.GetLineData()

    return [accel_data, line_data, [dist, horizontal_dist]]