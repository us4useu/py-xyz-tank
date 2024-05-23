class PathBuilder:
    def __init__(self, startX, startY, startZ, endX, endY, endZ, stepX, stepY, stepZ):
        self.startX = float(startX)
        self.startY = float(startY)
        self.startZ = float(startZ)
        self.endX = float(endX) #mm
        self.endY = float(endY)
        self.endZ = float(endZ)
        self.stepX = float(stepX)
        self.stepY = float(stepY)
        self.stepZ = float(stepZ)

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
        #subpath = []
        iz = 0
        iy = 0
        for z in self._frange(self.startZ, self.endZ + self.stepZ, self.stepZ):
            if iz % 2 == 0 :
                for y in self._frange(self.startY, self.endY + self.stepY, self.stepY):
                    if iy % 2 == 0 :
                        for x in self._frange(self.startX, self.endX + self.stepX, self.stepX):
                            path.append((x, y, z))
                    else :
                        for x in self._frange(self.endX, self.startX - self.stepX, -self.stepX, False):
                            path.append((x, y, z))
                    iy = iy + 1
            else :
                for y in self._frange(self.endY, self.startY - self.stepY, -self.stepY, False):
                    if iy % 2 == 0 :
                        for x in self._frange(self.startX, self.endX + self.stepX, self.stepX):
                            path.append((x, y, z))
                    else :
                        for x in self._frange(self.endX, self.startX - self.stepX, -self.stepX, False):
                            path.append((x, y, z))
                    iy = iy + 1
            iz = iz + 1
        return path

    def display_path(self, path):
        
        x = [t[0] for t in path]
        y = [t[1] for t in path]
        z = [t[2] for t in path]

        # Plot
        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        #ax.scatter(x, y, z, color='b', marker='o')

        #for i in range(len(path) - 1):
        #    ax.plot([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]], color='b')

        # Customize labels
        #ax.set_xlabel('X')
        #ax.set_ylabel('Y')
        #ax.set_zlabel('Z')

        #plt.show()