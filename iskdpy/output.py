import logging
logger = logging.getLogger(__name__)

from .utils.queued_thread import QueuedThread
thread=QueuedThread()
thread.start()

class OutputPlugin(object):
	_subs_ = {}
	_current_ = None

	@thread.decorate
	def __init__(self):
		pass

	@thread.decorate
	def run(self):
		pass

	@thread.decorate
	def set_slide(self, slide):
		pass

	@thread.decorate
	def refresh_slide_cache(self, slide):
		pass

	def task(self):
		global thread
		thread.work_all()

	@classmethod
	def factory(cls, name, *args, **kwargs):
		try:
			cls._current_ = cls._subs_[name](*args, **kwargs)
			return cls._current_
		except KeyError:
			raise FactoryError(name, "Unknown subclass")

	@classmethod
	def register(cls, name):
		def decorator(subclass):
			logger.debug("Registered %s" % name)
			cls._subs_[name] = subclass
			return subclass
		return decorator

	@classmethod
	def get_current(cls):
		return cls._current_

class FactoryError(Exception):
	pass

