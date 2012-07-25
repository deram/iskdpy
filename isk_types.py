import os
import config

class Display():
	def __init__(self, data):
		self.data=data
		self.presentation=Presentation(self.data['presentation'])
		del self.data['presentation']
                self.override=OverrideGroup(self.data['override_queue'])
		del self.data['override_queue']

	def get_presentation(self):
		return self.presentation

	def get_override(self):
		return self.override

	def get_metadata_updated_at(self):
		return self.data['metadata_updated_at']

	def get_all_slides(self):
		tmp={}
		for group in self.presentation:
			for slide in group:
				tmp[ slide['id'] ] = slide
		for slide in self.override:
			tmp[ slide['id'] ] = slide
		return tmp

class Presentation():
	def __init__(self, data):
		self.data=data
		self.groups=[]
		for group in self.data['groups']:
			self.groups.append(Group(group))
		del self.data['groups']

	def __iter__(self):
		return self.groups.__iter__()

	def __getitem__(self, pos):
		return self.groups[pos]

	def __len__(self):
		return self.data['total_groups']

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\t%s\n" % unicode(i)
		return 'Presentation "%s" Groups: %d Slides: %d\n%s' % ( self.data['name'], self.data['total_groups'], self.data['total_slides'], tmp)

	def __str__(self):
		return unicode(self)

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


class Group():
	def __init__(self, data):
		self.data=data
		self.slides=[]
		for slide in self.data['slides']:
			self.slides.append(Slide(slide))
		del self.data['slides']

	def __iter__(self):
		return self.slides.__iter__()

	def __getitem__(self, id):
		return self.slides[id]

	def __len__(self):
		return self.data['total_slides']

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\t%s\n" % unicode(i)
		return 'Group "%s" Position %s Slides: %d\n%s' % ( self.data['name'], self.data['position'], self.data['total_slides'], tmp)

	def __str__(self):
		return unicode(self)
	
	def get_id(self):
		return self.data['id']

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


class Slide():
	def __init__(self, data):
		self.data=data

	def __getitem__(self, id):
		return self.data[id]

	def __len__(self):
		return len(self.data)

	def __unicode__(self):
		return 'Slide "%s" Position %s file: %s' % ( self.data['name'], self.data['position'], self.get_filename())

	def __str__(self):
		return unicode(self)


	def get_id(self):
		return self['id']

	def get_groupid(self):
		return self['group']

	def get_duration(self):
		return self['duration']

	def get_filename(self):
		return '%d.png' % self.get_id()

	def get_cachefile(self):
		return '%s/%d.png' % (config.cache_path, self.get_id())

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
	def __init__(self, data):
		self.slides=[]
		for slide in data:
			self.slides.append(OverrideSlide(slide))

	def __unicode__(self):
		tmp=""
		for i in self:
			tmp+="\t%s\n" % unicode(i)
		return 'Override Slides: %d\n%s' % ( self.data['total_slides'], tmp)

	def __len__(self):
		return len(self.slides)

	def __delitem__(self, key):
		return self.slides.__delitem__(key)

class OverrideSlide(Slide):
	def __unicode__(self):
		return 'OverrideSlide "%s" Position %s file: %s' % ( self.data['name'], self.data['position'], self.get_filename())

	def is_override(self):
		return True

	def get_override_id(self):
		return self.data['override_queue_id']
		
	def is_valid(self):
		return self.is_ready()


if __name__ == "__main__":
	import json
	json_data=open("cache/main.json").read()
	data = json.loads(json_data, "utf8")
	display=Display(data)

	for s in display.get_all_slides().values():
		print s.get_filename()
	print "DEBUG: %s" % display


