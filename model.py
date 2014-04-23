#coding: gbk
import visual
import time
from FbxCommon import *
import d3d11
import d3d11x
from d3d11c import *
import asset_manager

#Our vertex layout description: position (x, y, z) and color (r, g, b, a).
#See the "Layouts and input layouts" article in the documentation.
# 7 Members:
# SemanticName
# SemanticIndex
# Format
# InputSlot
# AlignedByteOffset
# InputSlotClass
# InstanceDataStepRate
vertexDesc = [
    ("POSITION", 0, FORMAT_R32G32B32_FLOAT, 0, 0, INPUT_PER_VERTEX_DATA, 0),
    # ("NORMAL", 0, FORMAT_R32G32B32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),

    # This is functionally same as above, only easier to read. I use the complex one now
    # so that you don't get confused when you encounter it in samples.
    # ("POSITION", 0, FORMAT_R32G32B32_FLOAT),
    # ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT),
]

#16 and 32 bit indices.
indexLayoutDesc16 = [("", 0, FORMAT_R16_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]
indexLayoutDesc32 = [("", 0, FORMAT_R32_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]

class Model(object):
	def load(self, res):
		self.res = res
		pass

class NodelessModel(Model):
	def load(self, res):
		import resmgrdll
		import ResMgr
		super(NodelessModel, self).load(res)
		self.fileSection = ResMgr.openSection(res)
		self.visualName = self.fileSection.readString('nodelessVisual')
		self.visual = visual.Visual()
		self.visual.load('%s.visual' % self.visualName)

class NodefullModel(Model):
	def load(self, res):
		import resmgrdll
		import ResMgr
		super(NodefullModel, self).load(res)
		self.fileSection = ResMgr.openSection(res)
		self.visualName = self.fileSection.readString('nodefullVisual')
		self.visual = visual.Visual()
		self.visual.load('%s.visual' % self.visualName)
	pass

class FbxModel(Model):
	def __init__(self, name):
		self.name = name
		self.vertexData = []
		self.indexData = []

	def setDesc(self, desc):
		self.desc = desc

		effectPath = d3d11x.getResourceDir(".", self.desc.effect)
		self.effect = d3d11.Effect(effectPath)
		self.vertexDesc = self.desc.vtdesc

		print self.desc.effect, self.vertexDesc
		print self.effect
		#Input layout for the effect. Valid when technique index == 0 and it's pass index == 0 or
		#the pass's input signature is compatible with that combination.
		self.inputLayout = d3d11.InputLayout(self.vertexDesc, self.effect, 0, 0)

	def setWorld(self, matrix):
		self.world = matrix

	def fromFbxNode(self, node):
		lMesh = node.GetNodeAttribute()
		print "load:", node.GetName()

		controlPointsCount = lMesh.GetControlPointsCount()
		controlPoints = lMesh.GetControlPoints()
		indexCount = lMesh.GetPolygonVertexCount()
		indexData = lMesh.GetPolygonVertices()
		leNormals = lMesh.GetLayer(0).GetNormals()

		self.vertexData = []
		for i in xrange(indexCount):
			index = indexData[i]
			position = controlPoints[index]
			normal = (0, 0, 0)
			if leNormals:
				if leNormals.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
					if leNormals.GetReferenceMode() == FbxLayerElement.eDirect:
						normal = leNormals.GetDirectArray().GetAt(i)
			color = (1, 1, 1, 1)
			vertexDef = []
			for v in self.desc.vtdesc:
				if v[0] == 'POSITION':
					vertexDef += list(position)
				elif v[0] == 'NORMAL':
					vertexDef += list(normal)
				elif v[0] == 'COLOR':
					vertexDef += list(color)
			self.vertexData.append(vertexDef)
			print index, vertexDef 
		self.indexData = [(int(i),) for i in indexData]
		self.indexCount = indexCount

		self.indexBuffer = d3d11.Buffer(indexLayoutDesc32, self.indexData, BIND_INDEX_BUFFER, USAGE_IMMUTABLE)
		self.vertexBuffer = d3d11.Buffer(
				self.vertexDesc,
				self.vertexData,		# D3D11_SUBRESOURCE_DATA
				BIND_VERTEX_BUFFER,		# D3D11_BUFFER_DESC.BinadFlags
				USAGE_DYNAMIC,			# D3D11_BUFFER_DESC.Usage
				CPU_ACCESS_WRITE,		# D3D11_BUFFER_DESC.CPUAccessFlags
		)

	def render(self, device, view, proj):
		viewMatrix = view
		projMatrix = proj

		#Set vertex buffer, input layout and topology.
		device.setVertexBuffers([self.vertexBuffer])
		device.setIndexBuffer(self.indexBuffer)
		device.setInputLayout(self.inputLayout)
		device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_TRIANGLESTRIP)

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

		for var_key in effectVarsDesc:
			var = getattr(self.desc, var_key, None)
			if var:
				self.effect.set(var_key, var)

		# self.effect.set("vEye", d3d11x.Camera().pos)
		# self.effect.set("vLightDirection", [1, 0, 0, 1.0])
		# # self.effect.set("lightPos", [1, 4, 1.5, 0])
		# self.effect.set("ambientColor", [1, 0, 0, 1.0])
		# self.effect.set("diffuseColor", [0, 1, 0, 1.0])
		# self.effect.set("specularColor", [1.0, 0, 1, 1.0])
		#Apply technique number 0 and it's pass 0.
		self.effect.apply(0, 0)

		#Draw all three vertices using the currently bound vertex buffer
		#and other settings (Effect, input layout, topology etc.).
		# device.draw(len(self.vertexBuffer), 0)
		device.drawIndexed(self.indexCount, 0, 0)

if __name__ == "__main__":
	#m = NodefullModel()
	#m.load('char/other/debug/box.model')
	#m.load(r'char\tp\role\00000\2014\2014.model')
	m = FbxModel()
	m.load('export/test.fbx')
