'''
mypy test framework
'''
import math
import time

#Import DirectPython modules and constants.
import d3d11
import d3d11x
from d3d11c import *
import d3d11gui as gui
import scene
import marker
import gridplane

#d3d11.enableDebug()

lightPos = (0,0,40)
class Panel(object):
	def __init__(self, device, window):
		self.device = device
		self.window = window
		self.manager = gui.Manager(self.device, self.window)

		self.root = gui.Window(self.manager, d3d11x.Rect(0, 0, 400, 100))
		self.root.title = "Control Panel"

		self.slider = gui.Slider(self.root, d3d11x.Rect(50, 30, 270, 8))
		self.slider.range = 100
		self.slider.addSelector()
		self.slider.onSlide = self.onSlide

		self.yaw = 0

	def onMessage(self, msg):
		return self.manager.onMessage(msg)

	def onRender(self, frameTime):
		self.manager.render(frameTime)

	def onSlide(self, event, selector):
		#global lightPos
		#rot = d3d11.Matrix()
		#rot.rotate((0, selector.position*2*3.1415926/100.0, 0))
		#lightPos = rot.transformVector(d3d11.Vector(0, 0, 40))
		#print("Slided: %i of %i" % (selector.position, selector.stop))
		#print lightPos

		m = list(marker.mgr.marker_list)[0]
		m.roll = selector.position*2*3.1415926/100.0
		print("Slided: %i of %i" % (selector.position, selector.stop))

class App(d3d11x.Frame):
	def __init__(self, title, helpText=''):
		super(App, self).__init__(title, helpText)

	def onCreate(self):
		#self.device = d3d11.Device(self.window, DRIVER_TYPE_WARP)
		self.camera = d3d11x.Camera()

		self.cubeMarker = marker.CubeMarker()
		self.cubeMarker.position = d3d11.Vector(40, 40, 40)
		marker.mgr.addMarker(self.cubeMarker)

		gridplane.createPlanes()

		self.panel = Panel(self.device, self.window)
		self.scene = scene.FbxScene('assets/box_only.fbx')
		self.scene.load()

	def onUpdate(self):
		self.camera.onUpdate(self.frameTime)
		marker.mgr.update()
		gridplane.mgr.update()

	def onMessage(self, event):
		if self.panel.onMessage(event):
			return True
		return self.camera.onMessage(event)

	def onRender(self):
		viewMatrix = self.camera.getViewMatrix()
		projMatrix = self.createProjection(65, 0.1, 2000)
		self.scene.setLight(lightPos)
		self.scene.render(self.device, viewMatrix, projMatrix)
		marker.mgr.render(self.device, viewMatrix, projMatrix)
		gridplane.mgr.render(self.device, viewMatrix, projMatrix)
		self.panel.onRender(self.frameTime)

if __name__ == "__main__":
	#d3d11.enableDebug()

	app = App('mypy', __doc__)
	app.mainloop()
