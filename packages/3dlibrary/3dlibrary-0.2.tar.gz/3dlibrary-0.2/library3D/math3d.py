class Vector3:
    """3D vektör sınıfı"""

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def translate(self, dx=0, dy=0, dz=0):
        self.x += dx
        self.y += dy
        self.z += dz
        return self

    def scale(self, sx=1, sy=1, sz=1):
        self.x *= sx
        self.y *= sy
        self.z *= sz
        return self

    def rotate_x(self, angle):
        from math import cos, sin
        y = self.y * cos(angle) - self.z * sin(angle)
        z = self.y * sin(angle) + self.z * cos(angle)
        self.y, self.z = y, z
        return self

    def rotate_y(self, angle):
        from math import cos, sin
        x = self.x * cos(angle) + self.z * sin(angle)
        z = -self.x * sin(angle) + self.z * cos(angle)
        self.x, self.z = x, z
        return self

    def rotate_z(self, angle):
        from math import cos, sin
        x = self.x * cos(angle) - self.y * sin(angle)
        y = self.x * sin(angle) + self.y * cos(angle)
        self.x, self.y = x, y
        return self
