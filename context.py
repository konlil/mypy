#coding: gbk

import d3d11
import d3d11x
import d3d11c

class Context(object):
	def __init__(self):
		self._window = None
		self._device = None

	def build(self, title=''):
		self._window = d3d11.Window()
		self._window.setRect((100,100,800,600), client=True)
		self._window.setTitle(title)
		self._initDevice()

	def _initDevice(self):
		DeviceTypes = [
			d3d11c.DRIVER_TYPE_HARDWARE,
			d3d11c.DRIVER_TYPE_WARP,
			d3d11c.DRIVER_TYPE_REFERENCE,
			d3d11c.DRIVER_TYPE_SOFTWARE
		]

		for dt in DeviceTypes:
			self._device = d3d11.Device(self._window, d3d11c.DRIVER_TYPE_WARP)
			if self._device:
				return
		raise CommonException('Failed to create d3d11 device.')

	@property
	def window(self):
		return self._window

	@property
	def device(self):
		return self._device

inst = Context()
