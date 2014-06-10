import logging
logger = logging.getLogger(__name__)

from .utils.queued_thread import QueuedThread
thread=QueuedThread()
thread.start()

class Source(object):
	_subs_ = {}
	_current_ = None
	@thread.decorate
	def __init__(self, config=None):
		self.display=None
		self.control=None

	@thread.decorate
	def get_display(self):
		if (not self.display):
			self.update_display()
		return self.display

	@thread.decorate
	def update_display(self):
		return False

	@thread.decorate
	def update_slide(self, slide):
		return slide

	@thread.decorate
	def connect(self):
		return False

	@thread.decorate
	def slide_done(self, slide):
		return False

	@thread.decorate
	def get_path(self):
		return "."

	@classmethod
	def factory(cls, name, *args, **kwargs):
		try:
			cls._current_ = cls._subs_[name](*args, **kwargs)
			return cls._current_
		except KeyError:
			raise FactoryError(name, "Unknown subclass")

	@classmethod
	def register(cls):
		def decorator(subclass):
			name=subclass.__name__
			logger.debug("Registered %s" % name)
			cls._subs_[name] = subclass
			return subclass
		return decorator

	@classmethod
	def get_current(cls):
		return cls._current_

class FactoryError(Exception):
	pass
