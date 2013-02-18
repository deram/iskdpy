
class Source(object):
	_subs_ = {}
	_suborder_ = []

	def __init__(self):
		self.display=None

	def get_display(self):
		if (not self.display):
			self.update_display()
		return self.display

	def update_display(self):
		return false

	def update_slide(self, slide):
		return slide

	def connect(self):
		return False

	def slide_done(self, slide):
		return False

	def get_path(self):
		return "."

	@classmethod
	def factory(cls, name=None):
		if name:
			try:
				return cls._subs_[name]
			except KeyError:
				raise FactoryError(tag, "Unknown subclass")
		else:
			name = cls._suborder_.pop()
			print 'Used %s' % name
			return cls._subs_[name]

	@classmethod
	def register(cls, name):
		def decorator(subclass):
			print "Registered %s" % name
			cls._subs_[name] = subclass
			cls._suborder_.append(name)
			return subclass
		return decorator


