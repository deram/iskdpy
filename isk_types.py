import os
import config
import json
from time import localtime, strftime

class Base(object):
	def __init__(self, attribs={}):
		self.attribs=attribs

	def set_attribs(self, dict):
		self.attribs.update(dict)

	def set_attrib(self, name, value):
		self.attribs[name]=value

	def get_attrib(self, name, coalesce=None):
		try:
			return self.attribs[name]
		except KeyError:
			return coalesce


class Display(Base):
	def __init__(self, presentation=None, override=None, attribs=None, name=None):
		super(Display, self).__init__(attribs=attribs)
		self.set_attrib('name', name)
		self.presentation=presentation
		self.override=override

	def __unicode__(self):
		return 'Display "%s" Updated: %s\n\t%s\n\t%s' % (self.get_name(), strftime('%x-%X', localtime(self.get_metadata_updated_at())), unicode(self.override).replace('\n', '\n\t'), unicode(self.presentation).replace('\n', '\n\t'))

	def __str__(self):
		return unicode(self)

	def get_presentation(self):
		return self.presentation

	def get_override(self):
		return self.override

	def get_metadata_updated_at(self):
		return self.get_attrib('metadata_updated_at', 0)

	def get_name(self):
		return self.get_attrib('name', 'unnamed')

	def get_all_slides(self):
		tmp={}
		for group in self.presentation:
			for slide in group:
				tmp[ slide['id'] ] = slide
		for slide in self.override:
			tmp[ slide['id'] ] = slide
		return tmp


class Presentation(Base):
	def __init__(self,  groups=None, attribs=None):
		super(Presentation, self).__init__(attribs=attribs)
		self.groups=groups

	def __iter__(self):
		return self.groups.__iter__()

	def __getitem__(self, pos):
		return self.groups[pos]

	def __len__(self):
		return self.groups.__len__()

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="%s\n" % unicode(i)
		return 'Presentation "%s" Groups: %d Slides: %d\n\t%s' % ( self.get_name(), len(self), self.get_total_slides(), tmp.replace('\n', '\n\t'))

	def __str__(self):
		return unicode(self)

	def get_id(self):
		return self.get_attrib('id', 0)
	
	def get_total_slides(self):
		return self.get_attrib('total_slides', 0)
	
	def get_name(self):
		return self.get_attrib('name', 'unnamed_presentation')

	def get_groups(self):
		return self.groups

	def get_group(pos):
		return self[pos]

	def locate_group(self, id):
		index=0
		for group in self:
			if (group.get_id() == id):
				break
			index += 1
		return index % len(self)


class Group(Base):
	def __init__(self, slides=None, attribs=None):
		super(Group, self).__init__(attribs=attribs)
		self.slides=slides

	def __iter__(self):
		return self.slides.__iter__()

	def __getitem__(self, id):
		return self.slides[id]

	def __len__(self):
		return self.slides.__len__()

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\t%s\n" % unicode(i)
		return 'Group "%s" Position %s Slides: %d\n%s' % ( self.get_name(), self.get_position(), len(self), tmp)

	def __str__(self):
		return unicode(self)
	
	def get_id(self):
		return self.get_attrib('id', 0)
	
	def get_position(self):
		return self.get_attrib('position',  0)
	
	def get_name(self):
		return self.get_attrib('name',  "unnamed" )

	def get_slides(self):
		return self.slides

	def get_slide(id):
		return self[id]

	def locate_slide(self, id):
		index=0
		for slide in self:
			if (slide.get_id() == id):
				break
			index += 1
		return index % len(self)


class Slide(Base):
	def __init__(self, attribs=None):
		super(Slide, self).__init__(attribs=attribs)

	def __getitem__(self, id):
		return self.attribs[id]

	def __len__(self):
		return len(self.attribs)

	def __unicode__(self):
		return 'Slide "%s" Position %s file: %s' % ( self.get_name(), self.get_position(), self.get_filename())

	def __str__(self):
		return unicode(self)


	def get_name(self):
		return self.get_attrib('name', "unnamed_slide")

	def get_position(self):
		return self.get_attrib('position',  0)

	def get_id(self):
		return self.get_attrib('id',  0)

	def get_groupid(self):
		return self.get_attrib('group', 0)

	def get_duration(self):
		return self.get_attrib('duration', config.default_duration)

	def get_clock(self):
		return self.get_attrib('show_clock', True)

	def get_type(self):
		return self.get_attrib('type', '')

	def get_filename(self):
		if (self.get_type()=='video'):
			return '%d.mov' % self.get_id()
		return '%d.png' % self.get_id()

	def get_cachefile(self):
		return '%s/%s' % (config.cache_path, self.get_filename())

	def get_update_time(self):
		return self['updated_at']

	def is_ready(self):
		return self['ready']

	def is_cached(self):
        	file=self.get_cachefile()
		if os.path.isfile(file):
        		file_mtime=os.stat(file).st_mtime
			slide_mtime=self.get_update_time()
        		return (slide_mtime <= file_mtime or (not self.is_ready))
		else:
			return False

	def is_valid(self):
		return True

	def is_override(self):
		return False

class OverrideGroup(Group):
	def __init__(self, slides=None, attribs=None):
		super(OverrideGroup, self).__init__(attribs=attribs)
		self.slides=slides

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="t%s\n" % unicode(i)
		return 'Override Slides: %d\n%s' % ( len(self), tmp)

	def __len__(self):
		return len(self.slides)

	def __delitem__(self, key):
		return self.slides.__delitem__(key)

class OverrideSlide(Slide):
	def __unicode__(self):
		return 'OverrideSlide "%s" Position %s file: %s' % ( self.get_name(), self.get_position(), self.get_filename())

	def is_override(self):
		return True

	def get_override_id(self):
		return self.get_attrib('override_queue_id', 0)
		
	def is_valid(self):
		return self.is_ready()

