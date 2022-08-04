from Start import *

#Initial switch (changed by GPIO event)
Switch = False

def Run(Cam, ToF, Accel, Line, Start_Button, Bridge, servos):
    

if __name__ == "__main__":
    Cam, ToF, Accel, Line, Start_Button, Bridge, servos = Startup() #Retrieving sensor objects

    while True:
        if Switch == True: #TODO: check if modify to 0 or 1
            #START
            Run(Cam, ToF, Accel, Line, Start_Button, Bridge, servos)