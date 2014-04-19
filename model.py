#coding: gbk
import visual
import time
from FbxCommon import *
import d3d11
import d3d11x
from d3d11c import *

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
    ("NORMAL", 0, FORMAT_R32G32B32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),
    ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),

    #This is functionally same as above, only easier to read. I use the complex one now
    #so that you don't get confused when you encounter it in samples.
    #("POSITION", 0, FORMAT_R32G32B32_FLOAT),
    #("COLOR", 0, FORMAT_R32G32B32A32_FLOAT),
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
	def __init__(self):
		effectPath = d3d11x.getResourceDir("Effects", "mirror_reflection.fx")
		self.effect = d3d11.Effect(effectPath)

		#Input layout for the effect. Valid when technique index == 0 and it's pass index == 0 or
		#the pass's input signature is compatible with that combination.
		self.inputLayout = d3d11.InputLayout(vertexDesc, self.effect, 0, 0)
		pass

	def setWorld(self, matrix):
		self.world = matrix

	def fromFbxNode(self, node):
		lMesh = node.GetNodeAttribute()
		print "load:", node.GetName()

		controlPointsCount = lMesh.GetControlPointsCount()
		controlPoints = lMesh.GetControlPoints()

		# 使用索引缓冲
		indCount = lMesh.GetPolygonVertexCount()
		indices = lMesh.GetPolygonVertices()
		leVtxc = lMesh.GetLayer(0).GetVertexColors()
		vertexSources = []
		leNormals = lMesh.GetLayer(0).GetNormals()
		for i in xrange(indCount):
			index = indices[i]
			position = controlPoints[index]
			if leNormals:
				if leNormals.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
					if leNormals.GetReferenceMode() == FbxLayerElement.eDirect:
						normal = leNormals.GetDirectArray().GetAt(i)
			vertexSources.append((position[0], position[1], position[2], normal[0], normal[1], normal[2], 1,1,1,1))
		# ind = [(int(v),) for v in indices]
		# self.indexBuffer = d3d11.Buffer(indexLayoutDesc16, ind, BIND_INDEX_BUFFER, USAGE_IMMUTABLE)
		self.indexCount = indCount

		# vertexSources = []
		# leNormals = lMesh.GetLayer(0).GetNormals()
		# for i in xrange(controlPointsCount):
		# 	position = controlPoints[i];
		# 	if leNormals:
		# 		# print leNormals, leNormals.GetMappingMode(), leNormals.GetReferenceMode()
		# 		if leNormals.GetMappingMode() == FbxLayerElement.eByControlPoint:
		# 			if leNormals.GetReferenceMode() == FbxLayerElement.eDirect:
		# 				normal = leNormals.GetDirectArray().GetAt(i)
		# 	vertexSources.append((position[0], position[1], position[2], normal[0], normal[1], normal[2], 1,1,1,1))

		#Create a hardware buffer to hold our triangle.
		self.vertexBuffer = d3d11.Buffer(
				vertexDesc,
				vertexSources,				# D3D11_SUBRESOURCE_DATA
				BIND_VERTEX_BUFFER,		# D3D11_BUFFER_DESC.BinadFlags
				USAGE_DYNAMIC,			# D3D11_BUFFER_DESC.Usage
				CPU_ACCESS_WRITE,		# D3D11_BUFFER_DESC.CPUAccessFlags
		)

	def render(self, device, view, proj):
		viewMatrix = view
		projMatrix = proj

		#Set vertex buffer, input layout and topology.
		device.setVertexBuffers([self.vertexBuffer])
		# device.setIndexBuffer(self.indexBuffer)
		device.setInputLayout(self.inputLayout)
		device.setPrimitiveTopology(PRIMITIVE_TOPOLOGY_TRIANGLELIST)

		#The world matrix. Rotate the triangle (in radians) based
		#on the value returned by clock().
		worldMatrix = self.world

		#Combine matrices into one matrix by multiplying them.
		wordViewProj = worldMatrix * viewMatrix * projMatrix

		#Update effect variable(s).
		self.effect.set("worldViewProjection", wordViewProj)
		self.effect.set("worldMatrix", worldMatrix)
		self.effect.set("vEye", d3d11x.Camera().pos)
		self.effect.set("vLightDirection", [1, 0, 0, 1.0])
		# self.effect.set("lightPos", [1, 4, 1.5, 0])
		self.effect.set("ambientColor", [1, 0, 0, 1.0])
		self.effect.set("diffuseColor", [0, 1, 0, 1.0])
		self.effect.set("specularColor", [1.0, 0, 1, 1.0])
		#Apply technique number 0 and it's pass 0.
		self.effect.apply(0, 0)

		#Draw all three vertices using the currently bound vertex buffer
		#and other settings (Effect, input layout, topology etc.).
		device.draw(len(self.vertexBuffer), 0)
		# device.drawIndexed(self.indexCount, 0, 0)

if __name__ == "__main__":
	#m = NodefullModel()
	#m.load('char/other/debug/box.model')
	#m.load(r'char\tp\role\00000\2014\2014.model')
	m = FbxModel()
	m.load('export/test.fbx')
