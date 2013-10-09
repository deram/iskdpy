import logging
logger = logging.getLogger(__name__)


class Source(object):
	_subs_ = {}

	def __init__(self, config=None):
		self.display=None
		self.control=None

	def get_display(self):
		if (not self.display):
			self.update_display()
		return self.display

	def update_display(self):
		return False

	def update_slide(self, slide):
		return slide

	def connect(self):
		return False

	def slide_done(self, slide):
		return False

	def get_path(self):
		return "."
	
	def run_control(self):
		return False

	def register_control(self, control):
		self.control=control

	@classmethod
	def factory(cls, name):
		try:
			return cls._subs_[name]
		except KeyError:
			raise FactoryError(name, "Unknown subclass")

	@classmethod
	def register(cls, name):
		def decorator(subclass):
			logger.debug("Registered %s" % name)
			cls._subs_[name] = subclass
			return subclass
		return decorator

class FactoryError(Exception):
	pass
