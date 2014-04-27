
import math
import time

import cdata

#Import DirectPython modules and constants.
import d3d11
import d3d11x
from d3d11c import *

#First we need a window. If you don't want to do any visible
#rendering this could be omitted.
window = d3d11.Window()
window.setTitle("Tutorial 2 - A colored triangle")
window.show(SW_SHOW)

#Then create a Device and tell it to use our window for drawing.
#Use a software WARP-device, in real applications you might
#try hardware first and fall back to software if that fails.
device = d3d11.Device(window, DRIVER_TYPE_WARP)

#Our vertex layout description: position (x, y, z) and color (r, g, b, a).
#See the "Layouts and input layouts" article in the documentation.
vertexDesc = [
    ("POSITION", 0, FORMAT_R32G32B32_FLOAT, 0, 0, INPUT_PER_VERTEX_DATA, 0),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),

    #This is functionally same as above, only easier to read. I use the complex one now
    #so that you don't get confused when you encounter it in samples.
    #("POSITION", 0, FORMAT_R32G32B32_FLOAT),
    #("COLOR", 0, FORMAT_R32G32B32A32_FLOAT),
]

#Our triangle - three vertices with position and color. The layout must match 'vertexDesc'.
triangle = [
    (-5, 0, 0) + (1, 0, 0, 1), #Red vertex.
    (0, 10, 0) + (0, 1, 0, 1), #Green vertex.
    (5, 0, 0)  + (0, 0, 1, 1), #Blue vertex.
]

vertices = []
for p in cdata.Box:
	vertices.append((p[0], p[1], p[2], 1, 1, 1, 1))

#Effect for rendering. The file contains trivial vertex- and pixel-shader.
effect = d3d11.Effect(d3d11x.getResourceDir("Effects", "simple.fx"))

#Input layout for the effect. Valid when technique index == 0 and it's pass index == 0 or
#the pass's input signature is compatible with that combination.
inputLayout = d3d11.InputLayout(vertexDesc, effect, 0, 0)

#Create a hardware buffer to hold our triangle.
vertexBuffer = d3d11.Buffer(vertexDesc, vertices, BIND_VERTEX_BUFFER)

#Precalculate view matrix. Eye position is (0, 5, -15) and it is looking at (0, 5, 0). (0, 1, 0) points up.
viewMatrix = d3d11.Matrix()
viewMatrix.lookAt((0, 5, -15), (0, 5, 0), (0, 1, 0))

def mainloop():
    while 1:
        #Check all new messages.
        for msg in window.getMessages():
            if msg.code == WM_DESTROY:
                #Close the application.
                return

        #Set default render targets.
        device.setRenderTargetsDefault()

        #Set vertex buffer, input layout and topology.
        device.setVertexBuffers([vertexBuffer])
        device.setInputLayout(inputLayout)
        device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_TRIANGLESTRIP)

        #Projection matrix.
        screenDesc = device.getScreenDesc()
        fieldOfView = math.radians(60.0) #60 degrees.
        aspectRatio = float(screenDesc.width) / screenDesc.height
        projMatrix = d3d11.Matrix()
        projMatrix.perspectiveFov(fieldOfView, aspectRatio, 0.1, 100.0)

        #The world matrix. Rotate the triangle (in radians) based
        #on the value returned by clock().
        yRot = time.clock()
        worldMatrix = d3d11.Matrix()
        worldMatrix.rotate((0, yRot, 0))

        #Combine matrices into one matrix by multiplying them.
        wordViewProj = worldMatrix * viewMatrix * projMatrix

        #Update effect variable(s).
        effect.set("worldViewProjection", wordViewProj)
        #Apply technique number 0 and it's pass 0.
        effect.apply(0, 0)

        #Draw all three vertices using the currently bound vertex buffer
        #and other settings (Effect, input layout, topology etc.).
        device.draw(len(vertexBuffer), 0)

        #Present our rendering. Wait for vsync.
        device.present(1)

#Start the mainloop.
mainloop()
