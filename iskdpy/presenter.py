import logging
logger = logging.getLogger(__name__)

from .types import Slide, OverrideSlide
from .source import SourcePlugin
from .output import OutputPlugin 
#import gc
from . import config

from threading import Timer


class _PresenterState(object):
	def __init__(self, display=None):
		self.timer=None
		self._display=display
		self._pos=-1
		self._current_slide=get_empty_slide()
		self._schedule_show_slide=False

	def __str__(self):
		return "%s disp: %.25s pos: %3d %s" % (self.__class__.__name__, self.display, self.pos, self.current_slide)

	def seek_to_first(self):
		self.pos=-1

	def show_slide(self, slide=None):
		if self is _state:
			if self.pos<0 and len(self.presentation):
				self.pos=0
			_show_slide(self.current_slide)
		else:
			self._schedule_show_slide=True

	def update(self, new):
		logger.debug("state updated")
		self._display=new._display
		self._pos=new._pos
		self._current_slide=new._current_slide
		if new._schedule_show_slide:
			self.show_slide()

	@property	
	def display(self):
		return self._display
	@property
	def presentation(self):
			return self.display.presentation
	@property
	def manual(self):
		try:
			return self.display.manual
		except (AttributeError):
			return False

	@property
	def current_slide(self):
		try:
			return self._current_slide
		except (IndexError, AttributeError, TypeError):
			logger.warning("No active slide, returning empty")
			return get_empty_slide()

	@current_slide.setter
	def current_slide(self, slide):
		if slide is None:
			self.seek_to_first()
		elif isinstance(slide,OverrideSlide):
			self._current_slide=slide
		elif slide == self.current_presentation_slide:
			self._current_slide=slide
		else:
			self.pos=self.presentation.locate_slide(sid=slide.id, gid=slide.group)
			if self.pos is None:
				self.seek_to_first()

	@property
	def current_presentation_slide(self):
		if self.pos >=0:
			return self.presentation[self.pos]

	@property
	def pos(self):
		return self._pos

	@pos.setter
	def pos(self, pos):
		self._pos=pos
		if pos>=0:
			self.current_slide=self.current_presentation_slide

def run():
	output=OutputPlugin.factory(config.output)
	output_ret=output.run()
	_next_source()

	output_ret.get()


def _connect(conf):
	source = SourcePlugin.factory(conf.pop('source_name'), conf)
	if source.connect():
		with source.get_display() as disp:
			if disp:
				_state.display=disp
				_seek_to_presentation_beginning()

def _next_source():
	if len(config.sources):
		_connect(config.sources.pop())

def _handle_manual_mode(old, new):
	if new:
		if old:
			if old.manual == new.manual:
				return
		if new.manual:
			_cancel_slide_change()
		else:
			_schedule_slide_change()

def _handle_current_slide_updated(old, new):
	if old.id == new.id:
		if new.ready and (not old.ready or old.updated_at < new.updated_at):
			if old.type != 'video':
				_show_slide(new)

def _handle_display_changed(old, new):
	if not old == new:
		if not old or old.name != new.name:
			logger.info("Display changed.")
			_seek_to_presentation_beginning()
			return True
		elif old.presentation.id != new.presentation.id:
			logger.info("Presentation changed.")
			_seek_to_presentation_beginning()
			return True
	return False


def _handle_presentation_updated(old, new):
	try:
		slide=_get_current_slide()
		new_pos = new.locate_slide(slide.id, slide.group) 
	except (IndexError, AttributeError):
		logger.warning("Current slide not in presentation, restarting presentation")
		_seek_to_presentation_beginning()
	else:
		_state.pos=new_pos
	return True

def _update_display():
	if (get_source().update_display()):
		new_display=None
		with get_source().get_display() as disp:
			if disp:
				new_display=disp
		old_display=_state.display
		if _handle_display_changed(old_display, new_display):
			_state.display=new_display
		elif _handle_presentation_updated(old_display.presentation, new_display.presentation):
			old_slide=_get_current_slide()
			_state.display=new_display
			_handle_current_slide_updated(old_slide, _get_current_slide())
	
		_handle_manual_mode(old_display, new_display)
		return True
	return False

