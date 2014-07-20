import logging
logger = logging.getLogger(__name__)

from .utils.async_proc import AsyncProcess

class OutputPlugin(object):
	_subs_ = {}
	_current_ = None

	def __init__(self):
		pass

	def run(self):
		'''
		Plugin main method.
		Should return only after the output is closed.
		'''
		pass

	def set_slide(self, slide):
		'''
		Change the shown slide to another.

		Args:
			slide (iskdpy.types.Slide or iskdpy.types.OverrideSlide) -- Slide to be shown.
		'''
		pass

	def cancel_transition(self):
		'''Cancel any ongoing transition and set the transition target current'''
		pass

	def refresh_slide_cache(self, slide):
		'''
		Force refreshing the slide image from filesystem.

		Args:
			slide (iskdpy.types.Slide or iskdpy.types.OverrideSlide) -- Slide needing cache refresh.
		'''
		pass

	def task(self):
		pass

	def _get_callback(self):
		'''
		Return object that can be used for calling methods in main process.
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

### Module methods

def run():
	'''Shortcut to current OutputPlugin.run'''
	logger.debug("output.run")
	with OutputPlugin.get_current().run() as ret:
		logger.debug("output.run end")
		return ret

def set_slide(slide):
	'''Shortcut to current OutputPlugin.set_slide'''
	logger.debug("output.set_slide (%.100s)", slide)
	with OutputPlugin.get_current().set_slide(slide) as ret:
		logger.debug("output.set_slide end")
		return ret

def cancel_transition():
	'''Shortcut to current OutputPlugin x.cancel_transition()'''
	logger.debug("output.cancel_transition")
	with OutputPlugin.get_current().cancel_transition() as ret:
		logger.debug("output.cancel_transition end")
		return ret

def refresh_slide_cache(slide):
	'''Shortcut to current OutputPlugin.refresh_slide_cache'''
	'''
	Force refreshing the slide image from filesystem.

	Args:
		slide (iskdpy.types.Slide or iskdpy.types.OverrideSlide)
	'''
	logger.debug("refresh_slide_cache(%.100s)", slide)
	with OutputPlugin.get_current().refresh_slide_cache(slide) as ret:
		logger.debug("output.refresh_slide_cache end")
		return ret

