'''
mypy test framework
'''
import math
import time

#Import DirectPython modules and constants.
import d3d11
import d3d11x
from d3d11c import *

import scene

#d3d11.enableDebug()

class App(d3d11x.Frame):
	def __init__(self, title, helpText=''):
		super(App, self).__init__(title, helpText)

	def onCreate(self):
		self.camera = d3d11x.Camera()
		self.scene = scene.FbxScene('assets/box_only.fbx')
		self.scene.load()

	def onUpdate(self):
		self.camera.onUpdate(self.frameTime)

	def onMessage(self, event):
		return self.camera.onMessage(event)

	def onRender(self):
		viewMatrix = self.camera.getViewMatrix()
		projMatrix = self.createProjection(65, 0.1, 2000)
		self.scene.render(self.device, viewMatrix, projMatrix)

if __name__ == "__main__":
	app = App('mypy', __doc__)
	app.mainloop()
