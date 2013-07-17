from . import types
from .source import Source 
import gc
import json
from . import config

class _Presenter():
	__current=None
	def __init__(self):
		self.first_time=True
		self.seek_to_presentation_beginning()

	def __connect(self, conf):
		source_name=conf.pop('source_name')
		self.source=Source.factory(source_name)(conf)
		self.source.connect()
		self.display=self.source.get_display()

	def next_source(self):
		if len(config.sources):
			self.__connect(config.sources.pop())

	def update_display(self):
		if (self.source.update_display()):
			tmp=self.source.get_display()
			if not self.display == tmp:
				#print "%s" % tmp
				try:
					gid=self.get_current_groupid()
					sid=self.get_current_slideid()
					pres=tmp.get_presentation()
					grouppos = pres.locate_group(gid)
					slidepos = pres[grouppos].locate_slide(sid)
					self.group=grouppos
					self.slide=slidepos
					if self.display.get_presentation().get_id() != tmp.get_presentation().get_id():
						print "Presentation changed."
				except (IndexError, AttributeError):
					self.seek_to_presentation_beginning()
				self.display=tmp
				return True
		return False

	def seek_to_presentation_beginning(self):
		self.group=0
		self.slide=-1

	def get_metadata_updated_at(self):
		return self.display.get_metadata_updated_at()

	def get_current_groupid(self):
		return self.get_current_group().get_id()

	def get_current_slideid(self):
		return self.get_current_slide().get_id()

	def get_all_slides(self):
		return self.display.get_all_slides()

	def get_presentation(self):
		return self.display.get_presentation()

	def get_current_group(self):
		return self.get_presentation()[self.group]

	def get_current_slide(self):
		return self.get_presentation()[self.group][self.slide]

	def set_current_slide(self, group_id, slide_id):
		group=False
		slide=False

		for i, item in enumerate(self.get_presentation()):
			if item.get_id()==group_id:
				group=i
				break

		for i, item in enumerate(self.get_presentation()[group]):
			if item.get_id()==slide_id:
				slide=i
				break
		if group >= 0 and slide >=0 and self.get_presentation()[group][slide].is_valid():
			self.slide=slide
			self.group=group
			self.source.update_slide(self.get_current_slide())
			self.source.slide_done(self.get_current_slide()) #XXX move to somewhere more close to slide shown on screen
			return True
		return False


	def seek_to_next_valid_slide_in_presentation(self):
		valid_slide=False
		while (not valid_slide):
			n_groups = len(self.get_presentation())
			n_slides = len(self.get_current_group())
			self.slide += 1
			if ( self.slide >= n_slides ):
				self.slide = 0
				self.group += 1
				if ( self.group >= n_groups ):
					self.slide = 0
					self.group = 0
					print "Presentation wrapped"
					gc.collect()
					del gc.garbage[:]
				print "Next: %s" % unicode(self.get_current_group()).split('\n', 1)[0]

			if ( len(self.get_current_group()) > 0 ):
				valid_slide = self.get_current_slide().is_valid()

	def is_override(self):
		override=self.display.get_override()
		if len( override ):
			return override[0].is_valid()
		return False

	def pop_override_slide(self):
		override=self.display.get_override()
		if len( override ):
			ret=override[0]
			del override[0]
			return ret
		return False

	def is_empty_presentation(self):
		return ((self.display.get_presentation().get_total_slides()) == 0)

	def get_next(self):
		if not self.display:
			if not self.update_display():
				print "NO DISPLAY FROM SOURCE"
				return self.get_empty_slide()

		if ( not self.first_time ):
			self.update_display()
		else:
			self.first_time=False

		if ( self.is_override() ):
			ret = self.pop_override_slide()
		else:
			if (self.is_empty_presentation()):
				print "EMPTY PRESENTATION"
				return self.get_empty_slide()
			self.seek_to_next_valid_slide_in_presentation()
			ret = self.get_current_slide()

		self.source.update_slide(ret)
		self.source.slide_done(ret) #XXX move to somewhere more close to slide shown on screen
		print "Next: %s" % ret
		return ret

	def get_source(self):
		return self.source

	def get_empty_slide(self):
		return types.Slide(config.empty_slide)

_presenter=None
def Presenter():
	global _presenter
	if (not _presenter):
		print "creating singleton entity"
		_presenter=_Presenter()
		_presenter.next_source()
	return _presenter