def _seek_to_presentation_beginning():
	_state.pos = -1

def _get_presentation():
	return _state.display.presentation

def _get_current_slide():
	try:
		return _get_presentation()[_state.pos]
	except (IndexError, AttributeError, TypeError):
		logger.warning("Current slide not existing")
		return Slide()

def _set_current_slide(gid, sid):
	try:
		new_pos = _get_presentation().locate_slide(sid, gid)

		if _get_presentation()[new_pos].valid:
			_state.pos=new_pos
			return True
	except (IndexError, AttributeError, TypeError):
		logger.warning("Slide not in presentationi (%s,%s). Not changing.", gid, sid)
	return False

def _seek_to_next_valid_slide_in_presentation():
	n_slides = len(_get_presentation())
	for _ in xrange(_get_presentation().total_slides):
		_state.pos += 1
		if ( _state.pos >= n_slides ):
			_state.pos = 0
			logger.info("Presentation wrapped")
		logger.debug("Next: %s", unicode(_get_current_slide()).split('\n', 1)[0])

		if _get_current_slide().valid:
			return True
	return False

def _seek_to_previous_valid_slide_in_presentation():
	n_slides = len(_get_presentation())
	for _ in xrange(_get_presentation().total_slides):
		_state.pos -= 1
		if ( _state.pos < 0 ):
			_state.pos = n_slides - 1
			logger.info("Presentation wrapped")
		logger.debug("Prev: %s", unicode(_get_current_slide()).split('\n', 1)[0])

		if _get_current_slide().valid:
			return True
	return False

def _is_override():
	override=_state.display.override_queue
	if len( override ):
		return override[0].valid
	return False

def _pop_override_slide():
	override=_state.display.override_queue
	if len( override ):
		ret = override[0]
		del override[0]
		return ret
	return False

def _is_manual():
	return _state.display and _state.display.manual

def _is_empty_presentation():
	return ((_state.display.presentation.total_slides) == 0)

def _get_next():
	return _get_slide('next')

def _get_previous():
	return _get_slide('previous')

def _get_slide(slide='next'):
	if not _state.display:
		if not _update_display():
			logger.error("NO DISPLAY FROM SOURCE")
			return Slide()
	if ( _is_override() ):
		ret = _pop_override_slide()
	else:
		if (_is_empty_presentation()):
			logger.warning("EMPTY PRESENTATION")
			return Slide()
		if slide=='next':
			_seek_to_next_valid_slide_in_presentation()
		elif slide=='previous':
			_seek_to_previous_valid_slide_in_presentation()
		ret = _get_current_slide()

	logger.debug("Next: %s", ret)
	return ret

def _cancel_slide_change():
	if _state.timer and _state.timer.is_alive():
		_state.timer.cancel()
		_state.timer=None

def _schedule_slide_change(duration=1):
	if not _state.timer or not _state.timer.is_alive():
		_state.timer=Timer(duration, goto_next_slide)
		_state.timer.daemon=True
		_state.timer.start()

def _show_slide(slide):
	_cancel_slide_change()

	if not slide.ready:
		logger.error('Show Slide skipped: %s', (slide, ))
	else:
		output=OutputPlugin.get_current()
		output.cancel_transition()
		if not slide.uptodate:
			with get_source().update_slide(slide):
				pass
		output.set_slide(slide)
		get_source().slide_done(slide)

	duration=slide.duration
	if duration > 0 and not _is_manual():
		_schedule_slide_change(duration)

def display_updated():
	return _update_display()

def goto_next_slide():
	slide=_get_next()
	_show_slide(slide)
	return True

def goto_previous_slide():
	slide=_get_previous()
	_show_slide(slide)
	return True

def goto_slide(gid, sid):
	if _set_current_slide(gid, sid):
		slide=_get_current_slide()
		_show_slide(slide)
		return True
	return False

def get_source():
	if not SourcePlugin.get_current():
		_next_source()
	return SourcePlugin.get_current()

def refresh_slide_cache(slide):
	with OutputPlugin.get_current().refresh_slide_cache(slide) as ret:
		return ret

