from FbxCommon import *


class MeshData(object):
	def __init__(self, name):
		self.name = name
		self.vertexList = []
		self.triangleList = []
		self.materialList = []

	def addVertex(self, v):
		self.vertexList.append(v)

	def addTriangle(self, tri):
		self.triangleList.append(tri)

	def addMaterial(self, mat):
		self.materialList.append(mat)

	def __str__(self):
		strVertex = [str(v) for v in self.vertexList]
		strVertex = '\n'.join(strVertex)
		return strVertex


class MaterialData(object):
	def __init__(self, name):
		self.name = name
		self.textures = None

class TextureData(object):
	def __init__(self):
		self.name = None
		self.relativeFile = None
		self.scaleUV = []
		self.translationUV = []
		self.swapUV = []
		self.rotationUV = []
		self.rotationW = None

		#lAlphaSources = [ "None", "RGB Intensity", "Black" ]
		self.alphaSource = None		#lAlphaSources[tex.GetAlphaSource()]
		self.cropping = []		#left, top, right, bottom

		# lMappingTypes = [ "Null", "Planar", "Spherical", "Cylindrical", "Box", "Face", "UV", "Environment"]
		self.mappingType = None #lMappingTypes[tex.GetMappingType()]
		# if tex.GetMappingType() == FbxTexture.ePlanar:
		# 	lPlanarMappingNormals = ["X", "Y", "Z" ]
		# 	print "Planar Mapping Normal: ", lPlanarMappingNormals[tex.GetPlanarMappingNormal()]
		self.planarMappingNormal = None

		# lBlendModes   = ["Translucent", "Add", "Modulate", "Modulate2"]
		# if blendMode >= 0:
		# 	print "Blend Mode: ", lBlendModes[blendMode]
		self.blendMode = None
		self.defaultAlpha = None
		# print "Alpha: ", tex.GetDefaultAlpha()

		# lMaterialUses = ["Model Material", "Default Material"]
		self.materialUse = None #lMaterialUses[tex.GetMaterialUse()]

		# texUses = ["Standard", "Shadow Map", "Light Map", "Spherical Reflexion Map", "Sphere Reflexion Map"]
		self.textureUse = None #texUses[tex.GetTextureUse()]


class TriangleData(object):
	def __init__(self):
		self.vertices = []
		self.materialIndex = None
		self.material = None

	def addVertex(self, v):
		self.vertices.append(v)
		assert(len(self.vertices) <= 3)

class VertexData(object):
	def __init__(self, position=None, color=None, uv=None, normal=None, tagent=None):
		self.position = position
		self.color = color
		self.uv = uv
		self.normal = normal
		self.tagent = tagent

	def __str__(self):
		return 'pos:%s\tcolor:%s\tnormal:%s\ttagent:%s' \
			%(str(self.position), str(self.color), str(self.normal), str(self.tagent))


