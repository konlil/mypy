#coding: gbk
import d3d11
import d3d11x
from d3d11c import *

g_vertexDesc = [
    ("POSITION", 0, FORMAT_R32G32B32_FLOAT, 0, 0, INPUT_PER_VERTEX_DATA, 0),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),
]
g_indexLayoutDesc16 = [("", 0, FORMAT_R16_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]
g_indexLayoutDesc32 = [("", 0, FORMAT_R32_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]

class GridPlane(object):
	def __init__(self, effect=None):
		self.effecName = effect
		self.vertexBuffer = None
		self.indexBuffer = None
		self.effect = None
		self.position = d3d11.Vector(0, 0, 0)
		self.yaw = 0
		self.pitch= 0
		self.roll = 0
		self.scale = (1, 1, 1)

		self.width = 100
		self.height = 100
		self.gridsize = 10.0
		self.gridx = int(self.width/self.gridsize)
		self.gridy = int(self.height/self.gridsize)

		self.rotationMatrix = d3d11.Matrix()
		self.translationMatrix = d3d11.Matrix()
		self.scaleMatrix = d3d11.Matrix()
		self.world = d3d11.Matrix()
		self.build()

	def build(self):
		effectName = self.effecName
		if not self.effecName:
			effectName = "marker.fx"
		effectPath = d3d11x.getResourceDir(".", "effects/marker.fx")
		self.effect = d3d11.Effect(effectPath)
		#Input layout for the effect. Valid when technique index == 0 and it's pass index == 0 or
		#the pass's input signature is compatible with that combination.
		self.inputLayout = d3d11.InputLayout(g_vertexDesc, self.effect, 0, 0)

		vertexData = []
		for i in xrange(self.gridx+1):
			if i%2 == 0:
				vertexData.append( (0, 0, i*self.gridsize, 1, 1, 1, 1) )
				vertexData.append( (self.width, 0, i*self.gridsize, 1, 1, 1, 1) )
			else:
				vertexData.append( (self.width, 0, i*self.gridsize, 1, 1, 1, 1) )
				vertexData.append( (0, 0, i*self.gridsize, 1, 1, 1, 1) )

		for i in xrange(self.gridy+1):
			if self.height%2 == 0:
				if i%2 == 0:
					vertexData.append( (i*self.gridsize, 0, self.height, 1, 1, 1, 1) )
					vertexData.append( (i*self.gridsize, 0, 0, 1, 1, 1, 1) )
				else:
					vertexData.append( (i*self.gridsize, 0, 0, 1, 1, 1, 1) )
					vertexData.append( (i*self.gridsize, 0, self.height, 1, 1, 1, 1) )
			else:
				if i%2 == 0:
					vertexData.append( ( (self.width-i)*self.gridsize, 0, self.height, 1, 1, 1, 1) )
					vertexData.append( ( (self.width-i)*self.gridsize, 0, 0, 1, 1, 1, 1) )
				else:
					vertexData.append( ( (self.width-i)*self.gridsize, 0, 0, 1, 1, 1, 1) )
					vertexData.append( ( (self.width-i)*self.gridsize, 0, self.height, 1, 1, 1, 1) )

		self.vertexBuffer = d3d11.Buffer(
				g_vertexDesc,
				vertexData,				# D3D11_SUBRESOURCE_DATA
				BIND_VERTEX_BUFFER,		# D3D11_BUFFER_DESC.BinadFlags
				USAGE_DYNAMIC,			# D3D11_BUFFER_DESC.Usage
				CPU_ACCESS_WRITE,		# D3D11_BUFFER_DESC.CPUAccessFlags
		)


	def update(self):
		self.rotationMatrix.rotate((self.pitch, self.yaw, self.roll))
		self.translationMatrix.translate(self.position)
		self.scaleMatrix.scale(self.scale)
		self.world = self.rotationMatrix*self.translationMatrix*self.scaleMatrix

	def render(self, device, view, proj):
		viewMatrix = view
		projMatrix = proj

		#Set vertex buffer, input layout and topology.
		device.setVertexBuffers([self.vertexBuffer])
		#device.setIndexBuffer(self.indexBuffer)
		device.setInputLayout(self.inputLayout)
		device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_LINELIST)

		#The world matrix. Rotate the triangle (in radians) based
		#on the value returned by clock().
		worldMatrix = self.world

		#Combine matrices into one matrix by multiplying them.
		wordViewProj = worldMatrix * viewMatrix * projMatrix

		effectVarsDesc = self.effect.getVariablesDesc()

		#Update effect variable(s).
		if "WVPMatrix" in effectVarsDesc:
			self.effect.set("WVPMatrix", wordViewProj)
		if "worldMatrix" in effectVarsDesc:
			self.effect.set("worldMatrix", worldMatrix)
		if "cameraPos" in effectVarsDesc:
			self.effect.set("cameraPos", d3d11x.Camera().pos)

		#Apply technique number 0 and it's pass 0.
		self.effect.apply(0, 0)

		#Draw all three vertices using the currently bound vertex buffer
		#and other settings (Effect, input layout, topology etc.).
		if not self.indexBuffer:
			device.draw(len(self.vertexBuffer), 0)
		else:
			device.drawIndexed(len(self.indexBuffer), 0, 0)

class PlaneManager(object):
	def __init__(self):
		self.planes = {}

	def addPlane( self, plane, coord ):
		plane.position = d3d11.Vector( coord[0]*plane.width, 0, coord[1]*plane.height )
		self.planes[coord] = plane

	def update(self):
		for p in self.planes.values():
			p.update()

	def render(self, device, view, proj):
		for p in self.planes.values():
			p.render(device, view, proj) 
	
mgr = PlaneManager()

def createPlanes():
	global mgr
	mgr.addPlane( GridPlane(), (0, 0) )
	mgr.addPlane( GridPlane(), (-1, 0) )
	mgr.addPlane( GridPlane(), (-1, -1) )
	mgr.addPlane( GridPlane(), (0, -1) )