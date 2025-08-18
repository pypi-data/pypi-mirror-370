from graphics import Engine
from math3d import Vector3
import time

# Küp vertexleri
cube_vertices = [
    Vector3(-1,-1,-1), Vector3(1,-1,-1),
    Vector3(1,1,-1), Vector3(-1,1,-1),
    Vector3(-1,-1,1), Vector3(1,-1,1),
    Vector3(1,1,1), Vector3(-1,1,1)
]

# Yüzler
faces = [
    [0,1,2,3], [4,5,6,7],
    [0,1,5,4], [2,3,7,6],
    [0,3,7,4], [1,2,6,5]
]

engine = Engine()
angle = 0

while angle < 360:
    engine.clear()
    rotated = [v.rotate_x(angle).rotate_y(angle) for v in cube_vertices]
    for face in faces:
        engine.draw_polygon([rotated[i] for i in face])
    engine.show()
    angle += 10
    time.sleep(0.1)
