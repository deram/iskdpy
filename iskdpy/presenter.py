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

	def seek_to_next(self):
		pos=self.presentation.next(self.pos)
		if pos is not None:
			if pos < self.pos:
				logger.info("Presentation wrapped")
			logger.debug("Next: %s", unicode(self.presentation[pos]))
			self.pos=pos

	def seek_to_prev(self):
		pos=self.presentation.prev(self.pos)
		if pos is not None:
			if pos > self.pos:
				logger.info("Presentation wrapped")
			logger.debug("Next: %s", unicode(self.presentation[pos]))
			self.pos=pos

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
		elif isinstance(slide, OverrideSlide):
			self._current_slide=slide
		elif slide is self.current_presentation_slide:
			self._current_slide=slide
		else:
			self.pos=self.presentation.locate_slide(sid=slide.id, gid=slide.group)
			if self.pos is None:
				self.seek_to_first()

	@property
	def current_presentation_slide(self):
		if self.pos >= 0:
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

def get_empty_slide():
	return OverrideSlide(**config.empty_slide)

def _connect(conf):
	source = SourcePlugin.factory(conf.pop('source_name'), conf)
	with source.connect():
		pass

def _next_source():
	if len(config.sources):
		_connect(config.sources.pop())

def _manual_mode_updated(old_state, new_state):
	if old_state.manual == new_state.manual:
		return
	if new_state.manual:
		_cancel_slide_change()
	else:
		_schedule_slide_change()

def _current_slide_updated(old_state, new_state):
	if old_state.current_slide.id == new_state.current_slide.id:
		if new_state.current_slide.ready and (old_state.current_slide <= new_state.current_slide):
			if old_state.current_slide.type != 'video':
				new_state.show_slide()

def _display_changed(old_state, new_state):
	if old_state.display != new_state.display:
		logger.info("Display changed.")
		new_state.seek_to_first()
		if config.future.get('fast_presentation_change', False):
			new_state.show_slide()
		return True
def _presentation_changed(old_state, new_state):
	if old_state.presentation.id != new_state.presentation.id:
		logger.info("Presentation changed.")
		new_state.seek_to_first()
		if config.future.get('fast_presentation_change', False):
			new_state.show_slide()
		return True
def _presentation_updated(old_state, new_state):
	if old_state.presentation <= new_state.presentation:
		new_state.current_slide=old_state.current_presentation_slide
		new_state.current_slide=old_state.current_slide
		if old_state.current_presentation_slide != new_state.current_presentation_slide:
			logger.warning("Current slide not in presentation, restarting presentation")
			_state.seek_to_first()
		return True

def _update_display(new_display=None):
	logger.debug("_update_display")
	if not new_display:
		if (get_source().update_display()):
			with get_source().get_display() as display:
				if display:
					logger.debug("Got display")
					new_display=display
				else:
					logger.error("Could not get display from source")
		else:
			logger.error("No display form source")

	old_state=_state
	new_state=_PresenterState(new_display)

	handled=_display_changed(old_state, new_state) or \
		_presentation_changed(old_state, new_state) or \
		_presentation_updated(old_state, new_state)
	if handled:
		_current_slide_updated(old_state, new_state)
		_manual_mode_updated(old_state, new_state)

		logger.debug('State Change "%s" -> "%s"', old_state, new_state)
		_state.update(new_state)
		return True
	return False

def _set_current_slide(gid, sid):
	_state.current_slide=Slide(id=sid, group=gid)
	return _state.current_slide.id==sid and _state.current_slide.group==gid

def _get_slide(direction='next'):
	if not _state.display:
		return get_empty_slide()
	if direction=='next':
		override=_state.display.pop_override_slide()
		if override:
			return override
	if not _state.presentation:
		logger.warning("EMPTY PRESENTATION")
		return get_empty_slide()
	if direction=='next':
		_state.seek_to_next()
	if direction=='previous':
		_state.seek_to_prev()
	return _state.current_slide

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
	logger.debug("_show_slide(%.100s)", slide)
	_cancel_slide_change()

	if not slide.ready:
		logger.error('Show Slide skipped: %s', (slide, ))
	else:
		output=OutputPlugin.get_current()
		output.cancel_transition()
		if not slide.uptodate:
			with get_source().update_slide(slide):
				pass
		with output.set_slide(slide):
			get_source().slide_done(slide)

	duration=slide.duration
	if duration > 0 and not _state.manual:
		_schedule_slide_change(duration)

def display_updated(display=None):
	logger.debug("display_updated(%.100s)", display)
	return _update_display(display)

def goto_next_slide():
	logger.debug("goto_next_slide()")
	slide=_get_slide('next')
	_show_slide(slide)
	return True

def goto_previous_slide():
	logger.debug("goto_previous_slide()")
	slide=_get_slide('previous')
	_show_slide(slide)
	return True

def goto_slide(gid, sid):
	logger.debug("goto_slide(G_%s, S_%s)", gid, sid)
	if _set_current_slide(gid, sid):
		slide=_state.current_slide
		_show_slide(slide)
		return True
	return False

def get_source():
	if not SourcePlugin.get_current():
		_next_source()
	return SourcePlugin.get_current()

def refresh_slide_cache(slide):
	logger.debug("refresh_slide_cache(%.100s)", slide)
	with OutputPlugin.get_current().refresh_slide_cache(slide) as ret:
		return ret

# presenter state
_state=_PresenterState()