class FbxSceneLoader(object):
	def __init__(self, path):
		self.path = path
		self.meshes = {}
		self._load()

	def getMeshNames(self):
		return self.meshes.keys()

	def getMesh(self, name):
		return self.meshes[name]

	def	_load(self):
		lSdkManager, lScene = InitializeSdkObjects()
		lResult = LoadScene(lSdkManager, lScene, self.path)
		if not lResult:
			print("An error occurred while loading scene: %s"%self.path)
			return

		self.loadNode(lScene.GetRootNode())

		lSdkManager.Destroy()

	def loadNode(self, node):
		attr = node.GetNodeAttribute()
		if attr:
			attrType = attr.GetAttributeType()
			if attrType == FbxNodeAttribute.eMarker:
				pass
			elif attrType == FbxNodeAttribute.eSkeleton:
				pass
			elif attrType == FbxNodeAttribute.eMesh:
				meshData = self.loadMesh(node)
				self.meshes[meshData.name] = meshData
			elif attrType == FbxNodeAttribute.eNurbs:
				pass
			elif attrType == FbxNodeAttribute.ePatch:
				pass
			elif attrType == FbxNodeAttribute.eCamera:
				pass
			elif attrType == FbxNodeAttribute.eLight:
				pass

		for i in xrange(node.GetChildCount()):
			self.loadNode(node.GetChild(i))

	def loadTriangleMaterials(self, mesh, triangleCount):
		triangleMaterials = {}
		lMaterial = mesh.GetElementMaterial(0)
		if lMaterial:
			materialIndices = lMaterial.GetIndexArray()
			materialMappingMode = lMaterial.GetMappingMode()
			if materialIndices:
				if materialMappingMode == FbxLayerElement.eByPolygon:
					if materialIndices.GetCount() == triangleCount:
						for triIdx in xrange(triangleCount):
							materialIndex = materialIndices[triIdx]
							triangleMaterials[triIdx] = materialIndex
				elif materialMappingMode == FbxLayerElement.eAllSame:
					materialIndex = materialIndices[0]
					for triIdx in xrange(triangleCount):
						triangleMaterials[triIdx] = materialIndex
		return triangleMaterials

	def loadTextureInfo(self, tex, blendMode):
		texData = TextureData()
		texData.name = tex.GetName()
		texData.relativeFile = tex.GetRelativeFileName()
		return texData

	def loadMesh(self, node):
		name = node.GetName()
		mesh = node.GetNodeAttribute()
		meshData = MeshData(name)
		controlPoints = mesh.GetControlPoints()
		triangleCount = mesh.GetPolygonCount()
		vertexCounter=0

		for i in xrange(triangleCount):
			triangleData = TriangleData()
			for j in xrange(3):
				vertexData = VertexData()

				#position
				ctrlPointIndex = mesh.GetPolygonVertex(i, j)
				vertexData.position = list(controlPoints[ctrlPointIndex])[:3]

				#color
				color = None
				if mesh.GetElementVertexColorCount() > 0:
					vertexColor = mesh.GetElementVertexColor(0)
					vertexColorMappingMode = vertexColor.GetMappingMode()
					vertexColorRefMode = vertexColor.GetReferenceMode()
					vertexColorArray = vertexColor.GetDirectArray()

					if vertexColorMappingMode == FbxLayerElement.eByControlPoint:
						if vertexColorRefMode == FbxLayerElement.eDirect:
							color = list(vertexColorArray[ctrlPointIndex])
						elif vertexColorRefMode == FbxLayerElement.eIndexToDirect:
							idxArray = vertexColor.GetIndexArray()
							idx = idxArray[ctrlPointIndex]
							color = list(vertexColorArray[idx])
					elif vertexColorMappingMode == FbxLayerElement.eByPolygonVertex:
						if vertexColorRefMode == FbxLayerElement.eDirect:
							color = list(vertexColorArray[vertexCounter])
						elif vertexColorRefMode == FbxLayerElement.eIndexToDirect:
							idxArray = vertexColor.GetIndexArray()
							idx = idxArray[vertexCounter]
							color = list(vertexColorArray[idx])
				vertexData.color = color

				#uv (layers)
				uvs = []
				uvLayers = mesh.GetElementUVCount()
				for layer in xrange(uvLayers):
					vertexUV = mesh.GetElementUV(layer)
					if vertexUV.GetMappingMode() == FbxLayerElement.eByControlPoint:
						if vertexUV.GetReferenceMode() == FbxLayerElement.eDirect:
							uv = list(vertexUV.GetDirectArray()[ctrlPointIndex])
							uvs.append(uv)
						elif vertexUV.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							idx = vertexUV.GetIndexArray()[ctrlPointIndex]
							uv = list(vertexUV.GetDirectArray()[idx])
							uvs.append(uv)
					elif vertexUV.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
						uvIndex = mesh.GetTextureUVIndex(i, j)
						if vertexUV.GetReferenceMode() == FbxLayerElement.eDirect:
							uv = list(vertexUV.GetDirectArray()[uvIndex])
							uvs.append(uv)
						elif vertexUV.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							uv = list(vertexUV.GetDirectArray()[uvIndex])
							uvs.append(uv)
				vertexData.uv = uvs
				#print 'uv', uvs

				#normal
				normal = None
				if mesh.GetElementNormalCount() > 0:
					lNormal = mesh.GetElementNormal(0)
					if lNormal.GetMappingMode() == FbxLayerElement.eByControlPoint:
						if lNormal.GetReferenceMode() == FbxLayerElement.eDirect:
							normal = list(lNormal.GetDirectArray()[ctrlPointIndex])
						elif lNormal.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							idx = lNormal.GetIndexArray()[ctrlPointIndex]
							normal= list(lNormal.GetDirectArray()[idx])
					elif lNormal.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
						if lNormal.GetReferenceMode() == FbxLayerElement.eDirect:
							normal = list(lNormal.GetDirectArray()[vertexCounter])
						elif lNormal.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							idx = lNormal.GetIndexArray()[vertexCounter]
							normal= list(lNormal.GetDirectArray()[idx])
				vertexData.normal = normal
				#print 'normal', normal

				#tagent
				tagent = None
				if mesh.GetElementTangentCount() > 0:
					lTagent = mesh.GetElementTangent(0)
					if lTagent.GetMappingMode() == FbxLayerElement.eByControlPoint:
						if lTagent.GetReferenceMode() == FbxLayerElement.eDirect:
							tagent = list(lTagent.GetDirectArray()[ctrlPointIndex])
						elif lTagent.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							idx = lTagent.GetIndexArray()[ctrlPointIndex]
							tagent= list(lTagent.GetDirectArray()[idx])
					elif lTagent.GetMappingMode() == FbxLayerElement.eByPolygonVertex:
						if lTagent.GetReferenceMode() == FbxLayerElement.eDirect:
							tagent = list(lTagent.GetDirectArray()[vertexCounter])
						elif lTagent.GetReferenceMode() == FbxLayerElement.eIndexToDirect:
							idx = lTagent.GetIndexArray()[vertexCounter]
							tagent= list(lTagent.GetDirectArray()[idx])
				vertexData.tagent = tagent
				#print 'tagent', tagent

				#print vertexData

				triangleData.addVertex(vertexData)
				meshData.addVertex(vertexData)

				vertexCounter += 1
			#add triangle
			meshData.addTriangle(triangleData)

		#load Materials
		meshNode = mesh.GetNode()
		if meshNode:
			materialCount = meshNode.GetMaterialCount()
			for matIdx in xrange(materialCount):
				lSurfMaterial = meshNode.GetMaterial(matIdx)
				matName = lSurfMaterial.GetName()
				materialData = MaterialData(matName)
				if lSurfMaterial.ClassId.GetName() == 'FbxSurfacePhong':
					materialData.Ambient = list(lSurfMaterial.Ambient.Get())
					materialData.Diffuse = list(lSurfMaterial.Diffuse.Get())
					materialData.Specular = list(lSurfMaterial.Specular.Get())
					materialData.Emissive = list(lSurfMaterial.Emissive.Get())
					materialData.Transparency = lSurfMaterial.TransparencyFactor.Get()
					materialData.Shininess = lSurfMaterial.Shininess.Get()
					materialData.Reflection = lSurfMaterial.ReflectionFactor.Get()
				elif lSurfMaterial.ClassId.GetName() == 'FbxSurfaceLambert':
					materialData.Ambient = list(lSurfMaterial.Ambient.Get())
					materialData.Diffuse = list(lSurfMaterial.Diffuse.Get())
					materialData.Emissive = list(lSurfMaterial.Emissive.Get())
					materialData.Transparency = lSurfMaterial.TransparencyFactor.Get()
				else:
					raise NotImplementedError

				#load Textures
				materialData.textures = []
				for lTextureIndex in xrange(FbxLayerElement.sTypeTextureCount()):
					lProperty = lSurfMaterial.FindProperty(FbxLayerElement.sTextureChannelNames(lTextureIndex))
					if lProperty.IsValid():
						lLayeredTextureCount = lProperty.GetSrcObjectCount(FbxLayeredTexture.ClassId)
						if lLayeredTextureCount > 0:
							for j in range(lLayeredTextureCount):
								lLayeredTexture = lProperty.GetSrcObject(FbxLayeredTexture.ClassId, j)
								lNbTextures = lLayeredTexture.GetSrcObjectCount(FbxTexture.ClassId)
								for k in range(lNbTextures):
									lTexture = lLayeredTexture.GetSrcObject(FbxTexture.ClassId,k)
									if lTexture:
										print "Textures for ", lProperty.GetName().Buffer()
										lBlendMode = lLayeredTexture.GetTextureBlendMode(k)
										textureData = self.loadTextureInfo(lTexture, lBlendMode)
										materialData.textures.append(textureData)
						else:
							# no layered texture simply get on the property
							lNbTextures = lProperty.GetSrcObjectCount(FbxTexture.ClassId)
							for j in range(lNbTextures):
								lTexture = lProperty.GetSrcObject(FbxTexture.ClassId,j)
								if lTexture:
									print "Textures", j, " for ", lProperty.GetName().Buffer()
									textureData = self.loadTextureInfo(lTexture, -1)
									materialData.textures.append(textureData)

				#add to mesh
				meshData.addMaterial(materialData)

		#connect material
		triangleMaterials = self.loadTriangleMaterials(mesh, triangleCount)
		if triangleMaterials:
			for triIdx in xrange(triangleCount):
				triangle = meshData.triangleList[triIdx]
				triangle.materialIndex = triangleMaterials[triIdx]

		#print meshData

		return meshData


if __name__ == "__main__":
	#loader = FbxSceneLoader('assets/box_only_2013.fbx')
	#print '-------------------------------------------'
	#loader = FbxSceneLoader('assets/box_only_2014.fbx')
	FbxSceneLoader('assets/box_unit.fbx')

