from PIL import Image, ImageDraw
from .math3d import Vector3

class Engine:
    """Saf Python 3D motoru v0.2"""

    def __init__(self, width=400, height=400):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), "black")
        self.draw = ImageDraw.Draw(self.image)
        self.zbuffer = [[float('inf')]*width for _ in range(height)]
        self.camera = Vector3(0,0,-5)

    def clear(self):
        self.image = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.image)
        self.zbuffer = [[float('inf')]*self.width for _ in range(self.height)]

    def project(self, vertex, fov=256):
        """3D vertexi 2D ekrana çevir"""
        factor = fov / (vertex.z - self.camera.z)
        x = vertex.x * factor + self.width / 2
        y = -vertex.y * factor + self.height / 2
        return int(x), int(y), vertex.z

    def draw_polygon(self, vertices, color="white"):
        points = [self.project(v)[:2] for v in vertices]
        self.draw.polygon(points, outline=color)

    def get_image(self):
        return self.image
