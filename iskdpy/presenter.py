import logging
logger = logging.getLogger(__name__)

from .types import Slide
from .source import Source 
from .output import OutputPlugin 
#import gc
from . import config

from .utils.queued_thread import QueuedThread
from threading import Timer

thread=QueuedThread()
thread.start()

timer=None
display=None
gpos, spos = (0,-1)

def __connect(conf):
	global display
	source = Source.factory(conf.pop('source_name'), conf)
	source.connect()
	display=source.get_display()
	__seek_to_presentation_beginning()

def __next_source():
	if len(config.sources):
		__connect(config.sources.pop())

def __handle_manual_mode(old, new):
	if old != new:
		if new:
			__cancel_slide_change()
		else:
			__schedule_slide_change()

def __handle_current_slide_updated(old, new):
	if old.get_id() == new.get_id():
		if new.is_ready() and (not old.is_ready() or old.get_update_time() < new.get_update_time()):
			if old.get_type() != 'video':
				 __show_slide(new)

def __update_display():
	global display, spos, gpos
	if (get_source().update_display()):
		new_display=get_source().get_display()
		if not display == new_display:
			old_display=display
			old_slide=__get_current_slide()
			if display.get_presentation().get_id() != old_display.get_presentation().get_id():
				logger.info("Presentation changed.")
				__seek_to_presentation_beginning()
			else:
				try:
					pres=new_display.get_presentation()
					new_gpos = pres.locate_group(__get_current_groupid(), old=gpos)
					new_spos = pres[new_gpos].locate_slide(__get_current_slideid(), old=spos)
				except (IndexError, AttributeError):
					logger.warning("Current slide not in presentation, restarting presentation")
					__seek_to_presentation_beginning()
				else:
					gpos=new_gpos
					spos=new_spos
			display=new_display
			__handle_manual_mode(old_display.is_manual(), new_display.is_manual())
			__handle_current_slide_updated(old_slide, __get_current_slide())
			return True
	return False

def __seek_to_presentation_beginning():
	global gpos, spos
	gpos, spos = (0,-1)

def __get_current_groupid():
	return __get_current_group().get_id()

def __get_current_slideid():
	return __get_current_slide().get_id()

def __get_presentation():
	global display
	return display.get_presentation()

def __get_current_group():
	global gpos
	return __get_presentation()[gpos]

def __get_current_slide():
	global gpos, spos
	return __get_presentation()[gpos][spos]

def __set_current_slide(gid, sid):
	global spos, gpos
	new_gpos = __get_presentation().locate_group(gid)
	new_spos = __get_presentation()[new_gpos].locate_slide(sid)

	try:
		if __get_presentation()[new_gpos][new_spos].is_valid():
			spos=new_spos
			gpos=new_gpos
			return True
	except (IndexError, AttributeError):
		logger.warning("Slide not in presentation. Not changing.")
	return False

def __seek_to_next_valid_slide_in_presentation():
	global gpos, spos
	n_groups = len(__get_presentation())
	for i in xrange(__get_presentation().get_total_slides()):
		n_slides = len(__get_current_group())
		spos += 1
		if ( spos >= n_slides ):
			spos = 0
			gpos += 1
			if ( gpos >= n_groups ):
				spos = 0
				gpos = 0
				logger.info("Presentation wrapped")
			logger.info("Next: %s" % unicode(__get_current_group()).split('\n', 1)[0])

		if ( len(__get_current_group()) > 0 ):
			if __get_current_slide().is_valid():
				return True
	return False

def __seek_to_previous_valid_slide_in_presentation():
	global gpos, spos
	n_groups = len(__get_presentation())
	for i in xrange(__get_presentation().get_total_slides()):
		spos -= 1
		if ( spos < 0 ):
			gpos -= 1
			if ( gpos < 0 ):
				gpos = n_groups - 1
				logger.info("Presentation wrapped")
			logger.info("Prev: %s" % unicode(__get_current_group()).split('\n', 1)[0])
			spos = len(__get_current_group()) - 1

		if ( len(__get_current_group()) > 0 ):
			if __get_current_slide().is_valid():
				return True
	return False

def __is_override():
	global display
	override=display.get_override()
	if len( override ):
		return override[0].is_valid()
	return False

def __pop_override_slide():
	global display
	override=display.get_override()
	if len( override ):
		ret = override[0]
		del override[0]
		return ret
	return False

def __is_manual():
	global display
	return display and display.is_manual()

def __is_empty_presentation():
	global display
	return ((display.get_presentation().get_total_slides()) == 0)

def __get_next():
	return __get_slide('next')

def __get_previous():
	return __get_slide('previous')

def __get_slide(slide='next'):
	global display
	if not display:
		if not __update_display():
			logger.error("NO DISPLAY FROM SOURCE")
			return Slide()
	if ( __is_override() ):
		ret = __pop_override_slide()
	else:
		if (__is_empty_presentation()):
			logger.warning("EMPTY PRESENTATION")
			return Slide()
		if slide=='next':
			__seek_to_next_valid_slide_in_presentation()
		elif slide=='previous':
			__seek_to_previous_valid_slide_in_presentation()
		ret = __get_current_slide()

	logger.info("Next: %s" % ret)
	return ret

def __cancel_slide_change():
	global timer
	if timer:
		timer.cancel()
		timer=None

def __schedule_slide_change(duration=1):
	global timer
	if not timer:
		timer=Timer(duration, goto_next_slide)
		timer.start()

def __show_slide(slide):
	__cancel_slide_change()

	if not slide.is_ready():
		logger.error('Show Slide skipped: %s' % (slide, ))
	else:
		if not slide.is_uptodate():
			repr(get_source().update_slide(slide)) # repr makes possibly async call finish
		output=OutputPlugin.get_current()
		output.set_slide(slide)
		get_source().slide_done(slide)

	duration=slide.get_duration()
	if duration > 0 and not __is_manual():
		__schedule_slide_change(duration)

@thread.decorate
def display_updated():
	__update_display()

@thread.decorate
def goto_next_slide():
	slide=__get_next()
	__show_slide(slide)

@thread.decorate
def goto_previous_slide():
	slide=__get_previous()
	__show_slide(slide)

@thread.decorate
def goto_slide(gid, sid):
	if __set_current_slide(gid, sid):
		slide=__get_current_slide()
		__show_slide(slide)

@thread.decorate
def get_source():
	if not Source.get_current():
		__next_source()
	return Source.get_current()

#@thread.decorate
def refresh_slide_cache(slide):
	return OutputPlugin.get_current().refresh_slide_cache(slide).get()
	pass

