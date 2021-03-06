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

	def setLight(self, light):
		self.lightPos= light

	def readVertex(self, mesh, polygonIdx):
		controlPoints = mesh.GetControlPoints()
		x = controlPoints[polygonIdx][0]
		y = controlPoints[polygonIdx][1]
		z = controlPoints[polygonIdx][2]
		return (x, y, z)

	def DisplayTextureInfo(self, tex, blendMode):
		print "Name:", tex.GetName()
		print "File Name", tex.GetRelativeFileName()
		print "Scale U", tex.GetScaleU()
		print "Scale V", tex.GetScaleV()
		print "Translation U", tex.GetTranslationU()
		print "Translation V", tex.GetTranslationV()
		print "Swap UV", tex.GetSwapUV()
		print "Rotation U", tex.GetRotationU()
		print "Rotation V", tex.GetRotationV()
		print "Rotation W", tex.GetRotationW()

		lAlphaSources = [ "None", "RGB Intensity", "Black" ]
		print "Alpha Source: ", lAlphaSources[tex.GetAlphaSource()]
		print "Cropping Left: ", tex.GetCroppingLeft()
		print "Cropping Top: ", tex.GetCroppingTop()
		print "Cropping Right: ", tex.GetCroppingRight()
		print "Cropping Bottom: ", tex.GetCroppingBottom()

		lMappingTypes = [ "Null", "Planar", "Spherical", "Cylindrical", "Box", "Face", "UV", "Environment"]
		print "Mapping Type: ", lMappingTypes[tex.GetMappingType()]

		if tex.GetMappingType() == FbxTexture.ePlanar:
			lPlanarMappingNormals = ["X", "Y", "Z" ]
			print "Planar Mapping Normal: ", lPlanarMappingNormals[tex.GetPlanarMappingNormal()]

		lBlendModes   = ["Translucent", "Add", "Modulate", "Modulate2"]
		if blendMode >= 0:
			print "Blend Mode: ", lBlendModes[blendMode]
		print "Alpha: ", tex.GetDefaultAlpha()

		lMaterialUses = ["Model Material", "Default Material"]
		print "Material Use: ", lMaterialUses[tex.GetMaterialUse()]

		texUses = ["Standard", "Shadow Map", "Light Map", "Spherical Reflexion Map", "Sphere Reflexion Map"]
		print "Texture Use: ", texUses[tex.GetTextureUse()]

	def FindAndDisplayTextureInfoByProperty(self, pProperty, pDisplayHeader, pMaterialIndex):
		if pProperty.IsValid():
			#Here we have to check if it's layeredtextures, or just textures:
			lLayeredTextureCount = pProperty.GetSrcObjectCount(FbxLayeredTexture.ClassId)
			if lLayeredTextureCount > 0:
				for j in range(lLayeredTextureCount):
					print "Layered Texture: ", j
					lLayeredTexture = pProperty.GetSrcObject(FbxLayeredTexture.ClassId, j)
					lNbTextures = lLayeredTexture.GetSrcObjectCount(FbxTexture.ClassId)
					for k in range(lNbTextures):
						lTexture = lLayeredTexture.GetSrcObject(FbxTexture.ClassId,k)
						if lTexture:
							if pDisplayHeader:
								print "Textures connected to Material ", pMaterialIndex
								pDisplayHeader = False

							# NOTE the blend mode is ALWAYS on the LayeredTexture and NOT the one on the texture.
							# Why is that?  because one texture can be shared on different layered textures and might
							# have different blend modes.

							lBlendMode = lLayeredTexture.GetTextureBlendMode(k)
							print "Textures for:", pProperty.GetName()
							print "Texture ", k
							self.DisplayTextureInfo(lTexture, lBlendMode)
			else:
				# no layered texture simply get on the property
				lNbTextures = pProperty.GetSrcObjectCount(FbxTexture.ClassId)
				print lNbTextures
				for j in range(lNbTextures):
					lTexture = pProperty.GetSrcObject(FbxTexture.ClassId,j)
					if lTexture:
						# display connectMareial header only at the first time
						if pDisplayHeader:
							print "Textures connected to Material ", pMaterialIndex
							pDisplayHeader = False

						print "Textures for ", pProperty.GetName().Buffer()
						print "Texture ", j
						self.DisplayTextureInfo(lTexture, -1)

				lNbTex = pProperty.GetSrcObjectCount(FbxTexture.ClassId)
				for lTextureIndex in range(lNbTex):
					lTexture = pProperty.GetSrcObject(FbxTexture.ClassId, lTextureIndex)

	def readTextures(self, mesh):
		lNbMat = mesh.GetNode().GetSrcObjectCount(FbxSurfaceMaterial.ClassId)
		for lMaterialIndex in range(lNbMat):
			lMaterial = mesh.GetNode().GetSrcObject(FbxSurfaceMaterial.ClassId, lMaterialIndex)
			lDisplayHeader = True

			#go through all the possible textures
			if lMaterial:
				for lTextureIndex in range(FbxLayerElement.sTypeTextureCount()):
					lProperty = lMaterial.FindProperty(FbxLayerElement.sTextureChannelNames(lTextureIndex))
					self.FindAndDisplayTextureInfoByProperty(lProperty, lDisplayHeader, lMaterialIndex)

	def fromFbxNode(self, node):
		lMesh = node.GetNodeAttribute()
		print "load:", node.GetName()

		controlPointsCount = lMesh.GetControlPointsCount()
		controlPoints = lMesh.GetControlPoints()
		indexCount = lMesh.GetPolygonVertexCount()
		indexData = lMesh.GetPolygonVertices()
		leNormals = lMesh.GetLayer(0).GetNormals()

		self.readTextures(lMesh)

		print len(indexData), indexData
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
			print index, normal
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
		#device.setIndexBuffer(self.indexBuffer)
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

		for var_key in effectVarsDesc:
			var = getattr(self.desc, var_key, None)
			if var:
				self.effect.set(var_key, var)
	
		if "lightPos" in effectVarsDesc:
			self.effect.set("lightPos", (self.lightPos[0],self.lightPos[1], self.lightPos[2], 0))
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
		device.draw(len(self.vertexBuffer), 0)
		#device.drawIndexed(self.indexCount, 0, 0)

if __name__ == "__main__":
	#m = NodefullModel()
	#m.load('char/other/debug/box.model')
	#m.load(r'char\tp\role\00000\2014\2014.model')
	m = FbxModel()
	m.load('export/test.fbx')
