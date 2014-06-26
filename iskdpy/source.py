import logging
logger = logging.getLogger(__name__)

from .utils.async_proc import AsyncProcess

class Source(object):
	_subs_ = {}
	_current_ = None
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

	def get_callback(self):
		return getattr(self, '_AsyncProcess__callback')

	# Signals from source plugin to presenter
	def _display_updated(self):
		from .presenter import display_updated
		return display_updated()
	def _goto_next_slide(self):
		from .presenter import goto_next_slide
		return goto_next_slide()
	def _goto_previous_slide(self):
		from .presenter import goto_previous_slide
		return goto_previous_slide()
	def _goto_slide(self, *args, **kwargs):
		from .presenter import goto_slide
		return goto_slide(*args, **kwargs)
	def _refresh_slide_cache(self, *args, **kwargs):
		from .presenter import refresh_slide_cache
		return refresh_slide_cache(*args, **kwargs)

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
