import os
import config
import json
from time import gmtime, strftime
import presenter

class Base(object):
	def __init__(self, attribs={}):
		self.attribs=attribs

	def __unicode__(self):
		return unicode(self.attribs)

	def __str__(self):
		return unicode(self)

	def __eq__(self, other):
		return isinstance(other, self.__class__) and (self.__dict__== other.__dict__)

	def __neq__(self, other):
		return not self == other

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
	def __init__(self, presentation=None, override=None, attribs={}, name=None):
		super(Display, self).__init__(attribs=attribs)
		if name: self.set_attrib('name', name)
		self.presentation=presentation
		if override: 
			self.override=override
		else:
			self.override=OverrideGroup()

	def __unicode__(self):
		return 'Display "%s" Updated: %s\n %s\n %s' % (self.get_name(), strftime('%x-%X', gmtime(self.get_metadata_updated_at())), unicode(self.override).replace('\n', '\n '), unicode(self.presentation).replace('\n', '\n '))

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
	def __init__(self,  groups=None, attribs={}):
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
		return 'Presentation "%s" Groups: %d Slides: %d\n %s' % ( self.get_name(), len(self), self.get_total_slides(), tmp.replace('\n', '\n '))

	def __str__(self):
		return unicode(self)

	def get_id(self):
		return self.get_attrib('id', 0)
	
	def get_total_slides(self):
		return self.get_attrib('total_slides', 0)
	
	def get_name(self):
		return self.get_attrib('name', 'unnamed')

	def get_groups(self):
		return self.groups

	def get_group(pos):
		return self[pos]

	def locate_group(self, id):
		for index, group in enumerate(self):
			if (group.get_id() == id):
				return index
		return -1


class Group(Base):
	def __init__(self, slides=None, attribs={}):
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
			tmp+=" %s\n" % unicode(i)
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
		for index, slide in enumerate(self):
			if (slide.get_id() == id):
				return index
		return -1

_masterslidestore={}
class Slide(Base):
	def __init__(self, attribs={}):
		super(Slide, self).__init__(attribs={})
		self.id=attribs.get('id', 0)
		global _masterslidestore
		_masterslidestore.update({self.id: attribs})
	
	def master(self):
		global _masterslidestore
		return _masterslidestore.get(self.id, None)

	def get_attrib(self, id, default=None):
		if id in self.attribs:
			return self.attribs[id]
		else:
			return self.master().get(id, default)

	def __eq__(self, other):
		r=isinstance(other, self.__class__) and (self.master() == other.master())
		return r

	def __getitem__(self, id):
		return self.get_attrib(id)

	def __len__(self):
		return len(self.attribs) + len(self.master())

	def __unicode__(self):
		return 'Slide "%s" (%s) Position %s file: %s (%s)' % ( self.get_name(), self.get_id(), self.get_position(), self.get_filename(), strftime('%X', gmtime(self.get_update_time())))

	def __str__(self):
		return unicode(self)

	def get_name(self):
		return self.get_attrib('name', "unnamed")

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

	def get_suffix(self):
		if (self.get_type()=='video'): 
			return 'mov'
		else:
			return 'png'

	def get_filename(self):
		return self.get_attrib('filename', '%s/%s.%s' % (presenter.Presenter().get_source().get_path(), self.get_id(), self.get_suffix()))

	def get_update_time(self):
		return self['updated_at']

	def is_ready(self):
		return self.get_attrib('ready', True)

	def is_uptodate(self):
		file=self.get_filename()
		if os.path.isfile(file):
			file_mtime=os.stat(file).st_mtime
			slide_mtime=self.get_update_time()
			#print "is_uptodate %s %s" % (strftime('%X', gmtime(slide_mtime)), strftime('%X', gmtime(file_mtime)))
			return (slide_mtime <= file_mtime)
		else:
			return False

	def is_valid(self):
		return True

	def is_override(self):
		return False

class OverrideGroup(Group):
	def __init__(self, slides=[], attribs={}):
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

