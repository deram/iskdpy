import os
import config
from time import gmtime, strftime

class Base(object):
	def __init__(self, attribs=None):
		if attribs:
			self.attribs=attribs
		else:
			self.attribs={}

	def __str__(self):
		return unicode(self)

	def __eq__(self, other):
		return isinstance(other, self.__class__) and (self.__dict__== other.__dict__)

	def __ne__(self, other):
		return not self.__eq__(other)

	def set_attribs(self, dict):
		self.attribs.update(dict)

	def set_attrib(self, name, value):
		self.attribs[name]=value

	def get_attrib(self, name, coalesce=None):
		return self.attribs.get(name, coalesce)

	def get_id(self):
		return self.get_attrib('id',  0)

class Display(Base):
	def __init__(self, presentation=None, override=None, attribs=None, name=None):
		super(Display, self).__init__(attribs=attribs)
		if name: 
			self.set_attrib('name', name)
		if override:
			self.override=override
		else:
			self.override=[]
		if presentation:
			self.presentation=presentation
		else:
			self.presentation=Presentation()

	def __unicode__(self):
		tmp=""
		for i in self.override:
			tmp+="\n%s" % unicode(i)
		return 'Display "%s" (%d) Updated: %s\n Overrides: %d%s\n %s' % (self.get_name(), self.get_id(), strftime('%x-%X', gmtime(self.get_metadata_updated_at())), len(self.get_override()), tmp.replace('\n', '\n '), unicode(self.get_presentation()).replace('\n', '\n '))

	def get_presentation(self):
		return self.presentation

	def get_override(self):
		return self.override

	def get_metadata_updated_at(self):
		return self.get_attrib('metadata_updated_at', 0)

	def get_updated_at(self):
		return self.get_attrib('updated_at', 0)

	def get_name(self):
		return self.get_attrib('name', 'unnamed')

	def get_all_slides(self):
		tmp={}
		for slide in self.presentation.slides:
			tmp[ slide['id'] ] = slide
		for slide in self.override:
			tmp[ slide['id'] ] = slide
		return tmp

	def is_manual(self):
		return self.get_attrib('manual', False)


class Presentation(Base):
	def __init__(self,  slides=None, attribs=None):
		super(Presentation, self).__init__(attribs=attribs)
		if slides:
			self.slides=slides
		else:
			self.slides=[]

	def __iter__(self):
		return self.slides.__iter__()

	def __getitem__(self, pos):
		return self.slides[pos]

	def __len__(self):
		return len(self.slides)

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\n%s" % unicode(i)
		return 'Presentation "%s" (%d) Slides: %d%s' % (self.get_name(), self.get_id(), self.get_total_slides(), tmp.replace('\n', '\n '))

	def get_total_slides(self):
		total=self.get_attrib('total_slides', 0)
		if total==0:
			total=len(self)
			self.set_attrib('total_slides', total)
		return total
	
	def get_name(self):
		return self.get_attrib('name', 'unnamed')

	def locate_slide(self, sid, gid):
		for index, slide in enumerate(self):
			if (slide.get_groupid() == gid and slide.get_id() == sid):
				return index
		return None

class Slide(Base):
	def __init__(self, attribs=config.empty_slide):
		super(Slide, self).__init__(attribs=attribs)
	
	def __eq__(self, other):
		r=isinstance(other, self.__class__) and (self.attribs == other.attribs)
		return r

	def __getitem__(self, id):
		return self.get_attrib(id)

	def __len__(self):
		return len(self.attribs)

	def __unicode__(self):
		return 'Slide "%s" (%s) Group "%s" (%s) Position %s file: %s (%s) %s' % ( self.get_name(), self.get_id(), self.get_groupname(), self.get_groupid(), self.get_position(), self.get_filename(), strftime('%X', gmtime(self.get_update_time())), '' if self.is_ready() else 'NOT READY' )

	def get_name(self):
		return self.get_attrib('name', "unnamed")

	def get_position(self):
		return self.get_attrib('position',  0)

	def get_groupid(self):
		return self.get_attrib('group', 0)

	def get_groupname(self):
		return self.get_attrib('group_name', '')

	def get_duration(self):
		return self.get_attrib('duration', config.default_duration)

	def get_clock(self):
		return self.get_attrib('show_clock', True)

	def get_type(self):
		return self.get_attrib('type', '')

	def get_effect(self):
		try:
			return config.effect_ids[self.get_attrib('effect_id', 0)]
		except (KeyError, IndexError):
			return 'unknown'

	def get_suffix(self):
		if (self.get_type()=='video'): 
			return 'mp4'
		else:
			return 'png'

	def get_filename(self):
		return self.get_attrib('filename', '%s.%s' % (self.get_id(), self.get_suffix()))

	def get_update_time(self):
		return self.get_attrib('updated_at', 0)

	def is_ready(self):
		return self.get_attrib('ready', True)

	def is_uptodate(self):
		file=self.get_filename()
		if os.path.isfile(file):
			file_mtime=os.stat(file).st_mtime
			slide_mtime=self.get_update_time()
			return (slide_mtime <= file_mtime)
		else:
			return False

	def is_valid(self):
		return True

	def is_override(self):
		return False

class OverrideSlide(Slide):
	def __unicode__(self):
		return 'OverrideSlide "%s" Position %s file: %s' % ( self.get_name(), self.get_position(), self.get_filename())

	def is_override(self):
		return True

	def get_override_id(self):
		return self.get_attrib('override_queue_id', 0)
		
	def is_valid(self):
		return self.is_ready()

