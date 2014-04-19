#coding: gbk

class EffectProperty(object):
	def __init__(self):
		self.index = 0

class EffectMaterial(object):
	def __init__(self):
		self.identifier = ''
		self.effect = None  # Managed effect
		self.technique = None
		self.fxname = ''
		self.properties = []	# EffectProperty
		self.channelOverridden = False

	def load(self, section):
		effectProperties = {}
		self.loadInternal(section, effectProperties)
		# [TODO] fill the effect properties

	def loadInternal(self, section, outDict):
		if not self.identifier:
			self.identifier = section.readString('identifier')

		fxNames = section.readStrings('fx')
		if len(fxNames) > 1:
			raise Exception, "EffectMaterial::loadInternal - found multiple .fx files in %s" % self.identifier

		if not self.effect and len(fxNames) > 0:
			self.effect = None
			self.fxname = ''
			self.properties = []
			self.technique = None
			if not self.loadEffect(fxNames[0]):
				raise Exception, "EffectMaterial::loadInternal - unable to open .fx file %s" % fxNames[0]
			self.fxname = fxNames[0]

		if not self.channelOverridden:
			channel = section.readString('channel')
			if channel:
				self.channel = None # [TODO] get channel
				self.channelOverridden = True

		# load another material file if we are inheriting
		mfmsect = section.openSection('mfm')
		if mfmsect:
			basesect = ResMgr.openSection(mfmsect.asString())
			if basesect:
				self.loadInternal(basesect, outDict)

		propSections = section.openSections('property')
		if propSections:
			for propsect in propSections:
				pass

	def loadEffect(self, effectRes):
		# [TODO] create effect instance
		print 'loadEffect:', effectRes
		self.effect = None
		return True