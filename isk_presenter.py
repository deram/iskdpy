from pprint import pprint
from isk_types import *
import cache
import gc

import json

class Presenter():
	current=None
	def __init__(self):
		self.group=0
		self.slide=-1
		json_data=cache.get_json()
		data = json.loads(json_data, "utf8")
		self.display=Display(data)
		#self.display=cache.fill_cache_and_get_display()

	def update_display(self):
		json_data=cache.get_json(reload=False)
		if json_data:
			data = json.loads(json_data, "utf8")
			if( self.get_metadata_updated_at() < data['metadata_updated_at'] ):
				print "Updating... was: %d new: %d" % (self.get_metadata_updated_at(), data['metadata_updated_at'])
				tmp=Display(data)
				grouppos = tmp.get_presentation().locate_group(self.get_current_groupid())
				slidepos = tmp.get_presentation()[grouppos].locate_slide(self.get_current_slideid())
				self.group=grouppos
				self.slide=slidepos
				del self.display
				self.display=tmp
			else:
				del data
				del json_data
		
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

	def get_next(self):
		if ( not self.slide < 0 ):
			self.update_display()
		if ( self.is_override() ):
			ret = self.pop_override_slide()
		else:
			self.seek_to_next_valid_slide_in_presentation()
			ret = self.get_current_slide()

		cache.refresh_slide(ret)
		if ret.is_override():
			cache.post_override_slide(ret)
		else:
			cache.post_current_slide(ret)
		print "Next: %s" % ret
		return ret

def CurrentPresenter():
	if (not Presenter.current):
		Presenter.current = Presenter()
	return Presenter.current

