#coding:gbk
import d3d11
import d3d11x
from d3d11c import *
import mesh_builder

g_vertexDesc = [
    ("POSITION", 0, FORMAT_R32G32B32_FLOAT, 0, 0, INPUT_PER_VERTEX_DATA, 0),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),
]
g_indexLayoutDesc16 = [("", 0, FORMAT_R16_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]
g_indexLayoutDesc32 = [("", 0, FORMAT_R32_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]

class MarkerManager(object):
	def __init__(self):
		self.marker_list = set()

	def addMarker(self, m):
		self.marker_list.add(m)

	def update(self):
		for m in self.marker_list:
			m.update()

	def render(self, device, view, proj):
		for m in self.marker_list:
			m.render(device, view, proj) 
	
mgr = MarkerManager()

class Marker(object):
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
		device.setIndexBuffer(self.indexBuffer)
		device.setInputLayout(self.inputLayout)
		device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_TRIANGLELIST)

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


class CubeMarker(Marker):
	def build(self):
		super(CubeMarker, self).build()
		vertex_list, index_list = mesh_builder.build_cube(1.0)
		vertexData = []
		for v in vertex_list:
			vertexData.append((v[0], v[1], v[2], 1, 1, 1, 1))

		indexData = [(int(i),) for i in index_list]
		self.indexBuffer = d3d11.Buffer(g_indexLayoutDesc32, indexData, BIND_INDEX_BUFFER, USAGE_IMMUTABLE)
		self.vertexBuffer = d3d11.Buffer(
				g_vertexDesc,
				vertexData,				# D3D11_SUBRESOURCE_DATA
				BIND_VERTEX_BUFFER,		# D3D11_BUFFER_DESC.BinadFlags
				USAGE_DYNAMIC,			# D3D11_BUFFER_DESC.Usage
				CPU_ACCESS_WRITE,		# D3D11_BUFFER_DESC.CPUAccessFlags
		)

		print len(self.indexBuffer)