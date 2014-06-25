import logging
logger = logging.getLogger(__name__)

from .types import Slide, Display
from .source import Source
from .output import OutputPlugin 
#import gc
from . import config

from threading import Timer


timer=None
display=None
pos=-1

def _connect(conf):
	global display
	source = Source.factory(conf.pop('source_name'), conf)
	if source.connect():
		with source.get_display() as disp:
			if disp:
				display=disp
				_seek_to_presentation_beginning()

def _next_source():
	if len(config.sources):
		_connect(config.sources.pop())

def _handle_manual_mode(old, new):
	if new:
		if old:
			if old.is_manual() == new.is_manual():
				return
		if new.is_manual():
			_cancel_slide_change()
		else:
			_schedule_slide_change()

def _handle_current_slide_updated(old, new):
	if old.get_id() == new.get_id():
		if new.is_ready() and (not old.is_ready() or old.get_update_time() < new.get_update_time()):
			if old.get_type() != 'video':
				 _show_slide(new)

def _handle_display_changed(old, new):
	if not old == new:
		if not old or old.get_name() != new.get_name():
			logger.info("Display changed.")
			_seek_to_presentation_beginning()
			return True
		elif old.get_presentation().get_id() != new.get_presentation().get_id():
			logger.info("Presentation changed.")
			_seek_to_presentation_beginning()
			return True
	return False


def _handle_presentation_updated(old, new):
	global pos
	try:
		slide=_get_current_slide()
		new_pos = new.locate_slide(slide.get_id(), slide.get_groupid()) 
	except (IndexError, AttributeError):
		logger.warning("Current slide not in presentation, restarting presentation")
		_seek_to_presentation_beginning()
	else:
		pos=new_pos
	return True

def _update_display():
	global display
	if (get_source().update_display()):
		new_display=None
		with get_source().get_display() as disp:
			if disp:
				new_display=disp
		old_display=display
		if _handle_display_changed(old_display, new_display):
			display=new_display
		elif _handle_presentation_updated(old_display.get_presentation(), new_display.get_presentation()):
			old_slide=_get_current_slide()
			display=new_display
			_handle_current_slide_updated(old_slide, _get_current_slide())
	
		_handle_manual_mode(old_display, new_display)
		return True
	return False

def _seek_to_presentation_beginning():
	global pos
	pos = -1

def _get_presentation():
	global display
	return display.get_presentation()

def _get_current_slide():
	global pos
	try:
		return _get_presentation()[pos]
	except (IndexError, AttributeError, TypeError):
		logger.warning("Current slide not existing")
		return Slide()

def _set_current_slide(gid, sid):
	global pos
	try:
		new_pos = _get_presentation().locate_slide(sid, gid)

		if _get_presentation()[new_pos].is_valid():
			pos=new_pos
			return True
	except (IndexError, AttributeError, TypeError):
		logger.warning("Slide not in presentationi (%s,%s). Not changing."%(gid,sid))
	return False

def _seek_to_next_valid_slide_in_presentation():
	global pos
	n_slides = len(_get_presentation())
	for i in xrange(_get_presentation().get_total_slides()):
		pos += 1
		if ( pos >= n_slides ):
			pos = 0
			logger.info("Presentation wrapped")
		logger.debug("Next: %s" % unicode(_get_current_slide()).split('\n', 1)[0])

		if _get_current_slide().is_valid():
			return True
	return False

def _seek_to_previous_valid_slide_in_presentation():
	global pos
	n_slides = len(_get_presentation())
	for i in xrange(_get_presentation().get_total_slides()):
		pos -= 1
		if ( pos < 0 ):
			pos = n_slides - 1
			logger.info("Presentation wrapped")
		logger.debug("Prev: %s" % unicode(_get_current_slide()).split('\n', 1)[0])

		if _get_current_slide().is_valid():
			return True
	return False

def _is_override():
	global display
	override=display.get_override()
	if len( override ):
		return override[0].is_valid()
	return False

def _pop_override_slide():
	global display
	override=display.get_override()
	if len( override ):
		ret = override[0]
		del override[0]
		return ret
	return False

def _is_manual():
	global display
	return display and display.is_manual()

def _is_empty_presentation():
	global display
	return ((display.get_presentation().get_total_slides()) == 0)

def _get_next():
	return _get_slide('next')

def _get_previous():
	return _get_slide('previous')

def _get_slide(slide='next'):
	global display
	if not display:
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

	logger.debug("Next: %s" % ret)
	return ret

def _cancel_slide_change():
	global timer
	if timer:
		timer.cancel()
		timer=None

def _schedule_slide_change(duration=1):
	global timer
	if not timer:
		timer=Timer(duration, goto_next_slide)
		timer.daemon=True
		timer.start()

def _show_slide(slide):
	_cancel_slide_change()

	if not slide.is_ready():
		logger.error('Show Slide skipped: %s' % (slide, ))
	else:
		if not slide.is_uptodate():
			with get_source().update_slide(slide):
				pass
		output=OutputPlugin.get_current()
		output.set_slide(slide)
		get_source().slide_done(slide)

	duration=slide.get_duration()
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
	if not Source.get_current():
		_next_source()
	return Source.get_current()

def refresh_slide_cache(slide):
	with OutputPlugin.get_current().refresh_slide_cache(slide) as ret:
		return ret

