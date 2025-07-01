import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class PathBuilder:
    def __init__(self, spanX, spanY, spanZ, stepX, stepY, stepZ, priority = "xyz", Xup = True, Yup = True, Zup = True):
        self.startX = int(1e6*spanX[0])
        self.startY = int(1e6*spanY[0])
        self.startZ = int(1e6*spanZ[0])
        self.endX = int(1e6*spanX[1]) #mm
        self.endY = int(1e6*spanY[1])
        self.endZ = int(1e6*spanZ[1])
        self.stepX = int(1e6*stepX)
        self.stepY = int(1e6*stepY)
        self.stepZ = int(1e6*stepZ)
        self.priority = priority
        self.Xup = Xup
        self.Yup = Yup
        self.Zup = Zup

        if priority != "xyz" and priority != "xzy" and priority != "yxz" and priority != "yzx" and priority != "zxy" and priority != "zyx":
            raise Exception("Invalid priority")

    def _frange(self, start, stop, step, dir = True):
        if dir:
            while start <= stop:
                yield start
                start += step
        else:
            while stop >= start:
                yield stop
                stop -= step

    def generate_path(self):
        path = []

        dir1 = True
        dir2 = True
        dir3 = True

        if self.priority[0] == 'x' :
            axis1Start = self.startX 
            axis1End = self.endX 
            axis1Step = self.stepX
            if not self.Xup :
                dir1 = False
            if self.priority[1] == 'y' :
                axis2Start = self.startY 
                axis2End = self.endY 
                axis2Step = self.stepY
                axis3Start = self.startZ 
                axis3End = self.endZ
                axis3Step = self.stepZ
                if not self.Yup :
                    dir2 = False
                if not self.Zup :
                    dir3 = False
            else :
                axis2Start = self.startZ 
                axis2End = self.endZ
                axis2Step = self.stepZ
                axis3Start = self.startY 
                axis3End = self.endY 
                axis3Step = self.stepY
                if not self.Zup :
                    dir2 = False
                if not self.Yup :
                    dir3 = False

        elif self.priority[0] == 'y' :
            axis1Start = self.startY 
            axis1End = self.endY 
            axis1Step = self.stepY
            if not self.Yup :
                dir1 = False   
            if self.priority[1] == 'x' :
                axis2Start = self.startX 
                axis2End = self.endX 
                axis2Step = self.stepX
                axis3Start = self.startZ 
                axis3End = self.endZ
                axis3Step = self.stepZ
                if not self.Xup :
                    dir2 = False
                if not self.Zup :
                    dir3 = False
            else :
                axis2Start = self.startZ 
                axis2End = self.endZ
                axis2Step = self.stepZ
                axis3Start = self.startX 
                axis3End = self.endX 
                axis3Step = self.stepX
                if not self.Zup :
                    dir2 = False
                if not self.Xup :
                    dir3 = False
            
        elif self.priority[0] == 'z' :
            axis1Start = self.startZ 
            axis1End = self.endZ
            axis1Step = self.stepZ
            if not self.Zup :
                dir1 = False
            if self.priority[1] == 'x' :
                axis2Start = self.startX 
                axis2End = self.endX 
                axis2Step = self.stepX
                axis3Start = self.startY
                axis3End = self.endY
                axis3Step = self.stepY
                if not self.Xup :
                    dir2 = False
                if not self.Yup :
                    dir3 = False
            else :
                axis2Start = self.startY 
                axis2End = self.endY
                axis2Step = self.stepY
                axis3Start = self.startX 
                axis3End = self.endX 
                axis3Step = self.stepX
                if not self.Yup :
                    dir2 = False
                if not self.Xup :
                    dir3 = False

        x = 0
        y = 0
        z = 0

        for pos3 in self._frange(axis3Start, axis3End, axis3Step, dir3):
            for pos2 in self._frange(axis2Start, axis2End, axis2Step, dir2):
                #if ipos2 % 2 == 0 :

                for pos1 in self._frange(axis1Start, axis1End, axis1Step, dir1):
                    if self.priority[0] == 'x' :
                        x = pos1/1e6
                        if self.priority[1] == 'y' :
                            y = pos2/1e6
                            z = pos3/1e6
                        else:
                            y = pos3/1e6
                            z = pos2/1e6
                            
                    elif self.priority[0] == 'y' :
                        y = pos1/1e6
                        if self.priority[1] == 'x' :
                            x = pos2/1e6
                            z = pos3/1e6
                        else:
                            x = pos3/1e6
                            z = pos2/1e6

                    elif self.priority[0] == 'z' :
                        z = pos1/1e6
                        if self.priority[1] == 'x' :
                            x = pos2/1e6
                            y = pos3/1e6
                        else:
                            x = pos3/1e6
                            y = pos2/1e6

                    path.append((x,y,z))

                    # Toggle dir1 only if priority[0] is not 'x'
                    if self.priority[0] != 'z':
                        dir1 = not dir1

                # Toggle dir2 only if priority[1] is not 'x'
                if self.priority[1] != 'z':
                    dir2 = not dir2

            # Toggle dir3 only if priority[2] is not 'x'
            if self.priority[2] != 'z':
                dir3 = not dir3
                    #path.append((x,y,z))
                #dir1 = not dir1
            #dir2 = not dir2


        
        return path
