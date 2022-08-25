import math

#some definitions
Angle = 70 #TODO: measure angle correctly
std_dist = 13 / math.cos(Angle)

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