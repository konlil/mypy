#coding:gbk

class NodeDesc(object):
	def __init__(self, d):
		self.attrs_keys = []
		for k, v in d.iteritems():
			if k == 'vtdesc':
				v = self.formatVertexDesc(v)
			object.__setattr__(self, k, v)
			self.attrs_keys.append(k)

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
	# vertexDesc = [
	    # ("POSITION", 0, FORMAT_R32G32B32_FLOAT, 0, 0, INPUT_PER_VERTEX_DATA, 0),
	    # ("NORMAL", 0, FORMAT_R32G32B32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),
	    # ("COLOR", 0, FORMAT_R32G32B32A32_FLOAT, 0, APPEND_ALIGNED_ELEMENT, INPUT_PER_VERTEX_DATA, 0),

	    #This is functionally same as above, only easier to read. I use the complex one now
	    #so that you don't get confused when you encounter it in samples.
	    #("POSITION", 0, FORMAT_R32G32B32_FLOAT),
	    #("COLOR", 0, FORMAT_R32G32B32A32_FLOAT),
	# ]
	def formatVertexDesc(self, deflist):
		import d3d11c
		desc =[]
		idx = 0
		for v in deflist:
			SemanticName = v[0]
			Format = getattr(d3d11c, v[1])
			InputSlotClass = getattr(d3d11c, v[2])
			if idx == 0:
				AlignedByteOffset=0
			else:
				AlignedByteOffset=d3d11c.APPEND_ALIGNED_ELEMENT
			idx += 1
			desc.append((SemanticName, 0, Format, 0, AlignedByteOffset, InputSlotClass, 0))
		return desc	

	def __str__(self):
		result = []
		for k in self.attrs_keys:
			result.append("%s: %s"%(k, object.__getattribute__(self, k)))
		return '\n'.join(result)

class SceneDesc(object):
	def __init__(self, res):
		self.res = res
		self.descs = {}
		execfile(res, self.__dict__)
		for nodeName, v in self.data.iteritems():
			self.descs[nodeName] = NodeDesc(v)

	def getNode(self, nodeName):
		return self.descs.get(nodeName, None)



if __name__ == "__main__":
	a = SceneDesc('assets/box_only.desc')
	print a.getNode('Box001')
