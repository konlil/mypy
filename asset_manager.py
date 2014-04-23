#coding: utf8
import d3d11c

class AssetMgr(object):
	def __init__(self):
		self.assets = {}

	def load(self, res):
		self.assets[res] = Asset(res)
		return self.assets[res]

class Asset(object):
	def __init__(self, res):
		self.res = res
		execfile(res, self.__dict__)

	def __getattr__(self, name):
		try:
			return self.data[name]
		except:
			raise AttributeError("No property named: %s"%name)

	def __setattr__(self, name, value):
		if hasattr(self, name):
			raise AttributeError("Property %s is read only."%name)
		else:
			object.__setattr__(self, name, value)

	def __str__(self):
		return "%s:\n\t%s"%(self.res, str(self.data))



inst = AssetMgr()
if __name__ == "__main__":
	a = inst.load('assets/box_only.desc')
	print a
	print a.vertexDesc
