class PathBuilder:
    def __init__(self, startX, startY, startZ, endX, endY, endZ, stepX, stepY, stepZ):
        self.startX = startX
        self.startY = startY
        self.startZ = startZ
        self.endX = endX #mm
        self.endY = endY
        self.endZ = endZ
        self.stepX = stepX
        self.stepY = stepY
        self.stepZ = stepZ

    def generate_path(self):
        path = []
        subpath = []
        iz = 0
        iy = 0
        for z in range(self.startZ, self.endZ + 1, self.stepZ):
            if iz % 2 == 0 :
                for y in range(self.startY, self.endY + 1, self.stepY):
                    if iy % 2 == 0 :
                        for x in range(self.startX, self.endX + 1, self.stepX):
                            path.append((x, y, z))
                    else :
                        for x in range(self.endX, self.startX - 1, -self.stepX):
                            path.append((x, y, z))
                    iy = iy + 1
            else :
                for y in range(self.endY, self.startY - 1, -self.stepY):
                    if iy % 2 == 0 :
                        for x in range(self.startX, self.endX + 1, self.stepX):
                            path.append((x, y, z))
                    else :
                        for x in range(self.endX, self.startX - 1, -self.stepX):
                            path.append((x, y, z))
                    iy = iy + 1
            iz = iz + 1
        return path
