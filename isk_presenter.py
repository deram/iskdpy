from pprint import pprint
import isk_types
from isk_source import Source 
import gc

import json

class Presenter():
	__current=None
	def __init__(self):
		self.first_time=True
		self.seek_to_presentation_beginning()

	def __connect(self):
		self.source=Source.factory()()
		self.source.connect()
		self.display=self.source.get_display()

	def update_display(self):
		if (self.source.update_display()):
			tmp=self.source.get_display()
			#print "%s" % tmp
			try:
				gid=self.get_current_groupid()
				sid=self.get_current_slideid()
				pres=tmp.get_presentation()
				grouppos = pres.locate_group(gid)
				slidepos = pres[grouppos].locate_slide(sid)
				self.group=grouppos
				self.slide=slidepos
			except IndexError:
				self.seek_to_presentation_beginning()
			if self.display.get_presentation().get_id() != tmp.get_presentation().get_id():
				print "Presentation changed."
			self.display=tmp

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
					#pprint(gc.garbage)
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
		return isk_types.Slide({'filename': 'base.png', 'duration': 5, 'type': 'image', 'clock':False})

	@classmethod
	def current(cls):
		if (not cls.__current):
			print "creating singleton entity"
			cls.__current = Presenter()
			cls.__current.__connect()
		return cls.__current

