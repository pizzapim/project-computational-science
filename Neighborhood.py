"""
Class to create the Von Neumann neighorhoods.
We originally planned to use bigger neighborhoods, but this is unused.
"""

class VonNeumannNeighborhood():

    def __init__(self, r=1):
        self.coords = [(x, 0) for x in range(-r, r+1) if x != 0]

        # Top and bottom triangle
        for i in range(r, 0, -1):
            for x in range(-(r-i), r-i+1):
                self.coords.append((x, i))
                self.coords.append((x, -i))


    def for_coords(self, x, y, N):
        neighbors = []

        for (offsetx, offsety) in self.coords:
            resx = x + offsetx
            resy = y + offsety

            if resx > 0 and resy > 0 and resx < N-1 and resy < N-1:
                neighbors.append((resx, resy))

        return neighbors