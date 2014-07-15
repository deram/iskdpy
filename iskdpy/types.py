import os
import config
from time import gmtime, strftime
from collections import deque

class Base(object):
	_fields=()
	_defaults=()
	_uid=('id')
	def __init__(self, *args, **kwargs):
		self.data=dict(zip(self._fields, self._defaults))
		if len(args) == len(self._fields):
			self.data.update(zip(self._fields, args))
		self.data.update(kwargs)

		uid=[self.__class__.__name__]
		for item in self._uid:
			uid.append(str(self.data[item]))
		self.uid=".".join(uid)

	def __getnewargs__(self):
		return (self.data, )

	def __getattr__(self, name):
		if name in self._fields:
			return self.data.get(name)

	def __getstate__(self):
		return self.data

	def __setstate__(self, data):
		self.data=data

	def __enter__(self):
		"Stub for testing without AsyncProcesses"
		return self
	def __exit__(self, *a, **kw):
		"Stub for testing without AsyncProcesses"
		pass

	def __repr__(self):
		return "\n  %s(%s)" % (self.__class__.__name__, str(self.__dict__))

	def __str__(self):
		return unicode(self)

	def __unicode__(self):
		return repr(self)

	def __eq__(self, other):
		return isinstance(other, self.__class__) and (self.uid == other.uid)
	def __ne__(self, other):
		return not self.__eq__(other)

	def __ge__(self, other):
		return (self == other) and (self.updated_at >= other.updated_at)
	def __le__(self, other):
		return (self == other) and (self.updated_at <= other.updated_at)

class SlideBase(Base):
	@property
	def suffix(self):
		if (self.type=='video'): 
			return 'mp4'
		else:
			return 'png'

	@property
	def filename(self):
		if not 'filename' in self.data:
			return '%s.%s' % (self.id, self.suffix)
		return self.data['filename']

	@filename.setter
	def filename(self, name):
		self.data['filename']=name

	@property
	def uptodate(self):
		filename=self.filename
		if os.path.isfile(filename):
			file_mtime=os.stat(filename).st_mtime
			slide_mtime=self.updated_at
			return (slide_mtime <= file_mtime)
		else:
			return False

	@property
	def valid(self):
		return self.ready

	@property
	def effect(self):
		try:
			return config.effect_ids[self.effect_id]
		except (KeyError, IndexError):
			return 'unknown'

	@property
	def is_override(self):
		return isinstance(self, OverrideSlide)

class Display(Base):
	_fields=('current_slide_id', 'name', 'presentation', 'created_at', 'manual', 'updated_at', 'state_updated_at', 'last_contact_at', 'id', 'metadata_updated_at', 'current_group_id', 'override_queue')
	_defaults=(0, "unnamed", None, 0, 0, 0, 0, 0, 0, 0, 0, ())
	_uid=('id', 'created_at', 'name')

	def __init__(self, *a, **kw):
		super(Display, self).__init__(*a, **kw)
		self.override_queue=deque(self.override_queue)

	def __getitem__(self, i):
		if self.override_queue:
			return self.override_queue[i]
	def __iter__(self):
		return iter(self.override_queue)

	def __unicode__(self):
		tmp=""
		for i in self.override_queue:
			tmp+="\n%s" % unicode(i)
		return 'Display "%s" (%d) Updated: %s\n Overrides: %d%s\n %s' % (self.name, self.id, strftime('%x-%X', gmtime(self.metadata_updated_at)), len(self.override_queue), tmp.replace('\n', '\n '), unicode(self.presentation).replace('\n', '\n '))

	@property
	def presentation(self):
		pres=self.data.get('presentation', None)
		if pres:
			return pres
		else:
			pres=Presentation()
			self.data['presentation']=pres
			return pres

	@property
	def all_slides(self):
		tmp={}
		for slide in self.presentation:
			tmp[slide.id] = slide
		for slide in self.override_queue:
			tmp[slide.id] = slide
		return tmp

	def pop_override_slide(self):
		if self.override_queue:
			if self.override_queue[0].valid:
				return self.override_queue.popleft()

class Presentation(Base):
	_fields=('name', 'created_at', 'updated_at', 'effect', 'slides', 'total_groups', 'id')
	_defaults=('unnamed', 0, 0, 0, (), 0, 0)
	_uid=('id', 'created_at')

	def __init__(self, *a, **kw):
		super(Presentation, self).__init__(*a, **kw)
		self.slides=tuple(self.slides)

	def __getitem__(self, i):
		return self.slides.__getitem__(i)
	def __len__(self):
		return self.slides.__len__()
	def __iter__(self):
		return iter(self.slides)

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\n%s" % unicode(i)
		return 'Presentation "%s" (%d) Slides: %d%s' % (self.name, self.id, self.total_slides, tmp.replace('\n', '\n '))

	@property
	def total_slides(self):
		return self.data.get('total_slides', len(self.slides))

	def locate_slide(self, sid, gid):
		for index, slide in enumerate(self):
			if (slide.group == gid and slide.id == sid):
				return index

	def next(self, old_pos, delta=1):
		pos=old_pos
		n_slides=self.total_slides
		for _ in xrange(n_slides):
			pos = (pos + delta) % n_slides
			if self[pos].valid:
				return pos

	def prev(self, old_pos):
		return self.next(old_pos, delta=-1)

class Slide(SlideBase):
	_fields=('group', 'name', 'deleted', 'created_at', 'updated_at', 'show_clock', 'group_name', 'duration', 'images_updated_at', 'effect_id', 'ready', 'master_group', 'type', 'id')
	_defaults=(0, "unnamed", 0, 0, 0, False, "unnamed", config.default_duration, 0, 0, True, 0, "image", 0)
	_uid=('id', 'group', 'created_at')

	def __unicode__(self):
		return 'Slide "%s" (%s) Group "%s" (%s) file: %s (%s)%s' % ( self.name, self.id, self.group_name, self.group, self.filename, strftime('%X', gmtime(self.updated_at)), '' if self.ready else ' NOT READY' )

	def __eq__(self, other):
		return isinstance(other, self.__class__) and (self.id == other.id) and (self.group == other.group)
class OverrideSlide(SlideBase):
	_fields=('name', 'deleted', 'created_at', 'updated_at', 'show_clock', 'group_name', 'duration', 'images_updated_at', 'effect_id', 'ready', 'override_queue_id', 'master_group', 'type', 'id')
	_defaults=("unnamed", 0, 0, 0, False, "unnamed", config.default_duration, 0, 0, True, 0, 0, "image", 0)
	_uid=('id', 'override_queue_id', 'created_at')

	def __unicode__(self):
		return 'OverrideSlide "%s" file: %s' % (self.name, self.filename)

	def __eq__(self, other):
		return isinstance(other, self.__class__) and (self.id == other.id) and (self.override_queue_id == other.override_queue_id)



