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