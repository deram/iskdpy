import logging
logger = logging.getLogger(__name__)

from .types import Slide
from .source import Source 
import gc
from . import config

first_time=True
control=None
display=None
group, slide = (0,-1)

def __connect(conf):
	global display
	source = Source.factory(conf.pop('source_name'), conf)
	source.connect()
	display=source.get_display()
	seek_to_presentation_beginning()

def register_control(ctrl):
	global control
	control=ctrl
	get_source().register_control(control)

def run_control():
	get_source().run_control()
	update_display()

def next_source():
	if len(config.sources):
		__connect(config.sources.pop())

def update_display():
	global control, display, slide, group
	if (get_source().update_display()):
		tmp=get_source().get_display()
		if not display == tmp:
			old=display
			if display.get_presentation().get_id() != tmp.get_presentation().get_id():
				logger.info("Presentation changed.")
				seek_to_presentation_beginning()
			else:
				try:
					pres=tmp.get_presentation()
					tmp_group = pres.locate_group(get_current_groupid(), old=group)
					tmp_slide = pres[tmp_group].locate_slide(get_current_slideid(), old=slide)
					group=tmp_group
					slide=tmp_slide
				except (IndexError, AttributeError):
					logger.warning("Current slide not in presentation, restarting presentation")
					seek_to_presentation_beginning()
			display=tmp
			if old.is_manual() and not tmp.is_manual():
				control.goto_next_slide()
			return True
	return False

def seek_to_presentation_beginning():
	global group, slide
	group=0
	slide=-1

def get_metadata_updated_at():
	global display
	return display.get_metadata_updated_at()

def get_current_groupid():
	return get_current_group().get_id()

def get_current_slideid():
	return get_current_slide().get_id()

def get_all_slides():
	global display
	return display.get_all_slides()

def get_presentation():
	global display
	return display.get_presentation()

def get_current_group():
	global group
	return get_presentation()[group]

def get_current_slide():
	global group, slide
	return get_presentation()[group][slide]

def set_current_slide(gid, sid):
	global slide, group
	tmp_group = get_presentation().locate_group(gid)
	tmp_slide = get_presentation()[group].locate_slide(sid)

	if tmp_group >= 0 and tmp_slide >=0 and get_presentation()[tmp_group][tmp_slide].is_valid():
		slide=tmp_slide
		group=tmp_group
		get_source().update_slide(get_current_slide())
		get_source().slide_done(get_current_slide()) #XXX move to somewhere more close to slide shown on screen
		return True
	return False

def seek_to_next_valid_slide_in_presentation():
	global group, slide
	n_groups = len(get_presentation())
	for i in xrange(get_presentation().get_total_slides()):
		n_slides = len(get_current_group())
		slide += 1
		if ( slide >= n_slides ):
			slide = 0
			group += 1
			if ( group >= n_groups ):
				slide = 0
				group = 0
				logger.info("Presentation wrapped")
				gc.collect()
				del gc.garbage[:]
			logger.info("Next: %s" % unicode(get_current_group()).split('\n', 1)[0])

		if ( len(get_current_group()) > 0 ):
			if get_current_slide().is_valid():
				return True
	return False

def seek_to_previous_valid_slide_in_presentation():
	global group, slide
	n_groups = len(get_presentation())
	for i in xrange(get_presentation().get_total_slides()):
		slide -= 1
		if ( slide < 0 ):
			group -= 1
			if ( group < 0 ):
				group = n_groups - 1
				logger.info("Presentation wrapped")
				gc.collect()
				del gc.garbage[:]
			logger.info("Prev: %s" % unicode(get_current_group()).split('\n', 1)[0])
			slide = len(get_current_group()) - 1

		if ( len(get_current_group()) > 0 ):
			if get_current_slide().is_valid():
				return True
	return False

def is_override():
	global display
	override=display.get_override()
	if len( override ):
		return override[0].is_valid()
	return False

def pop_override_slide():
	global display
	override=display.get_override()
	if len( override ):
		return override.pop(0)
	return False

def is_manual():
	global display
	return display.is_manual()

def is_empty_presentation():
	global display
	return ((display.get_presentation().get_total_slides()) == 0)

def get_next():
	return _get_slide('next')

def get_previous():
	return _get_slide('previous')

def _get_slide(slide='next'):
	global display, first_time
	if not display:
		if not update_display():
			logger.error("NO DISPLAY FROM SOURCE")
			return get_empty_slide()

	if ( not first_time ):
		update_display()
	else:
		first_time=False

	if ( is_override() ):
		ret = pop_override_slide()
	else:
		if (is_empty_presentation()):
			logger.warning("EMPTY PRESENTATION")
			return get_empty_slide()
		if slide=='next':
			seek_to_next_valid_slide_in_presentation()
		elif slide=='previous':
			seek_to_previous_valid_slide_in_presentation()
		ret = get_current_slide()

	get_source().update_slide(ret)
	get_source().slide_done(ret) #XXX move to somewhere more close to slide shown on screen
	logger.info("Next: %s" % ret)
	return ret

def get_source():
	if not Source.get_current():
		next_source()
	return Source.get_current()

def get_empty_slide():
	return Slide(config.empty_slide)

