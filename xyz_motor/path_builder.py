import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class PathBuilder:
    def __init__(self, startX, startY, startZ, endX, endY, endZ, stepX, stepY, stepZ):
        self.startX = int(1e6*startX)
        self.startY = int(1e6*startY)
        self.startZ = int(1e6*startZ)
        self.endX = int(1e6*endX) #mm
        self.endY = int(1e6*endY)
        self.endZ = int(1e6*endZ)
        self.stepX = int(1e6*stepX)
        self.stepY = int(1e6*stepY)
        self.stepZ = int(1e6*stepZ)

    def _frange(self, start, stop, step, up = True):
        if up:
            while start < stop:
                yield start
                start += step
        else:
            while start > stop:
                yield start
                start += step

    def generate_path(self):
        path = []
        iz = 0
        iy = 0
        for z in self._frange(self.startZ, self.endZ + self.stepZ, self.stepZ):
            if iz % 2 == 0 :
                for y in self._frange(self.endY, self.startY - self.stepY, -self.stepY, False):
                    if iy % 2 == 0 :
                        for x in self._frange(self.startX, self.endX + self.stepX, self.stepX):
                            path.append((x/1e6,y/1e6,z/1e6))
                    else :
                        for x in self._frange(self.endX, self.startX - self.stepX, -self.stepX, False):
                            path.append((x/1e6,y/1e6,z/1e6))
                    iy = iy + 1
            else :
                for y in self._frange(self.startY, self.endY + self.stepY, self.stepY):
                    if iy % 2 == 0 :
                        for x in self._frange(self.startX, self.endX + self.stepX, self.stepX):
                            path.append((x/1e6,y/1e6,z/1e6))
                    else :
                        for x in self._frange(self.endX, self.startX - self.stepX, -self.stepX, False):
                            path.append((x/1e6,y/1e6,z/1e6))
                    iy = iy + 1
            iz = iz + 1
        
        return path
