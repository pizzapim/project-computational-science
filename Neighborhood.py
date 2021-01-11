class VonNeumannNeighborhood():

    def __init__(self, r=1):
        self.coords = []

        # Middle row
        for x in range(-r, r+1):
            self.coords.append((x, 0))

        # Top and bottom triangle
        for i in range(r, 0, -1):
            for x in range(-(r-i), r-i+1):
                self.coords.append((x, i))
                self.coords.append((x, -i))
        self.coords.remove((0,0))
    
    
    def for_coords(self, x, y, N):
        neighbors = []

        for (offsetx, offsety) in self.coords:
            resx = x + offsetx
            resy = y + offsety

            if resx >= 0 and resy >= 0 and resx < N and resy < N:
                neighbors.append((resx, resy))

        return neighbors