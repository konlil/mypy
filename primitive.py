#coding: gbk
import struct
import d3d11
from d3d11c import *

#16 and 32 bit indices.
indexLayoutDesc16 = [("", 0, FORMAT_R16_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]
indexLayoutDesc32 = [("", 0, FORMAT_R32_UINT, 0, 0, INPUT_PER_VERTEX_DATA, 0)]

class IndexHeader(object):
	FORMAT = "=64sii"
	SIZE = 72
	def __init__(self):
		self.indexFormat = []
		self.nIndices = 0
		self.nTriangleGroups = 0

class PrimGroup(object):
	FORMAT = "=4i"
	SIZE = 16
	def __init__(self):
		self.startIndex = 0
		self.nPrimitives = 0
		self.startVertex = 0
		self.nVertices = 0

class Primitive(object):
	def __init__(self):
		self.nIndices = 0
		self.primitiveType = PRIMITIVE_TOPOLOGY_UNDEFINED
		self.indexBuffer = None
		self.indices = []
		self.indexSize = 2		# FORMAT_R16_UINT

	def load(self, res):
		self.res = res
		import resmgrdll
		import ResMgr
		print 'load primitive:', res
		noff = self.res.find('.primitives/')
		if noff < 0:
			raise Exception
		noff += 11
		fileName = self.res[:noff]
		tagName = self.res[noff+1:]
		primFile = ResMgr.openSection(fileName)
		print 'open primitive', fileName
		if not primFile:
			raise Exception, 'load indices failed, %s' % fileName

		print 'read indices:', tagName
		indices = primFile.openSection(tagName)
		indices = indices.asBinary
		if indices:
			ih = IndexHeader()
			seg0 = 0
			seg1 = IndexHeader.SIZE
			print struct.calcsize(IndexHeader.FORMAT), IndexHeader.SIZE
			ih.indexFormat, ih.nIndices, ih.nTriangleGroups = struct.unpack(IndexHeader.FORMAT, indices[seg0:seg1])
			ih.indexFormat = ih.indexFormat.split('\0')[0]
			print ih.indexFormat, ih.nIndices, ih.nTriangleGroups

			if ih.indexFormat == 'list' or ih.indexFormat == 'list32':
				indexDesc = indexLayoutDesc16 if ih.indexFormat == 'list' else indexLayoutDesc32
				if ih.indexFormat == 'list32':
					raise Exception, 'not considered index format:', ih.indexFormat
				self.primitiveType = PRIMITIVE_TOPOLOGY_TRIANGLELIST

				seg0, seg1 = seg1, seg1 + ih.nIndices * self.indexSize
				self.indices = struct.unpack('%dH'%ih.nIndices, indices[seg0:seg1])
				self.nIndices = ih.nIndices

				#create index buffer
				tmpindices = [(int(v),) for v in self.indices]
				self.indexBuffer = d3d11.Buffer(indexLayoutDesc16, tmpindices, BIND_INDEX_BUFFER, USAGE_DYNAMIC, CPU_ACCESS_WRITE)
