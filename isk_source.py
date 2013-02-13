
class Source(object):
	_subs_ = {}

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

	@classmethod
	def factory(cls, name):
		try:
			return cls._subs_[name]
		except KeyError:
			raise FactoryError(tag, "Unknown subclass")

	@classmethod
	def register(cls, name):
		def decorator(subclass):
			cls._subs_[name] = subclass
			return subclass
		return decorator


