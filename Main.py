from Start import *


if __name__ == "__main__":
    Cam, ToF, Accel, Line, Start_Button, Bridge, servos = Startup() #Retrieving sensor objects

    while True:
        if Start_Button.check() == 0: #TODO: check if modify to 0 or 1
            #START
            Run(Cam, ToF, Accel, Line, Start_Button, Bridge, servos)

def Run(Cam, ToF, Accel, Line, Start_Button, Bridge, servos):
    balls = 69