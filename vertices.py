#coding: gbk
import struct
'''
Format 	C Type 				Python type 		Standard size 	Notes
x 		pad byte 			no value
c 		char 				string of length 	1 				1
b 		signed char 		integer 			1 				(3)
B 		unsigned char 		integer 			1 				(3)
? 		_Bool 				bool 				1 				(1)
h 		short 				integer 			2 				(3)
H 		unsigned short 		integer 			2 				(3)
i 		int 				integer 			4 				(3)
I 		unsigned int 		integer 			4 				(3)
l 		long 				integer 			4 				(3)
L 		unsigned long 		integer 			4 				(3)
q 		long long 			integer 			8 				(2), (3)
Q 		unsigned long long 	integer 			8 				(2), (3)
f 		float 				float 				4 				(4)
d 		double 				float 				8 				(4)
s 		char[] 				string
p 		char[] 				string
P 		void * 				integer 	  						(5), (3)
'''
class vt_baseType(object):
	FORMAT = ''
	SIZE = 0
	def __init__(self, t):
		self.__tuple = t

	def __str__(self):
		return str(self.__tuple)

class vt_XYZNUVTB(vt_baseType):
	FORMAT = "3fI2fII"
	SIZE = 32 	#bytes
	def __init__(self, t):
		super(vt_XYZNUVTB, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = t[3]
		self.uv = (t[4], t[5])
		self.tangent = t[6]
		self.binormal = t[7]

class vt_XYZNUV2(vt_baseType):
	FORMAT = "3f3f2f2f"
	SIZE = 40 	#bytes
	def __init__(self, t):
		super(vt_XYZNUV2, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = (t[3], t[4], t[5])
		self.uv = (t[6], t[7])
		self.uv2 = (t[8], t[9])

class vt_XYZNUV(vt_baseType):
	FORMAT = "3f3f2f"
	SIZE = 32 	#bytes
	def __init__(self, t):
		super(vt_XYZNUV, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = (t[3], t[4], t[5])
		self.uv = (t[6], t[7])

class vt_XYZNDUV(vt_baseType):
	FORMAT = "3f3fI2f"
	SIZE = 36 	#bytes
	def __init__(self, t):
		super(vt_XYZNDUV, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = (t[3], t[4], t[5])
		self.color = t[6]
		self.uv = (t[7], t[8])

class vt_XYZNUV2TB(vt_baseType):
	FORMAT = "3fi2f2fII"
	SIZE = 40 	#bytes
	def __init__(self, t):
		super(vt_XYZNUV2TB, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = t[3]
		self.uv = (t[4], t[5])
		self.uv2 = (t[6], t[7])
		self.tangent = t[8]
		self.binormal = t[9]

class vt_XYZNUVIIIWW(vt_baseType):
	FORMAT = "3fI2f5B"
	SIZE = 29 	#bytes
	def __init__(self, t):
		super(vt_XYZNUVIIIWW, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = t[3]
		self.uv = (t[4], t[5])
		self.index = t[6]
		self.index2 = t[7]
		self.index3 = t[8]
		self.weight = t[9]
		self.weight2 = t[10]

class vt_XYZNUVIIIWWTB(vt_baseType):
	FORMAT = "=3fI2f5BII"
	SIZE = 37 	#bytes
	def __init__(self, t):
		super(vt_XYZNUVIIIWWTB, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = t[3]
		self.uv = (t[4], t[5])
		self.index = t[6]
		self.index2 = t[7]
		self.index3 = t[8]
		self.weight = t[9]
		self.weight2 = t[10]
		self.tangent = t[11]
		self.binormal = t[12]

class vt_XYZNUVITB(vt_baseType):
	FORMAT = "3fI2ffII"
	SIZE = 36 	#bytes
	def __init__(self, t):
		super(vt_XYZNUVITB, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = t[3]
		self.uv = (t[4], t[5])
		self.index = t[6]
		self.tangent = t[7]
		self.binormal = t[8]

class vt_XYZNUVI(vt_baseType):
	FORMAT = "3f3f2ff"
	SIZE = 36 	#bytes
	def __init__(self, t):
		super(vt_XYZNUVI, self).__init__(t)
		self.pos = (t[0], t[1], t[2])
		self.normal = (t[3], t[4], t[5])
		self.uv = (t[6], t[7])
		self.index = t[8]

class VertexHeader(object):
	FORMAT = "64si"
	SIZE = 68
	def __init__(self):
		self.vertexFormat = ''	# 64 char
		self.verticesCount = 0

class Vertices(object):
	def __init__(self):
		self.vertexStride = 0
		self.vertices = []
		self.vertexPositions = []

	def load(self, res):
		self.res = res
		import resmgrdll
		import ResMgr
		print 'load vertices:', res
		noff = self.res.find('.primitives/')
		if noff < 0:
			raise Exception
		noff += 11
		fileName = self.res[:noff]
		tagName = self.res[noff+1:]
		primFile = ResMgr.openSection(fileName)
		print 'open primitive', fileName
		if not primFile:
			raise Exception, 'load vertices failed, %s' % fileName

		print 'read vertices:', tagName
		vertices = primFile.openSection(tagName)
		vertices = bytes(vertices.asBinary)
		if vertices:
			vh = VertexHeader()
			seg0 = 0
			seg1 = VertexHeader.SIZE
			vh.vertexFormat, vh.verticesCount = struct.unpack(VertexHeader.FORMAT, vertices[seg0:seg1])
			vh.vertexFormat = vh.vertexFormat.split('\0')[0]
			print vh.vertexFormat, vh.verticesCount
			if vh.vertexFormat == 'xyznuvtb':
				self.vertexStride = vt_XYZNUVTB.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUVTB.SIZE
					vertex = vt_XYZNUVTB( struct.unpack(vt_XYZNUVTB.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
					#print vertex
			elif vh.vertexFormat == 'xyznuv2':
				self.vertexStride = vt_XYZNUV2.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUV2.SIZE
					vertex = vt_XYZNUV2( struct.unpack(vt_XYZNUV2.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznuv':
				self.vertexStride = vt_XYZNUV.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUV.SIZE
					vertex = vt_XYZNUV( struct.unpack(vt_XYZNUV.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznduv':
				self.vertexStride = vt_XYZNDUV.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNDUV.SIZE
					vertex = vt_XYZNDUV( struct.unpack(vt_XYZNDUV.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznuv2tb':
				self.vertexStride = vt_XYZNUV2TB.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUV2TB.SIZE
					vertex = vt_XYZNUV2TB( struct.unpack(vt_XYZNUV2TB.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznuviiiww':
				self.vertexStride = vt_XYZNUVIIIWW.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUVIIIWW.SIZE
					vertex = vt_XYZNUVIIIWW( struct.unpack(vt_XYZNUVIIIWW.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznuviiiwwtb':
				self.vertexStride = vt_XYZNUVIIIWWTB.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUVIIIWWTB.SIZE
					vertex = vt_XYZNUVIIIWWTB( struct.unpack(vt_XYZNUVIIIWWTB.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
					#print vertex
			elif vh.vertexFormat == 'xyznuvitb':
				self.vertexStride = vt_XYZNUVITB.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUVITB.SIZE
					vertex = vt_XYZNUVITB( struct.unpack(vt_XYZNUVITB.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			elif vh.vertexFormat == 'xyznuvi':
				self.vertexStride = vt_XYZNUVI.SIZE
				for i in xrange(vh.verticesCount):
					seg0 = seg1
					seg1 = seg0 + vt_XYZNUVI.SIZE
					vertex = vt_XYZNUVI( struct.unpack(vt_XYZNUVI.FORMAT, vertices[seg0:seg1]) )
					self.vertices.append(vertex)
					self.vertexPositions.append(vertex.pos)
			else:
				raise Exception, "Failed to recognise vertex format: %s" % vh.vertexFormat
