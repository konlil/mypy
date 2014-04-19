from FbxCommon import *
import d3d11
import d3d11x
from d3d11c import *

import model

class Scene(object):
	def __init__(self, path):
		self.res = path

	def load(self):
		pass

class FbxScene(Scene):
	def __init__(self, path):
		super(FbxScene, self).__init__(path)
		self.models = []

	def load(self):
		lSdkManager, lScene = InitializeSdkObjects()
		lResult = LoadScene(lSdkManager, lScene, self.res)
		if not lResult:
			print("An error occurred while loading scene: %s"%self.res)
			return

		self.loadHierarchy(lScene)

		lSdkManager.Destroy()

	def loadHierarchy(self, scene):
		lRootNode = scene.GetRootNode()
		for i in xrange(lRootNode.GetChildCount()):
			self.loadNodeContent(lRootNode.GetChild(i))

	def loadNodeContent(self, node):
		if not node.GetNodeAttribute():
			return

		attrType = node.GetNodeAttribute().GetAttributeType()
		if attrType == FbxNodeAttribute.eMarker:
			pass
		elif attrType == FbxNodeAttribute.eSkeleton:
			pass
		elif attrType == FbxNodeAttribute.eMesh:
			m = model.FbxModel()
			m.fromFbxNode(node)
			m.setWorld(self.getNodeWorldMatrix(node))
			self.models.append(m)
		elif attrType == FbxNodeAttribute.eNurbs:
			pass
		elif attrType == FbxNodeAttribute.ePatch:
			pass
		elif attrType == FbxNodeAttribute.eCamera:
			pass
		elif attrType == FbxNodeAttribute.eLight:
			pass

	def getNodeWorldMatrix(self, node):
		worldMat = d3d11.Matrix()
		worldTrans = node.EvaluateGlobalTransform()
		#lTranslation = node.LclTranslation;
		#lRotation    = node.LclRotation;
		#lScaling     = node.LclScaling;
		#print type(worldMat), dir(worldMat)
		for i in xrange(4):
			for j in xrange(4):
				worldMat[i][j] = worldTrans.Get(i, j)
		return worldMat

	def render(self, device, view, proj):
		for m in self.models:
			m.render(device, view, proj)

if __name__ == "__main__":
	sc = FbxScene('export/test.fbx')
	sc.load()
