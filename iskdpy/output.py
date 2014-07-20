import logging
logger = logging.getLogger(__name__)

from .utils.async_proc import AsyncProcess

class OutputPlugin(object):
	_subs_ = {}
	_current_ = None

	def __init__(self):
		pass

	def run(self):
		pass

	def set_slide(self, slide):
		pass

	def refresh_slide_cache(self, slide):
		pass

	def task(self):
		pass
	
	def _get_callback(self):
		'''
		return getattr(self, '_AsyncProcess__callback')

	# Callbacks to output plugins needing to command presenter
	def _goto_next_slide(self):
		from .presenter import goto_next_slide
		goto_next_slide()
	def _goto_previous_slide(self):
		from .presenter import goto_previous_slide
		goto_previous_slide()

	@classmethod
	def factory(cls, name, *args, **kwargs):
		try:
			cls._current_ = AsyncProcess(cls._subs_[name](*args, **kwargs))
			return cls._current_
		except KeyError:
			raise FactoryError(name, "Unknown subclass")

	@classmethod
	def register(cls):
		def decorator(subclass):
			name=subclass.__name__
			logger.debug("Registered %s", name)
			cls._subs_[name] = subclass
			return subclass
		return decorator

	@classmethod
	def get_current(cls):
		return cls._current_

class FactoryError(Exception):
	pass

