'''
mypy test framework
'''
import math
import time

#Import DirectPython modules and constants.
import d3d11
import d3d11x
from d3d11c import *

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


class App(d3d11x.Frame):
	def onCreate(self):
		self.camera = d3d11x.Camera()
		effectPath = d3d11x.getResourceDir("Effects", "Tutorial2.fx")
		print effectPath
		self.effect = d3d11.Effect(effectPath)
		#Input layout for the effect. Valid when technique index == 0 and it's pass index == 0 or
		#the pass's input signature is compatible with that combination.
		self.inputLayout = d3d11.InputLayout(vertexDesc, self.effect, 0, 0)
		#Create a hardware buffer to hold our triangle.
		self.vertexBuffer = d3d11.Buffer(vertexDesc, triangle, BIND_VERTEX_BUFFER, USAGE_DYNAMIC, CPU_ACCESS_WRITE)
		pass

	def onUpdate(self):
		self.camera.onUpdate(self.frameTime)

	def onMessage(self, event):
		return self.camera.onMessage(event)

	def onRender(self):
		viewMatrix = self.camera.getViewMatrix()
		projMatrix = self.createProjection(60, 0.1, 200)

		#Set vertex buffer, input layout and topology.
		self.device.setVertexBuffers([self.vertexBuffer])
		self.device.setInputLayout(self.inputLayout)
		self.device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_TRIANGLELIST)

		#The world matrix. Rotate the triangle (in radians) based
		#on the value returned by clock().
		yRot = time.clock()
		worldMatrix = d3d11.Matrix()
		worldMatrix.rotate((0, yRot, 0))

		#Combine matrices into one matrix by multiplying them.
		wordViewProj = worldMatrix * viewMatrix * projMatrix

		#Update effect variable(s).
		self.effect.set("worldViewProjection", wordViewProj)
		#Apply technique number 0 and it's pass 0.
		self.effect.apply(0, 0)

		#Draw all three vertices using the currently bound vertex buffer
		#and other settings (Effect, input layout, topology etc.).
		self.device.draw(len(self.vertexBuffer), 0)


if __name__ == "__main__":
	app = App('mypy', __doc__)
	app.mainloop()
