#coding:gbk
import os
import vertices
import primitive
import effect_material

class PrimitiveGroup(object):
	def __init__(self):
		self.groupIdx = 0
		self.material = None #effect_material.EffectMaterial()

class Geometry(object):
	def __init__(self):
		self.name = ''
		self.vertices = None 	# vertices.Vertices()
		self.primitive = None 	# primitive.Primitive()
		self.primitiveGroups = []		#object: PrimitiveGroup

class RenderSet(object):
	def __init__(self):
		self.treatAsWorldSpaceObject = False
		self.skinnedNodeNames = []
		self.skinnedNodeVisitor = None
		self.clothBoneNames = []
		self.clothBoneVisitor = None
		self.geometry = []		#object: Geometry

#  Visual
#     +--renderSets
#	       +--geometry
#		         +--vertices
#				 +--primitive
class Visual(object):
	def __init__(self):
		self.ownMaterials = []
		self.renderSets = []
		pass

	def load(self, res):
		import resmgrdll
		import ResMgr
		self.res = res
		print 'load visual', self.res
		baseName = self.res.split('.')[0]
		self.fileSection = ResMgr.openSection(self.res)

		#[TODO]: load bsp tree

		# load primitives
		primitivesName = '%s.primitives' % baseName

		# load rendersets
		renderSets = self.fileSection.openSections("renderSet")
		if not renderSets:
			raise Exception, "no rendersets in %s" % self.res

		for rs in renderSets:
			rset = RenderSet()
			self.renderSets.append(rset)

			rset.treatAsWorldSpaceObject = rs.readBool('treatAsWorldSpaceObject')
			rset.skinnedNodeNames = rs.readStrings('node')
			rset.clothBoneNames = rs.readStrings('clothBone')

			geometries = rs.openSections('geometry')
			if not geometries:
				raise Exception, 'no geometry in renderset in %s' % self.res

			for gs in geometries:
				geo = Geometry()
				rset.geometry.append(geo)

				verticesName = gs.readString('vertices')
				geo.name = verticesName.split('.')[0]

				# read vertices
				if '/' not in verticesName:
					verticesName = '%s/%s' % (primitivesName, verticesName)
				geo.vertices = vertices.Vertices()
				geo.vertices.load(verticesName)

				# read indices of the geometry
				indicesName = gs.readString("primitive")
				if '/' not in indicesName:
					indicesName = '%s/%s' % (primitivesName, indicesName)
				geo.primitive = primitive.Primitive()
				geo.primitive.load(indicesName)

				# primitive group descriptions
				primitiveGroups = gs.openSections("primitiveGroup")
				for ps in primitiveGroups:
					pg = PrimitiveGroup()
					pg.groupIdx = ps.asInt

					mat = effect_material.EffectMaterial()
					self.ownMaterials.append(mat)
					pg.material = mat
					mat.load(ps.openSection("material"))

					geo.primitiveGroups.append(pg)
