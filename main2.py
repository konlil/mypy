
"""
Point sprites are billboards that are automatically
rotated so that they always face the camera. They are
handy for creating particle effects and explosions.
This sample uses a geometry shader to render points
and "fake" shadows. It is also possible to run
particle simulations on the GPU. You can use
the mouse and keyboard to control the camera.
"""

import math
import random
import time

import d3d11
import d3d11x
from d3d11c import *

POINT_COUNT = 150

spriteLayoutDesc = [
    ("POSITION", 0, FORMAT_R32G32B32_FLOAT),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT),
    ("PSIZE", 0, FORMAT_R32_FLOAT),
]

class SpriteSample(d3d11x.Frame):
    def onCreate(self):
        #self.heightmap = d3d11x.HeightMap(self.device, None, (32, 32), heightFunc, (2, 1, 2), (10, 10), False)
        #self.heightmap.textureView = self.loadTextureView("ground-marble.dds")

        effectPath = d3d11x.getResourceDir("Effects", "Tutorial2.fx")
        self.spriteEffect = d3d11.Effect(effectPath)
        self.spriteInputLayout = d3d11.InputLayout(spriteLayoutDesc, self.spriteEffect, 0, 0)

        self.camera = d3d11x.Camera()

        #Create a dynamic vertex buffer for our sprites. Double the
        #size for shadow sprites.
        self.spriteBuffer = d3d11.Buffer(spriteLayoutDesc, POINT_COUNT * 2,
            BIND_VERTEX_BUFFER, USAGE_DYNAMIC, CPU_ACCESS_WRITE)

    def onMessage(self, event):
        return self.camera.onMessage(event)

    def onUpdate(self):
        self.camera.onUpdate(self.frameTime)

    def onRender(self):
        viewMatrix = self.camera.getViewMatrix()
        projMatrix = self.createProjection(60, 0.1, 200)

        #Heightmap.
        #self.heightmap.effect.set("lightAmbient", (0.5, 0.5, 0.5, 0))
        #self.heightmap.render(d3d11.Matrix(), viewMatrix, projMatrix)

        #Then all sprites.
        self.device.setVertexBuffers([self.spriteBuffer])
        self.device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_POINTLIST)
        self.device.setInputLayout(self.spriteInputLayout)

        #First shadow points. Use an offset. Note that they are rotated
        #towards the camera too which is not that great. As an excercise
        #you could make them align using the surface normal. Or use real shadows.
        self.device.draw(len(self.spriteBuffer), 0)

        #Then colored and textured points.
        #self.device.draw(POINT_COUNT, 0)


if __name__ == "__main__":
    frame = SpriteSample("3D Sprites", __doc__)
    frame.mainloop()

