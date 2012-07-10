import config

class Presentation():
	def __init__(self, data):
		self.data=data
		self.groups=[]
		for group in self.data['groups']:
			self.groups.append(Group(group))
		del self.data['groups']

	def __iter__(self):
		return self.groups.__iter__()

	def __getitem__(self, id):
		return self.groups[id]

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

	def get_group(id):
		return self[id]

	def get_all_slides(self):
		tmp={}
		for g in self:
			for s in g:
				tmp[ s['id'] ] = s
		return tmp



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

	def get_slides(self):
		return self.slides

	def get_slide(id):
		return self[id]

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

	def get_filename(self):
		return '%d.png' % self.get_id()

	def get_cachefile(self):
		return '%s/%d.png' % (config.cache_path, self.get_id())

	def valid(self):
		return True

if __name__ == "__main__":
	import json
	json_data=open("cache/main.json").read()
	data = json.loads(json_data, "utf8")
	presentation=Presentation(data)

	for s in presentation.get_all_slides().values():
		print s.get_filename()
	print "DEBUG: %s" % presentation


