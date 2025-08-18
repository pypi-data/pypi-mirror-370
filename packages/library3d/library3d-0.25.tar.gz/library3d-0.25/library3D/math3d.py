class Vector3:
    def __init__(self, x, y, z):
        """
        x, y, z: koordinatlar
        """
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)

    def __mul__(self, scalar):
        return Vector3(self.x*scalar, self.y*scalar, self.z*scalar)

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"
