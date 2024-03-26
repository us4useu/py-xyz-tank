import pytrinamic
from pytrinamic.connections import ConnectionManager
from pytrinamic.modules import TMCM1276
import time

class XyzController :
    def __init__(self) :
        cm = ConnectionManager("--interface pcan_tmcl")
        can_interface = cm.connect()

        # Initialize TMCM modules
        self.axisX = TMCM1276(can_interface, 11)
        self.axisY = TMCM1276(can_interface, 12)
        self.axisZ = TMCM1276(can_interface, 13)

        self.motorX = self.axisX.motors[0]
        self.motorY = self.axisY.motors[0]
        self.motorZ = self.axisZ.motors[0]

        self.stop()

    def is_target_reached_x(self) :
        #print(str(self.motorX.get_position_reached()))
        if self.motorX.get_position_reached() == 1 :
            print("target X reached")
            return True
        else :
            return False

    def is_target_reached_y(self) :
        #print(str(self.motorY.get_position_reached()))
        if self.motorY.get_position_reached() == 1 :
            print("target Y reached")
            return True
        else :
            return False

    def is_target_reached_z(self) :
        #print(str(self.motorZ.get_position_reached()))
        if self.motorZ.get_position_reached() == 1 :
            print("target Z reached")
            return True
        else :
            return False
        
    def is_target_reached(self) :
        if (not(self.is_target_reached_x()) or not(self.is_target_reached_y()) or not(self.is_target_reached_z())):
            return False
        else :
            return True

    def is_home_reached_x(self) :
        #print("X stop = " + str(self.motorX.get_axis_parameter(self.motorX.AP.LeftEndstop)))
        if self.motorX.get_axis_parameter(self.motorX.AP.LeftEndstop) == 1 :
            return True
        else :
            return False

    def is_home_reached_y(self) :
        #print("Y stop = " + str(self.motorY.get_axis_parameter(self.motorY.AP.LeftEndstop)))
        if self.motorY.get_axis_parameter(self.motorY.AP.LeftEndstop) == 1 :
            return True
        else :
            return False

    def is_home_reached_z(self) :
        #print("Z stop = " + str(self.motorX.get_axis_parameter(self.motorZ.AP.LeftEndstop)))
        if self.motorZ.get_axis_parameter(self.motorZ.AP.LeftEndstop) == 1 :
            return True
        else :
            return False
        
    def stop(self) :
        self.motorX.stop()
        self.motorY.stop()
        self.motorZ.stop()


    def goto_home(self) :
        velocity = 25000
        self.motorX.move_to(-999999999, velocity)
        self.motorY.move_to(-999999999, velocity)
        self.motorZ.move_to(-999999999, velocity)

        while self.is_home_reached_x() != True or self.is_home_reached_y() != True or self.is_home_reached_z() != True:
            pass

        self.stop()
        print("XYZ home endstops reached")

        return
    
    def goto_xyz_absolute(self, x, y, z) :
        velocity = 100000
        self.motorX.move_to(x, velocity)
        self.motorY.move_to(y, velocity)
        self.motorZ.move_to(z, velocity)

        while(not(self.is_target_reached())):
            pass

        return

    def goto_xyz_relative(self, x, y, z) :
        velocity = 100000
        self.motorX.move_by(x, velocity)
        self.motorY.move_by(y, velocity)
        self.motorZ.move_by(z, velocity)

        while(not(self.is_target_reached())):
            pass

        return

    def zero_absolute_pos(self) :
        self.motorX.set_actual_position(0)
        self.motorY.set_actual_position(0)
        self.motorZ.set_actual_position(0)
        return

    def get_actual_pos(self) :
        x = self.motorX.get_actual_position()
        y = self.motorY.get_actual_position()
        z = self.motorZ.get_actual_position()
        return x, y, z
    
    def set_usteps(self, res) :
        if res > 8 :
            print("Invalid microstep resolution requested")
            return self.motorX.get_axis_parameter(self.motorX.AP.MicrostepResolution)
        else :
            self.motorX.set_axis_parameter(self.motorX.AP.MicrostepResolution, res)